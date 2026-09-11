"""Reference analysis uses the same already-produced measurement structures."""
import numpy as np
def compare(project, reference):
 pl=project.get('loudness',{}).get('integrated',{}).get('lufs'); rl=reference.get('loudness',{}).get('integrated',{}).get('lufs')
 pt=project.get('true_peak',{}).get('true_peak_dbtp'); rt=reference.get('true_peak',{}).get('true_peak_dbtp')
 pd=project.get('dynamics',{}).get('rms',{}).get('overall_dbfs'); rd=reference.get('dynamics',{}).get('rms',{}).get('overall_dbfs')
 ps=project.get('spectrum',{}).get('overall',{}); rs=reference.get('spectrum',{}).get('overall',{})
 pb=project.get('spectrum',{}).get('frequency_bands',[]); rb=reference.get('spectrum',{}).get('frequency_bands',[])
 bands=[]
 for a,b in zip(pb,rb): bands.append({'low_hz':a['low_hz'],'high_hz':a['high_hz'],'project_level_db':a.get('level_db'),'reference_level_db':b.get('level_db'),'difference_db':None if a.get('level_db') is None or b.get('level_db') is None else a['level_db']-b['level_db']})
 return {'alignment':'independent_timelines','loudness':{'project_integrated_lufs':pl,'reference_integrated_lufs':rl,'difference_lu':None if pl is None or rl is None else pl-rl},'true_peak':{'project_dbtp':pt,'reference_dbtp':rt,'difference_db':None if pt is None or rt is None else pt-rt},'dynamics':{'project_rms_dbfs':pd,'reference_rms_dbfs':rd,'difference_db':None if pd is None or rd is None else pd-rd},'spectrum':{'project_centroid_hz':ps.get('centroid_hz'),'reference_centroid_hz':rs.get('centroid_hz'),'centroid_difference_hz':None if ps.get('centroid_hz') is None or rs.get('centroid_hz') is None else ps['centroid_hz']-rs['centroid_hz']},'frequency_bands':bands,'methodology':'same analyzer pipeline; no automatic normalization; independent timelines'}
