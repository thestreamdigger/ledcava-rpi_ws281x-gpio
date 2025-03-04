from src.base import BaseEffect
import math
import random
import time

class AlienWarning(BaseEffect):
    """Simulates the vintage CRT-style VU meters of the Nostromo"""
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.last_update = time.time()
    
    @property
    def name(self):
        return "AlienWarning"
    
    def update(self, audio_data):
        time_val = time.time()
        
        # First 8 values for the left module
        left_data = audio_data[:self.display.width]
        # Last 8 values for the right module
        right_data = audio_data[self.display.width:]
        
        # Smoother pulsation
        base_pulse = (math.sin(time_val * 2) + 1) / 2 * 0.2 + 0.8
        background_variation = (math.sin(time_val * 0.7) + 1) / 2 * 0.3 + 0.7
        
        for module in range(self.display.num_modules):
            base = module * (self.display.width * self.display.height)
            data = left_data if module == 0 else right_data
            
            for x in range(self.display.width):
                is_left_vu = x < 4
                vu_x = x if is_left_vu else x - 4
                
                # Get the level for the entire VU bar (3 pixels wide)
                if is_left_vu:
                    level = int(data[0])  # Use first value for left VU bar
                else:
                    level = int(data[4])  # Use middle value for right VU bar
                
                # Calculate the intensity for the entire column
                if vu_x < 3:  # Main VU area
                    pwm_intensity = base_pulse
                    red = int(100 * pwm_intensity)
                    green = int(70 * pwm_intensity)
                    base_color = (red, green, 0)
                else:
                    edge_fade = (3 - (vu_x - 3)) / 3
                    intensity = max(int(8 * edge_fade * base_pulse), 
                                 int(5 * background_variation))
                    base_color = (intensity, intensity // 2, 0)
                
                for y in range(self.display.height):
                    y_inv = self.display.height - 1 - y
                    
                    if vu_x < 3:  # Main VU area
                        if y_inv < level:
                            color = base_color
                        else:
                            noise = random.random() * 0.1 + 0.95
                            dim_red = int(15 * background_variation * noise)
                            dim_green = int(8 * background_variation * noise)
                            color = (dim_red, dim_green, 0)
                    else:
                        color = base_color
                    
                    index = base + (y * self.display.width) + x
                    self.display.pixels[index] = color
        
        self.display.show() 