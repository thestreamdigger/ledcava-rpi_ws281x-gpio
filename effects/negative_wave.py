from src.base import BaseEffect

class NegativeWave(BaseEffect):
    """Wave effect with inverted colors - light gray background with dark activity"""
    
    @property
    def name(self):
        return "NegativeWave"
    
    def update(self, audio_data):
        for module in range(self.display.num_modules):
            base = module * self.display.width * self.display.height
            
            # Processa dados do módulo atual
            module_data = audio_data[module * self.display.width:(module + 1) * self.display.width]
            
            for x in range(self.display.width):
                value = module_data[x]
                
                for y in range(self.display.height):
                    if module == 0:
                        index = base + x * self.display.height + (self.display.height - 1 - y)
                    else:
                        index = base + (self.display.width - 1 - x) * self.display.height + y
                    
                    self.display.pixels[index] = (0, 0, 0) if y < value else (40, 40, 40)
        
        self.display.show() 