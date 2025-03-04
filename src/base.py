import os
import time
import json
from rpi_ws281x import PixelStrip, Color

class Logger:
    COLORS = {
        'INFO': '\033[92m',
        'WARN': '\033[93m',
        'ERROR': '\033[91m',
        'RESET': '\033[0m'
    }
    @staticmethod
    def log(level, message):
        color = Logger.COLORS.get(level, '')
        reset = Logger.COLORS['RESET']
        print(f"{color}[{level}] {message}{reset}")
    @staticmethod
    def info(message):
        Logger.log('INFO', message)
    @staticmethod
    def warn(message):
        Logger.log('WARN', message)
    @staticmethod
    def error(message):
        Logger.log('ERROR', message)

class DisplayController:
    def __init__(self, brightness, num_pixels, module_width, module_height, num_modules, gpio_pin):
        self.width = module_width
        self.height = module_height
        self.num_modules = num_modules
        self.num_pixels = num_pixels
        if self.width <= 0 or self.height <= 0 or self.num_modules <= 0:
            raise ValueError("Invalid display dimensions")
        if self.num_pixels != self.width * self.height * self.num_modules:
            raise ValueError("Total number of pixels does not match module dimensions")
        if not 0 < brightness <= 1:
            raise ValueError("Brightness must be between 0 and 1")
        self.indices = {}
        for module in range(self.num_modules):
            base = module * (self.width * self.height)
            for x in range(self.width):
                for y in range(self.height):
                    if module == 0:
                        index = base + x * self.height + (self.height - 1 - y)
                    else:
                        index = base + (self.width - 1 - x) * self.height + y
                    self.indices[(x, y, module)] = index
        LED_FREQ_HZ = 800000
        LED_DMA = 10
        LED_INVERT = False
        LED_CHANNEL = 0
        self.strip = PixelStrip(num_pixels, gpio_pin, LED_FREQ_HZ, LED_DMA, LED_INVERT, int(brightness * 255), LED_CHANNEL)
        self.strip.begin()
        self.pixels = self

    def clear(self):
        for i in range(self.num_pixels):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()

    def set_pixel(self, x, y, color, module):
        if 0 <= x < self.width and 0 <= y < self.height:
            index = self.indices.get((x, y, module))
            if index is None:
                raise ValueError("Invalid index")
            r, g, b = color
            self.strip.setPixelColor(index, Color(r, g, b))
    
    def show(self):
        self.strip.show()
    
    def __setitem__(self, index, color):
        r, g, b = color
        self.strip.setPixelColor(index, Color(r, g, b))
    
    def __getitem__(self, index):
        return None
    
    def __len__(self):
        return self.num_pixels

class BaseEffect:
    def __init__(self, display, audio):
        self.display = display
        self.audio = audio
        self.last_update = time.time()

    @property
    def name(self):
        return self.__class__.__name__

    def update(self, audio_data):
        raise NotImplementedError

class EffectManager:
    def __init__(self):
        with open('settings.json', 'r') as f:
            self.config = json.load(f)
        display_config = self.config['display']
        gpio_pin = display_config.get('gpio_pin', 18)
        self.display = DisplayController(
            brightness=display_config['brightness'],
            num_pixels=display_config['num_pixels'],
            module_width=display_config['module_width'],
            module_height=display_config['module_height'],
            num_modules=display_config['num_modules'],
            gpio_pin=gpio_pin
        )
        self.effects = []
        self.current_effect = 0
        self.last_effect_change = time.time()
        self.cava = None
        self.auto_cycle = self.config['effects']['auto_cycle']
        self.effect_duration = self.config['effects']['duration']
        self.load_effects()

    def load_effects(self):
        import importlib
        import inspect
        import pkgutil
        import effects
        effects_path = os.path.dirname(effects.__file__)
        if 'enabled' not in self.config['effects']:
            self.config['effects']['enabled'] = {}
        for _, name, _ in pkgutil.iter_modules([effects_path]):
            if name != '__init__':
                try:
                    module = importlib.import_module(f'effects.{name}')
                    for item_name, item in inspect.getmembers(module):
                        if (inspect.isclass(item) and issubclass(item, BaseEffect) and item != BaseEffect):
                            temp_instance = item(self.display, None)
                            effect_name = temp_instance.name
                            if effect_name not in self.config['effects']['enabled']:
                                self.config['effects']['enabled'][effect_name] = True
                                with open('settings.json', 'w') as f:
                                    json.dump(self.config, f, indent=4)
                            if self.config['effects']['enabled'].get(effect_name, True):
                                self.effects.append(item)
                                Logger.info(f"Effect auto-loaded: {effect_name}")
                except Exception as e:
                    Logger.error(f"Error loading effect {name}: {str(e)}")

    def set_cava_manager(self, cava):
        self.cava = cava

    def next_effect(self):
        if self.effects:
            self.current_effect = (self.current_effect + 1) % len(self.effects)
            self.last_effect_change = time.time()

    def run(self):
        if not self.effects:
            Logger.error("No effects enabled")
            return
        self.cava.start()
        current_effect = None
        Logger.info("System ready - Press Ctrl+C to exit")
        try:
            while True:
                current_time = time.time()
                if self.auto_cycle and current_time - self.last_effect_change >= self.effect_duration:
                    self.next_effect()
                    current_effect = None
                if current_effect is None:
                    effect_class = self.effects[self.current_effect]
                    current_effect = effect_class(self.display, self.cava)
                if self.cava:
                    audio_data = self.cava.get_data()
                    current_effect.update(audio_data)
                time.sleep(1/60)
        except KeyboardInterrupt:
            Logger.info("\nShutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        if self.cava:
            self.cava.stop()
        self.display.clear()
        Logger.info("System stopped")

    def get_effect_by_name(self, name):
        for effect_class in self.effects:
            effect = effect_class(self.display, self.cava)
            if effect.name == name:
                return effect_class
        return None 