import csv

def _write(rows,path,fields):
 with open(path,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def export_section_csv(data,path):
 fields=['section_index','start_seconds','end_seconds','duration_seconds','integrated_lufs','true_peak_dbtp','rms_dbfs','crest_db','spectral_centroid_hz','spectral_rolloff_hz','correlation','mid_rms_dbfs','side_rms_dbfs']; rows=[]
 for s in data.get('time_analysis',{}).get('detailed_sections',{}).get('sections',[]):
  l=s.get('loudness',{});d=s.get('dynamics',{});sp=s.get('spectrum',{});st=s.get('stereo',{}); corr=st.get('correlation',{}).get('overall') if isinstance(st.get('correlation'),dict) else st.get('correlation'); rows.append({'section_index':s.get('index'),'start_seconds':s.get('start_seconds'),'end_seconds':s.get('end_seconds'),'duration_seconds':s.get('duration_seconds'),'integrated_lufs':l.get('integrated',{}).get('lufs'),'true_peak_dbtp':s.get('true_peak',{}).get('true_peak_dbtp'),'rms_dbfs':d.get('rms',{}).get('overall_dbfs'),'crest_db':d.get('crest_factor',{}).get('overall_db'),'spectral_centroid_hz':sp.get('overall',{}).get('centroid_hz'),'spectral_rolloff_hz':sp.get('overall',{}).get('rolloff_hz'),'correlation':corr,'mid_rms_dbfs':st.get('mid_side',{}).get('mid_rms_dbfs'),'side_rms_dbfs':st.get('mid_side',{}).get('side_rms_dbfs')})
 _write(rows,path,fields)
def export_stereo_csv(data,path,stem='selected'):
 fields=['stem','time_start_seconds','time_end_seconds','center_seconds','correlation','mid_rms_dbfs','side_rms_dbfs','valid']; rows=[]; st=data.get('stereo',{}); c=st.get('correlation',{}) if isinstance(st.get('correlation'),dict) else {}
 for h in c.get('history',[]): rows.append({'stem':stem,'time_start_seconds':h.get('time_s'),'time_end_seconds':h.get('time_s'),'center_seconds':h.get('time_s'),'correlation':h.get('correlation'),'mid_rms_dbfs':h.get('mid_rms_dbfs'),'side_rms_dbfs':h.get('side_rms_dbfs'),'valid':h.get('correlation') is not None})
 _write(rows,path,fields)
def export_time_history_csv(data,path,stem='selected'):
 fields=['stem','metric','start_seconds','end_seconds','center_seconds','value','unit','valid']; rows=[]
 def add(metric,t,v,u): rows.append({'stem':stem,'metric':metric,'start_seconds':t,'end_seconds':t,'center_seconds':t,'value':v,'unit':u,'valid':v is not None})
 l=data.get('loudness',{}); d=data.get('dynamics',{}); st=data.get('stereo',{}); sp=data.get('spectrum',{})
 for z in l.get('momentary',{}).get('history',[]): add('loudness_momentary',z.get('time_s'),z.get('lufs'),'LUFS')
 for z in l.get('short_term',{}).get('history',[]): add('loudness_short_term',z.get('time_s'),z.get('lufs'),'LUFS')
 for z in d.get('rms',{}).get('history',[]): add('rms',z.get('time_s'),z.get('rms_dbfs'),'dBFS'); add('crest_factor',z.get('time_s'),z.get('crest_factor_db'),'dB')
 for z in sp.get('history',[]): add('spectral_centroid',z.get('time_s'),z.get('centroid_hz'),'Hz')
 c=st.get('correlation',{}) if isinstance(st.get('correlation'),dict) else {}
 for z in c.get('history',[]): add('correlation',z.get('time_s'),z.get('correlation'),'coefficient')
 _write(rows,path,fields)
