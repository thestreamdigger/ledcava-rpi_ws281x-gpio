from src.base import BaseEffect
import math
import random
import time

class AlienMother(BaseEffect):
    """Simulates the Mother computer interface"""
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.last_update = time.time()
    
    @property
    def name(self):
        return "AlienMother"
    
    def update(self, audio_data):
        time_val = time.time()
        
        # First 8 values for the left module
        left_data = audio_data[:self.display.width]
        # Last 8 values for the right module
        right_data = audio_data[self.display.width:]
        
        for module in range(self.display.num_modules):
            base = module * (self.display.width * self.display.height)
            data = left_data if module == 0 else right_data
            module_intensity = sum(data) / len(data)
            
            # Scan line igual para ambos os módulos (sem phase)
            scan_position = (time_val * 1.5) % (self.display.height + 1)
            
            for x in range(self.display.width):
                # Ruído digital baseado no áudio do módulo atual
                noise_threshold = data[x] / 16.0
                # Caracteres com fase específica por módulo para manter variação
                char_intensity = int(80 + (40 * math.sin(time_val * 3 + module * math.pi)))
                
                for y in range(self.display.height):
                    # Digital noise específico por módulo
                    noise = random.random() < noise_threshold
                    
                    # Calcula distância da linha de scan para efeito de fade
                    scan_distance = abs(y - scan_position)
                    is_scan_line = scan_distance < 1.0
                    scan_intensity = max(0, 1.0 - scan_distance)
                    
                    # Padrão de caracteres com movimento específico por módulo
                    char_pattern = ((x + int(time_val * 2 + module * 2)) % 3 == 0)
                    
                    if is_scan_line:
                        # Cursor com brilho suave e específico por módulo
                        orange_intensity = scan_intensity * (0.8 + module_intensity * 0.2)
                        red = min(255, int(180 * orange_intensity))
                        green = min(255, int(100 * orange_intensity))
                        blue = min(255, int(20 * orange_intensity))
                        color = (red, green, blue)
                    elif char_pattern and noise:
                        # Caracteres em verde com intensidade baseada no módulo
                        intensity = min(255, int(char_intensity * (0.8 + module_intensity * 0.2)))
                        color = (0, intensity, min(255, intensity//3))
                    else:
                        # Background totalmente preto
                        color = (0, 0, 0)
                    
                    index = base + (y * self.display.width) + x
                    self.display.pixels[index] = color
        
        self.display.show() 