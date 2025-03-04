from src.base import BaseEffect
import math
import time

class SuspiriaSpectrumFlip(BaseEffect):
    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.last_update = time.time()
        self.width = display.width
        self.height = display.height
        self.num_modules = display.num_modules
        self.energy_buffer = [
            [[0.0 for _ in range(self.height)] for _ in range(self.width)]
            for _ in range(self.num_modules)
        ]
        self.peak_tracker = [
            [[0.0 for _ in range(self.height)] for _ in range(self.width)]
            for _ in range(self.num_modules)
        ]
        mapping0 = [[x * self.height + y for y in range(self.height)]
                    for x in range(self.width)]
        mapping1 = [[(self.width - 1 - x) * self.height + (self.height - 1 - y) for y in range(self.height)]
                    for x in range(self.width)]
        self.index_maps = [mapping0, mapping1]

    @property
    def name(self):
        return "SuspiriaSpectrumFlip"

    def _calculate_decay(self, delta_time):
        return math.exp(-delta_time * 5.0)

    def _update_energy_buffer(self, audio_data, delta_time):
        decay_factor = self._calculate_decay(delta_time)
        for module in range(self.num_modules):
            module_data = audio_data[module * self.width:(module + 1) * self.width]
            for x in range(self.width):
                current_energy = min(module_data[x] / 8.0, 1.0)
                vertical_base = 1.2 - (x / self.width)
                for y in range(self.height):
                    vertical_factor = (1.0 - (y / self.height)) ** 2
                    new_energy = current_energy * vertical_factor * vertical_base
                    self.energy_buffer[module][x][y] = max(self.energy_buffer[module][x][y] * decay_factor, new_energy)
                    self.peak_tracker[module][x][y] = max(self.peak_tracker[module][x][y] * (0.92 + y * 0.003), self.energy_buffer[module][x][y])

    def _get_pulse_color(self, energy, peak):
        base_r = int(200 * energy)
        base_g = int(40 * energy ** 1.2)
        peak_blue = int(100 * peak ** 0.8)
        return (min(255, base_r + int(peak * 50)), min(255, base_g), min(255, peak_blue))

    def update(self, audio_data):
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        self._update_energy_buffer(audio_data, delta_time)
        num_pixels_module = self.width * self.height
        for module in range(self.num_modules):
            base = module * num_pixels_module
            mapping = self.index_maps[module] if module < len(self.index_maps) else None
            for x in range(self.width):
                for y in range(self.height):
                    energy = self.energy_buffer[module][x][y]
                    peak = self.peak_tracker[module][x][y]
                    color = self._get_pulse_color(energy, peak)
                    index = base + mapping[x][y] if mapping else base + x * self.height + y
                    self.display.pixels[index] = color
        self.display.show()

    # Apply interference pattern
