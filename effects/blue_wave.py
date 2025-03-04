from src.base import BaseEffect

class BlueWave(BaseEffect):
    @property
    def name(self):
        return "BlueWave"
    
    def update(self, audio_data):
        for module in range(self.display.num_modules):
            base = module * self.display.width * self.display.height
            
            for x in range(self.display.width):
                value = audio_data[module * self.display.width + x]
                
                for y in range(self.display.height):
                    if module == 0:
                        index = base + x * self.display.height + (self.display.height - 1 - y)
                    else:
                        index = base + (self.display.width - 1 - x) * self.display.height + y
                    
                    self.display.pixels[index] = (0, 0, 255) if y < value else (10, 0, 0)
        
        self.display.show() 