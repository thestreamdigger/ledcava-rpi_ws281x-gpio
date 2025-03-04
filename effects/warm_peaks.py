from src.base import BaseEffect

class WarmPeaks(BaseEffect):
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.peak_values = [[0] * display.width for _ in range(display.num_modules)]
        self.peak_decay = 0.2
    
    @property
    def name(self):
        return "WarmPeaks"
    
    def get_warm_color(self, intensity, max_intensity):
        ratio = intensity / max_intensity
        
        if ratio < 0.3:
            r = int(128 + (127 * (ratio * 3)))
            g = int(20 + (40 * (ratio * 3)))
            b = 0
        elif ratio < 0.6:
            r = 255
            g = int(60 + (100 * ((ratio - 0.3) * 3.33)))
            b = 0
        else:
            r = 255
            g = int(160 + (55 * ((ratio - 0.6) * 2.5)))
            b = int(50 * ((ratio - 0.6) * 2.5))
            
        return (min(255, r), min(255, g), min(255, b))
    
    def get_peak_color(self, value, max_value):
        ratio = value / max_value
        r = 255
        g = int(180 + (40 * ratio))
        b = int(30 * ratio)
        return (r, g, b)
    
    def update_peaks(self, values, module):
        for i in range(self.display.width):
            current_peak = self.peak_values[module][i]
            if values[i] > current_peak:
                self.peak_values[module][i] = values[i]
            else:
                self.peak_values[module][i] = max(0, current_peak - self.peak_decay)
    
    def set_rotated_pixel(self, x, y, color, module):
        if module == 0:
            rotated_x = y
            rotated_y = self.display.width - 1 - x
        else:
            rotated_x = self.display.height - 1 - y
            rotated_y = x
            
        self.display.set_pixel(rotated_x, rotated_y, color, module)
    
    def update(self, audio_data):
        left_data = audio_data[:self.display.width]
        self.update_peaks(left_data, 0)
        
        right_data = audio_data[self.display.width:]
        self.update_peaks(right_data, 1)
        
        for x in range(self.display.width):
            value = left_data[x]
            peak = int(self.peak_values[0][x])
            
            for y in range(self.display.height):
                if y < value:
                    color = self.get_warm_color(y + 1, self.display.height)
                    self.set_rotated_pixel(x, self.display.height - 1 - y, color, 0)
                elif y == peak:
                    peak_color = self.get_peak_color(peak, self.display.height)
                    self.set_rotated_pixel(x, self.display.height - 1 - y, peak_color, 0)
                else:
                    self.set_rotated_pixel(x, self.display.height - 1 - y, (0, 0, 0), 0)

        for x in range(self.display.width):
            value = right_data[x]
            peak = int(self.peak_values[1][x])
            
            for y in range(self.display.height):
                if y < value:
                    color = self.get_warm_color(y + 1, self.display.height)
                    self.set_rotated_pixel(x, self.display.height - 1 - y, color, 1)
                elif y == peak:
                    peak_color = self.get_peak_color(peak, self.display.height)
                    self.set_rotated_pixel(x, self.display.height - 1 - y, peak_color, 1)
                else:
                    self.set_rotated_pixel(x, self.display.height - 1 - y, (0, 0, 0), 1)

        self.display.show() 