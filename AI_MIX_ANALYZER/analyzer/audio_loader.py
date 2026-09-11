from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import tempfile
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


def _diagnose_path(source):
    """Return a useful Windows filesystem diagnosis without hiding the original path."""
    drive, _ = os.path.splitdrive(str(source))
    if drive:
        try:
            if not os.path.exists(drive + os.sep):
                return f'Drive {drive} is not accessible to this Python process. If it is a mapped/network drive, use the UNC path or launch the app under the same Windows account/session that owns the mapping.'
        except OSError:
            pass
    return 'The file may have been moved/deleted, the drive may be unavailable, or the process may not have permission to access it.'


def _read_soundfile(source):
    info = sf.info(str(source))
    data, sr = sf.read(str(source), dtype='float32', always_2d=False)
    return data, sr, info.subtype


def load_audio(path, blocksize=262144):
    """Load WAV/FLAC/AIFF/etc. robustly on Windows and network/mapped drives."""
    if sf is None:
        raise RuntimeError('Install dependencies with: pip install -r requirements.txt')

    source = Path(path).expanduser()
    if not source.exists():
        raise FileNotFoundError(f'Audio file not found: {source}\n{_diagnose_path(source)}')
    if not source.is_file():
        raise OSError(f'Audio path is not a file: {source}')

    try:
        data, sr, subtype = _read_soundfile(source)
    except Exception as first_error:
        # Some Windows/network-mounted files are readable by the shell/file dialog but
        # fail when libsndfile opens the mapped-drive path. Retry through a local temp
        # copy when Python itself can read the source. This also avoids transient network
        # filesystem locking issues without changing the source file.
        temp_path = None
        try:
            with open(source, 'rb') as src:
                suffix = source.suffix or '.audio'
                fd, temp_path = tempfile.mkstemp(prefix='ai_mix_analyzer_', suffix=suffix)
                os.close(fd)
                with open(temp_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst, length=1024 * 1024)
            data, sr, subtype = _read_soundfile(temp_path)
        except Exception as retry_error:
            raise OSError(
                f'Could not open audio file: {source}\n'
                f'Direct read: {type(first_error).__name__}: {first_error}\n'
                f'Local-copy retry: {type(retry_error).__name__}: {retry_error}\n'
                f'{_diagnose_path(source)}'
            ) from retry_error
        finally:
            if temp_path:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    if np.asarray(data).size == 0:
        raise ValueError(f'Audio file is empty: {source}')

    return AudioData(np.asarray(data), sr, str(source), subtype)
