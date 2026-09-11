import numpy as np
from analyzer.section_analysis import analyze_sections

def test_detailed_sections_boundaries():
 r=analyze_sections(np.ones(2000)*.1,1000,1.0); assert len(r['sections'])==2; assert r['sections'][0]['start_seconds']==0; assert r['sections'][0]['end_seconds']==1; assert 'spectrum' in r['sections'][0] and 'stereo' in r['sections'][0]
