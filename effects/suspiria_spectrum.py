from src.base import BaseEffect
import math
import time

class AudioPulse(BaseEffect):
    """Efeito de pulsação dinâmica com persistência por LED individual"""
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.last_update = time.time()
        # Buffer 3D: [módulo][x][y]
        self.energy_buffer = [[[0.0 for _ in range(display.height)] for _ in range(display.width)] for _ in range(display.num_modules)]
        self.peak_tracker = [[[0.0 for _ in range(display.height)] for _ in range(display.width)] for _ in range(display.num_modules)]
    
    @property
    def name(self):
        return "SuspiriaSpectrum"
    
    def _calculate_decay(self, delta_time):
        return math.exp(-delta_time * 5.0)  # Decaimento mais rápido para melhor resposta
    
    def _update_energy_buffer(self, audio_data, delta_time):
        decay_factor = self._calculate_decay(delta_time)
        
        for module in range(self.display.num_modules):
            module_data = audio_data[module*self.display.width : (module+1)*self.display.width]
            
            for x in range(self.display.width):
                current_energy = min(module_data[x] / 8.0, 1.0)
                vertical_base = 1.2 - (x / self.display.width)  # Variação horizontal
                
                for y in range(self.display.height):
                    vertical_factor = (1.0 - (y / self.display.height)) ** 2  # Curva quadrática
                    new_energy = current_energy * vertical_factor * vertical_base
                    
                    # Atualização com decaimento não-linear
                    self.energy_buffer[module][x][y] = max(
                        self.energy_buffer[module][x][y] * decay_factor,
                        new_energy
                    )
                    
                    # Persistência de picos com decay variável
                    self.peak_tracker[module][x][y] = max(
                        self.peak_tracker[module][x][y] * (0.92 + y*0.003),  # Decay mais lento na base
                        self.energy_buffer[module][x][y]
                    )
    
    def _get_pulse_color(self, energy, peak):
        # Base laranja-vermelho com saturação progressiva
        base_r = int(200 * energy)
        base_g = int(40 * energy ** 1.2)
        
        # Efeito de pico azulado
        peak_blue = int(100 * peak ** 0.8)
        
        return (
            min(255, base_r + int(peak * 50)),
            min(255, base_g),
            min(255, peak_blue)
        )
    
    def update(self, audio_data):
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        
        self._update_energy_buffer(audio_data, delta_time)
        
        for module in range(self.display.num_modules):
            base = module * (self.display.width * self.display.height)
            
            for x in range(self.display.width):
                for y in range(self.display.height):
                    energy = self.energy_buffer[module][x][y]
                    peak = self.peak_tracker[module][x][y]
                    
                    color = self._get_pulse_color(energy, peak)
                    
                    if module == 0:
                        index = base + x * self.display.height + (self.display.height - 1 - y)
                    else:
                        index = base + (self.display.width - 1 - x) * self.display.height + y
                    
                    self.display.pixels[index] = color
        
        self.display.show() 
