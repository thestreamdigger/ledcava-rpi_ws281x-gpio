from src.base import BaseEffect
import math
import random
import time

class QuantumFluid(BaseEffect):
    """Simula um fluido quântico com partículas que respondem a diferentes frequências"""
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.particles = []
        self.energy_field = [[0.0 for _ in range(8)] for _ in range(16)]  # Campo de energia para ambos os módulos
        self.last_update = time.time()
        
        # Configurações ajustáveis
        self.settings = {
            'max_particles': 80,
            'bass_force': 2.5,
            'treble_charge': 0.8,
            'trail_decay': 0.92,
            'color_shift_speed': 0.07,
            'time_warp_intensity': 0.3,
            'vortex_radius': 4.0
        }

    @property
    def name(self):
        return "QuantumFluid2"

    def _generate_energy_field(self, audio_data):
        # Processa os dados de áudio em diferentes faixas de frequência
        bass = sum(audio_data[:2]) / 2
        mids = sum(audio_data[2:5]) / 3
        treble = sum(audio_data[5:]) / 3
        
        # Atualiza o campo de energia
        for x in range(16):
            for y in range(8):
                # Padrão de interferência quântica
                wave = math.sin(x * 0.8 + time.time() * 2) * math.cos(y * 0.6 + time.time() * 1.5)
                self.energy_field[x][y] = (
                    bass * 0.5 * math.sin(x * 0.4) +
                    mids * 0.3 * wave +
                    treble * 0.2 * random.random()
                ) * 0.7

    def _update_particles(self, delta_time):
        # Gera novas partículas baseado na energia do campo
        if len(self.particles) < self.settings['max_particles']:
            for _ in range(int(self.energy_field[random.randint(0,15)][random.randint(0,7)] * 2)):
                self.particles.append({
                    'x': random.uniform(0, 16),
                    'y': random.uniform(0, 8),
                    'vx': random.gauss(0, 0.3),
                    'vy': random.gauss(0, 0.3),
                    'type': random.choice(['bass', 'mid', 'treble']),
                    'life': 1.0
                })

        # Atualiza física das partículas
        for p in self.particles:
            # Efeito de vórtice central
            dx = (p['x'] - 8) / self.settings['vortex_radius']
            dy = (p['y'] - 4) / self.settings['vortex_radius']
            force = math.exp(-(dx*dx + dy*dy)) * self.settings['time_warp_intensity']
            p['vx'] += -dy * force
            p['vy'] += dx * force
            
            # Dinâmica baseada no tipo de partícula
            if p['type'] == 'bass':
                p['vx'] += self.energy_field[int(p['x']) % 16][int(p['y']) % 8] * 0.1
                p['vy'] += math.sin(time.time()) * 0.2
            elif p['type'] == 'mid':
                p['vx'] += math.cos(p['x'] * 0.3) * 0.15
                p['vy'] += math.sin(p['y'] * 0.3) * 0.15
            else:  # treble
                p['vx'] += random.gauss(0, 0.1)
                p['vy'] += random.gauss(0, 0.1)

            # Atrito e limites
            p['vx'] *= 0.96
            p['vy'] *= 0.96
            p['x'] = (p['x'] + p['vx']) % 16
            p['y'] = (p['y'] + p['vy']) % 8
            p['life'] -= 0.01 * delta_time * 60

        # Remove partículas mortas
        self.particles = [p for p in self.particles if p['life'] > 0]

    def _get_particle_color(self, particle):
        # Mapeamento de cores dinâmico
        hue = (time.time() * self.settings['color_shift_speed'] + particle['x'] * 0.1) % 1.0
        saturation = 0.8 - (particle['life'] * 0.3)
        value = 0.5 + (self.energy_field[int(particle['x']) % 16][int(particle['y']) % 8] * 0.5)
        
        # Converte HSV para RGB
        r, g, b = self.hsv_to_rgb(hue, saturation, value)
        fade = min(1.0, particle['life'] * 1.2)
        return (int(r * fade), int(g * fade), int(b * fade))

    def hsv_to_rgb(self, h, s, v):
        # Conversão otimizada de HSV para RGB
        if s == 0.0: return (v, v, v)
        i = int(h*6.0)
        f = (h*6.0) - i
        p = v*(1.0 - s)
        q = v*(1.0 - s*f)
        t = v*(1.0 - s*(1.0-f))
        i %= 6
        return [
            (v, t, p),
            (q, v, p),
            (p, v, t),
            (p, q, v),
            (t, p, v),
            (v, p, q)
        ][i]

    def update(self, audio_data):
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time

        # Gera campo de energia
        self._generate_energy_field(audio_data)
        
        # Modula parâmetros pelo áudio
        bass_level = sum(audio_data[:3]) / 24  # 0-1
        self.settings['time_warp_intensity'] = 0.2 + bass_level * 0.5
        self.settings['vortex_radius'] = 3.0 + (1 - bass_level) * 2.0

        # Atualiza sistema de partículas
        self._update_particles(delta_time)

        # Renderização
        for module in range(2):
            base = module * 64
            for x in range(8):
                for y in range(8):
                    # Calcula a energia acumulada
                    energy = 0.0
                    for p in self.particles:
                        dist = math.hypot(
                            (p['x'] - (x + module*8)) * 0.7,
                            (p['y'] - y) * 0.7
                        )
                        if dist < 1.5:
                            energy += p['life'] * (1.5 - dist)

                    # Mapeia para cores
                    color = (
                        min(255, int(energy * 80)),
                        min(255, int(energy * 60)),
                        min(255, int(energy * 100))
                    )
                    
                    # Efeito de bloom
                    bloom_intensity = min(1.0, energy * 0.5)
                    color = (
                        min(255, color[0] + int(255 * bloom_intensity)),
                        min(255, color[1] + int(200 * bloom_intensity)),
                        min(255, color[2] + int(150 * bloom_intensity))
                    )
                    
                    # Aplica padrão de interferência
                    if (x + y) % 2 == 0:
                        color = tuple(int(c * 0.8) for c in color)
                    
                    # Atualiza pixel
                    index = base + x * 8 + (7 - y) if module == 0 else base + (7 - x) * 8 + y
                    self.display.pixels[index] = color

        self.display.show() 
