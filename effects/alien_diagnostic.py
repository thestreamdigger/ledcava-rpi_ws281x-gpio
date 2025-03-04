from src.base import BaseEffect
import math
import time

class AlienDiagnostic(BaseEffect):
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.last_update = time.time()
    
    @property
    def name(self):
        return "AlienDiagnostic"
    
    def update(self, audio_data):
        time_val = time.time()
        
        left_data = audio_data[:self.display.width]
        right_data = audio_data[self.display.width:]
        
        for module in range(self.display.num_modules):
            base = module * (self.display.width * self.display.height)
            data = left_data if module == 0 else right_data
            module_intensity = sum(data) / len(data)
            
            for x in range(self.display.width):
                level = data[x]
                
                for y in range(self.display.height):
                    # Aplica rotação de coordenadas
                    if module == 0:
                        # Rotação horária: (x,y) → (y, W-1-x)
                        rot_x = y
                        rot_y = self.display.width - 1 - x
                    else:
                        # Rotação anti-horária: (x,y) → (H-1-y, x)
                        rot_x = self.display.height - 1 - y
                        rot_y = x
                    
                    # Elementos visuais principais:
                    is_grid = (rot_x % 2 == 0) or (rot_y % 2 == 0)
                    data_line = (rot_y == int(time_val * 2) % self.display.height)
                    
                    if (rot_y < level if module == 0 else rot_x < level) and (rot_x < 6 if module == 0 else rot_y < 6):
                        intensity = int(180 + (75 * math.sin(time_val * 4 + module * math.pi)))
                        color = (0, intensity, intensity//2)
                    
                    elif is_grid:
                        grid_intensity = int(20 + (module_intensity * 2))
                        color = (0, grid_intensity, grid_intensity)
                    
                    elif data_line:
                        line_intensity = int(100 + (module_intensity * 5))
                        color = (0, line_intensity, line_intensity)
                    
                    else:
                        color = (0, 0, 0)
                    
                    index = base + (rot_y * self.display.height + rot_x)
                    self.display.pixels[index] = color
        
        self.display.show() 
