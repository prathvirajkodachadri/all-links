from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
from lxml import etree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import os, math
from PIL import ImageFont

ROOT='/home/user'
OUT=ROOT+'/deliverables/End_to_End_Project_Management.pptx'
prs=Presentation(); prs.slide_width=Inches(13.333333); prs.slide_height=Inches(7.5)
C={'navy':'142B45','text':'253A50','muted':'64768A','bg':'F4F7FB','line':'DDE5EE','white':'FFFFFF','m':'147D92','d':'3659A8','s':'AD741C','a':'22846E','x':'7950A0','red':'B74848','light':'EAF0F7'}
DEPTS=['Marketing','Design','Supply Chain','Assembly','Dispatch']; COLORS=[C[k] for k in ['m','d','s','a','x']]
SMART=[]
def rgb(c): return RGBColor.from_string(c)
def rect(s,x,y,w,h,fill,line=None,radius=False):
 sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
 sh.fill.solid(); sh.fill.fore_color.rgb=rgb(fill)
 if line: sh.line.color.rgb=rgb(line); sh.line.width=Pt(.8)
 else: sh.line.fill.background()
 ef=OxmlElement('a:effectLst');sh._element.spPr.append(ef)
 if radius:
  try: sh.adjustments[0]=.10
  except: pass
 return sh

def txt(s,x,y,w,h,text,size=17,color=None,bold=False,align=PP_ALIGN.LEFT,fill=None):
 sh=s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf=sh.text_frame
 tf.clear(); tf.word_wrap=True; tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
 for i,line in enumerate(str(text).split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.text=line; p.alignment=align; p.space_after=Pt(5)
  p.font.name='Calibri'; p.font.size=Pt(size); p.font.bold=bold; p.font.color.rgb=rgb(color or C['text'])
 return sh

def line(s,x1,y1,x2,y2,color=None,width=1.5,arrow=False,dash=False):
 sh=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)); sh.line.color.rgb=rgb(color or C['line']); sh.line.width=Pt(width)
 ln=sh._element.spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ln')
 if arrow:
  e=OxmlElement('a:tailEnd'); e.set('type','triangle'); e.set('w','sm'); e.set('len','sm'); ln.append(e)
 if dash:
  e=OxmlElement('a:prstDash');e.set('val','dash');ln.append(e)
 return sh

def pill(s,x,y,w,text,color=C['navy'],light=False):
 rect(s,x,y,w,.30, C['light'] if light else color,radius=True);txt(s,x+.06,y+.04,w-.12,.22,text,10.5,color if light else C['white'],True,PP_ALIGN.CENTER)

def footer(s,n,label='Proposed operating model • validate owners, dates and approval authority'):
 line(s,.45,7.02,12.88,7.02,C['line'],.7)
 txt(s,.48,7.13,11.85,.18,label,9,C['muted'])
 txt(s,12.3,7.10,.55,.22,f'{n:02d}',11,C['muted'],True,PP_ALIGN.RIGHT)

def slide(section,title,sub='',dark=False):
 s=prs.slides.add_slide(prs.slide_layouts[6]); s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(C['white'])
 rect(s,0,0,13.333,.075,C['navy']);txt(s,.48,.28,12.3,.24,section.upper(),10.5,C['d'],True)
 title_font=ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf',290)
 title_size=min(29, 29*(12.3*72*.96)/(title_font.getlength(title)/10))
 txt(s,.48,.76,12.3,.60,title,title_size,C['navy'],True)
 if sub: txt(s,.5,1.44,12.1,.42,sub,13.5,C['muted'])
 footer(s,len(prs.slides)); return s

def notes(s,text):
 s.notes_slide.notes_text_frame.text=text

def banner(s,text,y=6.42,color=None):
 rect(s,.48,y,12.37,.42,color or C['light'],radius=True);txt(s,.65,y+.08,12.02,.27,text,12,C['navy'],True)

def card(s,x,y,w,h,title,body,color=C['d'],num=None):
 rect(s,x,y,w,h,C['bg'],radius=True);rect(s,x,y,.055,h,color)
 txt(s,x+.18,y+.16,w-.35,.38,title,17,color,True)
 txt(s,x+.18,y+.70,w-.35,h-.82,body,15,C['text'])

def table(s,x,y,width,headers,rows,colwidths=None,rowheights=None,font=14,headerfont=12.5,firstcolors=None):
 nr=len(rows)+1; h=sum(rowheights) if rowheights else .46+len(rows)*.7
 shape=s.shapes.add_table(nr,len(headers),Inches(x),Inches(y),Inches(width),Inches(h));t=shape.table
 if colwidths:
  for col,w in zip(t.columns,colwidths): col.width=Inches(w)
 if rowheights:
  for r,h in zip(t.rows,rowheights):r.height=Inches(h)
 for ri,vals in enumerate([headers]+rows):
  for ci,val in enumerate(vals):
   ce=t.cell(ri,ci);ce.text=str(val);ce.margin_left=Inches(.12);ce.margin_right=Inches(.10);ce.margin_top=Inches(.055);ce.margin_bottom=Inches(.04)
   ce.fill.solid();ce.fill.fore_color.rgb=rgb(C['navy'] if ri==0 else (C['bg'] if ri%2 else C['white']))
   ce.vertical_anchor=MSO_ANCHOR.MIDDLE
   for p in ce.text_frame.paragraphs:
    p.font.name='Calibri';p.font.size=Pt(headerfont if ri==0 else font);p.font.color.rgb=rgb(C['white'] if ri==0 else C['text']);p.font.bold=(ri==0 or ci==0);p.space_after=Pt(1)
   if ri>0 and ci==0 and firstcolors:
    ce.fill.fore_color.rgb=rgb(firstcolors[(ri-1)%len(firstcolors)])
    for p in ce.text_frame.paragraphs:p.font.color.rgb=rgb(C['white'])
   # thin white grid
   tcPr=ce._tc.get_or_add_tcPr()
   for edge in ['lnL','lnR','lnT','lnB']:
    el=OxmlElement('a:'+edge);el.set('w','5000');sf=OxmlElement('a:solidFill');cl=OxmlElement('a:srgbClr');cl.set('val',C['white']);sf.append(cl);el.append(sf);tcPr.append(el)
 return shape

def smart(s,y,labels,height=1.02):
 # Replaced by native DrawingML SmartArt after saving.
 sh=rect(s,.48,y,12.37,height,C['white']);sh.name='SMARTART_PLACEHOLDER'
 SMART.append({'slide':len(prs.slides),'x':.48,'y':y,'w':12.37,'h':height,'labels':labels,'id':sh.shape_id})

def gate(s,x,y,num,title,body,w=2.34):
 pill(s,x,y,.5,num,C['navy']);txt(s,x,y+.44,w,.5,title,16,C['navy'],True);txt(s,x,y+1,w,1.02,body,14,C['muted'])

# 01
s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(C['navy'])
rect(s,9.85,0,3.49,7.5,'1B3654');txt(s,.62,.50,11,.30,'SENIOR MANAGEMENT REVIEW  /  PROPOSED OPERATING MODEL',11,'8FC9D4',True)
txt(s,.62,1.26,9.0,1.48,'End-to-End Project\nManagement',39,C['white'],True)
txt(s,.65,3.04,8.6,.58,'From Design to Dispatch',27,'C9D9EA')
txt(s,.65,3.98,8.50,.94,'Design-deputed Project Manager\nOne integrated plan. Five departments. Two machine projects.',18,C['white'])
pill(s,.65,5.45,3.38,'PROJECT 01  •  CNC ROUTER',C['d']);pill(s,4.21,5.45,3.72,'PROJECT 02  •  ED MILL',C['a'])
txt(s,.65,6.56,8.95,.30,'Presented by: [Name / designation]   |   Review date: [TBD]',12,'C9D9EA')
for i,(d,col) in enumerate(zip(DEPTS,COLORS)):
 yy=1.55+i*.82;rect(s,10.25,yy,.12,.48,col);txt(s,10.56,yy+.08,2.27,.35,d,16,C['white'],True)
txt(s,10.25,6.45,2.5,.40,'COORDINATED BY THE PM',10,'8FC9D4',True)
notes(s,'Purpose: establish a proposed cross-functional management system for CNC Router and ED Mill projects. User-provided facts: the Project Manager is deputed from Design; CNC design reference is Shoda, Japan; manufacturer is Ace Designers. No current schedule, project status, company authority matrix or machine specifications were provided. All process allocations are proposals requiring confirmation. [TBD] and bracketed entries are editable placeholders. Potential gaps are hypotheses to validate, not confirmed findings. Native SmartArt is on slides 2, 5 and 6; other visuals use editable PowerPoint shapes and tables. Use PowerPoint SmartArt Design > Text Pane to edit workflow labels.')
# 02
s=slide('01 / Project management overview','One lifecycle. Explicit gates. No silent handovers.','Each department accepts a defined input and releases evidence—not just a verbal update.')
smart(s,2.03,['Marketing\nRequirements','Design\nRelease baseline','Supply Chain\nMake / buy','Assembly\nBuild & validate','Dispatch\nRelease & ship'])
for i,args in enumerate([
 ('G0','Scope agreed','Approved requirement sheet, acceptance criteria and delivery need.'),
 ('G1','Design frozen','Reviewed drawings, BOM and controlled release approved.'),
 ('G2','Build ready','Required materials received, inspected and kitted.'),
 ('G3','Machine accepted','Stage checks, functional tests and defects closed.'),
 ('G4','Dispatch cleared','Release sign-offs, packing and shipping records ready.')]):
 gate(s,.56+i*2.49,3.40,*args)
banner(s,'PM control layer: integrated schedule • gate evidence • dependencies • risk / issue / change logs')
notes(s,'G0–G4 are proposed gates, not company gate names. Supply Chain is proposed to coordinate make/buy and supplier or internal manufacturing progress; confirm the actual manufacturing execution owner at kickoff. Assembly includes integration and test coordination. Stage and final quality sign-off must be assigned to the company-authorized person [TBD], not assumed to be the PM. For G0, confirm scope, contract obligations, acceptance criteria and an approved delivery baseline. For G4, verify actual dispatch and obtain shipment evidence before administrative project closure.')
#03
s=slide('02 / Project manager’s role','The PM integrates delivery across all five departments','Design-deputed PM = end-to-end coordination and tracking; functional specialists retain technical authority.')
# radial on left
cx,cy=3.5,4.32
nodes=[(.62,2.25,2.3,.7,'Marketing',C['m']),(4.33,2.25,2.3,.7,'Design',C['d']),(.62,5.37,2.3,.7,'Supply Chain',C['s']),(4.33,5.37,2.3,.7,'Assembly',C['a']),(2.47,6.18,2.35,.55,'Dispatch',C['x'])]
for x,y,w,h,label,col in nodes:line(s,cx,cy,x+w/2,y+h/2,col,1.5)
for x,y,w,h,label,col in nodes:
 rect(s,x,y,w,h,col,radius=True);txt(s,x+.08,y+.18 if h>.6 else y+.12,w-.16,.3,label,16,C['white'],True,PP_ALIGN.CENTER)
rect(s,2.24,3.54,2.52,1.43,C['navy'],radius=True);txt(s,2.42,3.79,2.16,1.00,'PROJECT MANAGER\nCoordinate • track\nEscalate & unblock',14,C['white'],True,PP_ALIGN.CENTER)
card(s,7.12,2.05,5.7,1.03,'Plan & allocate','Agree tasks, owners, dependencies and milestones.',C['d'])
card(s,7.12,3.25,5.7,1.03,'Follow up & unblock','Track actions, materials, readiness and bottlenecks.',C['s'])
card(s,7.12,4.45,5.7,1.03,'Control & escalate','Monitor revisions, approvals, risks and recovery plans.',C['x'])
card(s,7.12,5.65,5.7,1.03,'Close & dispatch','Confirm quality evidence, release readiness and shipment.',C['a'])
# adjust card text for short cards
for sh in list(s.shapes):
 if sh.has_text_frame and any(p.text.startswith(('Agree tasks','Track actions','Monitor revisions','Confirm quality')) for p in sh.text_frame.paragraphs):
  sh.top-=Inches(.11);sh.height=Inches(.35)
  for p in sh.text_frame.paragraphs:p.font.size=Pt(13)
notes(s,'PM responsibility: maintain the integrated project plan; allocate and follow up department-wise actions by agreement with functional leads; monitor schedule, gates, deliverables, design changes, approvals, material availability, assembly readiness, quality clearance and dispatch. Identify gaps and risks; coordinate solutions and escalate unresolved cross-functional conflicts. Functional leads own execution. Assign an authorized design reviewer/approver so that the PM’s Design role does not create an unapproved self-approval route. Define PM delegation and escalation thresholds with the sponsor [TBD].')
#04
s=slide('03 / Department-wise responsibilities','Every department owns an output and an acceptance point','Proposed responsibility model for both machines—confirm named owners and authorized signatories at kickoff.')
table(s,.48,2.03,12.37,['DEPARTMENT','CORE ACTIVITIES','DELIVERABLE / HANDOVER','RECEIVING CHECK'],[
 ['Marketing','Capture customer need; clarify scope; manage customer approvals.','Requirement and acceptance baseline → Design / PM','Scope, exclusions and acceptance criteria agreed.'],
 ['Design','Develop and review design; release drawings and BOM; control revisions.','Approved release pack → Supply Chain / Assembly','Current revisions, interfaces and specifications complete.'],
 ['Supply Chain','Plan procurement; coordinate manufacturing; expedite vendors; verify receipts.','Inspected material / part kits → Assembly','Quantity, specification and required-by readiness confirmed.'],
 ['Assembly','Check readiness; integrate; resolve build issues; coordinate tests and defects.','Tested machine + records → Dispatch','Tests accepted; blocking defects and shortages closed.'],
 ['Dispatch','Check release pack; pack; coordinate transport; record shipment.','Machine + shipment pack → Customer / Marketing','Clearance, packing list and transport documents verified.']
 ],[1.60,3.50,3.87,3.40],[.48,.70,.76,.80,.76,.76],font=13,firstcolors=COLORS)
banner(s,'PM owns coordination and visibility; departments own execution; approval authority remains [TBD].')
notes(s,'These are proposed allocations, not statements of the company’s existing organization. Confirm whether manufacturing is internal, outsourced or shared. No additional manufacturing department is assumed; Supply Chain coordinates the approved manufacturing source and records the actual execution owner [TBD]. Quality approval is a named authorized role, which may sit outside the five listed departments; confirm its authority and update the RACI accordingly. Marketing remains the proposed customer-facing channel. Dispatch documentation depends on the actual contract, destination and applicable rules.')
#05
s=slide('04 / Project 01 — CNC Router Machine','CNC Router: from customer requirement to dispatched machine','Design reference: Shoda, Japan  |  Manufacturer: Ace Designers  |  Technical specifications: [TBD]')
smart(s,2.02,['Marketing\nAgree router scope','Design\nFreeze router design','Supply Chain\nManufacture / procure','Assembly\nIntegrate & test','Dispatch\nClear & ship'])
for i,(d,col,body) in enumerate(zip(DEPTS,COLORS,[
 'ACTIVITY\nConfirm application, work envelope and acceptance needs.\n\nHANDOVER\nApproved requirement sheet → Design.',
 'ACTIVITY\nReview reference; define interfaces; approve drawings and BOM.\n\nHANDOVER\nFrozen release pack → Supply Chain / Assembly.',
 'ACTIVITY\nConfirm make/buy; track Ace Designers manufacturing milestones and receipts.\n\nHANDOVER\nInspected parts / kits → Assembly.',
 'ACTIVITY\nIntegrate machine; run approved safety, function and acceptance checks.\n\nHANDOVER\nAccepted machine + test pack → Dispatch.',
 'ACTIVITY\nVerify clearance, packing, documents and carrier readiness.\n\nHANDOVER\nShipment record → Marketing / Customer.'
 ])):
 x=.48+i*2.49;rect(s,x,3.34,2.39,2.67,C['bg'],radius=True);txt(s,x+.14,3.51,2.10,2.35,body,12.8,C['text']);rect(s,x,3.34,2.39,.045,col)
banner(s,'PM hold points: scope approval → design freeze → manufacturing / material readiness → test acceptance → dispatch release')
notes(s,'CNC facts supplied by the user: design reference Shoda, Japan; manufacturer Ace Designers. The slide does not infer a licensed design, a particular Shoda model, a specific Ace Designers factory allocation or a commercial relationship beyond the supplied description. Confirm the scope of Ace Designers manufacturing and the corresponding contract, internal manufacturing interface, make/buy plan and acceptance evidence. Work envelope, axes, spindle, control, guarding, utilities and acceptance criteria must come from the approved customer requirement and design pack; none are invented here. Design to define a test plan appropriate to the approved specification; the company-designated quality authority [TBD] clears acceptance. All milestone dates, quantities and people remain [TBD].')
#06
s=slide('05 / Project 02 — ED Mill Machine','ED Mill: a separate end-to-end delivery workstream','Education Milling Machine  |  Customer / institution: [TBD]  |  Manufacturer and specifications: [TBD]')
smart(s,2.02,['Marketing\nAgree education need','Design\nFreeze ED Mill design','Supply Chain\nSource & manufacture','Assembly\nBuild & demonstrate','Dispatch\nRelease delivery kit'])
for i,(col,body) in enumerate(zip(COLORS,[
 'ACTIVITY\nConfirm teaching use, site needs, accessories and acceptance scope.\n\nHANDOVER\nApproved education-use brief → Design.',
 'ACTIVITY\nReview milling concept, safety and usability; release drawings / BOM.\n\nHANDOVER\nApproved design + test plan → Supply Chain / Assembly.',
 'ACTIVITY\nPlan parts, bought-outs and manufacturing against the released BOM.\n\nHANDOVER\nInspected and complete build kit → Assembly.',
 'ACTIVITY\nAssemble; verify functions and safety; demonstrate agreed use cases.\n\nHANDOVER\nAccepted machine + test evidence → Dispatch.',
 'ACTIVITY\nVerify machine, agreed accessories, manuals and shipment documents.\n\nHANDOVER\nDelivery pack + shipment record → Customer.'
 ])):
 x=.48+i*2.49;rect(s,x,3.34,2.39,2.67,C['bg'],radius=True);txt(s,x+.14,3.51,2.10,2.35,body,12.8,C['text']);rect(s,x,3.34,2.39,.045,col)
banner(s,'Maintain a distinct ED Mill schedule, BOM / revision baseline, risk register, readiness tracker and release record.')
notes(s,'ED Mill is interpreted as Education Milling Machine as provided. Customer, manufacturing source, configuration, quantities, dates and institution requirements are unknown. Proposed education-specific questions include teaching use, operator familiarity, safeguarding, accessories, manuals and demonstrations; these are requirements to confirm, not claims of supplied features or contractual training commitments. Include training or commissioning only if the approved contract requires it. Do not copy the CNC Router technical baseline or acceptance criteria into ED Mill. Use separate project IDs and controlled registers.')
#07
s=slide('06 / Coordination and handovers','A handover is complete only when the next owner accepts it','Cross-functional swimlane • proposed gate path for each project separately')
# swimlane headings and lanes
x0=.48;y0=2.12; labelw=1.67; cw=2.12;rh=.66
for j,h in enumerate(['G0 / SCOPE','G1 / DESIGN','G2 / READINESS','G3–G4 / RELEASE']):
 txt(s,2.55+j*2.55,1.94,2.2,.24,h,10.5,C['muted'],True,PP_ALIGN.CENTER)
for i,(d,col) in enumerate(zip(DEPTS,COLORS)):
 y=y0+i*rh;rect(s,x0,y,12.37,rh-.025,C['bg'] if i%2==0 else 'FAFBFD');rect(s,x0,y,labelw,rh-.025,col);txt(s,x0+.12,y+.20,labelw-.2,.27,d,13,C['white'],True)
# process staircase, editable connectors
points=[(2.40,2.21,2.12,.45,'Approve scope',C['m']),(4.95,2.87,2.12,.45,'Release design',C['d']),(7.50,3.53,2.12,.45,'Accept build kit',C['s']),(10.05,4.19,2.45,.45,'Test & close defects',C['a']),(10.05,4.85,2.45,.45,'Clear & dispatch',C['x'])]
for i in range(len(points)-1):
 x,y,w,h,*_=points[i];nx,ny,nw,nh,*_=points[i+1]
 if i<3:
  line(s,x+w,y+h/2,nx+.12,y+h/2,C['muted'],1.4);line(s,nx+.12,y+h/2,nx+.12,ny,C['muted'],1.4,True)
 else:line(s,x+w/2,y+h,nx+nw/2,ny,C['muted'],1.4,True)
for x,y,w,h,label,col in points:
 rect(s,x,y,w,h,col,radius=True);txt(s,x+.06,y+.10,w-.12,.25,label,12.5,C['white'],True,PP_ALIGN.CENTER)
rect(s,.48,5.75,12.37,.79,C['navy'],radius=True)
txt(s,.68,5.91,12,.48,'PM OVERLAY   Record sender + receiver + document revision + acceptance date.\nMissing evidence or rejected input → assign action / due date; do not advance the gate.',13,C['white'],True)
notes(s,'Swimlane illustrates a proposed controlled handover route, not all day-to-day interactions. Sender attaches the approved deliverable and version, flags open items and requests receiver acceptance. Receiver verifies completeness and either accepts with dated evidence or rejects with a documented reason. PM records the decision, dependency impact and recovery action. Marketing obtains customer requirement approval; Design releases technical data; Supply Chain verifies material/manufacturing readiness; Assembly coordinates build and test evidence; Dispatch verifies final release. G3 test acceptance and G4 dispatch clearance are separate decisions even though shown in the final swimlane column.')
#08
s=slide('06 / RACI responsibility matrix','Separate integration accountability from functional execution','Proposed RACI • replace department labels with named people before baseline approval')
headers=['ACTIVITY / DELIVERABLE','PM','MKT','DESIGN','SUPPLY\nCHAIN','ASSEMBLY','DISPATCH']
rows=[['Integrated plan / milestone tracking','A/R','C','C','C','C','I'],['Requirement / customer approval','C','A/R','C','I','I','I'],['Design release / revision control','C','C','A/R','C','C','I'],['Procurement / manufacturing readiness','C','I','C','A/R','C','I'],['Assembly readiness / build execution','C','I','C','R','A/R','I'],['Test pack / defect closure*','C','C','C','C','A/R*','I'],['Packing / shipping execution','C','C','I','C','C','A/R'],['Change impact coordination**','A/R','R','R','R','R','C']]
t=table(s,.48,2.05,12.37,headers,rows,[4.35,1.0,1.0,1.22,1.6,1.65,1.55],[.50]+[.40]*8,font=12.5,headerfont=11)
# center RACI cells
for row in t.table.rows:
 for cell in list(row.cells)[1:]:
  for p in cell.text_frame.paragraphs:p.alignment=PP_ALIGN.CENTER
rect(s,.48,6.02,12.37,.60,C['light'],radius=True)
txt(s,.63,6.11,12.05,.42,'R = Responsible   A = Accountable   C = Consulted   I = Informed\n* Quality signatory [TBD].  ** Impact coordination only; change / cost / delivery approval authority [TBD].',11.5,C['navy'])
notes(s,'This RACI is a proposal, not an assertion of current company responsibilities. Confirm one accountable person per activity and name people, not just functions. PM A is for schedule integration and coordinating the change impact assessment, not for unilateral technical, financial, commercial or final quality approval. * For the test pack / defect closure row, Assembly is proposed to coordinate completion; replace the A allocation with the company-authorized quality signatory if different, retaining Assembly as R. Keep exactly one A after validation. Final dispatch authorization must be documented with the authorized release signatory [TBD]; packing/shipping execution accountability does not itself grant quality or commercial release authority. ** Route changes to delegated technical, commercial and sponsor approvers [TBD]. No budget authority is implied.')
#09
s=slide('07 / Potential gaps and solutions — 1 of 2','Close upstream gaps before they become build delays','Potential gaps for validation—not confirmed audit findings. The PM tracks closure; functional owners provide evidence.')
table(s,.48,2.02,12.37,['GAP / DEPARTMENT','POTENTIAL FAILURE','PRACTICAL CONTROL','CLOSURE EVIDENCE'],[
 ['01  Communication\nAll departments','Delayed information; unclear channels; weak coordination.','PM-led weekly reviews; one project channel and action log.','Published cadence; current decisions; actions acknowledged.'],
 ['02  Responsibility\nAll departments','Activities and handovers have no clear owner.','Approve a named RACI and deliverable acceptance owners.','One accountable owner per activity; signed handover map.'],
 ['03  Design\nDesign','Incomplete drawings, BOM errors, late changes / approvals.','Peer reviews; revision control; formal design freeze.','Reviewed drawings / BOM; approved freeze; change history.'],
 ['04  Supply Chain\nSupply Chain','Shortages, vendor delays or wrong specifications.','Time procurement to need dates; expedite critical items; track receipts.','PO-to-BOM alignment; confirmed dates; inspected kits.'],
 ['05  Assembly\nAssembly','Missing parts, delayed build, rework and technical issues.','Readiness checks; daily progress; rapid issue escalation.','Accepted readiness checklist; build log; closed defects.']
 ],[2.12,3.12,3.70,3.43],[.48]+[.76]*5,font=12.8,firstcolors=[C['navy'],C['navy'],C['d'],C['s'],C['a']])
banner(s,'Validate each gap using project records, department interviews and current gate evidence before assigning status.')
notes(s,'Gap hypotheses supplied by the user, translated into proposed controls. Validation should review actual drawings and BOMs, purchase commitments, receipt data, assembly records, meeting minutes and ownership records. Record the evidence, severity, impacted project, named owner, due date and effectiveness check in the corrective action log. No present failure, delay or material shortage is asserted.')
#10
s=slide('07 / Potential gaps and solutions — 2 of 2','Protect the finish: quality, visibility and controlled release','A control is complete only when it is used, evidenced and checked for effectiveness.')
table(s,.48,2.02,12.37,['GAP / DEPARTMENT','POTENTIAL FAILURE','PRACTICAL CONTROL','CLOSURE EVIDENCE'],[
 ['06  Quality\nDesign / Assembly / Dispatch','Inspections missed; defects or documents unresolved.','Stage inspections; checklists; final acceptance and sign-off.','Inspection records; defect closure; accepted test pack.'],
 ['07  Monitoring\nPM + all departments','No agreed milestones; delays are not visible.','Baseline Gantt; milestone tracker; weekly variance review.','Updated plan; forecast dates; recovery actions.'],
 ['08  Dispatch\nDispatch + interfaces','Pending checks, packing or transport; incomplete documents.','Pre-dispatch checklist and authorized release approval.','Release record; verified shipment pack; booked transport.'],
 ['09  Change control\nMarketing / Design / PM','Uncontrolled scope or design changes hit cost / delivery.','Formal request; impact assessment; delegated approvals.','Approved change; revised baseline; affected stock disposition.'],
 ['10  Risk management\nPM + all departments','Potential delays / risks not identified early.','Live risk register with owner, mitigation and closure date.','Reviewed risks; triggers; mitigation evidence; residual risk.']
 ],[2.12,3.12,3.70,3.43],[.48]+[.76]*5,font=12.8,firstcolors=[C['navy'],C['navy'],C['x'],C['d'],C['navy']])
banner(s,'No dispatch against unresolved blocking defects, missing release evidence or unapproved scope changes.')
notes(s,'Quality is a cross-cutting activity, not an invented sixth department. Assign inspection and release signatories using the approved company authority system [TBD]. Test coverage and acceptance criteria come from the contract and design baseline. Risk closure requires evidence and review of residual exposure; a completed mitigation action is not automatically a closed risk. Dispatch holds and change controls must align with delegated authority and contract requirements.')
#11
s=slide('08 / Gap closure and corrective action plan','Turn the gap list into an owned closure backlog','Sequence the controls by dependency; due dates and current status must be agreed separately for each machine.')
table(s,.48,2.03,12.37,['PRIORITY / GAPS','ACTION PACKAGE','PROPOSED OWNER','DUE / STATUS','VERIFY BEFORE CLOSURE'],[
 ['A  Align\n01 / 02 / 07','Name RACI; create one channel; baseline plan and review cadence.','PM + all functional leads','[TBD]\n[Not assessed]','Sponsor / leads accept owners, schedule and reporting method.'],
 ['B  Stabilize design\n03 / 09','Review release pack; freeze design; activate change approvals.','Design lead + PM','[TBD]\n[Not assessed]','Current approved drawings / BOM used by affected teams.'],
 ['C  Secure build\n04 / 05','Link procurement to need dates; clear shortages; approve assembly readiness.','Supply Chain + Assembly leads','[TBD]\n[Not assessed]','Critical materials verified; readiness signed; constraints closed.'],
 ['D  Protect release\n06 / 08','Introduce stage inspections, defect closure and dispatch authorization.','Assembly + Dispatch; quality signatory [TBD]','[TBD]\n[Not assessed]','Accepted test pack and complete release / shipping documents.'],
 ['E  Sustain control\n10 + all','Review risks; test control effectiveness; capture lessons learned.','PM + risk / action owners','[TBD]\n[Not assessed]','Evidence of use; repeat check shows no unresolved recurrence.']
 ],[1.63,3.66,2.22,1.40,3.46],[.5]+[.75]*5,font=12.5)
banner(s,'Closure rule: action completed + evidence attached + effectiveness verified + PM log updated.')
notes(s,'A–E are dependency-based action priorities, not calendar weeks. All dates, named owners and statuses are placeholders. Open one corrective action record per validated gap and project: action ID, gap / root cause, containment, corrective action, owner, target date, evidence, verifier and effectiveness review date. Where urgent work must proceed, record temporary containment and authorized exceptions without treating the underlying gap as closed. PM coordinates follow-up; functional owners implement the actions. Sponsor or designated verifier [TBD] accepts effectiveness and material residual risk.')
#12
s=slide('09 / Project monitoring and milestone tracking','Build the Gantt from approved dates—not assumptions','Editable Gantt template • Project: [CNC Router / ED Mill] • Baseline: [TBD] • Calendar and durations: [TBD]')
# Gantt custom grid
x=.48; y=2.17; leftw=2.68; datew=.75; gx=x+leftw+2*datew; gw=4.42; cellw=gw/6;rowh=.49
rect(s,x,y,8.60,.44,C['navy']);txt(s,x+.12,y+.10,leftw-.1,.24,'WORK PACKAGE',11,C['white'],True)
txt(s,x+leftw,y+.10,datew,.25,'START',10.5,C['white'],True,PP_ALIGN.CENTER);txt(s,x+leftw+datew,y+.10,datew,.25,'FINISH',10.5,C['white'],True,PP_ALIGN.CENTER)
for j in range(6):txt(s,gx+j*cellw,y+.10,cellw,.25,'[date]',10.5,C['white'],True,PP_ALIGN.CENTER)
acts=['Scope & acceptance','Design / release','Procure / manufacture','Receive / inspect / kit','Assembly / stage checks','Final test / close defects','Pack / dispatch']
for i,a in enumerate(acts):
 yy=y+.44+i*rowh;rect(s,x,yy,8.60,rowh-.015,C['bg'] if i%2==0 else 'FAFBFD');txt(s,x+.12,yy+.13,leftw-.15,.25,a,12,C['text'],True)
 for k in range(2):txt(s,x+leftw+k*datew,yy+.13,datew,.25,'[TBD]',10.5,C['muted'],False,PP_ALIGN.CENTER)
 for j in range(7):line(s,gx+j*cellw,yy,gx+j*cellw,yy+rowh,C['line'],.5)
 # neutral bar placeholder; same geometry deliberately carries no duration information
 yy2=yy+.10;rr=rect(s,gx+.13,yy2,gw-.26,.28,'F6F8FB',C['line'],True)
 ln=rr._element.spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ln');dd=OxmlElement('a:prstDash');dd.set('val','dash');ln.append(dd)
 txt(s,gx+.18,yy2+.035,gw-.36,.20,'[place approved baseline bar]',9.4,C['muted'],False,PP_ALIGN.CENTER)
# right milestone panel
rect(s,9.40,2.17,3.45,3.87,C['light'],radius=True);txt(s,9.60,2.36,3.05,.35,'MILESTONE REGISTER',13,C['navy'],True)
for i,(g,tg) in enumerate([('G0','Scope accepted'),('G1','Design frozen'),('G2','Assembly ready'),('G3','Machine accepted'),('G4','Dispatch released')]):
 txt(s,9.61,2.91+i*.48,.43,.28,g,12,C['d'],True);txt(s,10.12,2.91+i*.48,2.52,.28,tg+'  [date]',11.4,C['text'])
txt(s,9.61,5.43,3.0,.44,'Track baseline / forecast / actual\nand evidence reference for each gate.',10.5,C['muted'])
banner(s,'Dashed bars and date cells are placeholders—not durations, current progress or a delivery forecast.')
notes(s,'This is an intentionally unpopulated Gantt chart template because no company timeline or duration was provided. Duplicate for each project. Populate the time-bucket headers, approved start and finish dates, dependencies, resources and calendar; resize / move each editable bar to its baseline dates. No bar position or width in this template represents a real schedule. Add a contrasting actual / forecast bar only after collecting validated updates. Identify the critical path from real dependencies and durations in the planning tool; do not assume every activity shown is critical. For each gate capture baseline date, forecast date, actual acceptance date, owner and evidence link. PM reviews variance, next constraint and recovery decision at the weekly review.')
#13
s=slide('09 / Monitoring cadence and management visibility','Use one portfolio view—but keep project controls separate','Reporting date: [TBD] • Status is intentionally unassessed until project data is validated.')
table(s,.48,2.04,12.37,['PROJECT','CURRENT GATE / STATUS','NEXT MILESTONE','DELIVERY BASELINE / FORECAST','TOP CONSTRAINT / OWNER'],[
 ['CNC Router','[TBD] / [Not assessed]','[Gate + date TBD]','[Baseline TBD] / [Forecast TBD]','[Issue / decision / owner TBD]'],
 ['ED Mill','[TBD] / [Not assessed]','[Gate + date TBD]','[Baseline TBD] / [Forecast TBD]','[Issue / decision / owner TBD]']
 ],[1.55,2.50,2.25,3.08,2.99],[.54,.69,.69],font=12.5)
card(s,.48,4.30,3.98,1.52,'Daily • execution focus','Assembly progress, shortages, technical issues and immediate constraints.',C['a'])
card(s,4.68,4.30,3.98,1.52,'Weekly • PM review','Milestone variance, vendor dates, risk / issue / change actions and recovery.',C['d'])
card(s,8.87,4.30,3.98,1.52,'At each gate • release','Receiver accepts evidence; authorized approver signs; PM updates the baseline log.',C['x'])
banner(s,'Every update states: baseline vs forecast • variance cause • action owner • due date • decision required.')
notes(s,'Suggested cadence, to be agreed with functional leads. Use one agreed collaboration channel and a controlled repository with separate folders / registers by project ID. Do not treat the channel as a substitute for controlled drawing or BOM release. Define RAG status thresholds with the sponsor [TBD], based on milestone forecast variance, unresolved gate blockers and residual risk; do not assign color without evidence. Recommended metrics to baseline before setting targets: milestone on-time rate, overdue critical actions, material readiness, first-pass acceptance, change-driven rework and actual dispatch vs commitment. No metrics or delivery promises are reported in this template.')
#14
s=slide('09 / Material and assembly readiness','Do not release assembly against an unverified kit','Tracker templates • maintain one copy per project • all quantities, dates and readiness states are [TBD]')
txt(s,.50,2.05,12,.28,'MATERIAL READINESS  /  OWNER: SUPPLY CHAIN LEAD [NAME TBD]',12,C['s'],True)
table(s,.48,2.44,12.37,['ITEM / BOM REV','REQUIRED / RECEIVED','NEED DATE / ETA','INSPECTION / KIT STATUS','GAP ACTION / OWNER / DUE'],[
 ['[Critical item 01 / rev]','[Qty] / [Qty]','[Date] / [Date]','[Pending / accepted]','[Shortage action / name / date]'],
 ['[Critical item 02 / rev]','[Qty] / [Qty]','[Date] / [Date]','[Pending / accepted]','[Vendor action / name / date]']
 ],[2.10,2.10,2.15,2.65,3.37],[.45,.48,.48],font=11.7,headerfont=11)
txt(s,.50,4.22,12,.28,'ASSEMBLY READINESS  /  OWNER: ASSEMBLY LEAD [NAME TBD]',12,C['a'],True)
table(s,.48,4.62,12.37,['READINESS CHECK','EVIDENCE REQUIRED','STATE / OWNER','RELEASE CONDITION'],[
 ['Design / material','Current release + inspected kit','[TBD] / [Name]','No blocking revision or critical shortage.'],
 ['People / tools / bay','Capacity, tooling, utilities and safe work area','[TBD] / [Name]','Required resources and test provisions available.'],
 ['Build / inspection plan','Sequence, checkpoints and defect route','[TBD] / [Name]','Lead accepts readiness; PM records gate decision.']
 ],[2.1,4.25,2.1,3.92],[.44,.40,.44,.44],font=11.8,headerfont=11)
notes(s,'Material tracker fields shown are the minimum management view. Working register should also include project ID, part number, description, specification, BOM revision, source / supplier, PO reference, required quantity, received quantity, need date, supplier confirmed ETA, inspection result, kit / location, shortage action, owner and target closure date. Track critical items individually; use accepted quantity, not merely received quantity, for readiness. Assembly readiness includes released drawings and BOM; inspected parts; controlled deviations; resource capacity; tools and gauges; utilities; safety provisions; assembly sequence and inspection plan; technical support and test arrangements. State values can be Not checked / Blocked / Ready / Authorized exception, with evidence and authority. Do not infer current readiness from a template. Escalate critical shortages before the assembly need date.')
#15
s=slide('10 / Risk management and issue escalation','Escalate the delivery impact—not just the problem','Risk = uncertain future event. Issue = an event already affecting work. Log both, with different responses.')
# Editable issue/risk flow with an explicit escalation decision.
for i,(title,body,col) in enumerate([
 ('1  Identify & log','Event, impact, trigger\nand named owner',C['d']),
 ('2  Assess & act','Prioritize; contain\nor mitigate exposure',C['s']),
 ('3  PM triage','Integrate response and\nforecast milestone impact',C['navy'])]):
 xx=.48+i*2.79;rect(s,xx,2.10,2.51,1.14,C['bg'],radius=True);rect(s,xx,2.10,2.51,.07,col);txt(s,xx+.12,2.29,2.29,.3,title,15,col,True);txt(s,xx+.12,2.70,2.29,.44,body,12.5,C['text'])
 line(s,xx+2.53,2.65,xx+2.76,2.65,C['muted'],1.4,True)
d=s.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(8.84), Inches(2.08), Inches(1.52), Inches(1.20));d.fill.solid();d.fill.fore_color.rgb=rgb(C['light']);d.line.color.rgb=rgb(C['d']);d._element.spPr.append(OxmlElement('a:effectLst'))
txt(s,9.04,2.39,1.13,.57,'Within\nlimits?',12,C['navy'],True,PP_ALIGN.CENTER)
line(s,10.38,2.65,10.67,2.65,C['muted'],1.4,True);txt(s,10.35,2.29,.45,.23,'YES',9,C['muted'],True)
rect(s,10.73,2.10,2.12,1.14,C['bg'],radius=True);rect(s,10.73,2.10,2.12,.07,C['x']);txt(s,10.86,2.29,1.88,.3,'Resolve & verify',14,C['x'],True);txt(s,10.86,2.70,1.88,.44,'Record evidence;\nupdate the log.',12.5,C['text'])
line(s,9.60,3.28,9.60,3.51,C['x'],1.4,True);txt(s,9.80,3.28,1.7,.21,'NO → ESCALATE',9,C['x'],True)
rect(s,.48,3.53,12.37,.66,C['light'],radius=True);txt(s,.66,3.67,12.02,.40,'Unresolved / beyond delegated limits → PM → functional head → sponsor / authorized approver [TBD].\nCritical safety or quality concern → stop affected work; immediately notify the designated authority.',12.5,C['navy'],True)
table(s,.48,4.56,12.37,['REGISTER FIELD','RISK EXAMPLE — VALIDATE','ISSUE RECORD — POPULATE'],[
 ['Event / impact','Critical supplier slip may delay assembly.','[Actual event / affected milestone]'],
 ['Owner / response','Supply Chain [name]: confirm capacity; mitigate source risk.','[Owner / containment / recovery action]'],
 ['Due / trigger / closure','[Due date]; ETA passes need date; verify residual risk.','[Due / decision / evidence / closed date]']
 ],[2.20,5.18,4.99],[.45,.43,.55,.47],font=12)
notes(s,'Potential risk example is illustrative and not an actual supplier delay. A full risk register includes ID, project, cause-event-effect statement, likelihood, impact, score / priority, trigger, owner, mitigation / contingency, target date, current state, residual risk and review date. An issue register includes actual occurrence date, impact, containment, resolution owner, due date, escalation / decision, evidence and closure date. Escalation thresholds and response times are [TBD] and must be agreed; do not invent an SLA. Proposed triggers: threat to a committed milestone; safety / quality exposure; resource conflict; unresolved cross-department dependency; cost or scope beyond delegated limits; action overdue beyond an agreed tolerance. Stop affected unsafe work and use the established company safety route. PM coordinates but does not override technical or safety authority. Verify recurrence prevention and update the relevant risk after issue closure.')
#16
s=slide('10 / Formal change management','No uncontrolled change after the baseline is approved','Customer and internal design changes follow one documented route; urgent changes still require authority.')
steps=[('REQUEST','Marketing / Design\nRecord scope and reason.',C['m']),('ASSESS','All affected leads\nCost • stock • quality • time',C['d']),('APPROVE','Authorized approver [TBD]\nApprove / reject / defer.',C['x']),('RELEASE','Design + affected owners\nRevise and acknowledge.',C['a'])]
for i,(title,body,col) in enumerate(steps):
 xx=.48+i*3.15;rect(s,xx,2.12,2.92,1.63,C['bg'],radius=True);pill(s,xx+.15,2.29,1.3,title,col);txt(s,xx+.15,2.91,2.62,.60,body,14,C['text'])
 if i<3:line(s,xx+2.94,2.92,xx+3.12,2.92,C['muted'],1.5,True)
card(s,.48,4.18,6.08,1.56,'PM control points','Log the change ID; consolidate impact; obtain decisions; update schedule and track acknowledgments.',C['navy'])
card(s,6.77,4.18,6.08,1.56,'Release evidence','Approved request; revised drawings / BOM; stock and WIP disposition; revised delivery commitment if affected.',C['d'])
banner(s,'Hold affected work until authorized disposition is clear. Unaffected work may continue if safe and formally agreed.')
notes(s,'Formal change request fields: ID, project, originator, reason, affected requirements / drawings / BOM / PO / WIP, technical impact, safety and quality impact, cost, lead time, schedule / delivery impact, recommended disposition, delegated approvers, decision, effective revision and date. Marketing confirms customer acceptance where contractually required; Design controls technical revision release; Supply Chain identifies purchase / supplier impacts; Assembly identifies rework and WIP impacts; Dispatch identifies packing / delivery impacts. PM integrates the assessment, tracks approval and rebaselines only after authorization. Document treatment of existing stock, work in progress and already released purchase orders. Rejected or deferred changes remain traceable and do not enter production. Authority for commercial commitments, cost approval and final release is [TBD].')
#17
s=slide('11 / Quality control and dispatch readiness','Make dispatch a controlled release—not the next activity','Quality signatory: [TBD] • Dispatch clearance authority: [TBD] • Project / machine serial: [TBD]')
# two checklists
for xx,title,col,items in [(.48,'QUALITY / FINAL ACCEPTANCE',C['a'],[
 'Stage inspection records complete and accepted.',
 'Approved functional and safety tests passed.',
 'Blocking defects closed; concessions authorized.',
 'As-built revisions, manuals and test evidence complete.',
 'Customer acceptance / FAT recorded if required.'
 ]),(6.78,'PRE-DISPATCH / RELEASE',C['x'],[
 'Quality release and authorized clearance recorded.',
 'Machine, agreed accessories and packing list verified.',
 'Preservation, packing and handling checks accepted.',
 'Required commercial / transport documents ready.',
 'Carrier, destination and shipment communication confirmed.'
 ])]:
 rect(s,xx,2.09,6.07,3.86,C['bg'],radius=True);rect(s,xx,2.09,6.07,.10,col);txt(s,xx+.18,2.38,5.70,.36,title,15,col,True)
 for i,it in enumerate(items):
  yy=3.01+i*.52;rect(s,xx+.20,yy+.03,.17,.17,C['white'],C['muted']);txt(s,xx+.53,yy,5.31,.44,it,13,C['text'])
 txt(s,xx+.2,5.63,5.65,.23,'Result: [Pass / Hold]   Sign-off: [Name / date / reference]',10.5,C['muted'],True)
banner(s,'Release only when required sign-offs are complete. After shipment, record actual dispatch and share shipment evidence.')
notes(s,'Checklist is proposed and must be aligned to the approved machine specification, contract, destination and company quality system. FAT = Factory Acceptance Test; include customer witnessing / acceptance only when required. The PM verifies the presence and status of required evidence, not technical conformity in place of the authorized inspector. Do not dispatch with unresolved safety defects, blocking nonconformities, missing documentation or unauthorized deviations. Any permitted concession must be within the relevant technical, customer and regulatory authority; no concession is presumed acceptable. Actual documents may include invoice, packing list, carrier / transport records, delivery address and any applicable statutory or destination-specific documentation; do not assume a particular tax or export route. Shipping execution remains on hold until the release authority [TBD] signs. After dispatch, Marketing / PM share shipment details and record residual contractual obligations such as delivery acknowledgment, installation or training only if in scope.')
#18
s=slide('12 / Expected outcomes and conclusion','A coordinated delivery system—not just more follow-up','PM-led integration turns separate departmental activities into a visible, controlled route to dispatch.')
for i,(title,body,col) in enumerate([
 ('Clear ownership','Named owners, accepted handovers and visible decisions.',C['m']),
 ('Fewer preventable delays','Earlier design, procurement and readiness interventions.',C['s']),
 ('Controlled quality & change','Evidence-based gates, revisions and authorized release.',C['d']),
 ('Delivery confidence','One forecast per machine, recovery actions and dispatch proof.',C['a'])]):
 xx=.48+(i%2)*6.30; yy=2.12+(i//2)*1.57;card(s,xx,yy,6.07,1.34,title,body,col)
rect(s,.48,5.57,12.37,1.05,C['navy'],radius=True);txt(s,.68,5.76,11.95,.29,'MANAGEMENT DECISIONS REQUESTED',12,'8FC9D4',True)
txt(s,.68,6.13,11.95,.34,'Confirm mandate & sponsor  •  Name owners / approvers  •  Approve gates & cadence  •  Baseline each project',14,C['white'],True)
notes(s,'Outcomes are expected benefits, not quantified claims. Establish a baseline before assigning targets or reporting improvement. Track milestone on-time rate, overdue critical actions, accepted material readiness, defect closure, first-pass test acceptance, change impact and actual dispatch against the approved commitment. Management decisions requested: confirm the Design-deputed PM’s coordination mandate; name a sponsor and escalation route; nominate functional owners and independent authorized technical / quality / dispatch signatories; agree the proposed gates, cadence and common records; approve separate customer scope and delivery baselines for CNC Router and ED Mill. Next step is a joint kickoff to populate all [TBD] fields and validate the potential gaps using evidence.')

# set document props
prs.core_properties.title='End-to-End Project Management – From Design to Dispatch'
prs.core_properties.subject='CNC Router and ED Mill | Proposed cross-functional operating model'
prs.core_properties.author='Project Management | Design Department'
prs.core_properties.keywords='project management, CNC Router, ED Mill, SmartArt, RACI, Gantt, readiness, gap closure'
prs.core_properties.comments='Editable management presentation. Proposed processes and placeholders require company validation.'
# theme font and palette
for part in prs.part.package.iter_parts():
 if str(part.partname).startswith('/ppt/theme/'):
  root=ET.fromstring(part.blob);ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
  for tag in ['majorFont','minorFont']:
   for e in root.findall('.//a:'+tag+'/a:latin',ns): e.set('typeface','Calibri')
  for i,col in enumerate(COLORS+[C['navy']],1):
   el=root.find('.//a:clrScheme/a:accent'+str(i),ns)
   if el is not None:
    for ch in list(el): el.remove(ch)
    ET.SubElement(el,'{'+ns['a']+'}srgbClr',val=col)
  part._blob=ET.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
prs.save(ROOT+'/work/base.pptx')

# Native SmartArt injection, keeping full editable data/layout/style/color parts.
A='http://schemas.openxmlformats.org/drawingml/2006/main';P='http://schemas.openxmlformats.org/presentationml/2006/main';D='http://schemas.openxmlformats.org/drawingml/2006/diagram';DSP='http://schemas.microsoft.com/office/drawing/2008/diagram';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PKG='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
ns={'a':A,'p':P,'dgm':D,'dsp':DSP,'r':R}
def tag(n,t):return '{'+n+'}'+t
def emu(v):return int(Inches(v))
def ser(r):return ET.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
def txbody(parent,tname,text,size=15):
 t=ET.SubElement(parent,tag(DSP if tname=='txBody' else D,tname));bp=ET.SubElement(t,tag(A,'bodyPr'),wrap='square',anchor='ctr',lIns='140000',rIns='140000',tIns='45000',bIns='45000');ET.SubElement(bp,tag(A,'noAutofit'));ET.SubElement(t,tag(A,'lstStyle'))
 for i,st in enumerate(text.split('\n')):
  p=ET.SubElement(t,tag(A,'p'));pp=ET.SubElement(p,tag(A,'pPr'),algn='ctr');ET.SubElement(pp,tag(A,'buNone'));r=ET.SubElement(p,tag(A,'r'));rp=ET.SubElement(r,tag(A,'rPr'),lang='en-US',sz=str(size*100),b='1' if i==0 else '0');sf=ET.SubElement(rp,tag(A,'solidFill'));ET.SubElement(sf,tag(A,'srgbClr'),val=C['white']);ET.SubElement(rp,tag(A,'latin'),typeface='Calibri');ET.SubElement(r,tag(A,'t')).text=st
 return t
z=ZipFile(ROOT+'/work/base.pptx');parts={n:z.read(n) for n in z.namelist()};z.close();template=ZipFile(ROOT+'/work/smartart_many.pptx');ct=ET.fromstring(parts['[Content_Types].xml'])
for idx,spec in enumerate(SMART,1):
 sn=spec['slide'];sp=ET.fromstring(parts[f'ppt/slides/slide{sn}.xml']);relsname=f'ppt/slides/_rels/slide{sn}.xml.rels';rels=ET.fromstring(parts[relsname]);existing=[int(e.get('Id')[3:]) for e in rels];base=max(existing)+1
 keys=['dm','lo','qs','cs','dr'];types=['diagramData','diagramLayout','diagramQuickStyle','diagramColors','diagramDrawing'];files=['data','layout','quickStyle','colors','drawing'];ids={k:'rId'+str(base+i) for i,k in enumerate(keys)}
 for key,typ,fi in zip(keys,types,files):
  rtyp=(R+'/'+typ) if key!='dr' else 'http://schemas.microsoft.com/office/2007/relationships/diagramDrawing'
  ET.SubElement(rels,tag(PKG,'Relationship'),Id=ids[key],Type=rtyp,Target=f'../diagrams/{fi}{idx}.xml')
 # data model edits
 data=ET.fromstring(template.read('ppt/diagrams/data1.xml'))
 pts=[p for p in data.find('dgm:ptLst',ns) if p.get('type') is None]
 for i,(pt,text) in enumerate(zip(pts,spec['labels'])):
  pr=pt.find('dgm:prSet',ns);pr.set('phldr','0');pr.attrib.pop('phldrT',None)
  old=pt.find('dgm:t',ns)
  if old is not None:pt.remove(old)
  txbody(pt,'t',text,15)
  st=pt.find('dgm:spPr',ns)
  for e in list(st):st.remove(e)
  fill=ET.SubElement(st,tag(A,'solidFill'));ET.SubElement(fill,tag(A,'srgbClr'),val=COLORS[i])
 data.find('.//dsp:dataModelExt',ns).set('relId',ids['dr'])
 # cached drawing with 5 horizontal chevrons; these are native editable SmartArt nodes.
 dr=ET.fromstring(template.read('ppt/diagrams/drawing1.xml'))
 shapes=dr.findall('.//dsp:sp',ns)
 totalw=emu(spec['w']);height=emu(spec['h']);gap=emu(.07);nw=(totalw-gap*4)//5
 for i,(sh,text) in enumerate(zip(shapes,spec['labels'])):
  nv=sh.find('dsp:nvSpPr/dsp:cNvPr',ns);nv.set('id',str(i+1));nv.set('name',DEPTS[i]+' workflow step')
  sppr=sh.find('dsp:spPr',ns)
  for ch in list(sppr):sppr.remove(ch)
  xf=ET.SubElement(sppr,tag(A,'xfrm'));ET.SubElement(xf,tag(A,'off'),x=str(i*(nw+gap)),y='0');ET.SubElement(xf,tag(A,'ext'),cx=str(nw),cy=str(height))
  geom=ET.SubElement(sppr,tag(A,'prstGeom'),prst='chevron');adj=ET.SubElement(geom,tag(A,'avLst'));ET.SubElement(adj,tag(A,'gd'),name='adj',fmla='val 10000')
  sf=ET.SubElement(sppr,tag(A,'solidFill'));ET.SubElement(sf,tag(A,'srgbClr'),val=COLORS[i]);ln=ET.SubElement(sppr,tag(A,'ln'));ET.SubElement(ln,tag(A,'noFill'));ET.SubElement(sppr,tag(A,'effectLst'))
  for tagname in ['txBody','txXfrm','style']:
   ee=sh.find('dsp:'+tagname,ns)
   if ee is not None:sh.remove(ee)
  txbody(sh,'txBody',text,15)
  xf=ET.SubElement(sh,tag(DSP,'txXfrm'));ET.SubElement(xf,tag(A,'off'),x=str(i*(nw+gap)+emu(.08)),y='0');ET.SubElement(xf,tag(A,'ext'),cx=str(nw-emu(.16)),cy=str(height))
 # layout remains based on Office's editable Basic Block List algorithm, with process chevrons.
 layout=ET.fromstring(template.read('ppt/diagrams/layout1.xml'))
 title=layout.find('dgm:title',ns);title.set('val','Five-department project process')
 for el in layout.findall('.//dgm:layoutNode[@name="node"]/dgm:shape',ns):el.set('type','chevron')
 # keep all regenerated nodes in one row for the wide process aspect ratio
 for el in layout.findall('.//dgm:constr[@type="h"]',ns):el.set('fact','0.42')
 for el in layout.findall('.//dgm:constr[@type="primFontSz"]',ns):el.set('val','15')
 for el in layout.findall('.//dgm:bulletEnabled',ns):el.set('val','0')
 quick=template.read('ppt/diagrams/quickStyle1.xml');colors=ET.fromstring(template.read('ppt/diagrams/colors1.xml'))
 # constant departmental palette for regeneration
 for lst in colors.findall('.//dgm:fillClrLst',ns):
  for ch in list(lst):lst.remove(ch)
  for col in COLORS:ET.SubElement(lst,tag(A,'srgbClr'),val=col)
 for fi,blob,ctype in [('data',ser(data),'application/vnd.openxmlformats-officedocument.drawingml.diagramData+xml'),('layout',ser(layout),'application/vnd.openxmlformats-officedocument.drawingml.diagramLayout+xml'),('quickStyle',quick,'application/vnd.openxmlformats-officedocument.drawingml.diagramStyle+xml'),('colors',ser(colors),'application/vnd.openxmlformats-officedocument.drawingml.diagramColors+xml'),('drawing',ser(dr),'application/vnd.ms-office.drawingml.diagramDrawing+xml')]:
  name=f'ppt/diagrams/{fi}{idx}.xml';parts[name]=blob;ET.SubElement(ct,tag(CT,'Override'),PartName='/'+name,ContentType=ctype)
 # replace placeholder shape in-place with diagram frame
 old=sp.find(f'.//p:sp[p:nvSpPr/p:cNvPr[@id="{spec["id"]}"]]',ns) if False else None
 for el in sp.findall('.//p:sp',ns):
  nv=el.find('p:nvSpPr/p:cNvPr',ns)
  if nv is not None and nv.get('id')==str(spec['id']):old=el;break
 frame=ET.Element(tag(P,'graphicFrame'));nv=ET.SubElement(frame,tag(P,'nvGraphicFramePr'));ET.SubElement(nv,tag(P,'cNvPr'),id=str(spec['id']),name='Editable SmartArt — five-department process');ET.SubElement(nv,tag(P,'cNvGraphicFramePr'));ET.SubElement(nv,tag(P,'nvPr'))
 xf=ET.SubElement(frame,tag(P,'xfrm'));ET.SubElement(xf,tag(A,'off'),x=str(emu(spec['x'])),y=str(emu(spec['y'])));ET.SubElement(xf,tag(A,'ext'),cx=str(totalw),cy=str(height))
 gr=ET.SubElement(frame,tag(A,'graphic'));gd=ET.SubElement(gr,tag(A,'graphicData'),uri=D);rid=ET.SubElement(gd,tag(D,'relIds'),nsmap={'dgm':D,'r':R})
 for key in ['dm','lo','qs','cs']:rid.set(tag(R,key),ids[key])
 par=old.getparent();par.replace(old,frame);parts[f'ppt/slides/slide{sn}.xml']=ser(sp);parts[relsname]=ser(rels)
parts['[Content_Types].xml']=ser(ct)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
 for n,b in parts.items():z.writestr(n,b)
print(OUT, 'slides=',len(prs.slides), 'smartart=',len(SMART))
