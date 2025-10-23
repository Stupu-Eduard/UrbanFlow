#!/usr/bin/env python3
"""
UrbanFlowAI - Speed Detection Module
Estimates vehicle speed using object tracking (no radar needed)

How it works:
1. Track vehicles across multiple frames
2. Calculate pixel distance traveled
3. Convert to real-world speed using calibration
4. Flag speeding vehicles
"""

import cv2
import yaml
import numpy as np
from ultralytics import YOLO
from collections import defaultdict, deque
from datetime import datetime
import redis

class SpeedDetector:
    def __init__(self, config_path="config.yaml"):
        """Initialize speed detector."""
        print("🚗 UrbanFlowAI - Speed Detection System")
        print("=" * 70)
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load YOLO model with tracking
        print(f"📦 Loading model: {self.config['model']['weights']}...")
        self.model = YOLO(self.config['model']['weights'])
        
        # GPU detection
        import torch
        if torch.cuda.is_available():
            print(f"✓ Using GPU: {torch.cuda.get_device_name(0)}")
        
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
        except:
            print("⚠ Warning: Could not connect to Redis")
        
        # Speed calibration
        # Load from config if available, otherwise use default
        speed_config = self.config.get('speed_detection', {})
        self.pixels_per_meter = speed_config.get('pixels_per_meter', 50)  # DEFAULT
        self.speed_limit_kmh = speed_config.get('speed_limit_kmh', 50)
        
        if self.pixels_per_meter == 50:
            print("⚠️  WARNING: Using default calibration!")
            print("   Run 'python calibrate_speed.py' to calibrate accurately!")
        
        # Tracking data
        self.tracks = defaultdict(lambda: {
            'positions': deque(maxlen=30),  # Last 30 positions
            'frame_numbers': deque(maxlen=30),  # Frame numbers instead of real-time
            'speeds': deque(maxlen=10),
            'avg_speed': 0,
            'speeding': False
        })
        
        # Video FPS (for accurate time calculation)
        self.video_fps = None
        
        # Speed zones (optional - measure speed only in specific areas)
        self.speed_zones = self.config.get('speed_zones', {})
        
        print("=" * 70)
        print(f"⚙️  Calibration: {self.pixels_per_meter} pixels/meter")
        print(f"🚦 Speed limit: {self.speed_limit_kmh} km/h")
        print("=" * 70)
    
    def is_in_speed_zone(self, center):
        """Check if vehicle is in a speed measurement zone."""
        if not self.speed_zones:
            return True  # Measure everywhere if no zones defined
        
        for zone_name, zone in self.speed_zones.items():
            roi = zone.get('roi', [])
            if len(roi) < 3:
                continue
            
            # Point-in-polygon test
            polygon = np.array(roi, dtype=np.int32)
            result = cv2.pointPolygonTest(polygon, center, False)
            if result >= 0:
                return True
        
        return False
    
    def calculate_speed(self, track_id):
        """Calculate speed of a tracked vehicle using video FPS."""
        track = self.tracks[track_id]
        
        if len(track['positions']) < 2:
            return 0
        
        # Get recent positions and frame numbers
        positions = list(track['positions'])
        frame_numbers = list(track['frame_numbers'])
        
        # Calculate distance traveled (pixels)
        total_distance_px = 0
        for i in range(1, len(positions)):
            p1 = positions[i-1]
            p2 = positions[i]
            distance_px = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            total_distance_px += distance_px
        
        # Calculate time elapsed using VIDEO FPS (not processing time!)
        frame_difference = frame_numbers[-1] - frame_numbers[0]
        time_elapsed = frame_difference / self.video_fps  # Actual video time
        
        if time_elapsed <= 0:
            return 0
        
        # Convert to real-world distance (meters)
        distance_m = total_distance_px / self.pixels_per_meter
        
        # Calculate speed (m/s)
        speed_ms = distance_m / time_elapsed
        
        # Convert to km/h
        speed_kmh = speed_ms * 3.6
        
        return speed_kmh
    
    def update_tracking(self, detections, frame_number):
        """Update vehicle tracking with new detections."""
        for det in detections:
            track_id = det['track_id']
            center = det['center']
            
            # Check if in speed zone
            if not self.is_in_speed_zone(center):
                continue
            
            # Update position history with frame number
            self.tracks[track_id]['positions'].append(center)
            self.tracks[track_id]['frame_numbers'].append(frame_number)
            
            # Calculate speed if we have enough data
            if len(self.tracks[track_id]['positions']) >= 5:
                speed = self.calculate_speed(track_id)
                self.tracks[track_id]['speeds'].append(speed)
                
                # Calculate average speed
                if len(self.tracks[track_id]['speeds']) > 0:
                    avg_speed = np.mean(list(self.tracks[track_id]['speeds']))
                    self.tracks[track_id]['avg_speed'] = avg_speed
                    
                    # Check if speeding
                    if avg_speed > self.speed_limit_kmh:
                        self.tracks[track_id]['speeding'] = True
                        
                        # Publish to Redis
                        if self.redis_client:
                            self.redis_client.set(
                                f"urbanflow:speeding:{track_id}",
                                f"{avg_speed:.1f}",
                                ex=300  # Expire after 5 minutes
                            )
    
    def visualize(self, frame, detections, fps):
        """Draw speed information on frame."""
        vis = frame.copy()
        
        # Draw speed zones
        for zone_name, zone in self.speed_zones.items():
            roi = zone.get('roi', [])
            if len(roi) >= 3:
                pts = np.array(roi, dtype=np.int32)
                cv2.polylines(vis, [pts], True, (255, 255, 0), 2)
                cv2.putText(vis, f"SPEED ZONE", (roi[0][0], roi[0][1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Draw detections with speed
        speeding_count = 0
        
        for det in detections:
            track_id = det['track_id']
            bbox = det['bbox']
            center = det['center']
            
            x1, y1, x2, y2 = map(int, bbox)
            
            # Get speed info
            if track_id in self.tracks:
                track = self.tracks[track_id]
                avg_speed = track['avg_speed']
                speeding = track['speeding']
                
                # Color based on speed
                if speeding:
                    color = (0, 0, 255)  # Red for speeding
                    speeding_count += 1
                elif avg_speed > 0:
                    color = (0, 255, 0)  # Green for normal
                else:
                    color = (255, 255, 255)  # White for not enough data
                
                # Draw bounding box
                cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
                
                # Draw speed
                if avg_speed > 0:
                    speed_text = f"{avg_speed:.1f} km/h"
                    cv2.putText(vis, speed_text, (x1, y1 - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    # Draw "SPEEDING!" warning
                    if speeding:
                        cv2.putText(vis, "SPEEDING!", (x1, y2 + 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                # No tracking data yet
                cv2.rectangle(vis, (x1, y1), (x2, y2), (128, 128, 128), 2)
        
        # Draw stats panel
        panel_h = 150
        cv2.rectangle(vis, (0, 0), (450, panel_h), (0, 0, 0), -1)
        cv2.rectangle(vis, (0, 0), (450, panel_h), (255, 255, 255), 2)
        
        y = 30
        cv2.putText(vis, "SPEED DETECTION SYSTEM", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        y += 30
        cv2.putText(vis, f"Vehicles tracked: {len(detections)}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y += 30
        cv2.putText(vis, f"Speeding: {speeding_count}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        y += 30
        cv2.putText(vis, f"Speed limit: {self.speed_limit_kmh} km/h", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # FPS
        cv2.putText(vis, f"FPS: {fps:.1f}", (vis.shape[1] - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return vis
    
    def run(self):
        """Main detection loop."""
        video_source = self.config['video']['source']
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            print(f"❌ Error: Could not open video: {video_source}")
            return
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_fps = cap.get(cv2.CAP_PROP_FPS)  # Store video FPS for speed calculation
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"\nVideo: {width}x{height} @ {self.video_fps:.1f} FPS, {total_frames} frames")
        print("=" * 70)
        print("\n🎬 Starting speed detection... Press 'q' to quit\n")
        
        frame_count = 0
        import time
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_count = 0  # Reset frame counter when looping
                continue
            
            frame_count += 1
            
            # Run YOLO with tracking
            results = self.model.track(
                frame,
                imgsz=1280,
                conf=self.config['model']['confidence'],
                classes=self.config['model']['classes_to_detect'],
                persist=True,  # Enable tracking
                verbose=False
            )[0]
            
            # Extract detections with track IDs
            detections = []
            if results.boxes.id is not None:
                for i, box in enumerate(results.boxes):
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    track_id = int(box.id[0])
                    
                    detections.append({
                        'track_id': track_id,
                        'bbox': [x1, y1, x2, y2],
                        'center': ((x1 + x2) / 2, (y1 + y2) / 2),
                        'confidence': float(box.conf[0]),
                        'class': int(box.cls[0])
                    })
            
            # Update tracking and calculate speeds using frame number
            self.update_tracking(detections, frame_count)
            
            # Calculate FPS
            current_fps = frame_count / (time.time() - start_time)
            
            # Visualize
            if self.config['video'].get('display_preview', True):
                vis_frame = self.visualize(frame, detections, current_fps)
                cv2.imshow("UrbanFlowAI - Speed Detection", vis_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopping...")
                    break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 70)
        print(" Speed Detection stopped")
        print("=" * 70)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='UrbanFlowAI Speed Detection')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')
    args = parser.parse_args()
    
    detector = SpeedDetector(config_path=args.config)
    detector.run()

