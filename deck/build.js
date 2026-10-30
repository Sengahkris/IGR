const pptxgen = require('pptxgenjs');
const p = new pptxgen(); p.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
const NAVY='14213D', AMB='FCA311', LIGHT='F4F6FA', INK='1F2937', MUTE='6B7280', RED='C0392B', GRN='1E8E5A', WHITE='FFFFFF';
const H='Cambria', B='Calibri';
const T=(s,t,o)=>s.addText(t,Object.assign({isTextBox:true,fontFace:B,color:INK,margin:0},o));
function content(title, n){
  const s=p.addSlide(); s.background={color:WHITE};
  T(s,title,{x:0.6,y:0.4,w:12.1,h:0.9,fontFace:H,fontSize:34,bold:true,color:NAVY,valign:'middle'});
  T(s,String(n),{x:12.2,y:6.95,w:0.6,h:0.3,fontSize:11,color:MUTE,align:'right'});
  return s;
}
function card(s,x,y,w,h,fill){ s.addShape(p.ShapeType.roundRect,{x,y,w,h,fill:{color:fill||LIGHT},line:{color:fill||LIGHT},rectRadius:0.12}); }
function bullets(s,items,o){ s.addText(items.map((t,i)=>({text:t,options:{bullet:true,breakLine:i<items.length-1,paraSpaceAfter:8}})),Object.assign({isTextBox:true,fontFace:B,fontSize:16,color:INK,margin:0,valign:'top'},o)); }

// 1 Title
let s=p.addSlide(); s.background={color:NAVY};
s.addShape(p.ShapeType.ellipse,{x:9.6,y:1.2,w:3.6,h:3.6,fill:{color:AMB},line:{color:AMB}});
T(s,'$',{x:9.6,y:1.2,w:3.6,h:3.6,fontFace:H,fontSize:130,bold:true,color:NAVY,align:'center',valign:'middle'});
T(s,'MoMo Fraud Detection',{x:0.7,y:2.0,w:8.6,h:1.4,fontFace:H,fontSize:48,bold:true,color:WHITE,valign:'bottom'});
T(s,'Smarter, not just stricter: case analysis and recommendation',{x:0.7,y:3.5,w:8.4,h:0.9,fontSize:22,color:AMB});
T(s,'Slides 33–39 · Tasks 1–5',{x:0.7,y:6.3,w:6,h:0.4,fontSize:14,color:'CADCFC'});

// 2 First reaction
s=content('First reaction: stricter or more relaxed?',2);
card(s,0.6,1.6,5.9,2.4,'FDECEA'); card(s,6.8,1.6,5.9,2.4,'FEF3DC');
T(s,'Purely stricter',{x:0.9,y:1.8,w:5.3,h:0.5,fontFace:H,fontSize:22,bold:true,color:RED});
T(s,'Catches more fraud, but blocks more honest customers. Complaints are already rising alongside fraud losses.',{x:0.9,y:2.4,w:5.3,h:1.4,fontSize:16});
T(s,'Purely relaxed',{x:7.1,y:1.8,w:5.3,h:0.5,fontFace:H,fontSize:22,bold:true,color:'B26B00'});
T(s,'Fewer complaints, but more fraud gets through.',{x:7.1,y:2.4,w:5.3,h:1.4,fontSize:16});
card(s,0.6,4.3,12.1,2.3,NAVY);
T(s,'Smarter, not just stricter',{x:0.9,y:4.5,w:11.5,h:0.6,fontFace:H,fontSize:26,bold:true,color:AMB});
T(s,'Both charts on slide 34 rise together, so the flat "$500 at night" rule is too blunt. It cannot tell fraud from genuine unusual behaviour. Fix it with a precise, data-driven system rather than turning the same dial. Task 2 proves this with numbers.',{x:0.9,y:5.15,w:11.5,h:1.3,fontSize:16,color:WHITE});

// 3 Task1 problem
s=content('Task 1: one failure, two problems',3);
const stat=(x,big,lab,sub,col)=>{card(s,x,1.6,5.9,3.0);
 T(s,big,{x:x+0.3,y:1.8,w:5.3,h:1.2,fontFace:H,fontSize:54,bold:true,color:col,valign:'middle'});
 T(s,lab,{x:x+0.3,y:3.0,w:5.3,h:0.5,fontSize:20,bold:true});
 T(s,sub,{x:x+0.3,y:3.55,w:5.3,h:0.8,fontSize:15,color:MUTE});};
stat(0.6,'+50%','Fraud losses','$80K → $120K per month',RED);
stat(6.8,'+167%','Honest-customer complaints','1,500 → 4,000 per month, from wrongful blocks',RED);
T(s,'The current rule fails in both directions at once: too loose to stop determined criminals, too rigid to spare innocent customers.',{x:0.6,y:5.0,w:12.1,h:1.2,fontSize:20,color:NAVY,bold:true});

// 4 Four Vs
s=content('The four Vs in MoMo\'s data',4);
[['Volume','8 million payments processed every month'],['Velocity','Payments and app logins captured live, in real time'],['Variety','Structured payment records, live phone/login data, daily network reports, unstructured complaint text'],['Veracity','SIM-change data arrives 2 days late, agent withdrawal records have typos, complaints are unorganised']].forEach((c,i)=>{
 const x=0.6+(i%2)*6.2, y=1.6+Math.floor(i/2)*2.6; card(s,x,y,5.9,2.3);
 s.addShape(p.ShapeType.ellipse,{x:x+0.3,y:y+0.3,w:0.7,h:0.7,fill:{color:AMB},line:{color:AMB}});
 T(s,'V',{x:x+0.3,y:y+0.3,w:0.7,h:0.7,fontFace:H,fontSize:24,bold:true,color:NAVY,align:'center',valign:'middle'});
 T(s,c[0],{x:x+1.2,y:y+0.3,w:4.4,h:0.7,fontFace:H,fontSize:24,bold:true,color:NAVY,valign:'middle'});
 T(s,c[1],{x:x+0.3,y:y+1.15,w:5.3,h:1.0,fontSize:15});});

// 5 SIM delay
s=content('Why the SIM data delay matters most',5);
card(s,0.6,1.6,6.0,4.9);
T(s,'Why it is serious',{x:0.9,y:1.8,w:5.4,h:0.5,fontFace:H,fontSize:22,bold:true,color:NAVY});
bullets(s,['A fraud decision must be made at the moment of payment, in seconds','SIM swap is the most common fraud type','The best signal arrives 2 days too late','By the time MoMo "knows", the money is gone'],{x:0.9,y:2.5,w:5.4,h:3.8});
card(s,6.9,1.6,5.8,4.9,NAVY);
T(s,'If we fix only one data problem',{x:7.2,y:1.8,w:5.2,h:0.5,fontFace:H,fontSize:22,bold:true,color:AMB});
T(s,'Fix the SIM card data delay',{x:7.2,y:2.5,w:5.2,h:1.0,fontFace:H,fontSize:30,bold:true,color:WHITE});
T(s,'A real-time SIM signal has the biggest impact on stopping fraud at the point of payment, more than fixing typing errors or organising complaints.',{x:7.2,y:3.7,w:5.2,h:2.4,fontSize:17,color:WHITE});

// 6 Who is affected
s=content('Who is affected?',6);
[['Honest customers','Blocked: inconvenience and frustration'],['Fraud victims','Lose money'],['Customer-care staff','Handle the complaint volume'],['MoMo managers / owners','Financial losses, reputational damage'],['Agents','Face angry customers at cash points'],['Regulators','May investigate fraud and complaint trends']].forEach((c,i)=>{
 const x=0.6+(i%3)*4.1, y=1.6+Math.floor(i/3)*2.6; card(s,x,y,3.9,2.3);
 T(s,c[0],{x:x+0.3,y:y+0.3,w:3.3,h:0.9,fontFace:H,fontSize:20,bold:true,color:NAVY,valign:'top'});
 T(s,c[1],{x:x+0.3,y:y+1.2,w:3.3,h:0.9,fontSize:15,color:MUTE});});

// 7 Cost table
s=content('Task 2: cost of each setting',7);
const hd=(t)=>({text:t,options:{bold:true,color:WHITE,fill:{color:NAVY},align:'center'}});
const c=(t,o)=>({text:t,options:Object.assign({align:'center'},o||{})});
s.addTable([
 [hd('Setting'),hd('Missed fraud cost'),hd('Blocked customer cost'),hd('Total / month')],
 [c('Old rules',{align:'left'}),c('1,200 × $100 = $120,000'),c('12,000 × $5 = $60,000'),c('$180,000',{bold:true})],
 [c('A: Strict',{align:'left'}),c('200 × $100 = $20,000'),c('40,000 × $5 = $200,000'),c('$220,000',{bold:true,color:RED})],
 [c('B: Balanced',{align:'left',bold:true}),c('400 × $100 = $40,000'),c('10,000 × $5 = $50,000'),c('$90,000',{bold:true,color:GRN,fill:{color:'E3F5EC'}})],
 [c('C: Relaxed',{align:'left'}),c('1,000 × $100 = $100,000'),c('2,000 × $5 = $10,000'),c('$110,000',{bold:true})],
],{x:0.6,y:1.6,w:12.1,colW:[2.4,3.3,3.5,2.9],rowH:0.65,fontFace:B,fontSize:16,color:INK,border:{type:'solid',pt:0.75,color:'D5D9E0'},valign:'middle'});
T(s,'Total cost = (fraud missed × $100) + (honest customers blocked × $5)',{x:0.6,y:5.3,w:12.1,h:0.5,fontSize:16,italic:true,color:MUTE});
T(s,'Cheapest: Setting B at $90,000/month, saving $90,000/month (about $1.08M/year) vs. today.',{x:0.6,y:5.9,w:12.1,h:0.7,fontSize:20,bold:true,color:GRN});

// 8 chart + why
s=content('Strict catches the most fraud, yet costs the most',8);
s.addChart(p.charts.BAR,[{name:'Total monthly cost ($)',labels:['Old rules','A: Strict','B: Balanced','C: Relaxed'],values:[180000,220000,90000,110000]}],{x:0.6,y:1.5,w:6.6,h:5.0,barDir:'col',chartColors:[MUTE,RED,GRN,AMB],showValue:true,dataLabelFormatCode:'$#,##0',dataLabelPosition:'outEnd',dataLabelFontSize:12,showLegend:false,valGridLine:{color:'E5E7EB',size:0.5},catGridLine:{style:'none'},catAxisLabelColor:INK,valAxisLabelColor:MUTE,valAxisLabelFormatCode:'$#,##0',showTitle:true,title:'Total monthly cost',titleFontSize:14,titleColor:NAVY});
card(s,7.5,1.6,5.2,2.3);
T(s,'Why not Strict?',{x:7.8,y:1.75,w:4.6,h:0.45,fontFace:H,fontSize:20,bold:true,color:NAVY});
T(s,'It blocks 40,000 honest customers. Even at $5 each, that makes it the most expensive at $220,000. Catching the most fraud is not the same as costing the least.',{x:7.8,y:2.25,w:4.6,h:1.6,fontSize:14});
card(s,7.5,4.1,5.2,2.4,NAVY);
T(s,'Sensitivity check',{x:7.8,y:4.25,w:4.6,h:0.45,fontFace:H,fontSize:20,bold:true,color:AMB});
T(s,'If a block costs $10: A = $420K, B = $140K, C = $120K. Relaxed becomes cheapest. The right answer depends on the true cost of blocking a customer.',{x:7.8,y:4.75,w:4.6,h:1.65,fontSize:14,color:WHITE});

// 9 Data flow
s=content('Task 3: designing the data flow',9);
const steps=[['Data sources','Live payments, app logins, SIM-change feed'],['Tool 1: Kafka','Carries the continuous live stream without delay'],['Tool 2: Spark','Scores each payment against fraud rules in real time'],['Decision','Approve / ask for security code / block']];
steps.forEach((st,i)=>{const x=0.6+i*3.1; card(s,x,1.7,2.7,2.2,i==3?AMB:NAVY);
 const fc=i==3?NAVY:WHITE;
 T(s,st[0],{x:x+0.2,y:1.85,w:2.3,h:0.6,fontFace:H,fontSize:19,bold:true,color:i==3?NAVY:AMB});
 T(s,st[1],{x:x+0.2,y:2.5,w:2.3,h:1.3,fontSize:14,color:fc});
 if(i<3) s.addText('→',{x:x+2.7,y:2.4,w:0.4,h:0.6,isTextBox:true,margin:0,fontSize:24,bold:true,color:AMB,align:'center'});});
[['History storage: Hadoop','Cheap, large-scale storage for long-term records and later analysis'],['Manager reporting: Tableau','Dashboards and visual reports managers can review']].forEach((st,i)=>{const x=0.6+i*6.2; card(s,x,4.3,5.9,1.6);
 T(s,st[0],{x:x+0.3,y:4.45,w:5.3,h:0.5,fontFace:H,fontSize:19,bold:true,color:NAVY});
 T(s,st[1],{x:x+0.3,y:5.0,w:5.3,h:0.8,fontSize:15});});
T(s,'Decisions feed history, and history feeds the reports.',{x:0.6,y:6.2,w:12,h:0.4,fontSize:14,italic:true,color:MUTE});

// 10 speed + sources
s=content('Real-time versus daily, and what must change',10);
card(s,0.6,1.6,3.9,4.9);card(s,4.7,1.6,3.9,4.9);card(s,8.8,1.6,3.9,4.9,NAVY);
T(s,'In seconds',{x:0.9,y:1.8,w:3.3,h:0.5,fontFace:H,fontSize:22,bold:true,color:RED});
T(s,'Kafka → Spark → Decision. A payment is approved or blocked instantly. Live inputs: payments, app logins / phone details, SIM changes.',{x:0.9,y:2.4,w:3.3,h:3.9,fontSize:15});
T(s,'Once a day',{x:5.0,y:1.8,w:3.3,h:0.5,fontFace:H,fontSize:22,bold:true,color:GRN});
T(s,'Hadoop storage and Tableau reports. Agent withdrawals and customer complaints feed this side, since they do not need second-by-second speed.',{x:5.0,y:2.4,w:3.3,h:3.9,fontSize:15});
T(s,'SIM data must change',{x:9.1,y:1.8,w:3.3,h:0.5,fontFace:H,fontSize:22,bold:true,color:AMB});
T(s,'Move from a once-a-day feed that is 2 days late to a live feed, so a SIM swap is checked against a payment when it happens, not after the damage is done.',{x:9.1,y:2.4,w:3.3,h:3.9,fontSize:15,color:WHITE});

// 11 people
s=content('Task 4: thinking about the people',11);
card(s,0.6,1.6,6.0,4.9);card(s,6.8,1.6,5.9,4.9);
T(s,'Are new / rural customers treated fairly?',{x:0.9,y:1.8,w:5.4,h:0.8,fontFace:H,fontSize:20,bold:true,color:NAVY});
T(s,'No. They are penalised for lacking history, not suspicious behaviour, and they are the group MoMo wants to grow.',{x:0.9,y:2.65,w:5.4,h:1.0,fontSize:14,color:MUTE});
bullets(s,['Send a security code instead of blocking','Let local agents vouch for customers','Monitor block rates by segment monthly','Build new-customer rules that do not rely only on history'],{x:0.9,y:3.75,w:5.4,h:2.6,fontSize:15});
T(s,'Use the data for loans?',{x:7.1,y:1.8,w:5.3,h:0.8,fontFace:H,fontSize:20,bold:true,color:NAVY});
T(s,'Not as-is. Customers shared data for fraud prevention, and a new purpose breaks that agreement and likely data protection law. First:',{x:7.1,y:2.65,w:5.3,h:1.0,fontSize:14,color:MUTE});
bullets(s,['Get explicit new consent','Comply with data protection regulations','Start with small pilots','Test credit scoring for fairness'],{x:7.1,y:3.75,w:5.3,h:2.6,fontSize:15});

// 12 recommendation
s=content('Task 5: our recommendation',12);
[['The problem','Rule-based fraud control fails both ways: fraud losses and wrongful blocks are rising, largely because SIM data arrives too late.'],['Setting + calculation (30%)','Setting B (Balanced): $90,000/month, saving about $1.08M/year vs. current rules.'],['Data flow and tools','Kafka → Spark → instant decision; Hadoop for history; Tableau for dashboards; SIM data moved to a live feed.'],['Fairness and privacy (20%)','Review block rates by group monthly, use verification steps for low-history customers, no loan use without fresh consent.']].forEach((c,i)=>{
 const x=0.6+(i%2)*6.2, y=1.6+Math.floor(i/2)*2.6; card(s,x,y,5.9,2.3);
 T(s,c[0],{x:x+0.3,y:y+0.25,w:5.3,h:0.5,fontFace:H,fontSize:20,bold:true,color:NAVY});
 T(s,c[1],{x:x+0.3,y:y+0.85,w:5.3,h:1.3,fontSize:15});});

// 13 metrics
s=p.addSlide(); s.background={color:NAVY};
T(s,'How we will track success',{x:0.6,y:0.5,w:12,h:0.9,fontFace:H,fontSize:36,bold:true,color:WHITE,valign:'middle'});
[['$','Monthly fraud losses'],['#','Honest customers blocked'],['?','Complaints received'],['s','Time to detect SIM-swap fraud']].forEach((m,i)=>{
 const x=0.6+i*3.1; s.addShape(p.ShapeType.roundRect,{x,y:1.9,w:2.8,h:3.2,fill:{color:'1F2F57'},line:{color:'1F2F57'},rectRadius:0.12});
 s.addShape(p.ShapeType.ellipse,{x:x+0.85,y:2.2,w:1.1,h:1.1,fill:{color:AMB},line:{color:AMB}});
 T(s,m[0],{x:x+0.85,y:2.2,w:1.1,h:1.1,fontFace:H,fontSize:34,bold:true,color:NAVY,align:'center',valign:'middle'});
 T(s,m[1],{x:x+0.2,y:3.6,w:2.4,h:1.2,fontSize:18,bold:true,color:WHITE,align:'center'});});
T(s,'Smarter, not just stricter.',{x:0.6,y:5.7,w:12,h:0.8,fontFace:H,fontSize:28,italic:true,color:AMB});
p.writeFile({fileName:'MoMo_Fraud_Detection.pptx'}).then(()=>console.log('ok'));
