from src.base import BaseEffect
import math
import time

class BladeRunnerSmog(BaseEffect):
    """Police lights (Spinner) and smog effect"""
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.car_x = 7
        self.car_y = 2
        self.last_update = time.time()
    
    @property
    def name(self):
        return "BladeRunnerSmog"
    
    def update(self, audio_data):
        time_val = time.time()
        
        # First 8 values for the left module
        left_data = audio_data[:self.display.width]
        # Last 8 values for the right module
        right_data = audio_data[self.display.width:]
        
        for module in range(self.display.num_modules):
            base = module * (self.display.width * self.display.height)
            data = left_data if module == 0 else right_data
            
            # Calculate intensities using only current channel data
            bass_intensity = min(1.0, sum(data[:4]) / (4 * 8))
            treble_intensity = min(1.0, sum(data[4:]) / (4 * 8))
            
            for x in range(self.display.width):
                for y in range(self.display.height):
                    base_fog = 5
                    
                    plasma = (
                        math.sin(x/4 + time_val) * 
                        math.cos(y/4 + time_val * 0.5) * 
                        math.sin((x+y)/6 + time_val * 0.3)
                    )
                    
                    dist_from_center = math.sqrt((x-3.5)**2 + (y-3.5)**2)
                    plasma *= math.pow(0.9, dist_from_center)
                    
                    plasma2 = (
                        math.sin(x/3 - time_val * 0.7) * 
                        math.cos(y/3 - time_val * 0.4) * 
                        math.sin((x-y)/5 - time_val * 0.2)
                    )
                    
                    plasma3 = (
                        math.sin(x/5 + time_val * 0.2) * 
                        math.cos(y/5 + time_val * 0.15) * 
                        math.sin((x+y)/8 + time_val * 0.1)
                    )
                    plasma3 *= math.pow(0.95, dist_from_center)
                    
                    plasma = (plasma + plasma2) * 0.4 + plasma3 * 0.6
                    
                    audio_mod = data[x] / 8.0
                    plasma = plasma * (0.3 + audio_mod * 0.7)
                    
                    plasma_intensity = min(255, int(abs(plasma * 100))) + base_fog
                    
                    dist_to_car = math.sqrt((x - self.car_x)**2 + (y - self.car_y)**2)
                    car_light = max(0, 1 - (dist_to_car / 8)) * 60
                    
                    police_time = time_val * 1.5
                    rot_x = self.car_x + math.cos(police_time) * 2
                    rot_y = self.car_y + math.sin(police_time) * 2
                    
                    dist_to_rot = math.sqrt((x - rot_x)**2 + (y - rot_y)**2)
                    rot_light = max(0, 1 - (dist_to_rot / 3)) * 40
                    
                    police_intensity = car_light + rot_light
                    
                    is_red = (math.sin(police_time) > 0) != (module == 1)
                    
                    if is_red:
                        red = int(police_intensity * treble_intensity)
                        green = int(police_intensity * treble_intensity * 0.15)
                        blue = 0
                    else:
                        red = 0
                        green = int(police_intensity * bass_intensity * 0.4)
                        blue = int(police_intensity * bass_intensity)
                    
                    smoke_light_interaction = math.pow(0.7, dist_to_car) * plasma_intensity * 0.4
                    
                    base_color = base_fog + int(plasma_intensity * 0.3)
                    color = (
                        min(255, base_color + red + int(smoke_light_interaction * (1 if is_red else 0))),
                        min(255, base_color + green),
                        min(255, base_color + blue + int(smoke_light_interaction * (0 if is_red else 1)))
                    )
                    
                    index = base + (y * self.display.width) + x
                    self.display.pixels[index] = color
        
        self.display.show() 