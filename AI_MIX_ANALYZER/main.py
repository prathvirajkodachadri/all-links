import tkinter as tk
from tkinter import filedialog,messagebox,ttk
import threading,json,os,numpy as np
from analyzer.core import analyze_file
from analyzer.project_analysis import analyze_project,priority_actions
from evidence.package import save
from reports.report_generator import export_json
BG='#11151b'; PANEL='#202a38'; TEXT='#d9e2ef'; MUTED='#8fa7c2'
AUDIO_TYPES=[('Audio','*.wav *.flac *.aiff *.aif *.ogg *.mp3'),('All','*.*')]
ROLES=['Other','Kick','Snare','Drums','Bass','Lead Vocal','Backing Vocal','Guitar','Piano','Synth','FX']
class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title('AI Audio Mixing & Mastering Analyzer'); self.geometry('1250x820'); self.configure(bg=BG); self.results={}; self.roles={}; self.data=None; self.mix_path=None; self.reference_path=None; self.mix_data=None; self.reference_data=None; self.project_analysis=None
  tk.Label(self,text='AI AUDIO MIXING & MASTERING ANALYZER',fg='white',bg=BG,font=('Segoe UI',20,'bold')).pack(pady=(14,2)); tk.Label(self,text='Analyze a final mix together with its stems for evidence-based mix decisions',fg=MUTED,bg=BG).pack(pady=(0,10)); self._build_inputs()
  bar=tk.Frame(self,bg=BG); bar.pack(pady=7)
  for text,cmd in [('ANALYZE PROJECT',self.analyze),('EVIDENCE JSON',self.brief),('EXPORT JSON',self.ejson)]: tk.Button(bar,text=text,command=cmd,bg='#263449',fg='white',relief='flat',padx=16,pady=9).pack(side='left',padx=3)
  self.progress=ttk.Progressbar(self,length=380); self.progress.pack(pady=5); self._build_analysis(); self.status=tk.StringVar(value='Upload a Mix and one or more Stems to begin.'); tk.Label(self,textvariable=self.status,fg=MUTED,bg=BG).pack(pady=5)
 def _build_inputs(self):
  area=tk.Frame(self,bg=BG); area.pack(fill='x',padx=18)
  mix=tk.Frame(area,bg=PANEL,padx=12,pady=10); mix.pack(side='left',fill='both',expand=True,padx=(0,5)); tk.Label(mix,text='MIX / FINAL MIX',fg='white',bg=PANEL,font=('Segoe UI',10,'bold')).pack(anchor='w'); self.mix_label=tk.Label(mix,text='No mix selected',fg=MUTED,bg=PANEL,anchor='w'); self.mix_label.pack(fill='x',pady=7); mb=tk.Frame(mix,bg=PANEL); mb.pack(anchor='w'); tk.Button(mb,text='UPLOAD MIX',command=self.load_mix,bg='#263449',fg='white',relief='flat').pack(side='left',padx=(0,5)); tk.Button(mb,text='REMOVE',command=self.remove_mix,bg='#263449',fg='white',relief='flat').pack(side='left')
  stems=tk.Frame(area,bg=PANEL,padx=12,pady=10); stems.pack(side='left',fill='both',expand=True,padx=5); tk.Label(stems,text='STEMS',fg='white',bg=PANEL,font=('Segoe UI',10,'bold')).pack(anchor='w'); self.files=tk.Listbox(stems,height=5,bg='#171e28',fg=TEXT,selectbackground='#36506d',relief='flat',exportselection=False); self.files.pack(fill='x',pady=4); self.files.bind('<<ListboxSelect>>',self.select); sb=tk.Frame(stems,bg=PANEL); sb.pack(anchor='w')
  for text,cmd in [('ADD STEMS',self.load_stems),('REMOVE SELECTED',self.remove_selected),('CLEAR ALL',self.clear_stems)]: tk.Button(sb,text=text,command=cmd,bg='#263449',fg='white',relief='flat').pack(side='left',padx=(0,4))
  rb=tk.Frame(stems,bg=PANEL); rb.pack(fill='x',pady=(5,0)); tk.Label(rb,text='ROLE:',fg=MUTED,bg=PANEL).pack(side='left'); self.role=ttk.Combobox(rb,values=ROLES,state='readonly',width=16); self.role.set('Other'); self.role.pack(side='left',padx=6); tk.Button(rb,text='ASSIGN',command=self.assign_role,bg='#263449',fg='white',relief='flat').pack(side='left')
  ref=tk.Frame(area,bg=PANEL,padx=12,pady=10); ref.pack(side='left',fill='both',expand=True,padx=(5,0)); tk.Label(ref,text='REFERENCE MIX — OPTIONAL',fg='white',bg=PANEL,font=('Segoe UI',10,'bold')).pack(anchor='w'); self.ref_label=tk.Label(ref,text='No reference selected',fg=MUTED,bg=PANEL,anchor='w'); self.ref_label.pack(fill='x',pady=7); tk.Button(ref,text='UPLOAD REFERENCE',command=self.load_reference,bg='#263449',fg='white',relief='flat').pack(side='left'); tk.Button(ref,text='REMOVE',command=self.remove_reference,bg='#263449',fg='white',relief='flat').pack(side='left',padx=5)
 def _build_analysis(self):
  top=tk.Frame(self,bg=BG); top.pack(fill='x',padx=18,pady=8); tk.Label(top,text='SELECTED FILE ANALYSIS',fg=MUTED,bg=BG,font=('Segoe UI',9,'bold')).pack(anchor='w'); self.cards=tk.Frame(top,bg=BG); self.cards.pack(fill='x'); graphbar=tk.Frame(self,bg=BG); graphbar.pack(fill='x',padx=18); tk.Label(graphbar,text='INTERACTIVE ANALYSIS GRAPHS',fg=MUTED,bg=BG,font=('Segoe UI',9,'bold')).pack(anchor='w'); self.graph_mode=tk.StringVar(value='Loudness'); modes=tk.Frame(graphbar,bg=BG); modes.pack(anchor='w'); [tk.Button(modes,text=m,command=lambda m=m:self.set_graph(m),bg='#263449',fg='white',relief='flat').pack(side='left',padx=2) for m in ['Loudness','Spectrum','Dynamics','Stereo']]; self.graph=tk.Canvas(graphbar,height=175,bg='#0b0e12',highlightthickness=0); self.graph.pack(fill='x'); self.graph.bind('<Configure>',lambda e:self.draw_graph()); body=tk.Frame(self,bg=BG); body.pack(fill='both',expand=True,padx=18); self.out=tk.Text(body,bg='#0b0e12',fg=TEXT,font=('Consolas',9),relief='flat',padx=12,pady=10); self.out.pack(side='left',fill='both',expand=True); self.issues=tk.Text(body,width=42,bg='#171e28',fg=TEXT,font=('Segoe UI',10),relief='flat',padx=12,pady=10); self.issues.pack(side='right',fill='y',padx=(10,0)); self.issues.insert('end','Project checks will appear after analysis.'); self.issues.config(state='disabled')
 def load_mix(self):
  p=filedialog.askopenfilename(title='Select Final Mix',filetypes=AUDIO_TYPES)
  if p:self.mix_path=p; self.mix_label.config(text='✓ '+os.path.basename(p),fg=TEXT); self.status.set('Mix selected. Add the stems belonging to this mix.')
 def remove_mix(self): self.mix_path=None; self.mix_data=None; self.mix_label.config(text='No mix selected',fg=MUTED)
 def load_reference(self):
  p=filedialog.askopenfilename(title='Select Reference Mix (Optional)',filetypes=AUDIO_TYPES)
  if p:self.reference_path=p; self.ref_label.config(text='✓ '+os.path.basename(p),fg=TEXT)
 def remove_reference(self): self.reference_path=None; self.reference_data=None; self.ref_label.config(text='No reference selected',fg=MUTED)
 def load_stems(self):
  paths=filedialog.askopenfilenames(title='Select Stems',filetypes=AUDIO_TYPES)
  for p in paths:
   if p not in self.results:self.results[p]=None; self.roles[p]='Other'; self.files.insert('end',os.path.basename(p))
  self.status.set(f'{len(self.results)} stem(s) queued.')
 def remove_selected(self):
  sel=self.files.curselection()
  if not sel:return
  p=list(self.results)[sel[0]]; self.results.pop(p,None); self.roles.pop(p,None); self.files.delete(sel[0]); self.data=None
 def clear_stems(self): self.results.clear(); self.roles.clear(); self.files.delete(0,'end'); self.data=None; self.status.set('All stems cleared.')
 def assign_role(self):
  sel=self.files.curselection()
  if sel:
   p=list(self.results)[sel[0]]; self.roles[p]=self.role.get()
   if self.results.get(p) and 'error' not in self.results[p]:self.results[p]['role']=self.role.get()
 def analyze(self):
  if not self.mix_path:return messagebox.showwarning('Mix required','Upload the final Mix first.')
  if not self.results:return messagebox.showwarning('Stems required','Add one or more Stems first.')
  threading.Thread(target=self._batch,args=(list(self.results),),daemon=True).start()
 def _batch(self,paths):
  all_paths=[self.mix_path]+paths+([self.reference_path] if self.reference_path else []); total=len(all_paths)
  for n,p in enumerate(all_paths):
   self.after(0,lambda n=n,p=p:self.status.set(f'Analyzing {n+1}/{total}: {os.path.basename(p)}'))
   try:
    d=analyze_file(p,lambda x,s,n=n:self.after(0,lambda:self.progress.configure(value=((n+x)/total)*100)))
    if p==self.mix_path:self.mix_data=d
    elif p==self.reference_path:self.reference_data=d
    else:self.results[p]=d; d['role']=self.roles.get(p,'Other')
   except Exception as e:
    d={'error':str(e),'file':{'filename':os.path.basename(p)}}
    if p==self.mix_path:self.mix_data=d
    elif p==self.reference_path:self.reference_data=d
    else:self.results[p]=d
  self.after(0,self.finish_project)
 def finish_project(self):
  mix=self.mix_data; stems={p:d for p,d in self.results.items() if d and 'error' not in d}
  if not mix or 'error' in mix:return self.status.set('Project analysis failed: Mix could not be analyzed.')
  self.project_analysis=analyze_project(mix,stems,self.reference_data); self.project_analysis['priority_actions']=priority_actions(mix,stems,self.project_analysis); self.data=mix; self.show(mix); self._show_project_checks(self.project_analysis); self.status.set(f'Project analysis complete: Mix + {len(stems)} stem(s)'+(' + Reference Mix.' if self.reference_data and 'error' not in self.reference_data else '.'))
 def _show_project_checks(self,p):
  actions=p.get('priority_actions',[]); lines=['PRIORITY CHECKS','']
  if not actions:lines.append('No deterministic priority warnings found.')
  else:
   for i,a in enumerate(actions,1):lines += [f"{i}. [{a['priority']}] {a['type'].replace('_',' ').title()}",'   '+a.get('action',''),'   Evidence: '+json.dumps(a.get('evidence',{}),ensure_ascii=False)]
  self.issues.config(state='normal'); self.issues.delete('1.0','end'); self.issues.insert('end','\n'.join(lines)); self.issues.config(state='disabled')
 def select(self,event=None):
  sel=self.files.curselection()
  if not sel:return
  p=list(self.results)[sel[0]]; self.current_path=p; self.role.set(self.roles.get(p,'Other')); self.data=self.results[p]
  if self.data and 'error' not in self.data:self.show(self.data)
  else:self.out.delete('1.0','end'); self.out.insert('end','Not analyzed' if self.data is None else self.data.get('error','Not analyzed'))
 def show(self,d):
  for w in self.cards.winfo_children():w.destroy()
  f=d.get('file',{}); l=d.get('loudness',{}); t=d.get('true_peak',{}); q=d.get('quality',{}); s=d.get('stereo',{}); corr=s.get('correlation',1); corr=corr.get('overall',1) if isinstance(corr,dict) else corr; vals=[('DURATION',f"{f.get('duration_s',0):.2f}s"),('LUFS',str(round(l.get('integrated_lufs'),1)) if isinstance(l.get('integrated_lufs'),(int,float)) else '—'),('TRUE PEAK',f"{t.get('dbtp',0):.2f} dBTP" if isinstance(t.get('dbtp'),(int,float)) else '—'),('RMS',f"{q.get('rms_db',0):.2f} dBFS" if isinstance(q.get('rms_db'),(int,float)) else '—'),('CORRELATION',f"{corr:.2f}" if isinstance(corr,(int,float)) else '—'),('CLIPS',str(q.get('clipped_samples','—')))]
  for name,val in vals:
   b=tk.Frame(self.cards,bg=PANEL,padx=12,pady=7); b.pack(side='left',fill='x',expand=True,padx=3); tk.Label(b,text=name,fg=MUTED,bg=PANEL,font=('Segoe UI',8,'bold')).pack(); tk.Label(b,text=val,fg='white',bg=PANEL,font=('Segoe UI',11,'bold')).pack()
  self.out.delete('1.0','end'); self.out.insert('end',json.dumps(d,indent=2)); self.draw_graph()
 def set_graph(self,mode):self.graph_mode.set(mode); self.draw_graph()
 def draw_graph(self):
  if not self.data or 'error' in self.data:return
  c=self.graph; c.delete('all'); w=max(c.winfo_width(),500); h=max(c.winfo_height(),175); left,bottom=55,28; mode=self.graph_mode.get(); vals=[]
  if mode=='Loudness':vals=[x for x in self.data.get('loudness',{}).get('history',[]) if isinstance(x,(int,float))]
  elif mode=='Spectrum':
   f=self.data.get('spectrum',{}).get('frequencies_hz',[]); m=self.data.get('spectrum',{}).get('magnitude',[]); vals=[v for hz,v in zip(f,m) if 20<=hz<=20000 and isinstance(v,(int,float))][:500]
  elif mode=='Dynamics':vals=[x.get('rms_dbfs') for x in self.data.get('dynamics',{}).get('rms',{}).get('history',[]) if isinstance(x.get('rms_dbfs'),(int,float))]
  else:
   corr=self.data.get('stereo',{}).get('correlation',{}); vals=[x.get('correlation') for x in corr.get('history',[]) if isinstance(x.get('correlation'),(int,float))] if isinstance(corr,dict) else [corr]
  if not vals:vals=[0]
  lo=min(vals); hi=max(vals); lo-=.05*max(abs(lo),1); hi+=.05*max(abs(hi),1); c.create_line(left,10,left,h-bottom,fill='#607080'); c.create_line(left,h-bottom,w-10,h-bottom,fill='#607080'); pts=[(left+i/max(1,len(vals)-1)*(w-left-15),10+(hi-v)/(hi-lo)*(h-bottom-10)) for i,v in enumerate(vals)]
  if len(pts)>1:c.create_line(*[z for p in pts for z in p],fill='#38c792',width=2,smooth=True)
  else:c.create_oval(pts[0][0]-4,pts[0][1]-4,pts[0][0]+4,pts[0][1]+4,fill='#38c792')
 def _project_json(self):
  stems=[{'file':os.path.basename(p),'role':self.roles.get(p,'Other'),'analysis':d} for p,d in self.results.items() if d and 'error' not in d]; pa=self.project_analysis
  return {'schema_version':'2.0','project':{'mix_file':os.path.basename(self.mix_path) if self.mix_path else None,'reference_file':os.path.basename(self.reference_path) if self.reference_path else None,'stem_count':len(stems)},'mix_analysis':self.mix_data,'reference_analysis':self.reference_data,'stems':stems,'project_intelligence':pa,'ai_context':{'purpose':'Objective evidence for downstream AI or human mixing decisions.','limitations':['Spectral overlap is a screening hypothesis, not definitive psychoacoustic masking.','Independent stem timelines are not assumed aligned.']}}
 def brief(self):
  done={p:d for p,d in self.results.items() if d and 'error' not in d}
  if not done:return messagebox.showinfo('Evidence JSON','Analyze the stems first.')
  for p,d in done.items():d['role']=self.roles.get(p,'Other')
  p=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('AI evidence','*.json')])
  if p:save(done,p); self.status.set('Stem measurement evidence exported.')
 def ejson(self):
  if not self.mix_data or 'error' in self.mix_data:return messagebox.showinfo('Export JSON','Analyze the Mix and Stems first.')
  folder=filedialog.askdirectory(title='Choose folder for project JSON exports')
  if not folder:return
  project=self._project_json(); exported=[]; failed=[]; used=set()
  def safe_name(path):
   stem=os.path.splitext(os.path.basename(path))[0]; return ''.join(c if c.isalnum() or c in ' _-' else '_' for c in stem).strip() or 'audio'
  items=[(self.mix_path,self.mix_data)]+[(p,d) for p,d in self.results.items() if d and 'error' not in d]
  if self.reference_data and self.reference_path and 'error' not in self.reference_data:items.append((self.reference_path,self.reference_data))
  for source,d in items:
   try:
    name=safe_name(source); base=name; i=2
    while name.lower() in used:name=f'{base}_{i}'; i+=1
    used.add(name.lower()); export_json(d,os.path.join(folder,name+'.json')); exported.append(name+'.json')
   except Exception as exc:failed.append(f'{os.path.basename(source)}: {type(exc).__name__}: {exc}')
  try:export_json(project,os.path.join(folder,'MIX_ANALYSIS.json')); exported.append('MIX_ANALYSIS.json')
  except Exception as exc:failed.append(f'MIX_ANALYSIS.json: {type(exc).__name__}: {exc}')
  if failed:messagebox.showerror('JSON export errors','Exported:\n'+'\n'.join(exported)+'\n\nFailed:\n'+'\n'.join(failed))
  else:messagebox.showinfo('JSON export complete',f'Exported {len(exported)} JSON file(s) to:\n{folder}')
  self.status.set(f'Exported {len(exported)} JSON file(s).')
if __name__=='__main__':App().mainloop()
