import numpy as np
from analyzer.loudness import loudness

def test_silence_documented():
 r=loudness(np.zeros(44100),44100); assert r['integrated']['lufs'] is None; assert r['status']=='below_measurement_floor'
def test_histories_are_timed_and_separate():
 x=np.ones(44100*4,dtype=float)*0.1; r=loudness(x,44100)
 assert r['momentary']['history'] and 'time_s' in r['momentary']['history'][0]
 assert r['short_term']['history'] and r['short_term']['window_seconds']==3.0
def test_level_change_responds():
 x=np.r_[np.ones(44100*3)*.01,np.ones(44100*3)*.3,np.ones(44100*3)*.01]; r=loudness(x,44100)
 assert r['momentary']['maximum_lufs'] > r['momentary']['minimum_lufs']
 assert r['short_term']['maximum_lufs'] > r['short_term']['minimum_lufs']
def test_short_file():
 r=loudness(np.ones(1000)*.1,44100); assert 'integrated' in r and not np.isnan(r['momentary']['maximum_lufs'])
def test_stereo_level_change():
 x=np.c_[np.ones(44100)*.1,np.ones(44100)*.01]; r=loudness(x,44100); assert r['integrated']['lufs'] is not None
