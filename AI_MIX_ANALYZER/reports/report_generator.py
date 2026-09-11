import json
from pathlib import Path
def export_json(data,path): Path(path).write_text(json.dumps(data,indent=2),encoding='utf-8')
def export_csv(data,path):
    rows=[]
    def walk(d,p=''):
      for k,v in d.items():
       if isinstance(v,dict): walk(v,p+k+'.')
       elif not isinstance(v,list): rows.append((p+k,v))
    walk(data); Path(path).write_text('metric,value\n'+'\n'.join(f'{k},{v}' for k,v in rows),encoding='utf-8')
