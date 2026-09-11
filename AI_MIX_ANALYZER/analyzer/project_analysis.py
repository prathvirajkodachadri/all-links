"""Project-level deterministic evidence for downstream human/AI mix review."""
import numpy as np
from .masking import compare_spectral_masking

BANDS = [(20,40),(40,80),(80,120),(120,250),(250,500),(500,1000),(1000,2000),(2000,4000),(4000,8000),(8000,16000),(16000,20000)]


def _valid(d):
    return bool(d) and "error" not in d and isinstance(d.get("spectrum"), dict)


def _band_level(d, lo, hi):
    for b in d.get("spectrum", {}).get("frequency_bands", []):
        if b.get("low_hz") == lo and b.get("high_hz") == hi:
            return b.get("level_db")
    return None


def _rms(d):
    return d.get("dynamics",{}).get("rms",{}).get("overall_dbfs")


def _lufs(d):
    return d.get("loudness",{}).get("integrated_lufs")


def _corr(d):
    c=d.get("stereo",{}).get("correlation")
    return c.get("overall") if isinstance(c,dict) else c


def _metric_summary(d):
    if not _valid(d): return None
    f=d.get("file",{}); l=d.get("loudness",{}); t=d.get("true_peak",{}); q=d.get("quality",{}); dy=d.get("dynamics",{}); s=d.get("stereo",{})
    rms=_rms(d); peak=t.get("dbtp"); corr=_corr(d)
    return {
        "filename":f.get("filename"), "duration_s":f.get("duration_s"), "sample_rate":f.get("sample_rate"), "channels":f.get("channels"),
        "integrated_lufs":_lufs(d), "true_peak_dbtp":peak, "rms_dbfs":rms,
        "crest_factor_db":None if not isinstance(rms,(int,float)) or not isinstance(peak,(int,float)) else round(peak-rms,3),
        "stereo_correlation":corr, "clipped_samples":q.get("clipped_samples"),
        "dynamics":dy, "quality":q, "stereo":s
    }


def mix_contribution(stem, mix):
    bands=[]
    for lo,hi in BANDS:
        sv,mv=_band_level(stem,lo,hi),_band_level(mix,lo,hi)
        bands.append({'low_hz':lo,'high_hz':hi,'stem_level_db':sv,'mix_level_db':mv,'difference_db':None if sv is None or mv is None else round(sv-mv,3)})
    return {'bands':bands,'methodology':'Difference between independently measured FFT RMS band levels; not a gain or contribution percentage.'}


def reference_comparison(mix, reference):
    if not (_valid(mix) and _valid(reference)): return {'available':False}
    metrics={}
    for key,fn in [('integrated_lufs',_lufs),('rms_dbfs',_rms),('true_peak_dbtp',lambda d:d.get('true_peak',{}).get('dbtp')),('stereo_correlation',_corr)]:
        a,b=fn(mix),fn(reference)
        metrics[key]={'mix':a,'reference':b,'difference':None if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) else round(a-b,3)}
    bands=[]
    for lo,hi in BANDS:
        a,b=_band_level(mix,lo,hi),_band_level(reference,lo,hi)
        bands.append({'low_hz':lo,'high_hz':hi,'mix_level_db':a,'reference_level_db':b,'difference_db':None if a is None or b is None else round(a-b,3)})
    return {'available':True,'metrics':metrics,'frequency_bands':bands,'methodology':'Independent measurements; no loudness or spectral normalization is inferred.'}


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
    return {
        'stem_count_analyzed':len(stems),
        'mix':_metric_summary(mix),
        'reference':_metric_summary(reference) if _valid(reference) else None,
        'stem_relationships':{'pairs':pairs},
        'mix_vs_stem':contributions,
        'reference_comparison':reference_comparison(mix,reference),
        'reference_present':_valid(reference),
        'methodology':{
            'measurements':'Deterministic measurements produced by the analyzer modules; values are evidence, not automatic mixing decisions.',
            'masking':'Spectral overlap is a screening hypothesis, not definitive psychoacoustic masking.',
            'mix_vs_stem':'Relative FFT band-level comparison; no normalization or source separation is inferred.',
            'reference':'Mix/reference differences are based on independently measured values; alignment and mastering-chain equivalence are not assumed.',
            'time_alignment':'Independent stem timelines are not assumed aligned.'
        }
    }


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
