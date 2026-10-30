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

const lineChart=(s,x,y,w,h,name,labels,vals,col,title,fmt)=>s.addChart(p.charts.LINE,[{name,labels,values:vals}],{x,y,w,h,chartColors:[col],lineSize:3,lineDataSymbolSize:7,showValue:false,showLegend:false,showTitle:true,title,titleFontSize:14,titleColor:NAVY,valGridLine:{color:'E5E7EB',size:0.5},catGridLine:{style:'none'},catAxisLabelColor:INK,valAxisLabelColor:MUTE,valAxisLabelFormatCode:fmt,valAxisMinVal:0});
const mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep'];

// 1 Title
let s=p.addSlide(); s.background={color:NAVY};
s.addShape(p.ShapeType.ellipse,{x:9.6,y:1.2,w:3.6,h:3.6,fill:{color:AMB},line:{color:AMB}});
T(s,'$',{x:9.6,y:1.2,w:3.6,h:3.6,fontFace:H,fontSize:130,bold:true,color:NAVY,align:'center',valign:'middle'});
T(s,'MoMo Fraud Detection',{x:0.7,y:2.0,w:8.6,h:1.4,fontFace:H,fontSize:48,bold:true,color:WHITE,valign:'bottom'});
T(s,'Recommendation to MoMo\'s managers: smarter, not just stricter',{x:0.7,y:3.5,w:8.4,h:0.9,fontSize:22,color:AMB});
T(s,'BSA83316 · Industry Applications of Big Data · Case study, Tasks 1–5',{x:0.7,y:6.3,w:8,h:0.4,fontSize:14,color:'CADCFC'});

// 2 Problem
s=content('Task 1: MoMo has two problems at once',2);
card(s,0.6,1.4,12.1,1.35,NAVY);
T(s,'Simple rules like "block any payment over $500 at night" fail both ways: fraud losses are rising and honest customers are wrongly blocked, because the rules are too blunt and key data arrives too late.',{x:0.9,y:1.4,w:11.5,h:1.35,fontSize:17,bold:true,color:WHITE,valign:'middle'});
lineChart(s,0.6,2.95,5.9,3.0,'Fraud losses ($K)',mon,[80,85,90,95,100,105,110,115,120],RED,'Fraud losses per month ($ thousands)','$0"K"');
lineChart(s,6.8,2.95,5.9,3.0,'Complaints (K)',mon,[1.5,1.8,2,2.3,2.6,3,3.3,3.7,4],'B26B00','Complaints per month (thousands)','0.0"K"');
T(s,'Fraud +50% ($80K to $120K).',{x:0.6,y:6.1,w:5.9,h:0.5,fontSize:16,bold:true,color:RED,align:'center'});
T(s,'Complaints +167% (1,500 to 4,000).',{x:6.8,y:6.1,w:5.9,h:0.5,fontSize:16,bold:true,color:'B26B00',align:'center'});

// 3 Vs
s=content('Task 1: the four Vs and who is affected',3);
[['Volume','8 million payments every month'],['Velocity','Payments and app logins arrive live'],['Variety','Payment records, phone details, SIM changes, complaint texts and calls'],['Veracity','Typing errors in agent withdrawals; SIM data 2 days late; complaints not organised']].forEach((c,i)=>{
 const x=0.6+i*3.1; card(s,x,1.5,2.9,2.7);
 T(s,c[0],{x:x+0.25,y:1.65,w:2.4,h:0.5,fontFace:H,fontSize:22,bold:true,color:NAVY});
 T(s,c[1],{x:x+0.25,y:2.3,w:2.4,h:1.8,fontSize:14});});
card(s,0.6,4.5,5.9,2.2); card(s,6.8,4.5,5.9,2.2);
T(s,'Inside the company',{x:0.9,y:4.65,w:5.3,h:0.5,fontFace:H,fontSize:20,bold:true,color:NAVY});
T(s,'Managers and owners (losses, reputation) and customer-care staff (complaint calls).',{x:0.9,y:5.25,w:5.3,h:1.3,fontSize:15});
T(s,'Outside the company',{x:7.1,y:4.65,w:5.3,h:0.5,fontFace:H,fontSize:20,bold:true,color:NAVY});
T(s,'Honest customers who are blocked, fraud victims, agents at cash points, and regulators.',{x:7.1,y:5.25,w:5.3,h:1.3,fontSize:15});

// 4 SIM
s=content('Task 1: why late SIM data hurts, and what to fix first',4);
card(s,0.6,1.5,6.0,5.2); card(s,6.8,1.5,5.9,5.2,NAVY);
T(s,'Why two days late is serious',{x:0.9,y:1.7,w:5.4,h:0.5,fontFace:H,fontSize:22,bold:true,color:NAVY});
bullets(s,['A fraud decision must be made at the moment of payment, in seconds','Criminals steal SIM cards, so a SIM change is the best warning sign','The feed arrives 2 days late, so the money is gone before MoMo "knows"'],{x:0.9,y:2.45,w:5.4,h:4.0,fontSize:16});
T(s,'If we fix only ONE data problem',{x:7.1,y:1.7,w:5.3,h:0.5,fontFace:H,fontSize:22,bold:true,color:AMB});
T(s,'Fix the SIM card delay first',{x:7.1,y:2.4,w:5.3,h:0.9,fontFace:H,fontSize:28,bold:true,color:WHITE});
T(s,'It is the data that would help most to stop the most common fraud. Typing errors and unorganised complaints matter less for blocking a payment in time.',{x:7.1,y:3.5,w:5.3,h:2.9,fontSize:16,color:WHITE});

// 5 Cost table
s=content('Task 2: cost of each setting',5);
const hd=(t)=>({text:t,options:{bold:true,color:WHITE,fill:{color:NAVY},align:'center'}});
const c=(t,o)=>({text:t,options:Object.assign({align:'center'},o||{})});
s.addTable([
 [hd('Setting'),hd('Fraud caught'),hd('Fraud missed'),hd('Honest blocked'),hd('Missed × $100'),hd('Blocked × $5'),hd('Total cost')],
 [c('Old rules',{align:'left'}),c('800'),c('1,200'),c('12,000'),c('$120,000'),c('$60,000'),c('$180,000',{bold:true})],
 [c('A: Strict',{align:'left'}),c('1,800'),c('200'),c('40,000'),c('$20,000'),c('$200,000'),c('$220,000',{bold:true,color:RED})],
 [c('B: Balanced',{align:'left',bold:true}),c('1,600'),c('400'),c('10,000'),c('$40,000'),c('$50,000'),c('$90,000',{bold:true,color:GRN,fill:{color:'E3F5EC'}})],
 [c('C: Relaxed',{align:'left'}),c('1,000'),c('1,000'),c('2,000'),c('$100,000'),c('$10,000'),c('$110,000',{bold:true})],
],{x:0.6,y:1.5,w:12.1,colW:[2.0,1.5,1.6,1.8,1.8,1.7,1.7],rowH:0.62,fontFace:B,fontSize:15,color:INK,border:{type:'solid',pt:0.75,color:'D5D9E0'},valign:'middle'});
T(s,'Total cost = (missed × $100) + (blocked × $5). A blocked customer costs $5 in care calls and some customers leaving. Caught + missed = 2,000 each month.',{x:0.6,y:4.8,w:12.1,h:0.6,fontSize:14,italic:true,color:MUTE});
card(s,0.6,5.5,12.1,1.2,'E3F5EC');
T(s,'Cheapest: Setting B at $90,000 a month. That saves $90,000 a month (about $1.08M a year) vs. today\'s rules.',{x:0.9,y:5.5,w:11.5,h:1.2,fontSize:20,bold:true,color:GRN,valign:'middle'});

// 6 chart
s=content('Task 2: why Strict is not the best',6);
s.addChart(p.charts.BAR,[{name:'Total monthly cost ($)',labels:['Old rules','A: Strict','B: Balanced','C: Relaxed'],values:[180000,220000,90000,110000]}],{x:0.6,y:1.4,w:6.4,h:5.3,barDir:'col',chartColors:[MUTE,RED,GRN,AMB],showValue:true,dataLabelFormatCode:'$#,##0',dataLabelPosition:'outEnd',dataLabelFontSize:12,showLegend:false,valGridLine:{color:'E5E7EB',size:0.5},catGridLine:{style:'none'},catAxisLabelColor:INK,valAxisLabelColor:MUTE,valAxisLabelFormatCode:'$#,##0',showTitle:true,title:'Total monthly cost',titleFontSize:14,titleColor:NAVY});
card(s,7.3,1.5,5.4,1.75);card(s,7.3,3.4,5.4,1.75);card(s,7.3,5.3,5.4,1.4,NAVY);
T(s,'Strict catches the most fraud (1,800)',{x:7.55,y:1.6,w:4.9,h:0.4,fontFace:H,fontSize:16,bold:true,color:NAVY});
T(s,'but blocks 40,000 honest customers. At $5 each that costs $200,000, so its total is the highest.',{x:7.55,y:2.05,w:4.9,h:1.1,fontSize:13});
T(s,'Does it match our first reaction?',{x:7.55,y:3.5,w:4.9,h:0.4,fontFace:H,fontSize:16,bold:true,color:NAVY});
T(s,'Our instinct was "be stricter". The numbers show the cost of over-blocking outweighs the extra fraud caught. Smarter beats stricter.',{x:7.55,y:3.95,w:4.9,h:1.15,fontSize:13});
T(s,'If a block cost $10: A $420K, B $140K, C $120K, so Relaxed wins. The answer depends on this assumption.',{x:7.55,y:5.4,w:4.9,h:1.2,fontSize:13,color:WHITE,valign:'middle'});

// 7 Data flow
s=content('Task 3: the data flow and tools',7);
const steps=[['Data sources','Payments, app logins and phone details, SIM changes (all live)'],['Kafka','Carries every new payment instantly'],['Spark','Checks if the payment looks unusual'],['Decision','Approve, ask for code, or block']];
steps.forEach((st,i)=>{const x=0.6+i*3.1; card(s,x,1.35,2.7,1.6,i==3?AMB:NAVY);
 T(s,st[0],{x:x+0.2,y:1.42,w:2.3,h:0.4,fontFace:H,fontSize:17,bold:true,color:i==3?NAVY:AMB});
 T(s,st[1],{x:x+0.2,y:1.85,w:2.3,h:1.0,fontSize:13,color:i==3?NAVY:WHITE});
 if(i<3) s.addText('→',{x:x+2.7,y:1.85,w:0.4,h:0.5,isTextBox:true,margin:0,fontSize:22,bold:true,color:AMB,align:'center'});});
[['Hadoop','Keeps all past data for years (history, learning patterns)'],['Tableau','Shows managers daily fraud and complaint numbers']].forEach((st,i)=>{const x=6.8+i*3.1; card(s,x,3.15,2.7,1.3,'DDE3EE');
 T(s,st[0],{x:x+0.2,y:3.22,w:2.3,h:0.4,fontFace:H,fontSize:17,bold:true,color:NAVY});
 T(s,st[1],{x:x+0.2,y:3.65,w:2.3,h:0.75,fontSize:12});});
T(s,'Live path (seconds): top row.  History path (days, months): bottom row.',{x:0.6,y:3.35,w:6,h:0.9,fontSize:14,italic:true,color:MUTE});
[['Connect which sources?','Live: payments, logins and phone details, SIM changes. Daily is enough for agent withdrawals and complaints, which go to history and reports.'],['Seconds vs once a day','Seconds: Kafka, Spark, decision. Once a day: Hadoop and Tableau.'],['What changes for SIM data?','Switch from a once-a-day feed 2 days late to a live feed, so a SIM change can be checked at payment time.']].forEach((c,i)=>{
 const x=0.6+i*4.15; card(s,x,4.7,3.95,2.05);
 T(s,c[0],{x:x+0.25,y:4.78,w:3.45,h:0.4,fontFace:H,fontSize:16,bold:true,color:NAVY});
 T(s,c[1],{x:x+0.25,y:5.22,w:3.45,h:1.45,fontSize:12.5});});

// 8 People
s=content('Task 4: fairness and privacy',8);
card(s,0.6,1.4,6.0,5.3);card(s,6.8,1.4,5.9,5.3);
T(s,'News 1: new and rural customers are blocked most',{x:0.9,y:1.55,w:5.4,h:0.8,fontFace:H,fontSize:19,bold:true,color:NAVY});
T(s,'Not fair. Little history makes them look "unusual", and they are exactly the customers MoMo wants to attract. Instead of blocking:',{x:0.9,y:2.4,w:5.4,h:1.1,fontSize:14,color:MUTE});
bullets(s,['Ask for a security code','Let local agents vouch for customers','Check block rates by customer group every month','Use rules that do not depend only on history'],{x:0.9,y:3.6,w:5.4,h:3.0,fontSize:15});
T(s,'News 2: the CEO wants loans from the data',{x:7.1,y:1.55,w:5.3,h:0.8,fontFace:H,fontSize:19,bold:true,color:NAVY});
T(s,'Not yet. Customers shared data for security only, so a loan use breaks that agreement. First MoMo needs to:',{x:7.1,y:2.4,w:5.3,h:1.1,fontSize:14,color:MUTE});
bullets(s,['Ask customers for clear new consent','Follow data protection rules','Pilot with small loans','Test the scoring for unfair bias'],{x:7.1,y:3.6,w:5.3,h:3.0,fontSize:15});

// 9 Recommendation
s=content('Task 5: our recommendation',9);
[['Problem','Rules that are too blunt miss fraud and block honest customers, and SIM data arrives too late.'],['Setting','B: Balanced, $90,000 a month, saving about $1.08M a year vs. $180,000 today.'],['Data flow','Kafka, Spark, then decision in seconds; Hadoop and Tableau for history; SIM feed made live.'],['Fairness and privacy','Security codes for new and rural customers, monthly block-rate checks, no loan use without consent.'],['How we know it worked','Monthly fraud losses ($), honest customers blocked, complaints per month.']].forEach((r,i)=>{
 const y=1.4+i*1.06; card(s,0.6,y,12.1,0.94);
 s.addShape(p.ShapeType.ellipse,{x:0.8,y:y+0.17,w:0.6,h:0.6,fill:{color:AMB},line:{color:AMB}});
 T(s,String(i+1),{x:0.8,y:y+0.17,w:0.6,h:0.6,fontFace:H,fontSize:20,bold:true,color:NAVY,align:'center',valign:'middle'});
 T(s,r[0],{x:1.65,y,w:2.9,h:0.94,fontFace:H,fontSize:17,bold:true,color:NAVY,valign:'middle'});
 T(s,r[1],{x:4.6,y,w:7.9,h:0.94,fontSize:14,valign:'middle'});});
p.writeFile({fileName:'MoMo_Fraud_Detection_9slides_v2.pptx'}).then(()=>console.log('ok'));
