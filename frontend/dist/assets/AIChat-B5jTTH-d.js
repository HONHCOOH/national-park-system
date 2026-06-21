import{_ as Q,k as r,e as g,g as e,s as o,a as s,f as i,d as R,F as C,l as M,v as U,u as q,p as K,t as v,m as l,r as _,E as O,n as $,i as W,b as L}from"./index-ix376XYL.js";import{c as j}from"./index-D5tQXHu0.js";const G={class:"chat-page"},J={class:"dashboard-card chat-container"},P={class:"card-title"},X={key:0,class:"chat-welcome"},Y={class:"welcome-icon"},Z={class:"message-avatar"},nn={class:"message-content"},sn=["innerHTML"],tn={class:"message-time"},en={class:"chat-input"},on={class:"dashboard-card",style:{"margin-bottom":"12px"}},ln={class:"card-title"},an={class:"quick-questions"},rn={class:"dashboard-card"},un={class:"card-title"},cn={class:"about-ai"},dn={style:{"margin-top":"8px",color:"#999","font-size":"12px"}},gn={__name:"AIChat",setup(_n){const c=_([]),p=_(""),d=_(!1),m=_(null),T=_("本地/Qwen"),A=["分析当前系统的生态健康状况","哪些区域的火灾风险最高？","如何优化巡护资源分配？","当前有哪些活跃预警？","建议加强哪些方面的生态监测？","评估气候变化对园区的影响"];function h(){const t=p.value.trim();!t||d.value||(y(t),p.value="")}function z(t){y(t)}async function y(t){var n;c.value.push({role:"user",content:t,time:new Date().toLocaleTimeString()}),d.value=!0,k();try{const f=await j(t);c.value.push({role:"ai",content:((n=f.data)==null?void 0:n.reply)||"抱歉，AI回复异常。",time:new Date().toLocaleTimeString()})}catch{c.value.push({role:"ai",content:D(t),time:new Date().toLocaleTimeString()}),O.warning("AI服务未连接，使用本地规则回复")}d.value=!1,k()}function D(t){return t.includes("火灾")||t.includes("火险")?`【火灾风险分析报告】

基于多方数据分析，当前系统火灾风险评估如下：

1. <strong>高风险区域</strong>：祁连山草甸区（风险评分 82.3，极高风险），主要原因是干旱指数高（88.2）、风速大（22.1 m/s）、植被类型为易燃草原。

2. <strong>中高风险区域</strong>：大熊猫栖息地（风险评分 68.5，高风险），气温34.2°C、湿度仅25.3%。

3. <strong>低风险区域</strong>：海南热带雨林（风险评分 18.7）、三江源核心区（42.1）。

<strong>建议措施：</strong>
• 立即向祁连山草甸区增派巡护力量
• 启动无人机24小时连续监测
• 检查防火隔离带完整性
• 提前预置灭火装备至储备点`:t.includes("生态")||t.includes("健康")?`【生态健康分析报告】

当前系统监测8个国家公园区域，整体生态健康状况良好：

1. <strong>平均健康评分</strong>：78.5分（满分100），处于健康水平。

2. <strong>最佳区域</strong>：海南热带雨林（90分）、大熊猫栖息地（88分）、武夷山实验区（85分）

3. <strong>需关注区域</strong>：祁连山草甸区（71分），植被覆盖度有下降趋势；可可西里荒野区（74分），物种多样性指数偏低

4. <strong>异常指标</strong>：检测到2处异常，主要在草甸区植被退化和湿地水位变化。

<strong>建议措施：</strong>
• 加强祁连山草甸区生态修复
• 在可可西里增设红外相机监测点
• 关注气候变化对湿地的影响`:t.includes("资源")||t.includes("调度")||t.includes("巡护")?`【资源调度优化建议】

根据当前各区域风险评估和资源部署情况：

1. <strong>资源缺口</strong>：
   • 三江源核心区：当前2队，建议5队（面积大、保护级别高）
   • 可可西里荒野区：当前1队，建议4队
   • 东北虎豹栖息地：当前2队，建议4队

2. <strong>无人机调度</strong>：建议将无人机群的40%部署至高火险区域，30%覆盖核心保护区，30%用于常规巡护。

3. <strong>巡护路线优化</strong>：基于风险等级动态调整路线，高火险期增加夜间巡逻班次。

4. <strong>游客管理</strong>：监测到部分区域游客流量接近承载上限，建议在高峰时段实施预约限流。`:t.includes("预警")||t.includes("风险")?`【风险预警状态】

当前系统共有4个活跃预警：

1. 🔴 <strong>红色预警</strong>（1个）：祁连山草甸极高火险
2. 🟠 <strong>橙色预警</strong>（1个）：大熊猫栖息地高温干旱火险
3. 🟡 <strong>黄色预警</strong>（1个）：松材线虫病扩散预警
4. 🔵 <strong>蓝色预警</strong>（1个）：游客违规进入核心区

<strong>建议优先处理红色和橙色预警</strong>，已生成相应应急预案。`:`【综合回复】

关于"${t}"的分析：

这是一个关于国家公园管理的专业问题。基于系统中的人工智能分析引擎，建议从以下几个方面考虑：

1. 生态数据综合分析
2. 风险评估与预警机制
3. 资源调度优化
4. 应急预案准备

如需要更详细的分析，请提供具体区域名称或更精确的问题描述。`}function V(t){return t.replace(/\n/g,"<br/>")}function k(){$(()=>{m.value&&(m.value.scrollTop=m.value.scrollHeight)})}return(t,n)=>{const f=l("ChatDotRound"),u=l("el-icon"),I=l("el-tag"),F=l("Monitor"),B=l("UserFilled"),S=l("el-button"),x=l("el-input"),b=l("el-col"),N=l("Lightning"),E=l("InfoFilled"),H=l("el-row");return r(),g("div",G,[e(H,{gutter:16},{default:o(()=>[e(b,{span:16},{default:o(()=>[s("div",J,[s("div",P,[e(u,null,{default:o(()=>[e(f)]),_:1}),n[2]||(n[2]=i(" AI决策助手 ",-1)),e(I,{size:"small",type:"success",style:{"margin-left":"8px"}},{default:o(()=>[...n[1]||(n[1]=[i("LLM 驱动",-1)])]),_:1})]),s("div",{class:"chat-messages",ref_key:"chatMessages",ref:m},[c.value.length===0?(r(),g("div",X,[s("div",Y,[e(u,{size:48},{default:o(()=>[e(f)]),_:1})]),n[3]||(n[3]=s("h3",null,"国家公园智能决策助手",-1)),n[4]||(n[4]=s("p",null,"我可以帮您分析生态数据、评估火灾风险、制定应急预案、优化资源调度。请在下方输入您的问题。",-1))])):R("",!0),(r(!0),g(C,null,M(c.value,(a,w)=>(r(),g("div",{key:w,class:W(["chat-message",a.role])},[s("div",Z,[a.role==="ai"?(r(),L(u,{key:0,size:20},{default:o(()=>[e(F)]),_:1})):(r(),L(u,{key:1,size:20},{default:o(()=>[e(B)]),_:1}))]),s("div",nn,[s("div",{class:"message-text",innerHTML:V(a.content)},null,8,sn),s("div",tn,v(a.time),1)])],2))),128))],512),s("div",en,[e(x,{modelValue:p.value,"onUpdate:modelValue":n[0]||(n[0]=a=>p.value=a),placeholder:"输入您的问题，例如：分析当前火灾风险最高的区域，并给出应对建议",onKeyup:U(h,["enter"]),disabled:d.value,size:"large"},{suffix:o(()=>[e(S,{type:"primary",icon:q(K),onClick:h,loading:d.value},{default:o(()=>[...n[5]||(n[5]=[i(" 发送 ",-1)])]),_:1},8,["icon","loading"])]),_:1},8,["modelValue","disabled"])])])]),_:1}),e(b,{span:8},{default:o(()=>[s("div",on,[s("div",ln,[e(u,null,{default:o(()=>[e(N)]),_:1}),n[6]||(n[6]=i(" 快捷提问",-1))]),s("div",an,[(r(),g(C,null,M(A,a=>e(I,{key:a,class:"quick-tag",onClick:w=>z(a),effect:"plain",type:"info"},{default:o(()=>[i(v(a),1)]),_:2},1032,["onClick"])),64))])]),s("div",rn,[s("div",un,[e(u,null,{default:o(()=>[e(E)]),_:1}),n[7]||(n[7]=i(" 关于AI助手",-1))]),s("div",cn,[n[10]||(n[10]=s("p",null,"本AI助手基于大语言模型，整合了以下能力：",-1)),n[11]||(n[11]=s("ul",null,[s("li",null,"生态监测数据分析"),s("li",null,"火灾风险评估与建议"),s("li",null,"应急方案生成"),s("li",null,"资源调度优化"),s("li",null,"自然语言交互查询")],-1)),s("p",dn,[i(" 当前使用 "+v(T.value)+" 模型",1),n[8]||(n[8]=s("br",null,null,-1)),n[9]||(n[9]=i(" 支持 OpenA I/Ollama/DeepSeek 等接口 ",-1))]),n[12]||(n[12]=s("p",{style:{color:"#999","font-size":"11px"}}," 数据来源：系统模拟数据库 + 生态学知识库 ",-1))])])]),_:1})]),_:1})])}}},fn=Q(gn,[["__scopeId","data-v-4d367748"]]);export{fn as default};
