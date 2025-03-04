import os
import subprocess
from threading import Thread, Lock
import time
import json
import shutil
from src.base import Logger

def load_config():
    with open('settings.json', 'r') as f:
        return json.load(f)

class CAVAManager:
    def __init__(self):
        config = load_config()
        self.bars = config['audio']['bars']
        self.framerate = config['audio']['framerate']
        if self.bars <= 0 or self.framerate <= 0:
            raise ValueError("Invalid audio settings")
        self.audio_data = [0] * self.bars
        self.lock = Lock()
        self.process = None
        self.running = False
        self.config_file = '/tmp/cava_config'

    def create_config(self):
        if not shutil.which('cava'):
            Logger.error("CAVA executable not found")
            raise RuntimeError("CAVA not installed")
        config = f"""
[general]
bars = {self.bars}
framerate = {self.framerate}

[input]
method = alsa
source = hw:Loopback,1,0
channels = stereo

[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = 8

[smoothing]
noise_reduction = 0
monstercat = 0
waves = 0
gravity = 0
ignore = 0

[eq]
1 = 1
2 = 1
3 = 1
4 = 1
5 = 1
6 = 1
7 = 1
8 = 1
"""
        with open(self.config_file, 'w') as f:
            f.write(config)

    def start(self):
        try:
            self.create_config()
            self.running = True
            os.nice(-20)
            self.process = subprocess.Popen(
                ['cava', '-p', self.config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
                universal_newlines=False
            )
            time.sleep(0.1)
            if self.process.poll() is not None:
                error = self.process.stderr.read().decode()
                Logger.error(f"CAVA initialization failed: {error.strip()}")
                raise RuntimeError(f"CAVA startup failure: {error.strip()}")
            Thread(target=self._read_output, daemon=True).start()
            Logger.info("CAVA started")
        except Exception as e:
            self.running = False
            if self.process:
                self.process.terminate()
                self.process = None
            Logger.error(f"CAVA runtime exception: {str(e)}")
            raise RuntimeError(f"CAVA operation error: {str(e)}")

    def _read_output(self):
        consecutive_errors = 0
        while self.running and self.process:
            try:
                line = self.process.stdout.readline().decode().strip()
                if line:
                    values = [min(int(v), 8) for v in line.split(';') if v]
                    if len(values) == self.bars:
                        with self.lock:
                            self.audio_data = values
                        consecutive_errors = 0
                    else:
                        consecutive_errors += 1
                if consecutive_errors > 10:
                    Logger.warn("Multiple consecutive errors - restarting CAVA...")
                    self.restart()
                    consecutive_errors = 0
            except Exception as e:
                if self.running:
                    Logger.error(f"CAVA communication error: {e}")
                consecutive_errors += 1

    def restart(self):
        Logger.info("Restarting CAVA...")
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
        except:
            pass

    def get_data(self):
        with self.lock:
            return self.audio_data

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            self.process = None
            Logger.info("CAVA stopped")
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
        except:
            pass 