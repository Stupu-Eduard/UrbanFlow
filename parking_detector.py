#!/usr/bin/env python3
"""
UrbanFlowAI - Universal Parking System
Combines adaptive detection + behavior learning + grid inference

Strategies applied recursively:
1. Try normal car detection (classes 2,3,5,7)
2. If few/no cars → try phones (class 67) for overhead
3. If still nothing → try small objects (24,26,28,31)
4. Track stationary vehicles over time
5. Cluster into parking spots
6. Infer empty spots from grid pattern

Works on ANY camera angle: overhead, angled, street-level!
"""

import cv2
import yaml
import numpy as np
import time
from ultralytics import YOLO
from collections import defaultdict, deque
from datetime import datetime
import redis
from sklearn.cluster import DBSCAN
import json
from metrics_logger import MetricsLogger

class ParkingDetector:
    def __init__(self, config_path="config_parking.yaml"):
        """Initialize parking detector."""
        print("🅿️  UrbanFlowAI - Parking Detector")
        print("   (Adaptive Detection + Behavior Learning + Grid Inference)")
        print("=" * 70)
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load YOLO model
        print(f"📦 Loading model: {self.config['model']['weights']}...")
        self.model = YOLO(self.config['model']['weights'])
        
        # GPU detection
        device = self.config['model'].get('device', 'cuda')
        if device == 'cuda':
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                print(f"✓ Using GPU: {gpu_name}")
        
        # Redis connection
        self.redis_client = None
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            self.redis_client.ping()
            print("✓ Connected to Redis")
        except Exception as e:
            print(f"⚠ Warning: Could not connect to Redis")
        
        # Detection strategies (tried recursively)
        self.detection_strategies = [
            {'name': 'Normal Vehicles', 'classes': [2, 3, 5, 7], 'threshold': 5},
            {'name': 'Overhead (Phones)', 'classes': [67], 'threshold': 3},
            {'name': 'Small Objects', 'classes': [24, 26, 28, 31], 'threshold': 2},
        ]
        self.active_strategy = None
        
        # Learning phase
        self.learning_mode = True
        self.learning_duration = 60
        self.learning_start_time = None
        
        # Car tracking
        self.car_history = defaultdict(lambda: deque(maxlen=90))
        self.car_first_seen = {}
        self.car_last_moved = {}
        self.stationary_positions = []
        
        # Parking spots
        self.parking_spots = []
        self.spot_occupancy = {}
        
        # Parameters
        self.iou_threshold = 0.3
        self.stationary_threshold = 10
        self.min_stationary_frames = 60
        self.min_parking_duration = 5.0
        self.cluster_eps = 80
        self.cluster_min_samples = 3
        
        self.display_preview = self.config['video'].get('display_preview', True)
        
        # Metrics logger
        self.metrics_logger = MetricsLogger()
        
        print("=" * 70)
    
    def adaptive_detect(self, frame):
        """Recursively try detection strategies until we find vehicles."""
        # If we already have an active strategy, use it
        if self.active_strategy:
            results = self.model(
                frame,
                imgsz=1280,
                conf=self.config['model']['confidence'],
                classes=self.active_strategy['classes'],
                verbose=False
            )[0]
            return results, self.active_strategy['name']
        
        # Try each strategy recursively
        for strategy in self.detection_strategies:
            results = self.model(
                frame,
                imgsz=1280,
                conf=self.config['model']['confidence'],
                classes=strategy['classes'],
                verbose=False
            )[0]
            
            num_detected = len(results.boxes)
            
            # If we found enough objects, lock this strategy
            if num_detected >= strategy['threshold']:
                self.active_strategy = strategy
                print(f"\n🎯 STRATEGY LOCKED: {strategy['name']}")
                print(f"   Classes: {strategy['classes']}")
                print(f"   Initial detections: {num_detected}")
                return results, strategy['name']
        
        # Fallback: use first strategy even if no detections
        self.active_strategy = self.detection_strategies[0]
        results = self.model(
            frame,
            imgsz=1280,
            conf=self.config['model']['confidence'],
            classes=self.active_strategy['classes'],
            verbose=False
        )[0]
        return results, self.active_strategy['name']
    
    def calculate_iou(self, box1, box2):
        """Calculate IoU between two boxes."""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def match_detections_to_history(self, detections, prev_detections):
        """Match detections to previous frame."""
        matches = {}
        for curr_id, curr_box in enumerate(detections):
            best_iou = 0
            best_prev_id = -1
            for prev_id, prev_box in prev_detections.items():
                if not prev_box:
                    continue
                iou = self.calculate_iou(curr_box['bbox'], prev_box['bbox'])
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_prev_id = prev_id
            matches[curr_id] = best_prev_id
        return matches
    
    def is_stationary(self, car_id, current_time):
        """Check if car is stationary."""
        if len(self.car_history[car_id]) < self.min_stationary_frames:
            return False
        
        if car_id in self.car_first_seen:
            duration = (current_time - self.car_first_seen[car_id]).total_seconds()
            if duration < self.min_parking_duration:
                return False
        
        positions = list(self.car_history[car_id])
        recent = positions[-self.min_stationary_frames:]
        xs = [p['center'][0] for p in recent]
        ys = [p['center'][1] for p in recent]
        
        return (max(xs) - min(xs) < self.stationary_threshold and 
                max(ys) - min(ys) < self.stationary_threshold)
    
    def infer_parking_grid(self, occupied_spots):
        """Infer empty spots from grid pattern."""
        if len(occupied_spots) < 3:
            return []
        
        centers = np.array([[s['center'][0], s['center'][1]] for s in occupied_spots])
        avg_width = np.mean([s['width'] for s in occupied_spots])
        avg_height = np.mean([s['height'] for s in occupied_spots])
        
        inferred_spots = []
        
        for i, spot in enumerate(occupied_spots):
            cx, cy = spot['center']
            
            neighbors = []
            for j, other in enumerate(occupied_spots):
                if i == j:
                    continue
                ox, oy = other['center']
                dist = np.sqrt((cx - ox)**2 + (cy - oy)**2)
                
                if 50 < dist < 250:
                    neighbors.append({
                        'distance': dist,
                        'dx': ox - cx,
                        'dy': oy - cy
                    })
            
            for neighbor in neighbors:
                if neighbor['distance'] > avg_width * 2.5:
                    num_gaps = int(neighbor['distance'] / (avg_width * 1.3))
                    
                    for gap in range(1, num_gaps):
                        frac = gap / num_gaps
                        inferred_cx = int(cx + neighbor['dx'] * frac)
                        inferred_cy = int(cy + neighbor['dy'] * frac)
                        
                        overlaps = False
                        for existing in occupied_spots:
                            ex, ey = existing['center']
                            if np.sqrt((inferred_cx - ex)**2 + (inferred_cy - ey)**2) < avg_width * 0.5:
                                overlaps = True
                                break
                        
                        if not overlaps:
                            inferred_spots.append({
                                'center': (inferred_cx, inferred_cy),
                                'width': int(avg_width),
                                'height': int(avg_height),
                                'inferred': True
                            })
        
        return inferred_spots
    
    def learn_parking_spots(self):
        """Learn spots from stationary positions."""
        if len(self.stationary_positions) < self.cluster_min_samples:
            print(f"⚠️  Not enough data ({len(self.stationary_positions)} positions)")
            return
        
        print(f"\n🧠 Learning from {len(self.stationary_positions)} observations...")
        
        positions = np.array([[p['center'][0], p['center'][1]] 
                             for p in self.stationary_positions])
        
        clustering = DBSCAN(eps=self.cluster_eps, min_samples=self.cluster_min_samples)
        labels = clustering.fit_predict(positions)
        
        unique_labels = set(labels)
        unique_labels.discard(-1)
        
        occupied_spots = []
        for label in unique_labels:
            cluster_boxes = [self.stationary_positions[i] 
                           for i, l in enumerate(labels) if l == label]
            cluster_points = positions[labels == label]
            
            center_x = np.mean(cluster_points[:, 0])
            center_y = np.mean(cluster_points[:, 1])
            avg_width = np.mean([b['width'] for b in cluster_boxes])
            avg_height = np.mean([b['height'] for b in cluster_boxes])
            
            occupied_spots.append({
                'center': (int(center_x), int(center_y)),
                'width': int(avg_width),
                'height': int(avg_height),
                'inferred': False
            })
        
        print(f"✅ Detected {len(occupied_spots)} occupied spots")
        
        # Infer empty spots
        inferred_spots = self.infer_parking_grid(occupied_spots)
        print(f"✅ Inferred {len(inferred_spots)} empty spots")
        
        all_spots = occupied_spots + inferred_spots
        
        self.parking_spots = []
        for i, spot in enumerate(all_spots):
            cx, cy = spot['center']
            w, h = spot['width'], spot['height']
            
            self.parking_spots.append({
                'id': i + 1,
                'center': (cx, cy),
                'width': w,
                'height': h,
                'bbox': (int(cx - w/2), int(cy - h/2), int(cx + w/2), int(cy + h/2)),
                'inferred': spot.get('inferred', False)
            })
            
            self.spot_occupancy[i + 1] = {
                'occupied': False,
                'car_id': None,
                'confidence': 0.0
            }
        
        print(f"✅ Total spots: {len(self.parking_spots)}")
        print(f"   Switching to monitoring mode...")
        
        self.save_learned_spots()
    
    def save_learned_spots(self):
        """Save learned spots to JSON."""
        with open('parking_spots.json', 'w') as f:
            json.dump({
                'learned_at': datetime.now().isoformat(),
                'video_source': self.config['video']['source'],
                'strategy': self.active_strategy['name'] if self.active_strategy else 'Unknown',
                'total_spots': len(self.parking_spots),
                'spots': self.parking_spots
            }, f, indent=2)
        print(f"💾 Saved: parking_spots.json")
    
    def update_spot_occupancy(self, detections):
        """Update spot occupancy."""
        for spot_id in self.spot_occupancy:
            self.spot_occupancy[spot_id]['occupied'] = False
        
        for det_id, detection in enumerate(detections):
            det_center = detection['center']
            for spot in self.parking_spots:
                spot_bbox = spot['bbox']
                if (spot_bbox[0] <= det_center[0] <= spot_bbox[2] and
                    spot_bbox[1] <= det_center[1] <= spot_bbox[3]):
                    self.spot_occupancy[spot['id']]['occupied'] = True
                    self.spot_occupancy[spot['id']]['car_id'] = det_id
                    self.spot_occupancy[spot['id']]['confidence'] = detection['confidence']
                    break
    
    def publish_to_redis(self):
        """Publish to Redis."""
        if not self.redis_client:
            return
        try:
            total = len(self.parking_spots)
            occupied = sum(1 for s in self.spot_occupancy.values() if s['occupied'])
            available = total - occupied
            occupancy = (occupied / total * 100) if total > 0 else 0
            
            self.redis_client.set("urbanflow:parking:total_spots", total)
            self.redis_client.set("urbanflow:parking:occupied_spots", occupied)
            self.redis_client.set("urbanflow:parking:available_spots", available)
            self.redis_client.set("urbanflow:parking:occupancy_rate", f"{occupancy:.1f}")
            
            for spot_id, status in self.spot_occupancy.items():
                key = f"urbanflow:parking:spot_{spot_id}"
                self.redis_client.set(key, "occupied" if status['occupied'] else "free")
            
            # Update metrics logger (automatically logs to history every 5 seconds)
            parking_data = {
                'total_spots': total,
                'occupied_spots': occupied
            }
            self.metrics_logger.update_current_metrics(parking_data, {})
                
        except:
            self.redis_client = None
    
    def visualize(self, frame, detections, fps, strategy_name):
        """Visualize results."""
        vis = frame.copy()
        
        if self.learning_mode and self.learning_start_time:
            elapsed = (datetime.now() - self.learning_start_time).total_seconds()
            remaining = max(0, self.learning_duration - elapsed)
            
            cv2.rectangle(vis, (0, 0), (vis.shape[1], 120), (0, 0, 0), -1)
            cv2.putText(vis, "PARKING DETECTION - LEARNING...", (20, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(vis, f"Strategy: {strategy_name}", (20, 65),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(vis, f"Time remaining: {remaining:.1f}s | Observations: {len(self.stationary_positions)}", 
                       (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            for det in detections:
                x1, y1, x2, y2 = map(int, det['bbox'])
                cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 255), 2)
        else:
            if len(self.parking_spots) > 0:
                for spot in self.parking_spots:
                    x1, y1, x2, y2 = spot['bbox']
                    spot_id = spot['id']
                    
                    if self.spot_occupancy[spot_id]['occupied']:
                        color = (0, 0, 255)
                        status = "OCCUPIED"
                        thickness = 3
                    else:
                        color = (0, 255, 0)
                        status = "FREE"
                        thickness = 2
                    
                    cv2.rectangle(vis, (x1, y1), (x2, y2), color, thickness)
                    cv2.putText(vis, f"#{spot_id}", (x1 + 5, y1 + 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
                    if spot.get('inferred'):
                        cv2.putText(vis, "*", (x2 - 15, y1 + 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                total = len(self.parking_spots)
                occupied = sum(1 for s in self.spot_occupancy.values() if s['occupied'])
                available = total - occupied
                occupancy_rate = (occupied / total * 100) if total > 0 else 0
                
                panel_h = 200
                cv2.rectangle(vis, (0, 0), (550, panel_h), (0, 0, 0), -1)
                cv2.rectangle(vis, (0, 0), (550, panel_h), (255, 255, 255), 2)
                
                y = 30
                cv2.putText(vis, "PARKING MONITOR", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                y += 25
                cv2.putText(vis, f"Strategy: {strategy_name}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y += 30
                cv2.putText(vis, f"Total Spots: {total}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y += 30
                cv2.putText(vis, f"Occupied: {occupied}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                y += 30
                cv2.putText(vis, f"Available: {available}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y += 30
                cv2.putText(vis, f"Occupancy: {occupancy_rate:.1f}%", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(vis, f"FPS: {fps:.1f}", (vis.shape[1] - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return vis
    
    def run(self):
        """Main loop."""
        video_source = self.config['video']['source']
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            print(f"❌ Error: Could not open: {video_source}")
            return
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"\nVideo: {width}x{height} @ {fps:.1f} FPS, {total_frames} frames")
        print("=" * 70)
        print("\n🎬 Starting... Press 'q' to quit\n")
        
        frame_count = 0
        prev_detections = {}
        next_car_id = 0
        self.learning_start_time = datetime.now()
        strategy_name = "Adaptive"
        
        import time
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            frame_count += 1
            
            # Adaptive detection
            results, strategy_name = self.adaptive_detect(frame)
            
            detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'center': [(x1 + x2) / 2, (y1 + y2) / 2],
                    'width': x2 - x1,
                    'height': y2 - y1,
                    'confidence': float(box.conf[0]),
                    'class': int(box.cls[0])
                })
            
            if self.learning_mode:
                current_time = datetime.now()
                elapsed = (current_time - self.learning_start_time).total_seconds()
                
                if elapsed < self.learning_duration:
                    matches = self.match_detections_to_history(detections, prev_detections)
                    new_detections = {}
                    
                    for curr_id, det in enumerate(detections):
                        prev_id = matches.get(curr_id, -1)
                        if prev_id != -1:
                            car_id = prev_id
                        else:
                            car_id = next_car_id
                            next_car_id += 1
                            self.car_first_seen[car_id] = current_time
                            self.car_last_moved[car_id] = current_time
                        
                        self.car_history[car_id].append(det)
                        new_detections[car_id] = det
                        
                        if self.is_stationary(car_id, current_time):
                            self.stationary_positions.append(det)
                    
                    prev_detections = new_detections
                else:
                    self.learn_parking_spots()
                    self.learning_mode = False
            else:
                self.update_spot_occupancy(detections)
                self.publish_to_redis()
            
            current_fps = frame_count / (time.time() - start_time)
            
            if self.display_preview:
                vis_frame = self.visualize(frame, detections, current_fps, strategy_name)
                cv2.imshow("UrbanFlowAI - Parking Detector", vis_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopping...")
                    break
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n" + "=" * 70)
        print(" Parking Detector stopped")
        print("=" * 70)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='UrbanFlowAI Parking Detector')
    parser.add_argument('--config', type=str, default='config_parking.yaml')
    parser.add_argument('--learning-time', type=int, default=60)
    args = parser.parse_args()
    
    detector = ParkingDetector(config_path=args.config)
    if args.learning_time:
        detector.learning_duration = args.learning_time
    detector.run()

