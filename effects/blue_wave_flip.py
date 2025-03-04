from src.base import BaseEffect

class BlueWaveFlip(BaseEffect):
    @property
    def name(self):
        return "BlueWaveFlip"

    def __init__(self, display, audio):
        super().__init__(display, audio)
        self.width = display.width
        self.height = display.height
        self.num_modules = display.num_modules

        # Pré-cálculo dos mapeamentos de índices para cada módulo.
        # No BlueWave original:
        #   módulo 0 usava: index = base + x * height + (height - 1 - y)
        #   módulo 1 usava: index = base + (width - 1 - x) * height + y
        #
        # Aqui, desejamos inverter (flipar) as barras:
        #   Para module 0, usamos o mapeamento natural vertical:
        #       index = base + x * height + y
        #   Para module 1, invertemos ambos os eixos:
        #       index = base + (width - 1 - x) * height + (height - 1 - y)
        mapping0 = [
            [x * self.height + y for y in range(self.height)]
            for x in range(self.width)
        ]
        mapping1 = [
            [(self.width - 1 - x) * self.height + (self.height - 1 - y) for y in range(self.height)]
            for x in range(self.width)
        ]
        self.index_maps = [mapping0, mapping1]

    def update(self, audio_data):
        num_pixels_module = self.width * self.height
        # Itera nos módulos usando os mapeamentos pré-calculados
        for module in range(self.num_modules):
            base = module * num_pixels_module

            for x in range(self.width):
                # Obtém o valor do áudio para a coluna x deste módulo
                value = audio_data[module * self.width + x]

                for y in range(self.height):
                    index = base + self.index_maps[module][x][y]
                    # Se a linha "y" estiver abaixo de value, pinta de azul; caso contrário, fundo escuro.
                    self.display.pixels[index] = (0, 0, 255) if y < value else (10, 0, 0)

        self.display.show()
