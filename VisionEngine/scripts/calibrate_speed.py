#!/usr/bin/env python3
"""
UrbanFlowAI - Speed Calibration Tool
Draw a line on a known distance in your video to calibrate pixel-to-meter conversion

How to use:
1. Find a known distance in your video (e.g., road markings, building width)
2. Click two points on that distance
3. Enter the real-world distance in meters
4. Tool calculates pixels_per_meter for you!
"""

import cv2
import yaml
import numpy as np

class SpeedCalibrator:
    def __init__(self, config_path="config.yaml"):
        """Initialize calibration tool."""
        print("📏 UrbanFlowAI - Speed Calibration Tool")
        print("=" * 70)
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.config_path = config_path
        self.frame = None
        self.points = []
        
        print("✓ Calibrator loaded")
        print("=" * 70)
    
    def get_first_frame(self):
        """Extract frame from video."""
        video_path = self.config['video']['source']
        
        if video_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.frame = cv2.imread(video_path)
        else:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            skip_to_frame = min(int(fps * 3), 100)
            cap.set(cv2.CAP_PROP_POS_FRAMES, skip_to_frame)
            
            ret, self.frame = cap.read()
            cap.release()
            
            if not ret:
                return False
        
        return True
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks."""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.points) < 2:
                self.points.append((x, y))
                print(f"Point {len(self.points)}: ({x}, {y})")
                
                if len(self.points) == 2:
                    # Calculate pixel distance
                    p1, p2 = self.points
                    pixel_distance = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                    
                    print("\n" + "=" * 70)
                    print(f"📏 Pixel distance: {pixel_distance:.2f} pixels")
                    print("=" * 70)
                    print("\nExamples of known distances:")
                    print("  • Road lane width: ~3.5 meters")
                    print("  • Parking spot length: ~5.0 meters")
                    print("  • Road marking (dashed line): ~3.0 meters")
                    print("  • Building width: measure on Google Maps")
                    print("=" * 70)
                    
                    real_distance = float(input("\nEnter real-world distance (meters): "))
                    
                    pixels_per_meter = pixel_distance / real_distance
                    
                    print("\n" + "=" * 70)
                    print("✅ CALIBRATION COMPLETE!")
                    print("=" * 70)
                    print(f"Pixels per meter: {pixels_per_meter:.2f}")
                    print(f"Meters per pixel: {1/pixels_per_meter:.4f}")
                    print("=" * 70)
                    
                    # Save to config
                    if 'speed_detection' not in self.config:
                        self.config['speed_detection'] = {}
                    
                    self.config['speed_detection']['pixels_per_meter'] = float(pixels_per_meter)
                    self.config['speed_detection']['calibration_distance_m'] = float(real_distance)
                    self.config['speed_detection']['calibration_distance_px'] = float(pixel_distance)
                    
                    with open(self.config_path, 'w') as f:
                        yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
                    
                    print(f"💾 Saved calibration to: {self.config_path}")
                    print("\n📝 Copy this line to speed_detector.py:")
                    print(f"    self.pixels_per_meter = {pixels_per_meter:.2f}")
                    print("=" * 70)
    
    def run(self):
        """Main calibration loop."""
        if not self.get_first_frame():
            print("❌ Could not load frame")
            return
        
        cv2.namedWindow("Speed Calibration")
        cv2.setMouseCallback("Speed Calibration", self.mouse_callback)
        
        print("\n" + "=" * 70)
        print("📏 INSTRUCTIONS:")
        print("=" * 70)
        print("1. Find a known distance in the video (e.g., road markings)")
        print("2. Click the START of that distance")
        print("3. Click the END of that distance")
        print("4. Enter the real-world distance in meters")
        print("=" * 70)
        print("\nWaiting for clicks...")
        
        while True:
            display = self.frame.copy()
            
            # Draw points
            for i, point in enumerate(self.points):
                cv2.circle(display, point, 8, (0, 0, 255), -1)
                cv2.putText(display, f"P{i+1}", (point[0] + 15, point[1]),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Draw line between points
            if len(self.points) == 2:
                cv2.line(display, self.points[0], self.points[1], (0, 255, 0), 3)
                
                # Calculate and show distance
                p1, p2 = self.points
                pixel_distance = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                mid_point = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
                
                cv2.putText(display, f"{pixel_distance:.1f} px", 
                           (mid_point[0], mid_point[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Instructions overlay
            cv2.rectangle(display, (0, 0), (500, 100), (0, 0, 0), -1)
            cv2.rectangle(display, (0, 0), (500, 100), (255, 255, 255), 2)
            
            cv2.putText(display, "SPEED CALIBRATION", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            if len(self.points) == 0:
                cv2.putText(display, "Click START of known distance", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            elif len(self.points) == 1:
                cv2.putText(display, "Click END of known distance", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            else:
                cv2.putText(display, "Check terminal for next steps", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(display, "Press 'q' to exit", (10, 85),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Speed Calibration", display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or len(self.points) == 2:
                break
        
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Calibrate speed detection')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')
    args = parser.parse_args()
    
    calibrator = SpeedCalibrator(config_path=args.config)
    calibrator.run()

