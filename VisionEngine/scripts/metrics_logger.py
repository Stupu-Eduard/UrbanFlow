#!/usr/bin/env python3
"""
UrbanFlowAI - Metrics Logger
Real-time metrics collection and logging to files

Outputs:
- current_metrics.json → Latest snapshot (updates every second)
- metrics_history.csv → Time-series data (appends every 5 seconds)
- daily_summary.json → Daily statistics summary
"""

import json
import csv
import os
import numpy as np
from datetime import datetime
from pathlib import Path

class MetricsLogger:
    def __init__(self, output_dir="metrics"):
        """Initialize metrics logger."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # File paths
        self.current_file = self.output_dir / "current_metrics.json"
        self.history_file = self.output_dir / "metrics_history.csv"
        
        # Initialize CSV if not exists
        if not self.history_file.exists():
            self.init_history_csv()
        
        # Tracking
        self.last_log_time = 0
        self.log_interval = 5  # Seconds between history logs
        
        print(f"📊 Metrics Logger initialized")
        print(f"   Output directory: {self.output_dir}")
    
    def convert_to_native(self, obj):
        """Convert numpy types to Python native types for JSON serialization."""
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self.convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_to_native(item) for item in obj]
        else:
            return obj
    
    def init_history_csv(self):
        """Initialize CSV file with headers."""
        with open(self.history_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'parking_total',
                'parking_occupied',
                'parking_available',
                'parking_occupancy_pct',
                'traffic_total_vehicles',
                'traffic_avg_density_pct',
                'traffic_avg_speed_kmh',
                'speeding_vehicles'
            ])
    
    def calculate_parking_metrics(self, parking_data):
        """Calculate parking occupancy percentage."""
        total = parking_data.get('total_spots', 0)
        occupied = parking_data.get('occupied_spots', 0)
        
        if total == 0:
            return {
                'total_spots': 0,
                'occupied_spots': 0,
                'available_spots': 0,
                'occupancy_percentage': 0.0
            }
        
        available = total - occupied
        occupancy_pct = (occupied / total) * 100
        
        return {
            'total_spots': total,
            'occupied_spots': occupied,
            'available_spots': available,
            'occupancy_percentage': round(occupancy_pct, 1)
        }
    
    def calculate_traffic_metrics(self, traffic_data):
        """Calculate traffic congestion percentage."""
        if not traffic_data:
            return {
                'total_vehicles': 0,
                'average_density_percentage': 0.0,
                'average_speed_kmh': 0.0,
                'speeding_vehicles': 0
            }
        
        total_vehicles = 0
        total_density = 0
        total_speed = 0
        speed_count = 0
        speeding = 0
        
        for street_name, street_data in traffic_data.items():
            vehicle_count = street_data.get('vehicle_count', 0)
            density = street_data.get('density', 0.0)
            avg_speed = street_data.get('avg_speed', 0)
            speeding_count = street_data.get('speeding_count', 0)
            
            total_vehicles += vehicle_count
            total_density += density
            
            if avg_speed > 0:
                total_speed += avg_speed
                speed_count += 1
            
            speeding += speeding_count
        
        num_streets = len(traffic_data)
        avg_density_pct = (total_density / num_streets * 100) if num_streets > 0 else 0
        avg_speed = (total_speed / speed_count) if speed_count > 0 else 0
        
        return {
            'total_vehicles': total_vehicles,
            'average_density_percentage': round(avg_density_pct, 1),
            'average_speed_kmh': round(avg_speed, 1),
            'speeding_vehicles': speeding,
            'streets': traffic_data
        }
    
    def update_current_metrics(self, parking_data=None, traffic_data=None):
        """Update current metrics snapshot (real-time)."""
        timestamp = datetime.now()
        
        metrics = {
            'timestamp': timestamp.isoformat(),
            'last_updated': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'parking': self.calculate_parking_metrics(parking_data or {}),
            'traffic': self.calculate_traffic_metrics(traffic_data or {})
        }
        
        # Convert numpy types to native Python types
        metrics = self.convert_to_native(metrics)
        
        # Write to current metrics file (overwrites)
        with open(self.current_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Append to history if interval passed
        current_time = timestamp.timestamp()
        if current_time - self.last_log_time >= self.log_interval:
            self.append_to_history(metrics)
            self.last_log_time = current_time
        
        return metrics
    
    def append_to_history(self, metrics):
        """Append metrics to CSV history."""
        parking = metrics['parking']
        traffic = metrics['traffic']
        
        with open(self.history_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                metrics['timestamp'],
                parking['total_spots'],
                parking['occupied_spots'],
                parking['available_spots'],
                parking['occupancy_percentage'],
                traffic['total_vehicles'],
                traffic['average_density_percentage'],
                traffic['average_speed_kmh'],
                traffic['speeding_vehicles']
            ])
    
    def get_current_metrics(self):
        """Read current metrics from file."""
        if not self.current_file.exists():
            return {}
        
        with open(self.current_file, 'r') as f:
            return json.load(f)

if __name__ == "__main__":
    # Test the logger
    logger = MetricsLogger()
    
    # Test parking data
    parking_test = {
        'total_spots': 26,
        'occupied_spots': 18
    }
    
    # Test traffic data
    traffic_test = {
        'street_1': {
            'vehicle_count': 12,
            'density': 0.45,
            'avg_speed': 35.5,
            'speeding_count': 2
        },
        'street_2': {
            'vehicle_count': 8,
            'density': 0.30,
            'avg_speed': 42.0,
            'speeding_count': 1
        }
    }
    
    # Update metrics
    metrics = logger.update_current_metrics(parking_test, traffic_test)
    
    print("\n✅ Test metrics updated:")
    print(f"   Parking: {metrics['parking']['occupancy_percentage']}% occupied")
    print(f"   Traffic: {metrics['traffic']['average_density_percentage']}% density")
    print(f"\n📁 Files: {logger.output_dir}/current_metrics.json & metrics_history.csv")

