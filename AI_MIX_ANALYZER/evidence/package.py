import json
from datetime import datetime, timezone
from analyzer.masking import project_masking
from analyzer.role_analysis import analyze_roles
from analyzer.vocal_analysis import analyze_vocals
SCHEMA_VERSION='1.0'; ANALYZER_VERSION='2.0.0'
def build(results, project_name='Audio Project'):
 stems={}; flags=[]
 for path,data in results.items():
  if not data or 'error' in data: continue
  data=dict(data); role=data.get('role','Other'); stems[role.lower().replace(' ','_')+'__'+data['file']['filename']]=data
  if data['quality']['clipped_samples']: flags.append({'stem':data['file']['filename'],'type':'clipped_samples','count':data['quality']['clipped_samples']})
 return {'schema_version':SCHEMA_VERSION,'project':{'name':project_name,'created_at':datetime.now(timezone.utc).isoformat(),'analyzer_version':ANALYZER_VERSION},'stems':stems,'relationships':{'frequency_overlap':project_masking(results),'role_measurements':analyze_roles(results),'vocal_measurements':analyze_vocals(results)},'measurement_summary':{'stem_count':len(stems),'technical_flags':flags},'methodology':{'loudness':{'standard':'BS.1770-compatible when pyloudnorm is installed','method':'documented in analyzer/loudness.py'},'true_peak':{'oversampling':8,'method':'SciPy polyphase resampling'},'spectrum':{'fft_size':8192,'window':'Hann'},'sections':{'window_seconds':10.0}},'interpretation_notice':'This package contains measurements and deterministic technical observations only. It contains no AI reasoning or mixing recommendations.'}
def save(results,path):
 with open(path,'w',encoding='utf-8') as f: json.dump(build(results),f,indent=2)
