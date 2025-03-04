from src.base import BaseEffect
import math
import random
import time

class AlienMotionTracker(BaseEffect):
    """Simulates the iconic radar/motion tracker from the Alien movie"""
    
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.center_x = display.width / 2
        self.center_y = display.height  # Move center below the display
        self.sector_angle = math.pi / 2  # 90 degrees sector
        self.max_distance = math.sqrt((display.width * display.width) + (display.height * display.height))
        self.movement_points = []  # Lista de pontos de movimento ativos
        
    def is_crosshair_pixel(self, x, y):
        """Verifica se o pixel faz parte do símbolo + no centro"""
        center_x_int = int(self.center_x)
        center_y_int = int(self.center_y)
        
        # Verifica se está na linha vertical ou horizontal do +
        is_vertical = x == center_x_int and abs(y - center_y_int) <= 1
        is_horizontal = y == center_y_int and abs(x - center_x_int) <= 1
        
        return is_vertical or is_horizontal
        
    @property
    def name(self):
        return "AlienMotion"
    
    def update_movement_points(self, audio_data):
        # Remove pontos antigos
        self.movement_points = [p for p in self.movement_points if p['life'] > 0]
        
        # Processa dados de áudio para cada módulo separadamente
        for module in range(self.display.num_modules):
            module_data = audio_data[module * self.display.width:(module + 1) * self.display.width]
            
            for i, value in enumerate(module_data):
                if value > 3:  # Threshold para criar novo ponto
                    # Calcula posição baseada no índice do audio
                    angle = (i / len(module_data)) * self.sector_angle + (math.pi/2 - self.sector_angle/2)
                    # Distância aleatória, mas tendendo a ser maior
                    distance = random.uniform(0.5, 1.0) * self.max_distance
                    
                    # Calcula posição x,y
                    x = self.center_x + math.cos(angle) * distance
                    y = self.center_y - math.sin(angle) * distance
                    
                    # Adiciona novo ponto se dentro dos limites e no módulo correto
                    if (0 <= x < self.display.width and 0 <= y < self.display.height):
                        self.movement_points.append({
                            'x': x,
                            'y': y,
                            'intensity': value,
                            'life': 10,
                            'direction': random.uniform(-0.1, 0.1),
                            'module': module  # Guarda o módulo de origem
                        })
        
        # Atualiza posição e vida dos pontos
        for point in self.movement_points:
            # Move ponto em direção ao centro
            dx = self.center_x - point['x']
            dy = self.center_y - point['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Movimento em direção ao centro + alguma aleatoriedade
                point['x'] += (dx/dist * 0.2 + point['direction'])
                point['y'] += (dy/dist * 0.2 + point['direction'])
            
            point['life'] -= 1
    
    def update(self, audio_data):
        time_val = time.time()
        scan_angle = (time_val * 2) % (2 * math.pi)  # Full rotation
        
        self.update_movement_points(audio_data)
        
        # Clear all pixels first
        for i in range(len(self.display.pixels)):
            self.display.pixels[i] = (0, 0, 0)
        
        for module in range(self.display.num_modules):
            base = module * (self.display.width * self.display.height)
            # Calcula intensidade média apenas para os dados deste módulo
            module_data = audio_data[module * self.display.width:(module + 1) * self.display.width]
            module_intensity = sum(module_data) / len(module_data)
            
            for x in range(self.display.width):
                for y in range(self.display.height):
                    # Calculate distance and angle from center
                    dx = x - self.center_x
                    dy = y - self.center_y
                    distance = math.sqrt(dx*dx + dy*dy)
                    angle = math.atan2(-dy, dx)
                    
                    # Normalize angle to 0-2π range
                    if angle < 0:
                        angle += 2 * math.pi
                    
                    sector_start = math.pi/2 - self.sector_angle/2
                    sector_end = math.pi/2 + self.sector_angle/2
                    
                    if sector_start <= angle <= sector_end:
                        # Base radar effect
                        scan_diff = abs(angle - (scan_angle % (2 * math.pi)))
                        scan_intensity = max(0, 1 - scan_diff)
                        normalized_distance = distance / self.max_distance
                        
                        # Verifica se há pontos de movimento próximos
                        movement_intensity = 0
                        for point in self.movement_points:
                            # Só considera pontos do mesmo módulo
                            if point['module'] == module:
                                px, py = point['x'], point['y']
                                if abs(px - x) < 0.75 and abs(py - y) < 0.75:
                                    dist_to_point = math.sqrt((px-x)**2 + (py-y)**2)
                                    movement_intensity = max(movement_intensity, 
                                        point['intensity'] * (1 - dist_to_point) * (point['life']/10))
                        
                        # Verifica se é parte do crosshair central
                        if self.is_crosshair_pixel(x, y):
                            # Crosshair vermelho pulsante baseado no áudio do módulo
                            base_intensity = 20  # Intensidade mínima menor
                            # Resposta mais dramática ao áudio
                            if module_intensity > 4:  # Threshold para "detecção"
                                pulse_intensity = int(module_intensity * 60)  # Multiplicador maior
                            else:
                                pulse_intensity = 0
                            intensity = min(255, base_intensity + pulse_intensity)
                            color = (intensity, 0, 0)  # Vermelho pulsante
                        elif movement_intensity > 0:
                            # Ponto de movimento com variação de cor baseada na distância e intensidade
                            base_intensity = min(255, int(255 * movement_intensity * normalized_distance))
                            
                            # Quanto mais próximo do centro, mais branco fica
                            white_factor = max(0, min(1, 1 - normalized_distance))
                            green_intensity = min(255, base_intensity)
                            white_intensity = min(255, int(base_intensity * white_factor * 0.8))  # 80% de branco no máximo
                            
                            # Garante que todos os valores estão no intervalo 0-255
                            r = max(0, min(255, white_intensity))
                            g = max(0, min(255, green_intensity))
                            b = max(0, min(255, white_intensity))
                            color = (r, g, b)
                        else:
                            # Apenas o efeito de varredura, sem grid
                            base_intensity = min(255, int(30 * scan_intensity))
                            color = (0, base_intensity, 0)
                        
                        index = base + (y * self.display.width) + x
                        self.display.pixels[index] = color
        
        self.display.show()