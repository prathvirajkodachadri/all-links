import json
from datetime import datetime
from .interpreter import interpret
from analyzer.masking import project_masking
from analyzer.role_analysis import analyze_roles
from analyzer.vocal_analysis import analyze_vocals

def build_ai_brief(results, target=-14.0):
    tracks=[]
    for path, data in results.items():
        tracks.append({'filename':data['file']['filename'],'role':data.get('role','Other'),'analysis':data,'recommendations':interpret(data,target)})
    return {'purpose':'Evidence-based audio mixing/mastering decision support. Do not invent measurements.','created_utc':datetime.utcnow().isoformat()+'Z','target_lufs':target,'track_count':len(tracks),'tracks':tracks,'potential_stem_masking':project_masking(results),'role_aware_analysis':analyze_roles(results),'vocal_analysis':analyze_vocals(results),'instructions':'Use only supplied measurements. Treat frequency and stereo warnings as hypotheses to investigate, not guaranteed defects. Recommend priorities with evidence and confidence. Never apply processing blindly.'}

def save_brief(results, path, target=-14.0):
    with open(path,'w',encoding='utf-8') as f: json.dump(build_ai_brief(results,target),f,indent=2)
