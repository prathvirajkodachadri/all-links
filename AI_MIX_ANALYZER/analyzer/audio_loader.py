from dataclasses import dataclass
from pathlib import Path
import numpy as np
try:
    import soundfile as sf
except ImportError:
    sf = None


@dataclass
class AudioData:
    samples: np.ndarray
    sample_rate: int
    path: str
    subtype: str = 'unknown'

    @property
    def channels(self):
        return 1 if self.samples.ndim == 1 else self.samples.shape[1]

    @property
    def frames(self):
        return len(self.samples)

    @property
    def duration(self):
        return self.frames / self.sample_rate

    @property
    def mono(self):
        return self.samples if self.samples.ndim == 1 else self.samples.mean(axis=1)


def load_audio(path, blocksize=262144):
    """Load audio with a clear, OS-neutral error when the source cannot be opened."""
    if sf is None:
        raise RuntimeError('Install dependencies with: pip install -r requirements.txt')

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f'Audio file not found: {source}')
    if not source.is_file():
        raise OSError(f'Audio path is not a file: {source}')

    try:
        info = sf.info(str(source))
        data, sr = sf.read(str(source), dtype='float32', always_2d=False)
    except Exception as exc:
        raise OSError(f'Could not open audio file: {source}\n{type(exc).__name__}: {exc}') from exc

    if data.size == 0:
        raise ValueError(f'Audio file is empty: {source}')
    return AudioData(np.asarray(data), sr, str(source), info.subtype)
