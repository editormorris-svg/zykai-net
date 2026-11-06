document.addEventListener('DOMContentLoaded',()=>{const nav=document.querySelector('.navin'),button=document.querySelector('.menu'),desktopLinks=document.querySelector('.links'),desktopLang=document.querySelector('.lang');if(!nav||!button)return;const lang=(document.documentElement.lang||'en').toLowerCase(),isHK=lang.includes('hk'),isCN=lang.startsWith('zh')&&!isHK;const labels=isHK?{explore:'深入了解',infra:'基礎設施',knowledge:'校本知識',assess:'評估',control:'治理控制',gateway:'AI Gateway',training:'培訓',regional:'集團與區域',partner:'Host School',advisory:'AI顧問',investors:'投資者',referral:'內推與AI工作室'}:isCN?{explore:'深入了解',infra:'基础设施',knowledge:'校本知识',assess:'评估',control:'治理控制',gateway:'AI Gateway',training:'培训',regional:'集团与区域',partner:'Host School',advisory:'AI咨询',investors:'投资者',referral:'内推与AI工作室'}:{explore:'Explore',infra:'Infrastructure',knowledge:'Knowledge',assess:'Assessment',control:'Control',gateway:'AI Gateway',training:'Training',regional:'Groups & regional',partner:'Host School',advisory:'Advisory',investors:'Investors',referral:'Referrals & AI Studio'};const deep=[['referral.html',labels.referral],['infrastructure.html',labels.infra],['knowledge.html',labels.knowledge],['assessment.html',labels.assess],['control.html',labels.control],['gateway.html',labels.gateway],['training.html',labels.training],['regional.html',labels.regional],['partnership.html',labels.partner],['advisory.html',labels.advisory],['investors.html',labels.investors]];if(desktopLinks&&!desktopLinks.querySelector('.explore')){const details=document.createElement('details');details.className='explore';const summary=document.createElement('summary');summary.textContent=labels.explore;details.appendChild(summary);const panel=document.createElement('div');panel.className='explorepanel';deep.forEach(([href,text])=>{const a=document.createElement('a');a.href=href;a.textContent=text;if(location.pathname.endsWith('/'+href)||location.pathname.endsWith(href))a.classList.add('active');panel.appendChild(a)});details.appendChild(panel);desktopLinks.appendChild(details);document.addEventListener('click',event=>{if(details.open&&!details.contains(event.target))details.removeAttribute('open')})}button.setAttribute('type','button');button.setAttribute('aria-label',isHK?'開啟導覽選單':isCN?'打开导航菜单':'Open navigation menu');button.setAttribute('aria-expanded','false');let mobile=document.querySelector('.mobilelinks');if(!mobile){mobile=document.createElement('div');mobile.className='mobilelinks';mobile.id='mobile-navigation';if(desktopLinks){desktopLinks.querySelectorAll(':scope > a').forEach(link=>mobile.appendChild(link.cloneNode(true)))}const heading=document.createElement('div');heading.className='mobileheading';heading.textContent=labels.explore;mobile.appendChild(heading);deep.forEach(([href,text])=>{const a=document.createElement('a');a.href=href;a.textContent=text;if(location.pathname.endsWith('/'+href)||location.pathname.endsWith(href))a.classList.add('active');mobile.appendChild(a)});if(desktopLang){const langs=document.createElement('div');langs.className='mobilelangs';desktopLang.querySelectorAll('a').forEach(link=>langs.appendChild(link.cloneNode(true)));mobile.appendChild(langs)}nav.appendChild(mobile)}button.setAttribute('aria-controls','mobile-navigation');const close=()=>{mobile.classList.remove('open');button.setAttribute('aria-expanded','false')};button.addEventListener('click',()=>{const open=mobile.classList.toggle('open');button.setAttribute('aria-expanded',open?'true':'false')});mobile.querySelectorAll('a').forEach(link=>link.addEventListener('click',close));document.addEventListener('keydown',event=>{if(event.key==='Escape')close()});document.addEventListener('click',event=>{if(mobile.classList.contains('open')&&!nav.contains(event.target))close()});const file=(location.pathname.split('/').pop()||'index.html').toLowerCase();if(file==='index.html'||file==='platform.html'||file===''){const copy=isHK?{k:'架構一覽',h:'一套體驗，四層機構能力。',p:'由教師與學生使用的AI工具開始，向下連接校本知識與評估、治理與模型路由，再由私有基礎設施及持續運維承載。',layers:[['使用者體驗','Chat · Create · Analyze · Voice · Code · Agent','platform.html'],['教育智能','ZYK Knowledge · ZYK Assess','knowledge.html'],['治理與模型服務','ZYK Control · AI Gateway','control.html'],['基礎設施與運維','校內 · 受控託管 · 混合 · 支援','infrastructure.html']]}:isCN?{k:'架构一览',h:'一种体验，四层机构能力。',p:'从教师与学生使用的AI工具开始，向下连接校本知识与评估、治理与模型路由，再由私有基础设施和持续运维承载。',layers:[['用户体验','Chat · Create · Analyze · Voice · Code · Agent','platform.html'],['教育智能','ZYK Knowledge · ZYK Assess','knowledge.html'],['治理与模型服务','ZYK Control · AI Gateway','control.html'],['基础设施与运维','校内 · 受控托管 · 混合 · 支持','infrastructure.html']]}:{k:'Architecture at a glance',h:'One experience. Four institutional layers.',p:'Start with the AI tools teachers and students use, connect them to governed knowledge and assessment, place policy and model routing underneath, then operate the whole environment on private infrastructure with ongoing support.',layers:[['User experience','Chat · Create · Analyze · Voice · Code · Agent','platform.html'],['Education intelligence','ZYK Knowledge · ZYK Assess','knowledge.html'],['Governance & model services','ZYK Control · AI Gateway','control.html'],['Infrastructure & operations','On-prem · Managed · Hybrid · Support','infrastructure.html']]};const hero=document.querySelector('.hero');if(hero&&!document.querySelector('.archstory')){const section=document.createElement('section');section.className='archstory';const wrap=document.createElement('div');wrap.className='wrap';wrap.innerHTML=`<div class="kicker">${copy.k}</div><h2>${copy.h}</h2><p class="archintro">${copy.p}</p>`;const flow=document.createElement('div');flow.className='archflow';copy.layers.forEach((layer,i)=>{const a=document.createElement('a');a.className='archlayer';a.href=layer[2];a.innerHTML=`<span class="archnum">0${i+1}</span><strong>${layer[0]}</strong><small>${layer[1]}</small>`;flow.appendChild(a)});wrap.appendChild(flow);section.appendChild(wrap);hero.insertAdjacentElement('afterend',section)}}if(file==='index.html'||file===''){const journey=isHK?{k:'給學校領導的決策路徑',h:'不是「要不要用AI」，而是如何把AI變成可管理的機構能力。',p:'ZYK的切入點是幫學校把零散使用、風險、技術選擇及能力建設整理成一條可驗證的路徑。',items:[['01','看清現況','教師和學生已經在使用甚麼？哪些資料、帳戶、政策和工作流程正在失去機構可視性？'],['02','選擇第一個值得解決的問題','先選一個教育或營運價值清楚、範圍可控的場景，而不是一次部署所有AI能力。'],['03','建立機構控制','把身份、知識、權限、模型政策、審計和人工覆核放進同一架構，再決定校內、託管或混合部署。'],['04','用證據決定是否擴展','以採用率、品質、風險、成本和支援負擔判斷下一步，而不是因為AI熱潮而擴張。']],cta:'從AI就緒度評估開始',cta2:'查看AI顧問方法'}:isCN?{k:'给学校领导的决策路径',h:'问题不是“要不要用AI”，而是如何把AI变成可管理的机构能力。',p:'ZYK的切入点是帮助学校把零散使用、风险、技术选择和能力建设整理成一条可验证的路径。',items:[['01','看清现状','教师和学生已经在使用什么？哪些数据、账号、政策和工作流正在失去机构可视性？'],['02','选择第一个值得解决的问题','先选择一个教育或运营价值清晰、范围可控的场景，而不是一次部署所有AI能力。'],['03','建立机构控制','把身份、知识、权限、模型政策、审计和人工复核放进同一架构，再决定校内、托管或混合部署。'],['04','用证据决定是否扩展','以采用率、质量、风险、成本和支持负担判断下一步，而不是因为AI热潮而扩张。']],cta:'从AI就绪度评估开始',cta2:'查看AI咨询方法'}:{k:'A decision path for school leaders',h:'The question is not whether AI will be used. It is whether the institution can govern how it is used.',p:'ZYK starts by turning fragmented adoption, risk, technology choices and capability building into a staged decision process that a school can test.',items:[['01','See the current reality','What are teachers and students already using—and where is the institution losing visibility over accounts, data, policy and workflows?'],['02','Choose the first problem worth solving','Start with one bounded educational or operational use case with clear value instead of deploying every possible AI capability at once.'],['03','Create institutional control','Bring identity, knowledge, permissions, model policy, audit and human review into one architecture, then choose on-premise, managed or hybrid deployment.'],['04','Scale only from evidence','Use adoption, quality, risk, cost and support burden to decide the next step rather than expanding simply because AI is fashionable.']],cta:'Start with an AI readiness assessment',cta2:'See the advisory approach'};const main=document.querySelector('main');if(main&&!document.querySelector('.decisionjourney')){const section=document.createElement('section');section.className='section decisionjourney';const wrap=document.createElement('div');wrap.className='wrap';wrap.innerHTML=`<div class="kicker">${journey.k}</div><h2>${journey.h}</h2><p class="intro">${journey.p}</p>`;const grid=document.createElement('div');grid.className='decisiongrid';journey.items.forEach(item=>{const article=document.createElement('article');article.className='decisioncard';article.innerHTML=`<span>${item[0]}</span><h3>${item[1]}</h3><p>${item[2]}</p>`;grid.appendChild(article)});wrap.appendChild(grid);const actions=document.createElement('div');actions.className='cta';actions.innerHTML=`<a class="btn primary" href="services.html">${journey.cta}</a><a class="btn secondary" href="advisory.html">${journey.cta2}</a>`;wrap.appendChild(actions);section.appendChild(wrap);const firstContent=main.querySelector('.archstory')||main.querySelector('.hero');if(firstContent)firstContent.insertAdjacentElement('afterend',section)}}const trustPages=['about.html','investors.html','infrastructure.html','assessment.html','academy.html','training.html','regional.html','partnership.html'];if(trustPages.includes(file)&&!document.querySelector('.statuslegend')){const copy=isHK?{title:'如何閱讀本頁的成熟度表述',intro:'ZYK把已保存的項目證據、目前的產品／服務設計，以及較長期的策略方向分開處理。這可保留完整構想，同時避免把計劃寫成已交付成果。',items:[['evidence','已保存證據','有項目記錄或已恢復材料支持，但公開引用前仍可能需要重新核實狀態、權利或許可。'],['planned','規劃／設計中','屬於目前商業計劃或content-v2架構；不代表已正式推出、售出或部署。'],['future','策略方向','值得保留的較長期延伸；只有在能力、需求、治理及證據成熟後才應升級為正式產品。']]}:isCN?{title:'如何理解本页的成熟度表述',intro:'ZYK把已保存的项目证据、当前产品／服务设计，以及较长期战略方向分开处理。这样既能保留完整构想，也能避免把计划写成已经交付的成果。',items:[['evidence','已保存证据','有项目记录或已恢复材料支持，但公开引用前仍可能需要重新核实状态、权利或许可。'],['planned','规划／设计中','属于当前商业计划或content-v2架构；不代表已经正式推出、售出或部署。'],['future','战略方向','值得保留的长期延伸；只有在能力、需求、治理和证据成熟后才应升级为正式产品。']]}:{title:'How to read maturity claims on this page',intro:'ZYK separates preserved project evidence, current product/service design and longer-term strategic directions. This keeps the full concept visible without presenting plans as delivered outcomes.',items:[['evidence','Preserved evidence','Supported by recovered project records or materials, but status, rights or permission may still need re-verification before public use.'],['planned','Planned / designed','Part of the current business plan or content-v2 architecture; not a claim that it is already launched, sold or deployed.'],['future','Strategic direction','A longer-term extension worth preserving, to be promoted only when capability, demand, governance and evidence justify it.']]};const hero=document.querySelector('.hero');if(hero){const aside=document.createElement('aside');aside.className='statuslegend wrap';aside.innerHTML=`<div class="statushead"><strong>${copy.title}</strong><p>${copy.intro}</p></div><div class="statusitems">${copy.items.map(i=>`<div class="statusitem ${i[0]}"><span>${i[1]}</span><small>${i[2]}</small></div>`).join('')}</div>`;hero.insertAdjacentElement('afterend',aside)}}
if((file==='index.html'||file==='')&&hero&&!document.querySelector('.zyk-media-showcase')){
const sc=isHK?{
badge:'2026 實景展示 · AI 與語言創意工作室',
k:'旗艦工作室與語音簡報',
h:'走進受治理的校園 AI 與創意語言工作室。',
p:'結合 AI 思維夥伴、視覺插畫實驗室、雲端語音廣播、劍橋語法與閱讀精修，以及多玩家知識探險。立即聆聽智能禮賓 Alfred 的 40 秒高管語音導覽。',
audioTitle:'🎩 Alfred 高管語音簡報（Google AI Studio 驅動）',
audioDesc:'由創辦人兼 AI 系統架構師 William Morris 設計，為國際及雙語學校提供安全、可審計、具英倫學術美學的校園 AI 生態。',
pills:['AI 思維夥伴','視覺插畫實驗室','雲端語音廣播','劍橋英語與評估','AI Club 會員工作室'],
cta1:'預約學校試點或演示',
cta2:'申請 AI Club 會員與合作'
}:isCN?{
badge:'2026 实景展示 · AI 与语言创意工作室',
k:'旗舰工作室与语音简报',
h:'走进受治理的校园 AI 与创意语言工作室。',
p:'融合 AI 思维伙伴、视觉插画实验室、云端语音广播、剑桥语法与阅读精修以及互动探索挑战。立即收听智能礼宾 Alfred 的 40 秒高管语音导览。',
audioTitle:'🎩 Alfred 高管语音简报（Google AI Studio 驱动）',
audioDesc:'由创始人兼 AI 系统架构师 William Morris 打造，助力国际与双语学校将零散 AI 工具升级为受机构治理的精品教学与创意中心。',
pills:['AI 思维伙伴','视觉插画实验室','云端语音广播','剑桥英语与评估','AI Club 会员工作室'],
cta1:'预约学校试点或演示',
cta2:'咨询 AI Club 会员与合作'
}:{
badge:'2026 Live Showcase · Creative AI & Language Studio',
k:'Flagship Studio & Audio Briefing',
h:'Inside the Creative AI & Language Studio.',
p:'Where governed institutional AI meets editorial craftsmanship: guided AI thinking partners, visual illustration labs, cloud audio broadcasting, Cambridge mastery, and multiplayer learning expeditions.',
audioTitle:'🎩 Executive Audio Briefing by Alfred',
audioDesc:'Listen to a 40-second overview of how Founder & AI Systems Architect William Morris and ZYK transform fragmented AI tools into a high-craft institutional learning environment.',
pills:['AI Thinking Partner','Visual Illustration Lab','Cloud Audio Broadcast','Cambridge Mastery','AI Club Membership'],
cta1:'Book a School Pilot or Demo',
cta2:'Explore AI Club & Advisory'
};
const sec=document.createElement('section');
sec.className='zyk-media-showcase';
const epLabel=isHK?'🎬 第一集先導片：Mr. Sterling & Ms. Lin（試講前30秒校長在想甚麼？）· 諾德安達內推直通車（最高 ¥12,000）':isCN?'🎬 第一集先导片：Mr. Sterling & Ms. Lin（试讲前30秒校长在想什么？）· 诺德安达内推直通车（最高 ¥12,000）':'🎬 Pilot Ep #1: Mr. Sterling & Ms. Lin (“First 30s of Your Demo Lesson”) · Nord Anglia Referral Fast-Track (Up to ¥12,000)';
const refBtn=isHK?'進入諾德安達內推與 AI 試講中心 →':isCN?'进入诺德安达内推与 AI 试讲中心 →':'Nord Anglia Referrals & AI Demo Lab →';
sec.innerHTML=`<div class="wrap"><div class="kicker">${sc.k}</div><h2>${sc.h}</h2><p class="archintro">${sc.p}</p><div class="zyk-showcase-grid"><div class="zyk-showcase-frame"><span class="zyk-showcase-badge">${sc.badge}</span><video controls preload="metadata" poster="../assets/media/mr-sterling-ref.png" style="display:block;width:100%;height:auto"><source src="../assets/media/pilot-ep1-16x9.mp4" type="video/mp4"></video><div style="padding:12px 16px;font-size:13px;color:var(--cyan);border-top:1px solid var(--line);background:rgba(7,17,31,.92)">${epLabel}</div></div><div class="zyk-audio-card"><h3>${sc.audioTitle}</h3><p>${sc.audioDesc}</p><audio class="zyk-audio-player" controls preload="metadata" src="../assets/media/alfred-executive-briefing.wav"></audio><div class="zyk-pill-list">${sc.pills.map(x=>`<span>${x}</span>`).join('')}</div><div class="cta" style="margin-top:22px"><a class="btn primary" href="referral.html">${refBtn}</a><a class="btn secondary" href="contact.html">${sc.cta1}</a></div></div></div></div>`;
hero.insertAdjacentElement('afterend',sec);
}
if(!document.querySelector('.alfred-Launcher')){
const w=isHK?{
btn:'🎩 詢問 Alfred · ZYK 禮賓',
title:'Alfred · ZYK 機構 AI 禮賓',
sub:'24/7 線上解答 · 直連創辦人團隊',
welcome:'您好！我是 Alfred 🎩，智安雲科（ZYK）與 William Morris 的執行禮賓官。請問您想了解學校 AI 試點、AI Club 創意工作室會員、劍橋／雙語課程 AI 整合，還是預約演示？',
ph:'輸入您的問題（例如：如何開展學校試點？）...',
send:'發送',
chips:[
['AI Club 會員與工作室','AI Club 提供受治理的 AI 思維夥伴、視覺插畫實驗室（Gemini / Imagen）、雲端語音合成與專題項目指導。如需為學校或個人申請體驗，請電郵 aiclub@zykai.net。'],
['學校試點與部署方案','ZYK 支援校內私有、受控雲端及混合部署三種模式，並從 4–6 週的「AI 就緒度評估與界定試點」開始。歡迎發送郵件至 hello@zykai.net 預約架構演示。'],
['劍橋英語與校本評估','我們將校本課程、劍橋評分標準（Rubrics）、聽力廣播與寫作批改融入 ZYK Knowledge 與 ZYK Assess，確保教師擁有最終覆核權。'],
['聯繫創辦人 William Morris','您可以直接發送郵件至 william@zykai.net 或 concierge@zykai.net，我會第一時間為您安排與創辦人 William Morris 的一對一交流！']
]
}:isCN?{
btn:'🎩 询问 Alfred · ZYK 礼宾',
title:'Alfred · ZYK 机构 AI 礼宾',
sub:'24/7 在线解答 · 直连创始人团队',
welcome:'您好！我是 Alfred 🎩，智安云科（ZYK）与 William Morris 的执行礼宾官。请问您想了解学校 AI 试点、AI Club 创意工作室会员、剑桥／双语课程 AI 整合，还是预约演示？',
ph:'输入您的问题（例如：如何开展学校试点？）...',
send:'发送',
chips:[
['AI Club 会员与工作室','AI Club 提供受治理的 AI 思维伙伴、视觉插画实验室（Gemini / Imagen）、云端语音合成与专题项目指导。如需为学校或学生申请体验，请致信 aiclub@zykai.net。'],
['学校试点与部署方案','ZYK 支持校内私有、受控云端与混合部署三种模式，通常从 4–6 周的“AI 就绪度评估与有界试点”起步。欢迎致信 hello@zykai.net 预约架构演示。'],
['剑桥英语与校本评估','我们将校本课程、剑桥评分标准（Rubrics）、云端听力广播与写作反馈融入 ZYK Knowledge 与 ZYK Assess，确保教师保留最终复核权。'],
['联系创始人 William Morris','您可以直接致信 william@zykai.net 或 concierge@zykai.net，我会第一时间为您安排与创始人 William Morris 的一对一交流！']
]
}:{
btn:'🎩 Ask Alfred · ZYK Concierge',
title:'Alfred · ZYK Executive Concierge',
sub:'Instant Architecture, AI Club & Pilot Guidance',
welcome:'Good day! I am Alfred 🎩, Executive Concierge for ZhiAn YunKe (ZYK) and Founder William Morris. How may I assist you with school AI pilots, AI Club & Creative Studio memberships, Cambridge curriculum integration, or strategic partnerships?',
ph:'Ask about pilots, AI Club, governance, or contact...',
send:'Ask',
chips:[
['AI Club & Creative Studio','Our Creative AI & Language Studio combines a guided AI Thinking Partner, Visual Illustration Lab, Cloud Audio Studio, and Cambridge Mastery under strict institutional budget & safety controls. Email aiclub@zykai.net to request access.'],
['School Pilots & Deployment','ZYK supports On-Premise, Managed Cloud, and Hybrid deployments—starting with a scoped 4-to-6 week AI Readiness Assessment & Pilot. Reach us at hello@zykai.net to schedule a live walkthrough.'],
['Cambridge & Curriculum AI','Designed by UK QTS Senior Educator & AI Architect William Morris, ZYK Knowledge and ZYK Assess ground AI marking, listening broadcasts, and guided writing directly in Cambridge rubrics with teacher-in-the-loop review.'],
['Speak with William Morris','You can reach Founder & AI Systems Architect William Morris directly at william@zykai.net or via my desk at concierge@zykai.net. I monitor both desks hourly and will arrange a prompt introduction.']
]
};
const launcher=document.createElement('button');
launcher.className='alfred-Launcher';
launcher.setAttribute('type','button');
launcher.innerHTML=`<span class="alfred-dot"></span><span>${w.btn}</span>`;
const panel=document.createElement('div');
panel.className='alfred-Panel';
panel.innerHTML=`<div class="alfred-Header"><div><strong>${w.title}</strong><small>${w.sub}</small></div><button type="button" class="alfred-Close" aria-label="Close">×</button></div><div class="alfred-Body"><div class="alfred-Msg bot">${w.welcome}</div></div><div class="alfred-Chips"></div><form class="alfred-Form"><input class="alfred-Input" type="text" placeholder="${w.ph}" required><button class="alfred-Send" type="submit">${w.send}</button></form>`;
const bodyEl=panel.querySelector('.alfred-Body');
const chipsEl=panel.querySelector('.alfred-Chips');
const addMsg=(txt,who)=>{const d=document.createElement('div');d.className='alfred-Msg '+who;d.innerHTML=txt;bodyEl.appendChild(d);bodyEl.scrollTop=bodyEl.scrollHeight};
const replyFor=(q)=>{
const s=q.toLowerCase();
if(s.includes('club')||s.includes('studio')||s.includes('image')||s.includes('audio')||s.includes('会员')||s.includes('工作室'))return w.chips[0][1]+` <br><a href="mailto:aiclub@zykai.net?subject=${encodeURIComponent('ZYK AI Club Enquiry')}" style="color:var(--cyan);text-decoration:underline">→ aiclub@zykai.net</a>`;
if(s.includes('pilot')||s.includes('deploy')||s.includes('price')||s.includes('cost')||s.includes('school')||s.includes('试点')||s.includes('部署'))return w.chips[1][1]+` <br><a href="mailto:hello@zykai.net?subject=${encodeURIComponent('ZYK School Pilot Enquiry')}" style="color:var(--cyan);text-decoration:underline">→ hello@zykai.net</a>`;
if(s.includes('cambridge')||s.includes('english')||s.includes('assess')||s.includes('mark')||s.includes('剑桥')||s.includes('评估'))return w.chips[2][1]+` <br><a href="assessment.html" style="color:var(--cyan);text-decoration:underline">→ View ZYK Assess</a>`;
if(s.includes('william')||s.includes('founder')||s.includes('partner')||s.includes('invest')||s.includes('创始人')||s.includes('合作'))return w.chips[3][1]+` <br><a href="mailto:william@zykai.net?subject=${encodeURIComponent('Executive Enquiry for William Morris')}" style="color:var(--cyan);text-decoration:underline">→ william@zykai.net</a>`;
return (isHK?'感謝您的提問！我已為您準備好專屬通道：您可以點擊下方連結直接發送電郵至我的禮賓信箱，我會在每小時巡檢時立即回覆您：':isCN?'感谢您的提问！我已为您准备好专属通道：您可以点击下方链接直接发送邮件至我的礼宾邮箱，我会在每小时巡检时立即回复您：':'Thank you for your question! You can send that directly to my executive concierge desk with one click below—I check and respond every hour:')+` <br><a href="mailto:concierge@zykai.net?subject=${encodeURIComponent('ZYK Concierge Question: '+q.slice(0,50))}&body=${encodeURIComponent(q)}" style="color:var(--cyan);font-weight:700;text-decoration:underline">✉ Send to concierge@zykai.net →</a>`;
};
w.chips.forEach(([label,ans])=>{
const b=document.createElement('button');
b.type='button';
b.className='alfred-Chip';
b.textContent=label;
b.addEventListener('click',()=>{addMsg(label,'user');setTimeout(()=>addMsg(ans,'bot'),220)});
chipsEl.appendChild(b);
});
panel.querySelector('.alfred-Form').addEventListener('submit',e=>{
e.preventDefault();
const inp=panel.querySelector('.alfred-Input');
const val=inp.value.trim();
if(!val)return;
addMsg(val.replace(/[<>]/g,''),'user');
inp.value='';
setTimeout(()=>addMsg(replyFor(val),'bot'),260);
});
launcher.addEventListener('click',()=>panel.classList.toggle('open'));
panel.querySelector('.alfred-Close').addEventListener('click',()=>panel.classList.remove('open'));
document.body.appendChild(launcher);
document.body.appendChild(panel);
}});