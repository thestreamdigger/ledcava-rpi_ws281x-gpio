from src.base import BaseEffect
import colorsys
import time

class Rainbow(BaseEffect):
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.hue = 0
        self.last_update = time.time()
        self.peak_values = [0] * (display.width * display.num_modules)
        self.peak_decay = 0.1
    
    @property
    def name(self):
        return "Rainbow"
    
    def hsv_to_rgb(self, h, s, v):
        """Converts HSV to RGB"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def update(self, audio_data):
        time_val = time.time()
        delta_time = time_val - self.last_update
        self.last_update = time_val
        
        # Update peaks and calculate total energy
        total_energy = 0
        for i, value in enumerate(audio_data):
            if value > self.peak_values[i]:
                self.peak_values[i] = value
            else:
                self.peak_values[i] = max(0, self.peak_values[i] - self.peak_decay)
            total_energy += value
        
        # Use total energy to influence color change speed
        energy_ratio = total_energy / (len(audio_data) * self.display.height)
        self.hue = (self.hue + energy_ratio * delta_time) % 1.0
        
        for module in range(self.display.num_modules):
            base = module * self.display.width * self.display.height
            
            for x in range(self.display.width):
                idx = module * self.display.width + x
                value = audio_data[idx]
                peak = self.peak_values[idx]
                
                # Use audio value to determine hue and saturation
                column_hue = (self.hue + (value / self.display.height * 0.5)) % 1.0
                
                for y in range(self.display.height):
                    if y < value:
                        # Higher sound means more saturated color
                        saturation = 0.5 + (value / self.display.height * 0.5)
                        # Brightness based on vertical position and energy
                        brightness = 0.3 + (y / value * 0.7)
                        
                        color = self.hsv_to_rgb(column_hue, saturation, brightness)
                    elif y == int(peak):
                        # Peak with lighter color
                        peak_color = self.hsv_to_rgb(column_hue, 0.5, 1.0)
                        color = peak_color
                    else:
                        # Smooth fade out
                        fade = max(0, 1 - (y - value) / 3)
                        if fade > 0:
                            dim_color = self.hsv_to_rgb(column_hue, 0.8, fade * 0.3)
                            color = dim_color
                        else:
                            color = (0, 0, 0)
                    
                    # Apply correct rotation for each module
                    if module == 0:
                        index = base + x * self.display.height + (self.display.height - 1 - y)
                    else:
                        index = base + (self.display.width - 1 - x) * self.display.height + y
                    
                    self.display.pixels[index] = color
        
        self.display.show() 