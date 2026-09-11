from dataclasses import dataclass
from pathlib import Path
import numpy as np
try: import soundfile as sf
except ImportError: sf = None

@dataclass
class AudioData:
    samples: np.ndarray; sample_rate: int; path: str; subtype: str = 'unknown'
    @property
    def channels(self): return 1 if self.samples.ndim == 1 else self.samples.shape[1]
    @property
    def frames(self): return len(self.samples)
    @property
    def duration(self): return self.frames / self.sample_rate
    @property
    def mono(self): return self.samples if self.samples.ndim == 1 else self.samples.mean(axis=1)

def load_audio(path, blocksize=262144):
    if sf is None: raise RuntimeError('Install dependencies with: pip install -r requirements.txt')
    info = sf.info(str(path)); data, sr = sf.read(str(path), dtype='float32', always_2d=False)
    if data.size == 0: raise ValueError('Audio file is empty')
    return AudioData(np.asarray(data), sr, str(path), info.subtype)
