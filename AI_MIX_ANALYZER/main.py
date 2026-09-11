import tkinter as tk
from tkinter import filedialog,messagebox,ttk
import threading,json,os, numpy as np
from analyzer.core import analyze_file
from evidence.package import save
from reports.report_generator import export_json,export_csv
from reports.pdf_report import export_pdf
from reports.structured_csv import export_section_csv, export_stereo_csv, export_time_history_csv
BG='#11151b'; PANEL='#202a38'; TEXT='#d9e2ef'; MUTED='#8fa7c2'; ACCENT='#38c792'
class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title('AI Audio Mixing & Mastering Analyzer'); self.geometry('1250x780'); self.configure(bg=BG); self.results={}; self.roles={}; self.data=None
  tk.Label(self,text='AI AUDIO MIXING & MASTERING ANALYZER',fg='white',bg=BG,font=('Segoe UI',20,'bold')).pack(pady=(14,2)); tk.Label(self,text='Upload one or many files — generate evidence ready for AI mixing decisions',fg=MUTED,bg=BG).pack(pady=(0,10))
  bar=tk.Frame(self,bg=BG); bar.pack()
  for text,cmd in [('UPLOAD FILES',self.load),('ANALYZE ALL',self.analyze),('EVIDENCE JSON',self.brief),('EXPORT JSON — ALL STEMS',self.ejson),('EXPORT PDF',self.epdf),('EXPORT CSV',self.ecsv),('EXPORT ALL',self.eall),('SECTION CSV',self.esec),('TIME CSV',self.etime)]: tk.Button(bar,text=text,command=cmd,bg='#263449',fg='white',relief='flat',padx=15,pady=9).pack(side='left',padx=3)
  self.progress=ttk.Progressbar(self,length=380); self.progress.pack(pady=8)
  top=tk.Frame(self,bg=BG); top.pack(fill='x',padx=18)
  tk.Label(top,text='UPLOADED FILES',fg=MUTED,bg=BG,font=('Segoe UI',9,'bold')).pack(anchor='w'); self.files=tk.Listbox(top,height=4,bg='#171e28',fg=TEXT,selectbackground='#36506d',relief='flat'); self.files.pack(fill='x'); self.files.bind('<<ListboxSelect>>',self.select); rolebar=tk.Frame(top,bg=BG); rolebar.pack(fill='x',pady=4); tk.Label(rolebar,text='ROLE FOR SELECTED FILE:',fg=MUTED,bg=BG).pack(side='left'); self.role=ttk.Combobox(rolebar,values=['Other','Kick','Snare','Drums','Bass','Lead Vocal','Backing Vocal','Guitar','Piano','Synth','FX'],state='readonly',width=18); self.role.set('Other'); self.role.pack(side='left',padx=8); tk.Button(rolebar,text='ASSIGN ROLE',command=self.assign_role,bg='#263449',fg='white',relief='flat').pack(side='left')
  self.cards=tk.Frame(self,bg=BG); self.cards.pack(fill='x',padx=18,pady=8)
  graphbar=tk.Frame(self,bg=BG); graphbar.pack(fill='x',padx=18); tk.Label(graphbar,text='INTERACTIVE ANALYSIS GRAPHS',fg=MUTED,bg=BG,font=('Segoe UI',9,'bold')).pack(anchor='w'); self.graph_mode=tk.StringVar(value='Loudness'); modes=tk.Frame(graphbar,bg=BG); modes.pack(anchor='w'); [tk.Button(modes,text=m,command=lambda m=m:self.set_graph(m),bg='#263449',fg='white',relief='flat').pack(side='left',padx=2) for m in ['Loudness','Spectrum','Dynamics','Stereo']]; self.graph=tk.Canvas(graphbar,height=190,bg='#0b0e12',highlightthickness=0); self.graph.pack(fill='x'); self.graph.bind('<Configure>',lambda e:self.draw_graph())
  body=tk.Frame(self,bg=BG); body.pack(fill='both',expand=True,padx=18); self.out=tk.Text(body,bg='#0b0e12',fg=TEXT,font=('Consolas',10),relief='flat',padx=12,pady=10); self.out.pack(side='left',fill='both',expand=True); self.issues=tk.Text(body,width=40,bg='#171e28',fg=TEXT,font=('Segoe UI',10),relief='flat',padx=12,pady=10); self.issues.pack(side='right',fill='y',padx=(10,0)); self.issues.insert('end','Select a file after analysis to inspect its results.'); self.issues.config(state='disabled')
  self.status=tk.StringVar(value='Upload audio files to begin.'); tk.Label(self,textvariable=self.status,fg=MUTED,bg=BG).pack(pady=5)
 def load(self):
  paths=filedialog.askopenfilenames(filetypes=[('Audio','*.wav *.flac *.aiff *.aif *.ogg *.mp3'),('All','*.*')]);
  for p in paths:
   if p not in self.results: self.results[p]=None; self.roles[p]='Other'; self.files.insert('end',os.path.basename(p))
  self.status.set(f'{len(self.results)} file(s) queued for analysis.')
 def assign_role(self):
  sel=self.files.curselection()
  if sel:
   p=list(self.results)[sel[0]]; self.roles[p]=self.role.get()
   if self.results.get(p) and 'error' not in self.results[p]: self.results[p]['role']=self.role.get()
   self.status.set(f'Assigned {self.role.get()} to {os.path.basename(p)}')
 def analyze(self):
  paths=list(self.results)
  if not paths: return messagebox.showinfo('Upload files','Choose one or more audio files first.')
  threading.Thread(target=self._batch,args=(paths,),daemon=True).start()
 def _batch(self,paths):
  for n,p in enumerate(paths):
   self.after(0,lambda n=n,p=p:self.status.set(f'Analyzing {n+1}/{len(paths)}: {os.path.basename(p)}'))
   try: self.results[p]=analyze_file(p,lambda x,s:self.after(0,lambda:self.progress.configure(value=((n+x)/len(paths))*100)))
   except Exception as e: self.results[p]={'error':str(e),'file':{'filename':os.path.basename(p)}}
  self.after(0,lambda:self.finish(paths))
 def finish(self,paths): self.status.set(f'Completed {len(paths)} file(s). Select any file for results.'); self.files.selection_set(0); self.select()
 def select(self,event=None):
  sel=self.files.curselection()
  if not sel:return
  p=list(self.results)[sel[0]]; self.current_path=p; self.role.set(self.roles.get(p,'Other')); self.data=self.results[p]
  if self.data and 'error' not in self.data:self.show(self.data)
  else:
   self.out.delete('1.0','end')
   message = 'Not analyzed' if self.data is None else self.data.get('error','Not analyzed')
   self.out.insert('end',message)
   self.status.set(message)
 def show(self,d):
  for w in self.cards.winfo_children():w.destroy()
  f,l,t,q,s=d['file'],d['loudness'],d['true_peak'],d['quality'],d['stereo']; vals=[('DURATION',f"{f['duration_s']:.2f}s"),('LUFS',f"{l['integrated_lufs']:.1f}"),('TRUE PEAK',f"{t['dbtp']:.2f} dBTP"),('RMS',f"{q['rms_db']:.2f} dBFS"),('CORRELATION',f"{(s.get('correlation',1).get('overall',1) if isinstance(s.get('correlation',1),dict) else s.get('correlation',1)):.2f}"),('CLIPS',str(q['clipped_samples']))]
  for name,val in vals:
   b=tk.Frame(self.cards,bg=PANEL,padx=12,pady=8);b.pack(side='left',fill='x',expand=True,padx=3);tk.Label(b,text=name,fg=MUTED,bg=b['bg'],font=('Segoe UI',8,'bold')).pack();tk.Label(b,text=val,fg='white',bg=b['bg'],font=('Segoe UI',11,'bold')).pack()
  self.out.delete('1.0','end');self.out.insert('end',json.dumps(d,indent=2));self.render([]); self.draw_graph()
 def set_graph(self,mode):
  self.graph_mode.set(mode); self.draw_graph()
 def draw_graph(self):
  if not self.data or 'error' in self.data:return
  c=self.graph; c.delete('all'); w=max(c.winfo_width(),500); h=max(c.winfo_height(),190); left,bottom=55,28
  mode=self.graph_mode.get(); vals=[]; label=mode
  if mode=='Loudness': vals=self.data['loudness'].get('history',[]); label='LUFS history'
  elif mode=='Spectrum':
   f=self.data['spectrum']['frequencies_hz']; m=self.data['spectrum']['magnitude']; vals=[20*np.log10(max(v,1e-12)) for hz,v in zip(f,m) if 20<=hz<=20000][:500]; label='FFT magnitude dB'
  elif mode=='Dynamics': vals=[x['rms_dbfs'] for x in self.data.get('sections',{}).get('sections',[])]; label='Section RMS dBFS'
  else:
   corr=self.data['stereo'].get('correlation',0)
   vals=[corr.get('overall',0) if isinstance(corr,dict) else corr]; label='Stereo correlation'
  if not vals: vals=[0]
  lo=min(vals)-2; hi=max(vals)+2
  c.create_line(left,10,left,h-bottom,fill='#607080'); c.create_line(left,h-bottom,w-10,h-bottom,fill='#607080')
  pts=[(left+i/max(1,len(vals)-1)*(w-left-15),10+(hi-v)/(hi-lo)*(h-bottom-10)) for i,v in enumerate(vals)]
  if len(pts)>1:c.create_line(*[z for p in pts for z in p],fill='#38c792',width=2,smooth=True)
  else:c.create_oval(pts[0][0]-4,pts[0][1]-4,pts[0][0]+4,pts[0][1]+4,fill='#38c792')
  c.create_text(8,12,text=f'{hi:.1f}',fill='#8fa7c2',anchor='w'); c.create_text(8,h-bottom,text=f'{lo:.1f}',fill='#8fa7c2',anchor='w'); c.create_text(w-10,10,text=label,fill='#38c792',anchor='e')
  c.bind('<Motion>',lambda e:self.graph_tip(e,vals,left,w,h,lo,hi,label))
 def graph_tip(self,e,vals,left,w,h,lo,hi,label):
  i=round((e.x-left)/max(1,w-left-15)*(len(vals)-1)); i=max(0,min(len(vals)-1,i)); self.status.set(f'{label}: {vals[i]:.2f} | point {i+1}/{len(vals)}')
 def render(self,issues):
  self.issues.config(state='normal');self.issues.delete('1.0','end');self.issues.insert('end','MEASUREMENT EVIDENCE\n\n');
  if not issues:self.issues.insert('end','GOOD\nNo major evidence-based issues detected.')
  for i in issues:self.issues.insert('end',f"{i['severity'].upper()} — {i['problem']}\nEvidence: {i['evidence']}\nCheck: {i['what_to_check']}\nConfidence: {i['confidence']}\n\n")
  self.issues.config(state='disabled')
 def brief(self):
  done={p:d for p,d in self.results.items() if d and 'error' not in d}
  for p,d in done.items(): d['role']=self.roles.get(p,'Other')
  if done:
   p=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('AI brief','*.json')]);
   if p:save(done,p);self.status.set('Measurement evidence package exported.')
 def ejson(self):
  done={p:d for p,d in self.results.items() if d and 'error' not in d}
  if not done:
   return messagebox.showinfo('Export JSON','Analyze the loaded stems first.')
  folder=filedialog.askdirectory(title='Choose folder for JSON stem exports')
  if not folder:return
  exported=[]; failed=[]
  for source_path,d in done.items():
   try:
    stem=os.path.splitext(os.path.basename(source_path))[0]
    filename=f'{stem}.json'
    target=os.path.join(folder,filename)
    export_json(d,target)
    exported.append(filename)
   except Exception as exc:
    failed.append(f'{os.path.basename(source_path)}: {type(exc).__name__}: {exc}')
  if failed:
   self.status.set(f'Exported {len(exported)} JSON file(s); {len(failed)} failed.')
   messagebox.showerror('JSON export completed with errors','Exported:\n'+'\n'.join(exported)+'\n\nFailed:\n'+'\n'.join(failed))
  else:
   self.status.set(f'Exported {len(exported)} JSON file(s).')
   messagebox.showinfo('JSON export complete',f'Exported {len(exported)} stem JSON file(s) to:\n{folder}\n\n'+'\n'.join(exported))
 def epdf(self):
  if self.data and 'error' not in self.data:
   p=filedialog.asksaveasfilename(defaultextension='.pdf',filetypes=[('PDF report','*.pdf')]);
   if p: export_pdf(self.data,p,[]); self.status.set('PDF report exported.')
 def eall(self):
  if not self.data or 'error' in self.data: return messagebox.showinfo('Export all','Analyze and select a file first.')
  folder=filedialog.askdirectory(title='Choose output folder')
  if not folder:return
  from pathlib import Path
  safe=''.join(c if c.isalnum() or c in ' _-' else '_' for c in os.path.splitext(os.path.basename(getattr(self,'current_path',self.path)))[0]).strip() or 'audio'
  out=Path(folder)/safe; out.mkdir(parents=True,exist_ok=True)
  try:
   export_json(self.data,out/f'{safe}.json'); export_pdf(self.data,out/f'{safe}.pdf',[]); export_csv(self.data,out/f'{safe}.csv'); export_section_csv(self.data,out/f'{safe}_sections.csv'); export_time_history_csv(self.data,out/f'{safe}_time_history.csv'); export_stereo_csv(self.data,out/f'{safe}_stereo.csv',safe)
   self.status.set(f'All outputs saved to {out}'); messagebox.showinfo('Export complete',f'All files were saved to:\n{out}')
  except Exception as exc:
   self.status.set('Export failed'); messagebox.showerror('Export failed',f'{type(exc).__name__}: {exc}')
 def esec(self):
  if self.data:
   p=filedialog.asksaveasfilename(defaultextension='.csv');
   if p: export_section_csv(self.data,p)
 def etime(self):
  if self.data:
   p=filedialog.asksaveasfilename(defaultextension='.csv');
   if p: export_time_history_csv(self.data,p)
 def ecsv(self):
  if self.data:
   p=filedialog.asksaveasfilename(defaultextension='.csv');
   if p:export_csv(self.data,p)
if __name__=='__main__':App().mainloop()