from .audio_loader import load_audio
from .loudness import loudness
from .true_peak import true_peak
from .spectrum import analyze as spectrum
from .stereo import analyze as stereo
from .quality import analyze as quality
from .sections import analyze_sections
def analyze_file(path, progress=None):
    a=load_audio(path); steps=[('loudness',lambda:loudness(a.samples,a.sample_rate)),('true_peak',lambda:true_peak(a.samples)),('spectrum',lambda:spectrum(a.samples,a.sample_rate)),('stereo',lambda:stereo(a.samples,a.sample_rate)),('quality',lambda:quality(a.samples,a.sample_rate))]; out={'file':{'path':a.path,'filename':path.split('/')[-1],'duration_s':a.duration,'sample_rate':a.sample_rate,'channels':a.channels,'subtype':a.subtype,'format':path.split('.')[-1].upper()},'sections':analyze_sections(a)}
    for i,(k,fn) in enumerate(steps): out[k]=fn(); progress and progress((i+1)/len(steps),k)
    return out
