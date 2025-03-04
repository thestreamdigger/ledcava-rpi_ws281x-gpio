from src.base import BaseEffect

class NegativeWaveFlip(BaseEffect):
    """Wave effect with inverted colors (NegativeWaveFlip) - light gray background with dark activity"""
    
    @property
    def name(self):
        return "NegativeWaveFlip"
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.width = display.width
        self.height = display.height
        self.num_modules = display.num_modules

        # Pre-calculates index mapping for each module.
        # For module 0, we use natural mapping:
        #   index = x * height + y
        # For module 1, we apply axis flip:
        #   index = (width - 1 - x) * height + (height - 1 - y)
        mapping0 = [
            [x * self.height + y for y in range(self.height)]
            for x in range(self.width)
        ]
        mapping1 = [
            [(self.width - 1 - x) * self.height + (self.height - 1 - y)
             for y in range(self.height)]
            for x in range(self.width)
        ]
        self.index_maps = [mapping0, mapping1]

    def update(self, audio_data):
        num_pixels_module = self.width * self.height
        
        for module in range(self.num_modules):
            base = module * num_pixels_module
            module_data = audio_data[module * self.width:(module + 1) * self.width]
            
            for x in range(self.width):
                value = module_data[x]
                for y in range(self.height):
                    index = base + self.index_maps[module][x][y]
                    # If y is below audio value, light up with active color (black),
                    # otherwise, assign gray background (40, 40, 40)
                    self.display.pixels[index] = (0, 0, 0) if y < value else (40, 40, 40)
        
        self.display.show()
