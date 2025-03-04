from src.base import BaseEffect
import math
import time

class BladeRunnerNeon(BaseEffect):
    """Neon sign effect with water reflection"""
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.last_update = time.time()
    
    @property
    def name(self):
        return "BladeRunnerNeon"
    
    def update(self, audio_data):
        time_val = time.time()
        delta_time = time_val - self.last_update
        self.last_update = time_val
        
        # First 8 values for the left module
        left_data = audio_data[:self.display.width]
        # Last 8 values for the right module
        right_data = audio_data[self.display.width:]
        
        for module in range(self.display.num_modules):
            base = module * (self.display.width * self.display.height)
            data = left_data if module == 0 else right_data
            module_intensity = sum(data) / len(data)
            
            # Fase específica para cada módulo
            module_phase = module * math.pi / 2
            
            for x in range(self.display.width):
                level = data[x]
                
                # Pulso específico para cada módulo
                pulse = math.sin(time_val * 2 + x * 0.5 + module_phase) * 0.5 + 0.5
                # Cor específica para cada módulo
                hue = (time_val * 0.2 + x * 0.2 + module_phase) % 3
                
                for y in range(self.display.height):
                    # Upper part (neons)
                    if y < self.display.height//2:
                        if y < level:
                            # Intensidade baseada no módulo
                            intensity = pulse * (0.8 + module_intensity * 0.2)
                            if hue < 1:
                                color = (min(255, int(200 * intensity)), 0, min(255, int(100 * intensity)))
                            elif hue < 2:
                                color = (0, min(255, int(200 * intensity)), min(255, int(200 * intensity)))
                            else:
                                color = (min(255, int(200 * intensity)), min(255, int(200 * intensity)), 0)
                        else:
                            color = (0, 0, 0)
                    
                    # Lower part (water reflection)
                    else:
                        mirror_y = self.display.height - 1 - y
                        reflection_strength = 0.15 * (1 - (y - self.display.height//2) / (self.display.height//2))
                        # Ondulação específica para cada módulo
                        water_ripple = math.sin(time_val * 1.5 + x * 0.8 + y * 0.3 + module_phase) * 0.1 + 0.9
                    
                        if mirror_y < level:
                            # Intensidade baseada no módulo
                            intensity = pulse * (0.8 + module_intensity * 0.2)
                            
                            if hue < 1:
                                base_color = (min(255, int(200 * intensity)), 0, min(255, int(100 * intensity)))
                            elif hue < 2:
                                base_color = (0, min(255, int(200 * intensity)), min(255, int(200 * intensity)))
                            else:
                                base_color = (min(255, int(200 * intensity)), min(255, int(200 * intensity)), 0)
                            
                            # Reflexo mais intenso baseado no áudio do módulo
                            reflection_mod = reflection_strength * (1 + module_intensity * 0.2)
                            color = tuple(int(c * reflection_mod * water_ripple) for c in base_color)
                        else:
                            color = (0, 0, 0)
                    
                    index = base + (y * self.display.width) + x
                    self.display.pixels[index] = color
        
        self.display.show() 