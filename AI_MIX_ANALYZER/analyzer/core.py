from .audio_loader import load_audio
from .loudness import loudness
from .true_peak import true_peak
from .spectrum import analyze as spectrum
from .stereo import analyze as stereo
from .quality import analyze as quality
from .sections import analyze_sections
from .dynamics import analyze as dynamics
from .time_analysis import analyze as time_analysis
from .section_analysis import analyze_sections as detailed_sections


def analyze_file(path, progress=None):
    """Analyze one audio file and return structured evidence."""
    a = load_audio(path)
    steps = [
        ('loudness', lambda: loudness(a.samples, a.sample_rate)),
        ('true_peak', lambda: true_peak(a.samples, sample_rate=a.sample_rate)),
        ('dynamics', lambda: dynamics(a.samples, a.sample_rate)),
        ('spectrum', lambda: spectrum(a.samples, a.sample_rate)),
        ('stereo', lambda: stereo(a.samples, a.sample_rate)),
        ('quality', lambda: quality(a.samples, a.sample_rate)),
    ]
    out = {
        'file': {
            'path': a.path,
            'filename': a.path.split('\\')[-1].split('/')[-1],
            'duration_s': a.duration,
            'sample_rate': a.sample_rate,
            'channels': a.channels,
            'subtype': a.subtype,
            'format': a.path.rsplit('.', 1)[-1].upper() if '.' in a.path else '',
        },
        'sections': analyze_sections(a),
        'time_analysis': {
            **time_analysis(a.samples, a.sample_rate),
            'detailed_sections': detailed_sections(a.samples, a.sample_rate),
        },
    }
    for i, (key, fn) in enumerate(steps):
        out[key] = fn()
        if progress:
            progress((i + 1) / len(steps), key)
    return out
