#!/usr/bin/env python3
"""
UrbanFlowAI - Vision Engine (detector.py)

The "Eyes" of the system - processes video feeds and publishes real-time data to Redis.

Outputs:
    - Traffic: {"urbanflow:traffic:street_1": 0.82}  (density 0.0-1.0)
    - Parking: {"urbanflow:parking:SPOT_A1": "occupied" | "free"}
    - Emergency: {"urbanflow:emergency:truck_01": '{"id": "truck_01", "location": [x, y]}'}
"""

import cv2
import yaml
import redis
import json
import time
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from metrics_logger import MetricsLogger


class UrbanFlowDetector:
    def __init__(self, config_path="config.yaml"):
        """Initialize the Vision Engine."""
        self.config_path = config_path
        self.load_config()
        self.setup_model()
        self.setup_redis()
        self.setup_tracking()
        self.setup_metrics()
        
        print("\n" + "="*70)
        print(" UrbanFlowAI - Vision Engine")
        print("="*70)
        print(f" Model: {self.config['model']['weights']}")
        print(f" Video: {self.config['video']['source']}")
        print(f" Target FPS: {self.config['video']['target_fps']}")
        print(f" Streets monitored: {len(self.config['traffic']['streets'])}")
        print(f" Parking spots: {len(self.config['parking']['spots'])}")
        print("="*70 + "\n")
    
    def load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: {self.config_path} not found!")
            exit(1)
    
    def setup_model(self):
        """Initialize YOLOv8 model."""
        model_path = self.config['model']['weights']
        device = self.config['model']['device']
        
        print(f"Loading YOLO model: {model_path}...")
        self.model = YOLO(model_path)
        
        # Move to GPU if available
        if device == "cuda":
            import torch
            if torch.cuda.is_available():
                print(f"✓ Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                print("⚠ CUDA not available, falling back to CPU")
                self.config['model']['device'] = 'cpu'
    
    def setup_redis(self):
        """Connect to Redis database."""
        redis_config = self.config['redis']
        
        try:
            self.redis_client = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config['db'],
                password=redis_config.get('password'),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            print(f"✓ Connected to Redis at {redis_config['host']}:{redis_config['port']}")
        except redis.ConnectionError as e:
            print(f"⚠ Warning: Could not connect to Redis: {e}")
            print("  Detector will run but data won't be published.")
            self.redis_client = None
        except Exception as e:
            print(f"⚠ Warning: Redis error: {e}")
            self.redis_client = None
    
    def setup_tracking(self):
        """Initialize tracking variables."""
        self.emergency_vehicles = {}  # Track emergency vehicle IDs
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.actual_fps = 0
        
        # Speed detection setup
        from collections import defaultdict, deque
        self.tracks = defaultdict(lambda: {
            'positions': deque(maxlen=30),
            'frame_numbers': deque(maxlen=30),
            'speeds': deque(maxlen=10),
            'avg_speed': 0,
            'speeding': False,
            'street': None
        })
        
        # Load speed calibration
        speed_config = self.config.get('speed_detection', {})
        self.pixels_per_meter = speed_config.get('pixels_per_meter', 31.3)
        self.speed_limit_kmh = speed_config.get('speed_limit_kmh', 50)
        self.video_fps = None  # Will be set when video loads
        
        if self.pixels_per_meter == 50:  # Default value
            print("⚠️  Using default speed calibration (31.3 px/m)")
            print("   Run 'python calibrate_speed.py' for accurate speeds")
    
    def setup_metrics(self):
        """Initialize metrics logger."""
        self.metrics_logger = MetricsLogger()
    
    def point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon using ray casting algorithm."""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_bbox_center(self, bbox):
        """Calculate center point of bounding box."""
        x1, y1, x2, y2 = bbox
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        return [center_x, center_y]
    
    def process_traffic(self, detections, frame):
        """Process traffic density for each street ROI."""
        streets = self.config['traffic']['streets']
        traffic_data = {}
        
        for street_name, street_config in streets.items():
            roi = street_config.get('roi', [])
            
            if not roi or len(roi) < 3:
                continue  # Skip if ROI not defined
            
            # Count vehicles in this street ROI
            vehicle_count = 0
            speeds_in_street = []
            speeding_count = 0
            
            for detection in detections:
                bbox = detection['bbox']
                center = self.get_bbox_center(bbox)
                
                # Check if vehicle center is in street ROI
                if self.point_in_polygon(center, roi):
                    vehicle_count += 1
                    
                    # Collect speed data if available
                    vehicle_speed = 0
                    is_speeding = False
                    if 'track_id' in detection:
                        track_id = detection['track_id']
                        if track_id in self.tracks:
                            track = self.tracks[track_id]
                            if track['avg_speed'] > 0:
                                vehicle_speed = track['avg_speed']
                                speeds_in_street.append(vehicle_speed)
                                is_speeding = track['speeding']
                                if is_speeding:
                                    speeding_count += 1
                    
                    # Draw detection on frame (if preview enabled)
                    if self.config['video']['display_preview']:
                        x1, y1, x2, y2 = [int(v) for v in bbox]
                        # Color: red if speeding, blue otherwise
                        color = (0, 0, 255) if is_speeding else (255, 0, 0)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Display speed if available
                        if vehicle_speed > 5:  # Only show if speed is meaningful
                            speed_text = f"{vehicle_speed:.0f}km/h"
                            cv2.putText(frame, speed_text, (x1, y1 - 5),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Calculate density (0.0 to 1.0)
            max_vehicles = street_config['max_vehicles']
            density = min(vehicle_count / max_vehicles, 1.0)
            
            # Calculate average speed
            avg_speed = np.mean(speeds_in_street) if speeds_in_street else 0
            
            # Store traffic data for metrics
            traffic_data[street_name] = {
                'vehicle_count': vehicle_count,
                'density': density,
                'avg_speed': avg_speed,
                'speeding_count': speeding_count
            }
            
            # Publish to Redis
            redis_key = street_config['redis_key']
            if self.redis_client:
                self.redis_client.set(redis_key, round(density, 2))
            
            # Draw street ROI and info
            if self.config['video']['display_preview']:
                pts = np.array(roi, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                
                # Label with speed info
                centroid = np.mean(roi, axis=0).astype(int)
                label = f"{street_name}: {vehicle_count}/{max_vehicles} ({density:.0%})"
                if avg_speed > 0:
                    label += f" | {avg_speed:.0f}km/h"
                cv2.putText(frame, label, tuple(centroid - [0, 20]),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return traffic_data
    
    def process_parking(self, detections, frame):
        """Process parking spot occupancy and parking lot statistics."""
        spots = self.config['parking']['spots']
        
        # Count parking metrics
        total_spots = len([s for s in spots.values() if s.get('roi') and len(s.get('roi', [])) >= 3])
        occupied_count = 0
        
        for spot_name, spot_config in spots.items():
            roi = spot_config.get('roi', [])
            
            if not roi or len(roi) < 3:
                continue  # Skip if ROI not defined
            
            # Check if any car is in this parking spot
            occupied = False
            
            for detection in detections:
                # Only check for cars in parking spots
                if detection['class'] == 2:  # COCO class 2 = car
                    bbox = detection['bbox']
                    center = self.get_bbox_center(bbox)
                    
                    if self.point_in_polygon(center, roi):
                        occupied = True
                        occupied_count += 1
                        break
            
            # Determine status
            status = "occupied" if occupied else "free"
            
            # Publish individual spot to Redis
            redis_key = spot_config['redis_key']
            if self.redis_client:
                self.redis_client.set(redis_key, status)
            
            # Draw parking spot ROI
            if self.config['video']['display_preview']:
                color = (0, 0, 255) if occupied else (0, 255, 0)  # Red=occupied, Green=free
                pts = np.array(roi, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, color, 2)
                
                # Label
                centroid = np.mean(roi, axis=0).astype(int)
                cv2.putText(frame, f"{spot_name}: {status}", tuple(centroid),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Calculate parking lot statistics
        available_spots = total_spots - occupied_count
        occupancy_rate = (occupied_count / total_spots * 100) if total_spots > 0 else 0
        
        # Publish parking lot summary to Redis
        if self.redis_client and total_spots > 0:
            self.redis_client.set("urbanflow:parking:total_spots", total_spots)
            self.redis_client.set("urbanflow:parking:occupied_spots", occupied_count)
            self.redis_client.set("urbanflow:parking:available_spots", available_spots)
            self.redis_client.set("urbanflow:parking:occupancy_rate", f"{occupancy_rate:.1f}")
        
        # Display parking lot summary on frame
        if self.config['video']['display_preview'] and total_spots > 0:
            # Create summary box
            summary_y = 80
            cv2.rectangle(frame, (10, summary_y), (350, summary_y + 120), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, summary_y), (350, summary_y + 120), (255, 255, 255), 2)
            
            # Title
            cv2.putText(frame, "PARKING LOT SUMMARY", (20, summary_y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Total spots
            cv2.putText(frame, f"Total Spots: {total_spots}", (20, summary_y + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Occupied (red)
            cv2.putText(frame, f"Occupied: {occupied_count}", (20, summary_y + 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Available (green)
            cv2.putText(frame, f"Available: {available_spots}", (20, summary_y + 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Occupancy rate
            color = (0, 0, 255) if occupancy_rate > 80 else (0, 255, 0) if occupancy_rate < 50 else (0, 165, 255)
            cv2.putText(frame, f"Occupancy: {occupancy_rate:.1f}%", (200, summary_y + 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Return parking data for metrics
        return {
            'total_spots': total_spots,
            'occupied_spots': occupied_count
        }
    
    def process_emergency(self, detections, frame):
        """Process emergency vehicle tracking."""
        emergency_class = self.config['emergency']['vehicle_class']
        redis_prefix = self.config['emergency']['redis_key_prefix']
        
        # Clear old emergency vehicles
        current_frame_vehicles = set()
        
        for detection in detections:
            if detection['class'] == emergency_class:  # Truck (our ambulance stand-in)
                bbox = detection['bbox']
                center = self.get_bbox_center(bbox)
                
                # Create a simple ID based on position (in production, use proper tracking)
                vehicle_id = f"truck_{center[0] // 50}_{center[1] // 50}"
                current_frame_vehicles.add(vehicle_id)
                
                # Prepare data payload
                payload = {
                    "id": vehicle_id,
                    "location": center,
                    "bbox": [int(v) for v in bbox],
                    "timestamp": time.time()
                }
                
                # Publish to Redis
                redis_key = f"{redis_prefix}{vehicle_id}"
                if self.redis_client:
                    self.redis_client.set(redis_key, json.dumps(payload))
                    self.redis_client.expire(redis_key, 5)  # Expire after 5 seconds if not updated
                
                # Draw on frame
                if self.config['video']['display_preview']:
                    x1, y1, x2, y2 = [int(v) for v in bbox]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(frame, "EMERGENCY", (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                self.emergency_vehicles[vehicle_id] = payload
    
    def calculate_speed(self, track_id):
        """Calculate speed of a tracked vehicle using video FPS."""
        track = self.tracks[track_id]
        
        if len(track['positions']) < 2 or self.video_fps is None:
            return 0
        
        positions = list(track['positions'])
        frame_numbers = list(track['frame_numbers'])
        
        # Calculate distance traveled (pixels)
        total_distance_px = 0
        for i in range(1, len(positions)):
            p1 = positions[i-1]
            p2 = positions[i]
            distance_px = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            total_distance_px += distance_px
        
        # Calculate time elapsed using video FPS
        frame_difference = frame_numbers[-1] - frame_numbers[0]
        time_elapsed = frame_difference / self.video_fps
        
        if time_elapsed <= 0:
            return 0
        
        # Convert to real-world distance and speed
        distance_m = total_distance_px / self.pixels_per_meter
        speed_ms = distance_m / time_elapsed
        speed_kmh = speed_ms * 3.6
        
        return speed_kmh
    
    def update_vehicle_tracking(self, detections, video_frame_idx):
        """Update tracking for speed calculation."""
        for det in detections:
            if 'track_id' not in det:
                continue
            
            track_id = det['track_id']
            bbox = det['bbox']
            center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
            
            # Update position history (use actual video frame index, not processing count)
            self.tracks[track_id]['positions'].append(center)
            self.tracks[track_id]['frame_numbers'].append(video_frame_idx)
            
            # Calculate speed if we have enough data
            if len(self.tracks[track_id]['positions']) >= 5:
                speed = self.calculate_speed(track_id)
                self.tracks[track_id]['speeds'].append(speed)
                
                # Calculate average speed
                if len(self.tracks[track_id]['speeds']) > 0:
                    avg_speed = np.mean(list(self.tracks[track_id]['speeds']))
                    self.tracks[track_id]['avg_speed'] = avg_speed
                    self.tracks[track_id]['speeding'] = avg_speed > self.speed_limit_kmh
                    
                    # Store which street this vehicle is in
                    for street_name, street in self.config['traffic']['streets'].items():
                        if self.point_in_polygon(center, street['roi']):
                            self.tracks[track_id]['street'] = street_name
                            break
    
    def run_detection(self, frame, video_frame_idx):
        """Run YOLO detection with tracking for speed measurement."""
        # Run inference with tracking enabled
        results = self.model.track(
            frame,
            imgsz=1280,
            conf=self.config['model']['confidence'],
            classes=self.config['model']['classes_to_detect'],
            persist=True,  # Enable tracking
            verbose=False
        )
        
        # Parse detections with track IDs
        detections = []
        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes
            
            for i, box in enumerate(boxes):
                det = {
                    'bbox': box.xyxy[0].cpu().numpy(),
                    'confidence': float(box.conf[0]),
                    'class': int(box.cls[0])
                }
                
                # Add track ID if available
                if hasattr(box, 'id') and box.id is not None:
                    det['track_id'] = int(box.id[0])
                
                detections.append(det)
        
        # Update tracking for speed calculation (use actual video frame index)
        self.update_vehicle_tracking(detections, video_frame_idx)
        
        return detections
    
    def calculate_fps(self):
        """Calculate actual processing FPS."""
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            elapsed = time.time() - self.fps_start_time
            self.actual_fps = 30 / elapsed
            self.fps_start_time = time.time()
    
    def run(self):
        """Main processing loop."""
        video_path = self.config['video']['source']
        
        # Check if video exists
        if not Path(video_path).exists():
            print(f"Error: Video file not found: {video_path}")
            print("Please download a video and update 'video.source' in config.yaml")
            return
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Could not open video: {video_path}")
            return
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        self.video_fps = fps  # Store for speed calculation
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video info: {width}x{height} @ {fps} FPS, {total_frames} frames")
        print(f"Speed detection: {self.pixels_per_meter:.1f} px/m, limit: {self.speed_limit_kmh} km/h")
        print("\nProcessing started... Press 'q' to quit\n")
        
        # Calculate frame skip for target FPS
        target_fps = self.config['video']['target_fps']
        frame_skip = max(1, int(fps / target_fps))
        
        frame_idx = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    # Loop video
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Skip frames to achieve target FPS
                if frame_idx % frame_skip != 0:
                    frame_idx += 1
                    continue
                
                frame_idx += 1
                
                # Run detection (pass actual video frame index for accurate speed calculation)
                detections = self.run_detection(frame, frame_idx)
                
                # Process all three services
                traffic_data = self.process_traffic(detections, frame)
                parking_data = self.process_parking(detections, frame)
                self.process_emergency(detections, frame)
                
                # Update metrics (automatically logs to history every 5 seconds)
                self.metrics_logger.update_current_metrics(parking_data, traffic_data)
                
                # Calculate FPS
                self.calculate_fps()
                
                # Display preview
                if self.config['video']['display_preview']:
                    # Add FPS counter
                    fps_text = f"FPS: {self.actual_fps:.1f} | Detections: {len(detections)}"
                    cv2.putText(frame, fps_text, (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow("UrbanFlowAI - Vision Engine", frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("\nStopping detector...")
                        break
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
            if self.redis_client:
                self.redis_client.close()
            
            print("\n" + "="*70)
            print(" Vision Engine stopped")
            print("="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='UrbanFlowAI Vision Engine')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file (default: config.yaml)')
    args = parser.parse_args()
    
    detector = UrbanFlowDetector(config_path=args.config)
    detector.run()



