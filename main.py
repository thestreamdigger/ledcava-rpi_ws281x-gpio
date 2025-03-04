#!/usr/bin/env python3
from src.base import EffectManager, Logger
from src.processor.cava_manager import CAVAManager
from src.__version__ import __version__, __author__, __copyright__
import argparse
import os

BANNER = f"""LEDCAVA-WS2812
Version {__version__}
{__copyright__}
"""

def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(description='LED effects controller')
    parser.add_argument('--version', '-v', action='version', version=f'LEDCAVA-WS2812 {__version__}')
    parser.add_argument('--effect', type=str, help='Name of the effect to start (ex: BlueWave, WarmPeaks, etc)')
    args = parser.parse_args()

    os.nice(-20)

    manager = EffectManager()
    cava = CAVAManager()

    manager.set_cava_manager(cava)

    if args.effect:
        for i, effect_class in enumerate(manager.effects):
            effect = effect_class(manager.display, None)
            if effect.name == args.effect:
                Logger.info(f"Starting effect: {args.effect}")
                manager.current_effect = i
                manager.auto_cycle = False
                break
        else:
            Logger.error(f"Effect not found: {args.effect}")
            return

    try:
        manager.run()
    except KeyboardInterrupt:
        Logger.info("\nShutting down...")
    except Exception as e:
        Logger.error(f"Critical system error: {str(e)}")
    finally:
        manager.cleanup()

if __name__ == '__main__':
    main() 