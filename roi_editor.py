#!/usr/bin/env python3
"""
UrbanFlowAI - ROI Editor v2 (Improved)
Enhanced ROI editor with better UX and productivity features

NEW FEATURES:
- Keyboard shortcuts
- Grid-based parking spot generation
- Copy/Paste ROIs
- Undo/Redo (Ctrl+Z, Ctrl+Y)
- Quick shapes (rectangles, grids)
- ROI templates
- Better visual feedback
"""

import cv2
import yaml
import numpy as np

class ROIEditorV2:
    def __init__(self, config_path="config.yaml"):
        """Initialize enhanced ROI editor."""
        print("🎨 UrbanFlowAI - ROI Editor v2 (Enhanced)")
        print("=" * 70)
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.config_path = config_path
        self.frame = None
        self.original_frame = None
        self.points = []
        self.current_roi_type = "street"  # 'street' or 'parking'
        self.drawing = False
        
        # History for undo/redo
        self.history = []
        self.history_index = -1
        
        # Clipboard for copy/paste
        self.clipboard = None
        
        # Auto-naming counters
        self.street_counter = 1
        self.parking_counter = 1
        
        # Quick draw mode
        self.quick_mode = None  # 'rectangle' or 'grid'
        self.rect_start = None
        
        print("✓ Editor loaded")
        print("=" * 70)
    
    def get_first_frame(self):
        """Extract frame from video."""
        video_path = self.config['video']['source']
        
        if video_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Static image
            self.frame = cv2.imread(video_path)
            if self.frame is None:
                print(f"❌ Could not load image: {video_path}")
                return False
        else:
            # Video file
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"❌ Could not open video: {video_path}")
                return False
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            skip_to_frame = min(int(fps * 3), 100)
            cap.set(cv2.CAP_PROP_POS_FRAMES, skip_to_frame)
            
            ret, self.frame = cap.read()
            cap.release()
            
            if not ret:
                print(f"❌ Could not read frame from video")
                return False
        
        self.original_frame = self.frame.copy()
        print(f"✓ Loaded frame: {self.frame.shape[1]}x{self.frame.shape[0]}")
        return True
    
    def save_to_history(self):
        """Save current state to history for undo."""
        state = {
            'traffic': self.config.get('traffic', {}).copy(),
            'parking': self.config.get('parking', {}).copy()
        }
        
        # Remove future history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(state)
        self.history_index += 1
    
    def undo(self):
        """Undo last action."""
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.config['traffic'] = state['traffic'].copy()
            self.config['parking'] = state['parking'].copy()
            print("↶ Undo")
            return True
        print("⚠ Nothing to undo")
        return False
    
    def redo(self):
        """Redo last undone action."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.config['traffic'] = state['traffic'].copy()
            self.config['parking'] = state['parking'].copy()
            print("↷ Redo")
            return True
        print("⚠ Nothing to redo")
        return False
    
    def draw_rectangle_roi(self, x, y):
        """Quick draw: rectangle ROI."""
        if self.rect_start is None:
            self.rect_start = (x, y)
            print(f"📐 Rectangle start: ({x}, {y}) - click again for opposite corner")
        else:
            x1, y1 = self.rect_start
            x2, y2 = x, y
            
            # Create rectangle points
            self.points = [
                [x1, y1],
                [x2, y1],
                [x2, y2],
                [x1, y2]
            ]
            
            self.save_roi()
            self.points = []
            self.rect_start = None
            self.quick_mode = None
            print("✓ Rectangle ROI saved!")
    
    def generate_parking_grid(self, x, y):
        """Quick draw: generate parking grid."""
        if self.rect_start is None:
            self.rect_start = (x, y)
            print(f"🅿️  Grid start: ({x}, {y}) - click for opposite corner")
        else:
            x1, y1 = self.rect_start
            x2, y2 = x, y
            
            # Ask for grid dimensions
            print("\n" + "=" * 50)
            cols = int(input("Number of columns (spots per row): "))
            rows = int(input("Number of rows: "))
            
            # Calculate spot dimensions
            total_width = abs(x2 - x1)
            total_height = abs(y2 - y1)
            spot_width = total_width // cols
            spot_height = total_height // rows
            
            # Generate grid
            spots_created = 0
            for row in range(rows):
                for col in range(cols):
                    spot_x = min(x1, x2) + col * spot_width
                    spot_y = min(y1, y2) + row * spot_height
                    
                    self.points = [
                        [spot_x, spot_y],
                        [spot_x + spot_width, spot_y],
                        [spot_x + spot_width, spot_y + spot_height],
                        [spot_x, spot_y + spot_height]
                    ]
                    
                    self.save_roi()
                    spots_created += 1
            
            print(f"✓ Created {spots_created} parking spots in {rows}x{cols} grid!")
            self.points = []
            self.rect_start = None
            self.quick_mode = None
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events."""
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.quick_mode == 'rectangle':
                self.draw_rectangle_roi(x, y)
            elif self.quick_mode == 'grid':
                self.generate_parking_grid(x, y)
            else:
                # Regular polygon drawing
                self.points.append([x, y])
                print(f"Point {len(self.points)}: ({x}, {y})")
    
    def save_roi(self):
        """Save current ROI to config."""
        if len(self.points) < 3:
            print("⚠ Need at least 3 points for an ROI")
            return False
        
        # Save to history before making changes
        self.save_to_history()
        
        if self.current_roi_type == "street":
            # Auto-generate name
            while f"street_{self.street_counter}" in self.config['traffic']['streets']:
                self.street_counter += 1
            
            roi_name = f"street_{self.street_counter}"
            
            self.config['traffic']['streets'][roi_name] = {
                'roi': self.points.copy(),
                'max_vehicles': 20,
                'redis_key': f"urbanflow:traffic:{roi_name}"
            }
            
            print(f"✅ Saved street ROI: {roi_name}")
            self.street_counter += 1
            
        else:  # parking
            # Auto-generate name (A1, A2, ..., B1, B2, ...)
            row_letter = chr(65 + (self.parking_counter - 1) // 10)  # A, B, C...
            spot_number = ((self.parking_counter - 1) % 10) + 1
            roi_name = f"SPOT_{row_letter}{spot_number}"
            
            self.config['parking']['spots'][roi_name] = {
                'roi': self.points.copy(),
                'redis_key': f"urbanflow:parking:{roi_name}"
            }
            
            print(f"✅ Saved parking spot: {roi_name}")
            self.parking_counter += 1
        
        return True
    
    def save_config(self):
        """Save config to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        print(f"💾 Config saved to: {self.config_path}")
    
    def draw_overlay(self):
        """Draw current ROIs and UI overlay."""
        display = self.original_frame.copy()
        
        # Draw existing traffic ROIs
        for street_name, street in self.config['traffic']['streets'].items():
            roi = street.get('roi', [])
            if len(roi) >= 3:
                pts = np.array(roi, dtype=np.int32)
                cv2.polylines(display, [pts], True, (0, 255, 0), 2)
                cv2.putText(display, street_name, (roi[0][0], roi[0][1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw existing parking ROIs
        for spot_name, spot in self.config['parking']['spots'].items():
            roi = spot.get('roi', [])
            if len(roi) >= 3:
                pts = np.array(roi, dtype=np.int32)
                cv2.polylines(display, [pts], True, (255, 0, 255), 2)
                cv2.putText(display, spot_name, (roi[0][0], roi[0][1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        # Draw current polygon being drawn
        if len(self.points) > 0:
            pts = np.array(self.points, dtype=np.int32)
            if len(self.points) > 1:
                cv2.polylines(display, [pts], False, (0, 255, 255), 2)
            
            for i, point in enumerate(self.points):
                cv2.circle(display, tuple(point), 5, (0, 0, 255), -1)
                cv2.putText(display, str(i+1), (point[0]+10, point[1]),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Draw rectangle preview if in quick mode
        if self.rect_start and len(self.points) == 0:
            cv2.circle(display, self.rect_start, 5, (255, 255, 0), -1)
        
        # Draw UI panel
        panel_h = 320
        cv2.rectangle(display, (0, 0), (700, panel_h), (0, 0, 0), -1)
        cv2.rectangle(display, (0, 0), (700, panel_h), (255, 255, 255), 2)
        
        y = 25
        cv2.putText(display, "ROI EDITOR v2 - ENHANCED", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        y += 30
        mode_color = (0, 255, 0) if self.current_roi_type == "street" else (255, 0, 255)
        cv2.putText(display, f"Mode: {self.current_roi_type.upper()}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)
        
        if self.quick_mode:
            y += 25
            cv2.putText(display, f"Quick Mode: {self.quick_mode.upper()}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        y += 35
        cv2.putText(display, "KEYBOARD SHORTCUTS:", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        y += 25
        cv2.putText(display, "[M] Toggle mode (street/parking)", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 20
        cv2.putText(display, "[R] Quick rectangle ROI", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 20
        cv2.putText(display, "[G] Quick parking grid", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 20
        cv2.putText(display, "[S] Save current ROI", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 20
        cv2.putText(display, "[C] Clear current points", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 20
        cv2.putText(display, "[Z] Undo | [Y] Redo", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 20
        cv2.putText(display, "[D] Delete last ROI", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 20
        cv2.putText(display, "[W] Save config & exit", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 20
        cv2.putText(display, "[Q] Quit without saving", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        y += 30
        cv2.putText(display, f"Current points: {len(self.points)}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        return display
    
    def run(self):
        """Main editor loop."""
        if not self.get_first_frame():
            return
        
        # Save initial state
        self.save_to_history()
        
        cv2.namedWindow("ROI Editor v2")
        cv2.setMouseCallback("ROI Editor v2", self.mouse_callback)
        
        print("\n" + "=" * 70)
        print("🎨 ROI Editor v2 Running")
        print("=" * 70)
        print("Click to add points. Use keyboard shortcuts (see window).")
        print("=" * 70)
        
        while True:
            display = self.draw_overlay()
            cv2.imshow("ROI Editor v2", display)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):  # Quit
                print("❌ Exiting without saving")
                break
            
            elif key == ord('w'):  # Save and exit
                self.save_config()
                print("✅ Saved and exiting")
                break
            
            elif key == ord('m'):  # Toggle mode
                self.current_roi_type = "parking" if self.current_roi_type == "street" else "street"
                print(f"🔄 Mode: {self.current_roi_type}")
            
            elif key == ord('s'):  # Save ROI
                if self.save_roi():
                    self.points = []
            
            elif key == ord('c'):  # Clear points
                self.points = []
                self.rect_start = None
                self.quick_mode = None
                print("🗑️  Cleared current points")
            
            elif key == ord('r'):  # Rectangle mode
                self.quick_mode = 'rectangle'
                self.points = []
                print("📐 Rectangle mode: click 2 opposite corners")
            
            elif key == ord('g'):  # Grid mode
                if self.current_roi_type == "parking":
                    self.quick_mode = 'grid'
                    self.points = []
                    print("🅿️  Grid mode: click 2 corners, then enter dimensions")
                else:
                    print("⚠ Grid mode only works in parking mode")
            
            elif key == ord('z'):  # Undo
                if self.undo():
                    self.points = []
            
            elif key == ord('y'):  # Redo
                if self.redo():
                    self.points = []
            
            elif key == ord('d'):  # Delete last ROI
                self.save_to_history()
                if self.current_roi_type == "street" and self.config['traffic']['streets']:
                    last_street = list(self.config['traffic']['streets'].keys())[-1]
                    del self.config['traffic']['streets'][last_street]
                    print(f"🗑️  Deleted {last_street}")
                elif self.current_roi_type == "parking" and self.config['parking']['spots']:
                    last_spot = list(self.config['parking']['spots'].keys())[-1]
                    del self.config['parking']['spots'][last_spot]
                    print(f"🗑️  Deleted {last_spot}")
        
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='UrbanFlowAI ROI Editor v2')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')
    args = parser.parse_args()
    
    editor = ROIEditorV2(config_path=args.config)
    editor.run()

