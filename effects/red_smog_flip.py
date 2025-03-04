from src.base import BaseEffect
import math
import random
import time

class RedSmogFlip(BaseEffect):
    """
    Monochrome red effect with dynamic smog (Flip version)
    In this version, LED mappings are pre-calculated to invert
    the bars in relation to the original red_smog.
    """
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.last_update = time.time()
        self.width = display.width
        self.height = display.height
        self.num_modules = display.num_modules

        # Smog particles
        # Initialize smog particles
        # Number of particles
        # Distributed across both modules
        # Pre-calculating mappings to transform coordinates of each module
        # vertical inversion removed
        # invert both axes
        self.smog_particles = []
        # Inicializa partículas de smog
        for _ in range(20):  # Number of particles
            self.smog_particles.append({
                'x': random.uniform(0, display.width),
                'y': random.uniform(0, display.height * 2),  # Distributed across both modules
                'size': random.uniform(1.5, 3.0),
                'speed': random.uniform(0.02, 0.08),
                'phase': random.uniform(0, 2 * math.pi),
                'density': random.uniform(0.3, 0.7)
            })
        
        # Pré-calculando mapeamentos para transformar as coordenadas de cada módulo.
        # In original red_smog:
        #   Module 0: index = base + x * height + (height - 1 - y)
        #   Module 1: index = base + (width - 1 - x) * height + y
        # For FLIP effect, we invert:
        #   Module 0: index = base + x * height + y         (vertical inversion removed)
        #   Module 1: index = base + (width - 1 - x) * height + (height - 1 - y)  (invert both axes)
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
    
    @property
    def name(self):
        return "RedSmogFlip"
    
    def get_neon_color(self, x, y, time_val, intensity, module):
        """
        Gera a cor de neon monocromática vermelha baseada na posição e no tempo.
        """
        # Pulso suave com leve variação por módulo
        pulse = math.sin(time_val * 2 + x * 0.5 + module * 0.1) * 0.5 + 0.5
        # Intensidade baseada no pulso e na análise de áudio
        base_intensity = pulse * (0.7 + intensity * 0.3)
        red_value = min(255, int(255 * base_intensity))
        return (red_value, 0, 0)
    
    def get_smog_intensity(self, x, y, time_val):
        """
        Calcula a intensidade do smog em um ponto.
        """
        total_density = 0
        
        for particle in self.smog_particles:
            # Movimento ondulante
            particle_x = particle['x'] + math.sin(time_val + particle['phase']) * 0.5
            particle_y = particle['y'] + time_val * particle['speed']
            # Mantém as partículas dentro da área
            particle['y'] = particle_y % (self.height * 2)
            
            # Distância até a partícula
            dx = x - particle_x
            dy = y - particle_y
            dist = math.sqrt(dx * dx + dy * dy)
            
            # Contribuição da partícula para a densidade
            if dist < particle['size']:
                contribution = (1 - dist / particle['size']) * particle['density']
                total_density = max(total_density, contribution)
        
        return total_density
    
    def blend_colors(self, color1, color2, factor):
        """
        Mistura duas cores com um fator de blend.
        """
        return tuple(
            int(c1 * (1 - factor) + c2 * factor)
            for c1, c2 in zip(color1, color2)
        )
    
    def update(self, audio_data):
        time_val = time.time()
        self.last_update = time_val
        
        num_pixels_module = self.width * self.height
        # Processa dados de áudio para cada módulo
        for module in range(self.num_modules):
            base = module * num_pixels_module
            module_data = audio_data[module * self.width:(module + 1) * self.width]
            module_intensity = sum(module_data) / len(module_data)
            
            for x in range(self.width):
                level = module_data[x]
                
                for y in range(self.height):
                    # Ajusta y para o cálculo do smog (considerando os dois módulos)
                    smog_y = y + (module * self.height)
                    
                    # Usa o mapeamento pré-calculado para obter o índice
                    index = base + self.index_maps[module][x][y]
                    
                    # Cor base do neon (apenas tons de vermelho)
                    if y < level:
                        neon_color = self.get_neon_color(x, y, time_val, module_intensity, module)
                    else:
                        neon_color = (0, 0, 0)
                    
                    # Calcula efeito do smog
                    smog_density = self.get_smog_intensity(x, smog_y, time_val)
                    
                    # Cor do smog (tom vermelho suave)
                    smog_color = (30, 0, 0)
                    
                    if neon_color == (0, 0, 0):
                        # Se não há neon, aplica apenas o smog
                        final_color = self.blend_colors(
                            (0, 0, 0),
                            smog_color,
                            smog_density * 0.7
                        )
                    else:
                        # Se há neon, cria um efeito de difusão através do smog
                        glow_factor = smog_density * 0.4
                        diffused_neon = tuple(int(c * (1 - glow_factor)) for c in neon_color)
                        smog_influence = self.blend_colors(
                            smog_color,
                            neon_color,
                            0.3
                        )
                        final_color = self.blend_colors(
                            diffused_neon,
                            smog_influence,
                            smog_density * 0.6
                        )
                    
                    self.display.pixels[index] = final_color
        
        self.display.show()
