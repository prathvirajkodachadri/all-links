"""Project-level deterministic relationships and AI-decision evidence."""
import numpy as np
from .masking import compare_spectral_masking


def _valid(d):
    return bool(d) and "error" not in d and isinstance(d.get("spectrum"), dict)


def _band_level(d, lo, hi):
    for b in d.get("spectrum", {}).get("frequency_bands", []):
        if b.get("low_hz") == lo and b.get("high_hz") == hi:
            return b.get("level_db")
    return None


def mix_contribution(stem, mix):
    ranges=[(20,40),(40,80),(80,120),(120,250),(250,500),(500,1000),(1000,2000),(2000,4000),(4000,8000),(8000,16000),(16000,20000)]
    bands=[]
    for lo,hi in ranges:
        sv,mv=_band_level(stem,lo,hi),_band_level(mix,lo,hi)
        bands.append({'low_hz':lo,'high_hz':hi,'stem_level_db':sv,'mix_level_db':mv,'difference_db':None if sv is None or mv is None else round(sv-mv,3)})
    return {'bands':bands,'methodology':'Difference between independently measured relative FFT RMS band levels; not a gain or contribution percentage.'}


def _rms(d): return d.get('dynamics',{}).get('rms',{}).get('overall_dbfs')
def _lufs(d): return d.get('loudness',{}).get('integrated_lufs')
def _corr(d):
    c=d.get('stereo',{}).get('correlation')
    return c.get('overall') if isinstance(c,dict) else c


def analyze_project(mix, stems, reference=None):
    stems={p:d for p,d in stems.items() if _valid(d)}
    pairs=[]; items=list(stems.items())
    for i,(pa,a) in enumerate(items):
        for pb,b in items[i+1:]:
            r=compare_spectral_masking(a,b,a['file'].get('sample_rate',48000))
            diff=None if _rms(a) is None or _rms(b) is None else round(_rms(a)-_rms(b),3)
            pairs.append({'stem_a':a['file']['filename'],'role_a':a.get('role','Other'),'stem_b':b['file']['filename'],'role_b':b.get('role','Other'),'relative_rms_difference_db':diff,'spectral_relationship':r})
    contributions=[]
    if _valid(mix):
        for p,d in stems.items():
            contributions.append({'file':d['file']['filename'],'role':d.get('role','Other'),'mix_comparison':mix_contribution(d,mix)})
    return {'stem_count_analyzed':len(stems),'mix':{'filename':mix.get('file',{}).get('filename') if mix else None,'integrated_lufs':_lufs(mix or {}),'rms_dbfs':_rms(mix or {}),'true_peak_dbtp':(mix or {}).get('true_peak',{}).get('dbtp'),'stereo_correlation':_corr(mix or {})},'stem_relationships':{'pairs':pairs},'mix_vs_stem':contributions,'reference_present':_valid(reference),'methodology':{'masking':'Spectral overlap is a screening hypothesis, not definitive psychoacoustic masking.','mix_vs_stem':'Relative FFT band-level comparison; no normalization or source separation is inferred.','time_alignment':'Independent measurements; no timeline alignment is inferred.'}}


def priority_actions(mix, stems, relationships):
    actions=[]; peak=(mix or {}).get('true_peak',{}).get('dbtp')
    if isinstance(peak,(int,float)) and peak>-1:
        actions.append({'priority':'HIGH','type':'headroom','subject':mix['file']['filename'],'evidence':{'true_peak_dbtp':peak},'action':'Inspect final-bus headroom and limiter behavior.'})
    for pair in relationships.get('stem_relationships',{}).get('pairs',[]):
        score=pair.get('spectral_relationship',{}).get('overlap_score',0)
        if score>.30:
            roles={pair.get('role_a'),pair.get('role_b')}; priority='HIGH' if roles=={'Kick','Bass'} or 'Lead Vocal' in roles else 'MEDIUM'
            actions.append({'priority':priority,'type':'frequency_overlap','subjects':[pair['stem_a'],pair['stem_b']],'evidence':{'overlap_score':score,'bands':pair['spectral_relationship'].get('bands',[])},'action':'Audit the overlapping frequency regions with solo/mute and EQ/level checks.'})
    corr=(mix or {}).get('stereo',{}).get('correlation',{}); cv=corr.get('overall') if isinstance(corr,dict) else corr
    if isinstance(cv,(int,float)) and cv<0:
        actions.append({'priority':'HIGH','type':'phase_risk','subject':mix['file']['filename'],'evidence':{'correlation':cv},'action':'Check polarity/phase and mono compatibility before widening further.'})
    order={'HIGH':0,'MEDIUM':1,'LOW':2}; actions.sort(key=lambda x:order.get(x['priority'],9)); return actions
