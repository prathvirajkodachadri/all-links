from dataclasses import dataclass
from pathlib import Path
import ctypes
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


def _mapped_drive_unc(path):
    """Resolve a Windows mapped drive (for example K:) to its UNC target when possible."""
    if os.name != 'nt':
        return None
    drive, tail = os.path.splitdrive(os.path.abspath(str(path)))
    if not drive or not drive.endswith(':'):
        return None
    try:
        # mpr.dll WNetGetConnectionW is preferable to parsing `net use`, because it
        # asks Windows for the mapping associated with the current logon session.
        mpr = ctypes.WinDLL('mpr')
        fn = mpr.WNetGetConnectionW
        fn.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint32)]
        fn.restype = ctypes.c_uint32
        size = ctypes.c_uint32(1024)
        buf = ctypes.create_unicode_buffer(size.value)
        rc = fn(drive, buf, ctypes.byref(size))
        if rc == 0:
            return os.path.join(buf.value, tail.lstrip('\\/'))
    except Exception:
        pass
    return None


def _path_candidates(path):
    original = os.path.abspath(os.path.expanduser(str(path)))
    candidates = [original]

    unc = _mapped_drive_unc(original)
    if unc:
        candidates.append(unc)

    if os.name == 'nt' and not original.startswith('\\\\?\\'):
        # Extended-length path syntax helps with Windows path-length edge cases.
        candidates.append('\\\\?\\' + original)
        if unc:
            candidates.append('\\\\?\\UNC\\' + unc.lstrip('\\'))

    seen = set()
    for candidate in candidates:
        key = candidate.casefold()
        if key not in seen:
            seen.add(key)
            yield candidate


def _diagnose_path(source):
    drive, _ = os.path.splitdrive(str(source))
    if drive:
        try:
            if not os.path.exists(drive + os.sep):
                return (
                    f'Drive {drive} is not accessible to this Python process. '
                    'If it is a mapped/network drive, use its UNC path or run the app '
                    'under the same Windows account/session that owns the mapping.'
                )
        except OSError:
            pass
    unc = _mapped_drive_unc(source)
    if unc:
        return f'Windows mapped-drive target detected: {unc}'
    return (
        'The file may have been moved/deleted, the drive may be unavailable, '
        'or the process may not have permission to access it.'
    )


def _read_soundfile(source):
    info = sf.info(str(source))
    data, sr = sf.read(str(source), dtype='float32', always_2d=False)
    return data, sr, info.subtype


def load_audio(path, blocksize=262144):
    """Load audio robustly on Windows, including mapped/network drives."""
    if sf is None:
        raise RuntimeError('Install dependencies with: pip install -r requirements.txt')

    source = Path(path).expanduser()
    candidates = list(_path_candidates(source))
    first_error = None
    attempted = []

    for candidate in candidates:
        attempted.append(candidate)
        try:
            if not os.path.isfile(candidate):
                continue
            data, sr, subtype = _read_soundfile(candidate)
            if np.asarray(data).size == 0:
                raise ValueError(f'Audio file is empty: {candidate}')
            return AudioData(np.asarray(data), sr, str(source), subtype)
        except Exception as exc:
            if first_error is None:
                first_error = exc

    # If a directly accessible path exists but libsndfile cannot open it, retry through
    # a local copy. This handles some network/filesystem locking cases.
    for candidate in attempted:
        temp_path = None
        try:
            if not os.path.isfile(candidate):
                continue
            with open(candidate, 'rb') as src:
                fd, temp_path = tempfile.mkstemp(prefix='ai_mix_analyzer_', suffix=Path(candidate).suffix or '.audio')
                os.close(fd)
                with open(temp_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst, length=1024 * 1024)
            data, sr, subtype = _read_soundfile(temp_path)
            if np.asarray(data).size == 0:
                raise ValueError(f'Audio file is empty: {source}')
            return AudioData(np.asarray(data), sr, str(source), subtype)
        except Exception as exc:
            if first_error is None:
                first_error = exc
        finally:
            if temp_path:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    if not os.path.exists(source):
        raise FileNotFoundError(
            f'Audio file not accessible: {source}\n'
            f'{_diagnose_path(source)}\n'
            f'Attempted paths: {attempted}'
        )

    raise OSError(
        f'Could not open audio file: {source}\n'
        f'{type(first_error).__name__}: {first_error}\n'
        f'{_diagnose_path(source)}'
    )
