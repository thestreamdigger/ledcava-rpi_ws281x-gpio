from src.base import BaseEffect
import math
import random
import time

class NegativeMotion(BaseEffect):
    """Motion effect with inverted colors - gray background with black movement"""
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        # Define centers for each module
        self.centers = [
            (display.width / 2, display.height / 2),  # Center of module 0
            (display.width / 2, display.height / 2)   # Center of module 1
        ]
        self.max_distance = math.sqrt((display.width * display.width) + (display.height * display.height))
        self.movement_points = []  # List of active movement points
        
    @property
    def name(self):
        return "NegativeMotion"
    
    def update_movement_points(self, audio_data):
        # Remove old points
        self.movement_points = [p for p in self.movement_points if p['life'] > 0]
        
        # Process audio data separately for each module
        for module in range(self.display.num_modules):
            module_data = audio_data[module * self.display.width:(module + 1) * self.display.width]
            center_x, center_y = self.centers[module]
            
            for i, value in enumerate(module_data):
                if value > 3:  # Threshold to create new point
                    # Random position in module
                    x = random.uniform(0, self.display.width)
                    y = random.uniform(0, self.display.height)
                    
                    # Add new point with reduced intensity
                    self.movement_points.append({
                        'x': x,
                        'y': y,
                        'intensity': value * 0.7,  # Reduce base intensity
                        'life': 12,  # Reduce lifetime a bit
                        'direction': random.uniform(-0.15, 0.15),  # Reduce randomness
                        'module': module,
                        'center_x': center_x,
                        'center_y': center_y
                    })
        
        # Update position and lifetime of points
        for point in self.movement_points:
            # Move point towards module center
            dx = point['center_x'] - point['x']
            dy = point['center_y'] - point['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Movement towards center + some randomness
                point['x'] += (dx/dist * 0.15 + point['direction'])
                point['y'] += (dy/dist * 0.15 + point['direction'])
            
            point['life'] -= 0.7  # Decrease lifetime more quickly
    
    def update(self, audio_data):
        self.update_movement_points(audio_data)
        
        # First define all pixels as light gray
        for i in range(len(self.display.pixels)):
            self.display.pixels[i] = (40, 40, 40)  # Same gray as NegativeWave
        
        for module in range(self.display.num_modules):
            base = module * (self.display.width * self.display.height)
            
            for x in range(self.display.width):
                for y in range(self.display.height):
                    # Calculate index based on snake profile
                    if module == 0:
                        index = base + x * self.display.height + (self.display.height - 1 - y)
                    else:
                        index = base + (self.display.width - 1 - x) * self.display.height + y
                    
                    # Check if there are nearby movement points
                    total_intensity = 0
                    for point in self.movement_points:
                        if point['module'] == module:
                            dx = point['x'] - x
                            dy = point['y'] - y
                            dist = math.sqrt(dx*dx + dy*dy)
                            
                            if dist < 1.2:  # Reduce influence area
                                # Calculate intensity with steeper falloff
                                intensity = (1 - dist/1.2) * (point['life']/12) * point['intensity']
                                total_intensity = max(total_intensity, intensity)
                    
                    if total_intensity > 0:
                        # Adjust darkening curve
                        darkness = min(1.0, total_intensity * 0.6)  # Reduces darkening factor
                        # Interpolate between light gray (40) and black (0)
                        color_value = int(40 * (1 - darkness))
                        self.display.pixels[index] = (color_value, color_value, color_value)
        
        self.display.show() 

# Check if pixel is part of center cross symbol 