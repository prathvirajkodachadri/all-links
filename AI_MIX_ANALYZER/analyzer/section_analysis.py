"""Section measurements derived from exact section sample boundaries."""
from .loudness import loudness
from .true_peak import true_peak
from .dynamics import analyze as dynamics
from .spectrum import analyze as spectrum
from .stereo import analyze as stereo

def analyze_sections(samples,sr,section_seconds=30.0):
 n=max(1,round(section_seconds*sr)); out=[]
 for i in range(0,len(samples),n):
  j=min(len(samples),i+n); chunk=samples[i:j]; valid=len(chunk)>0
  if not valid: continue
  out.append({'index':len(out),'start_seconds':i/sr,'end_seconds':j/sr,'center_seconds':(i+j)/(2*sr),'duration_seconds':(j-i)/sr,'label':None,'valid':True,'loudness':loudness(chunk,sr),'true_peak':true_peak(chunk,sample_rate=sr),'dynamics':dynamics(chunk,sr),'spectrum':spectrum(chunk,sr),'stereo':stereo(chunk,sr)})
 return {'methodology':{'segmentation':'fixed_duration','section_duration_seconds':section_seconds,'hop_seconds':section_seconds,'timestamp_convention':'start/end/center are exact sample-derived seconds'},'sections':out}
