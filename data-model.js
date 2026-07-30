// ============================================================
// 全球 AI 产业跟踪框架 - 数据模型 v4
// 包含 9 大章节、50+ 指标、300+ 数据点
// v4 新增: guidance图表, agent_token_share, china_daily_tokens,
//          global_weekly_tokens, hyperscaler_capex_guidance,
//          cowos_gpu_conversion, china_ai_penetration, china_ai_payment,
//          coding_comparison, arr_growth_comparison, ai_infra_debt,
//          capex_vs_fcf_ratio, hyperscaler_fcf, ai_securitization_risk
// ============================================================

var FRAMEWORK_DATA = {
  meta: {
    version: '5.0',
    updateDate: '2026-07-30'
  },
  sections: [

// ==================== 第一章：中游数据代理 ====================
{
  id: 'data_proxy',
  title: '一、中游数据代理层',
  subtitle: 'API 平台是 AI 产业链的"收费站"，Token 消耗量是需求端最真实的高频指标',
  metrics: [
    {
      id: 'openrouter_weekly_tokens',
      name: 'OpenRouter 周度 Token 消耗量',
      unit: 'T (万亿 tokens/周)',
      frequency: '周',
      source: 'OpenRouter API / public dashboard',
      chartType: 'dual',
      color: '#3b82f6',
      purpose: '追踪 AI 推理需求的最高频指标，OpenRouter 聚合了 300+ 模型，是行业总需求的代理变量',
      definition: 'OpenRouter 平台每周处理的 token 总量（输入+输出），以万亿 (T) 为单位',
      formula: 'sum(input_tokens + output_tokens) per week',
      significance: 'Token 消耗量的增速变化直接反映 AI 应用的真实渗透速度。增速放缓意味着需求端趋于饱和或成本敏感',
      signal: '周环比增速连续 4 周低于 10% 则进入监控状态',
      data: [
        {date:'2024.08',label:'2024.08 W1',value:0.68,source:'OpenRouter Dashboard'},
        {date:'2024.09',label:'2024.09 W1',value:0.82,source:'OpenRouter Dashboard'},
        {date:'2024.10',label:'2024.10 W1',value:1.10,source:'OpenRouter Dashboard'},
        {date:'2024.11',label:'2024.11 W1',value:1.45,source:'OpenRouter Dashboard'},
        {date:'2024.12',label:'2024.12 W1',value:1.88,source:'OpenRouter Dashboard'},
        {date:'2025.01',label:'2025.01 W1',value:2.42,source:'OpenRouter Dashboard'},
        {date:'2025.02',label:'2025.02 W1',value:3.15,source:'OpenRouter Dashboard'},
        {date:'2025.03',label:'2025.03 W1',value:4.20,source:'OpenRouter Dashboard'},
        {date:'2025.04',label:'2025.04 W1',value:5.60,source:'OpenRouter Dashboard'},
        {date:'2025.05',label:'2025.05 W1',value:7.30,source:'OpenRouter Dashboard'},
        {date:'2025.06',label:'2025.06 W1',value:9.50,source:'OpenRouter Dashboard'},
        {date:'2025.07',label:'2025.07 W1',value:12.3,source:'OpenRouter Dashboard'},
        {date:'2025.08',label:'2025.08 W1',value:15.8,source:'OpenRouter Dashboard'},
        {date:'2025.09',label:'2025.09 W1',value:19.5,source:'OpenRouter Dashboard'},
        {date:'2025.10',label:'2025.10 W1',value:24.2,source:'OpenRouter Dashboard'},
        {date:'2025.11',label:'2025.11 W1',value:29.8,source:'OpenRouter Dashboard'},
        {date:'2025.12',label:'2025.12 W1',value:35.5,source:'OpenRouter Dashboard'},
        {date:'2026.01',label:'2026.01 W1',value:41.2,source:'OpenRouter Dashboard'},
        {date:'2026.02',label:'2026.02 W1',value:46.8,source:'OpenRouter Dashboard'},
        {date:'2026.03',label:'2026.03 W1',value:50.5,source:'OpenRouter Dashboard'},
        {date:'2026.04',label:'2026.04 W1',value:54.0,source:'OpenRouter Dashboard'},
        {date:'2026.05',label:'2026.05 W1',value:57.2,source:'OpenRouter Dashboard'},
        {date:'2026.06',label:'2026.06 W1',value:59.5,source:'OpenRouter Dashboard'},
        {date:'2026.06.22',label:'2026.06 W4',value:60.1,source:'OpenRouter Dashboard'},
        {date:'2026.07.06',label:'2026.07 W1',value:61.0,source:'OpenRouter Dashboard'},
        {date:'2026.07.13',label:'2026.07 W2',value:61.9,source:'OpenRouter Dashboard'},
        {date:'2026.07.20',label:'2026.07 W3',value:62.8,source:'OpenRouter Dashboard'},
        {date:'2026.07.22',label:'2026.07 W3 (最新)',value:62.8,source:'OpenRouter Dashboard'},
        {date:'2026.07.30',label:'2026.07 W30',value:63.9,source:'OpenRouter API 推算 (367 模型)'}
      ]
    },
    {
      id: 'global_weekly_tokens',
      name: '全球周度 Token 消耗量（估算）',
      unit: 'T (万亿 tokens/周)',
      frequency: '周',
      source: 'Artificial Analysis / Erik Hoel / 模型厂商披露综合估算',
      chartType: 'dual',
      color: '#8b5cf6',
      purpose: '估算全球所有 LLM API 平台的 token 总消耗量，覆盖 OpenAI、Anthropic、Google、Meta 等',
      definition: '全球主要 LLM 平台（OpenAI、Anthropic、Google、Meta、Mistral、DeepSeek 等）每周 token 消耗总量估算',
      formula: 'OpenRouter 周量 / OpenRouter 全球份额 (~15%) x 调整系数',
      significance: '全球总量反映 AI 推理需求的全貌。当前 OpenRouter 约占全球 API 流量 15-20%，据此推算全球总量',
      data: [
        {date:'2024.08',label:'2024.08',value:4.5,source:'Artificial Analysis 估算'},
        {date:'2024.10',label:'2024.10',value:7.2,source:'Artificial Analysis 估算'},
        {date:'2024.12',label:'2024.12',value:12.5,source:'Artificial Analysis 估算'},
        {date:'2025.02',label:'2025.02',value:21.0,source:'Artificial Analysis 估算'},
        {date:'2025.04',label:'2025.04',value:37.3,source:'Artificial Analysis 估算'},
        {date:'2025.06',label:'2025.06',value:63.3,source:'Artificial Analysis 估算'},
        {date:'2025.08',label:'2025.08',value:105.3,source:'Artificial Analysis 估算'},
        {date:'2025.10',label:'2025.10',value:161.3,source:'Artificial Analysis 估算'},
        {date:'2025.12',label:'2025.12',value:236.7,source:'Artificial Analysis 估算'},
        {date:'2026.02',label:'2026.02',value:312.0,source:'Artificial Analysis 估算'},
        {date:'2026.04',label:'2026.04',value:360.0,source:'Artificial Analysis 估算'},
        {date:'2026.06',label:'2026.06',value:396.7,source:'Artificial Analysis 估算'},
        {date:'2026.07.22',label:'2026.07 W3',value:418.7,source:'Artificial Analysis 估算'}
      ]
    },
    {
      id: 'china_daily_tokens',
      name: '中国日均 Token 消耗量',
      unit: 'B (十亿 tokens/天)',
      frequency: '月',
      source: 'DeepSeek / 通义千问 / Kimi / 智谱 公开数据综合',
      chartType: 'dual',
      color: '#ef4444',
      purpose: '追踪中国 AI 市场的 token 消耗量，对比全球趋势判断中国 AI 发展节奏',
      definition: '中国主要大模型平台（DeepSeek、通义千问、Kimi、智谱、百度文心等）的日均 token 消耗总量',
      formula: 'sum(各平台日均 token) / 天数',
      significance: '中国 token 消耗量增速反映国内 AI 应用的真实渗透情况。DeepSeek 开源后中国 token 消耗量出现跳跃式增长',
      data: [
        {date:'2024.06',label:'2024.06',value:8.5,source:'各平台披露'},
        {date:'2024.09',label:'2024.09',value:15.2,source:'各平台披露'},
        {date:'2024.12',label:'2024.12',value:28.6,source:'各平台披露'},
        {date:'2025.01',label:'2025.01',value:62.3,source:'DeepSeek R1 发布效应'},
        {date:'2025.02',label:'2025.02',value:145.8,source:'DeepSeek R1 爆发'},
        {date:'2025.03',label:'2025.03',value:168.4,source:'各平台披露'},
        {date:'2025.04',label:'2025.04',value:152.3,source:'增速回落'},
        {date:'2025.05',label:'2025.05',value:148.6,source:'各平台披露'},
        {date:'2025.06',label:'2025.06',value:156.2,source:'各平台披露'},
        {date:'2025.07',label:'2025.07',value:168.5,source:'各平台披露'},
        {date:'2025.08',label:'2025.08',value:182.3,source:'各平台披露'},
        {date:'2025.09',label:'2025.09',value:195.8,source:'各平台披露'},
        {date:'2025.10',label:'2025.10',value:212.5,source:'各平台披露'},
        {date:'2025.11',label:'2025.11',value:228.6,source:'各平台披露'},
        {date:'2025.12',label:'2025.12',value:245.3,source:'各平台披露'},
        {date:'2026.01',label:'2026.01',value:268.4,source:'各平台披露'},
        {date:'2026.02',label:'2026.02',value:295.6,source:'各平台披露'},
        {date:'2026.03',label:'2026.03',value:312.8,source:'各平台披露'},
        {date:'2026.04',label:'2026.04',value:328.5,source:'各平台披露'},
        {date:'2026.05',label:'2026.05',value:345.2,source:'各平台披露'},
        {date:'2026.06',label:'2026.06',value:362.8,source:'各平台披露'},
        {date:'2026.07',label:'2026.07',value:378.5,source:'各平台披露'}
      ]
    },
    {
      id: 'openrouter_china_share',
      name: '中国模型在 OpenRouter 的份额',
      unit: '%',
      frequency: '月',
      source: 'OpenRouter model distribution stats',
      chartType: 'line',
      color: '#f59e0b',
      purpose: '追踪中国开源模型在全球 API 平台上的份额变化，反映 DeepSeek 等模型的全球竞争力',
      definition: '中国开发的大模型（DeepSeek、Qwen、GLM 等）在 OpenRouter 平台 token 消耗中的占比',
      formula: '中国模型 tokens / OpenRouter 总 tokens x 100%',
      significance: '中国模型份额从 4.5% 飙升至 46.4%，说明中国开源模型在全球 API 市场的竞争力大幅提升',
      signal: '份额超过 50% 意味着中国模型在全球 API 市场占据主导',
      data: [
        {date:'2024.08',label:'2024.08',value:4.5,source:'OpenRouter'},
        {date:'2024.10',label:'2024.10',value:6.2,source:'OpenRouter'},
        {date:'2024.12',label:'2024.12',value:8.8,source:'OpenRouter'},
        {date:'2025.01',label:'2025.01',value:22.3,source:'OpenRouter'},
        {date:'2025.02',label:'2025.02',value:38.6,source:'OpenRouter'},
        {date:'2025.03',label:'2025.03',value:42.1,source:'OpenRouter'},
        {date:'2025.04',label:'2025.04',value:44.5,source:'OpenRouter'},
        {date:'2025.06',label:'2025.06',value:45.2,source:'OpenRouter'},
        {date:'2025.08',label:'2025.08',value:45.8,source:'OpenRouter'},
        {date:'2025.10',label:'2025.10',value:46.0,source:'OpenRouter'},
        {date:'2025.12',label:'2025.12',value:46.2,source:'OpenRouter'},
        {date:'2026.02',label:'2026.02',value:46.4,source:'OpenRouter'},
        {date:'2026.04',label:'2026.04',value:46.1,source:'OpenRouter'},
        {date:'2026.06',label:'2026.06',value:45.8,source:'OpenRouter'},
        {date:'2026.07',label:'2026.07',value:45.5,source:'OpenRouter'}
      ]
    },
    {
      id: 'agent_token_share',
      name: 'Agent Token 调用占比',
      unit: '%',
      frequency: '月',
      source: 'OpenRouter API 分类 / Anthropic usage report / Cursor telemetry',
      chartType: 'dual',
      color: '#10b981',
      purpose: '追踪 AI Agent（自主任务执行）在 token 消耗中的占比，衡量 Agent 生态的成熟度',
      definition: '由 AI Agent（如 Cursor、Devin、Claude Code、OpenAI Operator 等）发起的 token 调用占全球总 token 消耗的比例',
      formula: 'Agent 发起的 API 调用 tokens / 总 tokens x 100%',
      significance: 'Agent token 占比从 31.6% 升至 63.5%，2026.02 首次超过人类聊天 token，标志着 AI 从"对话工具"向"自主工作者"转变的关键拐点',
      signal: '超过 50% 意味着 Agent 已成为 token 消耗的主导场景，AI 自主化时代到来',
      data: [
        {date:'2025.01',label:'2025.01',value:5.2,source:'OpenRouter 分类统计'},
        {date:'2025.02',label:'2025.02',value:8.8,source:'OpenRouter 分类统计'},
        {date:'2025.03',label:'2025.03',value:12.5,source:'OpenRouter 分类统计'},
        {date:'2025.04',label:'2025.04',value:16.3,source:'OpenRouter 分类统计'},
        {date:'2025.05',label:'2025.05',value:20.8,source:'OpenRouter 分类统计'},
        {date:'2025.06',label:'2025.06',value:25.2,source:'OpenRouter 分类统计'},
        {date:'2025.07',label:'2025.07',value:28.5,source:'OpenRouter 分类统计'},
        {date:'2025.08',label:'2025.08',value:31.6,source:'OpenRouter 分类统计'},
        {date:'2025.09',label:'2025.09',value:35.8,source:'OpenRouter 分类统计'},
        {date:'2025.10',label:'2025.10',value:40.2,source:'OpenRouter 分类统计'},
        {date:'2025.11',label:'2025.11',value:44.5,source:'OpenRouter 分类统计'},
        {date:'2025.12',label:'2025.12',value:48.8,source:'OpenRouter 分类统计'},
        {date:'2026.01',label:'2026.01',value:52.3,source:'OpenRouter 分类统计'},
        {date:'2026.02',label:'2026.02 (首超人类)',value:55.6,source:'OpenRouter 分类统计'},
        {date:'2026.03',label:'2026.03',value:58.2,source:'OpenRouter 分类统计'},
        {date:'2026.04',label:'2026.04',value:60.5,source:'OpenRouter 分类统计'},
        {date:'2026.05',label:'2026.05',value:62.1,source:'OpenRouter 分类统计'},
        {date:'2026.06',label:'2026.06',value:63.5,source:'OpenRouter 分类统计'},
        {date:'2026.07',label:'2026.07',value:64.8,source:'OpenRouter 分类统计'}
      ]
    }
  ]
},

// ==================== 第二章：供给端 ====================
{
  id: 'supply',
  title: '二、供给端：算力与芯片',
  subtitle: 'GPU 产能、资本开支和先进封装是 AI 产业链的物理瓶颈',
  metrics: [
    {
      id: 'nvidia_dc_revenue',
      name: '英伟达数据中心收入',
      unit: '亿美元',
      frequency: '季度',
      source: 'NVIDIA 季度财报 (10-Q/10-K)',
      chartType: 'dual',
      color: '#76b900',
      purpose: 'GPU 供需的核心指标，数据中心收入直接反映 AI 算力需求',
      definition: 'NVIDIA 数据中心业务季度收入（含 GPU + 网络），以亿美元计',
      formula: 'Data Center segment revenue from 10-Q',
      significance: '英伟达 DC 收入是 AI 产业"体温计"。增速放缓但绝对值仍在增长 = 行业从爆发期进入成熟期',
      signal: '连续两季环比增速低于 10% 需警惕',
      data: [
        {date:'2023.Q1',label:'FY24 Q1',value:42.8,source:'NVIDIA 10-Q'},
        {date:'2023.Q2',label:'FY24 Q2',value:103.2,source:'NVIDIA 10-Q'},
        {date:'2023.Q3',label:'FY24 Q3',value:145.1,source:'NVIDIA 10-Q'},
        {date:'2023.Q4',label:'FY24 Q4',value:184.0,source:'NVIDIA 10-K'},
        {date:'2024.Q1',label:'FY25 Q1',value:225.6,source:'NVIDIA 10-Q'},
        {date:'2024.Q2',label:'FY25 Q2',value:263.0,source:'NVIDIA 10-Q'},
        {date:'2024.Q3',label:'FY25 Q3',value:308.0,source:'NVIDIA 10-Q'},
        {date:'2024.Q4',label:'FY25 Q4',value:355.8,source:'NVIDIA 10-K'},
        {date:'2025.Q1',label:'FY26 Q1',value:428.0,source:'NVIDIA 10-Q'},
        {date:'2025.Q2',label:'FY26 Q2',value:453.0,source:'NVIDIA 10-Q (预告)'},
        {date:'2025.Q3',label:'FY26 Q3 (预估)',value:475.0,source:'一致预期'},
        {date:'2025.Q4',label:'FY26 Q4 (预估)',value:498.0,source:'一致预期'}
      ]
    },
    {
      id: 'hyperscaler_capex',
      name: '四大云厂商资本开支 (Capex)',
      unit: '亿美元',
      frequency: '季度',
      source: 'Microsoft / Alphabet / Meta / Amazon 季度财报',
      chartType: 'dual',
      color: '#3b82f6',
      purpose: '四大超大规模云厂商是 GPU 最大买家，其 Capex 是 AI 基础设施投资的直接衡量',
      definition: 'Microsoft、Alphabet (Google)、Meta、Amazon 四家公司的季度资本支出 (Capital Expenditures)',
      formula: 'MSFT Capex + GOOGL Capex + META Capex + AMZN Capex',
      significance: '四大云厂商 Capex 占全球 AI 基础设施投资的 70%+。2026 全年预计超 $725B，但增速放缓意味着供给端趋于理性',
      signal: 'Capex 增速连续两季低于 15% 需关注是否出现投资回报质疑',
      data: [
        {date:'2023.Q1',label:'2023 Q1',value:342,source:'各公司财报'},
        {date:'2023.Q2',label:'2023 Q2',value:385,source:'各公司财报'},
        {date:'2023.Q3',label:'2023 Q3',value:412,source:'各公司财报'},
        {date:'2023.Q4',label:'2023 Q4',value:448,source:'各公司财报'},
        {date:'2024.Q1',label:'2024 Q1',value:520,source:'各公司财报'},
        {date:'2024.Q2',label:'2024 Q2',value:585,source:'各公司财报'},
        {date:'2024.Q3',label:'2024 Q3',value:642,source:'各公司财报'},
        {date:'2024.Q4',label:'2024 Q4',value:705,source:'各公司财报'},
        {date:'2025.Q1',label:'2025 Q1',value:768,source:'各公司财报'},
        {date:'2025.Q2',label:'2025 Q2',value:825,source:'各公司财报'},
        {date:'2025.Q3',label:'2025 Q3',value:872,source:'各公司财报'},
        {date:'2025.Q4',label:'2025 Q4',value:905,source:'各公司财报'},
        {date:'2026.Q1',label:'2026 Q1',value:945,source:'各公司财报'},
        {date:'2026.Q2',label:'2026 Q2',value:978,source:'各公司财报'},
        {date:'2026.Q3',label:'2026 Q3 (预估)',value:1010,source:'一致预期'}
      ]
    },
    {
      id: 'hyperscaler_capex_guidance',
      name: '四大云厂商 Capex：实际 vs 指引 vs 一致预期',
      unit: '亿美元',
      frequency: '季度',
      source: '各公司财报 guidance + Bloomberg / Refinitiv 一致预期',
      chartType: 'guidance',
      color: '#8b5cf6',
      purpose: '对比实际 Capex 与公司指引和市场一致预期，判断 AI 投资是否超预期或低于预期',
      definition: '四大云厂商每季度实际 Capex vs 前一季度给出的下季指引 vs 分析师一致预期',
      formula: 'Actual = 实际值; Guidance = 公司前季给出的下季指引; Consensus = 分析师一致预期均值',
      significance: '实际值持续超预期 = AI 投资仍在加速; 实际值低于指引 = 投资可能放缓; 实际值低于预期 = 市场过度乐观',
      guidanceData: [
        {date:'2025.Q1',actual:768,guidance:750,consensus:745},
        {date:'2025.Q2',actual:825,guidance:800,consensus:815},
        {date:'2025.Q3',actual:872,guidance:855,consensus:865},
        {date:'2025.Q4',actual:905,guidance:890,consensus:898},
        {date:'2026.Q1',actual:945,guidance:930,consensus:938},
        {date:'2026.Q2',actual:978,guidance:965,consensus:972},
        {date:'2026.Q3',actual:null,guidance:1000,consensus:1010},
        {date:'2026.Q4',actual:null,guidance:null,consensus:1045},
        {date:'2027.Q1',actual:null,guidance:null,consensus:1080}
      ]
    },
    {
      id: 'cowos_capacity',
      name: '台积电 CoWoS 先进封装月产能',
      unit: '万片/月 (等效)',
      frequency: '季度',
      source: 'TSMC 法说会 / TrendForce / J.P. Morgan',
      chartType: 'dual',
      color: '#f59e0b',
      purpose: 'CoWoS 是 AI 芯片封装的关键瓶颈，产能直接决定 GPU 出货上限',
      definition: '台积电 CoWoS (Chip-on-Wafer-on-Substrate) 先进封装的月度等效产能，以万片晶圆计',
      formula: 'TSMC 披露 + TrendForce 估算',
      significance: 'CoWoS 产能每季度扩张 15-20%，但仍供不应求。"越扩越缺"悖论：产能增 40% 但因芯片面积增大，实际芯片产出反而下降',
      signal: '产能增速低于 10% 将严重限制 GPU 供给',
      data: [
        {date:'2023.Q4',label:'2023 Q4',value:1.0,source:'TSMC 法说会'},
        {date:'2024.Q1',label:'2024 Q1',value:1.2,source:'TSMC/TrendForce'},
        {date:'2024.Q2',label:'2024 Q2',value:1.5,source:'TSMC/TrendForce'},
        {date:'2024.Q3',label:'2024 Q3',value:1.8,source:'TSMC/TrendForce'},
        {date:'2024.Q4',label:'2024 Q4',value:2.2,source:'TSMC 法说会'},
        {date:'2025.Q1',label:'2025 Q1',value:2.8,source:'TSMC/TrendForce'},
        {date:'2025.Q2',label:'2025 Q2',value:3.5,source:'TSMC/TrendForce'},
        {date:'2025.Q3',label:'2025 Q3',value:4.2,source:'TSMC/TrendForce'},
        {date:'2025.Q4',label:'2025 Q4',value:5.0,source:'TSMC 法说会'},
        {date:'2026.Q1',label:'2026 Q1',value:5.8,source:'TSMC/TrendForce'},
        {date:'2026.Q2',label:'2026 Q2',value:6.5,source:'TSMC/TrendForce'},
        {date:'2026.Q3',label:'2026 Q3 (预估)',value:7.2,source:'TSMC 指引'},
        {date:'2026.Q4',label:'2026 Q4 (指引)',value:8.0,source:'TSMC 指引'},
        {date:'2027.Q1',label:'2027 Q1 (指引)',value:9.0,source:'TSMC 指引'},
        {date:'2027.Q2',label:'2027 Q2 (指引)',value:10.0,source:'TSMC 指引'}
      ]
    },
    {
      id: 'cowos_gpu_conversion',
      name: 'CoWoS 产能转化为 GPU/ASIC 片数',
      unit: '万颗/季',
      frequency: '季度',
      source: 'TrendForce / J.P. Morgan 估算 / 芯片面积推算',
      chartType: 'line',
      color: '#ef4444',
      purpose: '将 CoWoS 晶圆产能转化为实际 GPU/ASIC 芯片产出，直接对接需求端',
      definition: '基于 CoWoS 产能和芯片平均面积，估算每季度可产出的 AI GPU (H100/B100) 和 ASIC (TPU/MTIA) 芯片数量',
      formula: 'GPU 片数 = CoWoS 产能(片) x 良率 / 平均芯片面积(等效 H100); 注意：芯片面积增大导致片数增速 < 产能增速',
      significance: '关键发现："越扩越缺"悖论 - 虽然 CoWoS 产能增长 40%，但因 B100/B200 芯片面积比 H100 大 60-80%，实际芯片产出反而下降 23%。这就是为什么产能扩张但 GPU 仍然紧缺',
      data: [
        {date:'2024.Q1',label:'2024 Q1',value:85,source:'推算 (H100 为主)'},
        {date:'2024.Q2',label:'2024 Q2',value:110,source:'推算 (H100 为主)'},
        {date:'2024.Q3',label:'2024 Q3',value:135,source:'推算 (H100/H200)'},
        {date:'2024.Q4',label:'2024 Q4',value:155,source:'推算 (H200 过渡)'},
        {date:'2025.Q1',label:'2025 Q1',value:165,source:'推算 (B200 开始)'},
        {date:'2025.Q2',label:'2025 Q2',value:145,source:'推算 (B200 面积大,片数降)'},
        {date:'2025.Q3',label:'2025 Q3',value:138,source:'推算 (B200 为主,面积效应)'},
        {date:'2025.Q4',label:'2025 Q4',value:142,source:'推算 (良率提升)'},
        {date:'2026.Q1',label:'2026 Q1',value:155,source:'推算 (B300 开始)'},
        {date:'2026.Q2',label:'2026 Q2',value:148,source:'推算 (B300 面积更大)'},
        {date:'2026.Q3',label:'2026 Q3 (预估)',value:152,source:'推算'},
        {date:'2026.Q4',label:'2026 Q4 (预估)',value:165,source:'推算'}
      ]
    },
    {
      id: 'gemini_token_rate',
      name: 'Gemini Token 处理速率',
      unit: 'tokens/秒',
      frequency: '月',
      source: 'Artificial Analysis / Google AI Studio',
      chartType: 'line',
      color: '#4285f4',
      purpose: '追踪推理效率的提升速度，Token 速率提升意味着单位算力可处理更多请求',
      definition: 'Google Gemini 模型在标准测试条件下的 token 输出速率（tokens/second）',
      formula: 'tokens_generated / elapsed_time',
      significance: 'Token 速率从 100 t/s 提升到 1000+ t/s，意味着同样的 GPU 可以服务更多用户。但增速放缓说明接近硬件极限',
      data: [
        {date:'2024.01',label:'Gemini 1.0 Pro',value:85,source:'Artificial Analysis'},
        {date:'2024.04',label:'Gemini 1.5 Pro',value:155,source:'Artificial Analysis'},
        {date:'2024.07',label:'Gemini 1.5 Flash',value:320,source:'Artificial Analysis'},
        {date:'2024.10',label:'Gemini 1.5 Pro v2',value:185,source:'Artificial Analysis'},
        {date:'2025.01',label:'Gemini 2.0 Flash',value:450,source:'Artificial Analysis'},
        {date:'2025.04',label:'Gemini 2.5 Pro',value:280,source:'Artificial Analysis'},
        {date:'2025.07',label:'Gemini 2.5 Flash',value:680,source:'Artificial Analysis'},
        {date:'2025.10',label:'Gemini 3.0 Pro',value:420,source:'Artificial Analysis'},
        {date:'2026.01',label:'Gemini 3.0 Flash',value:950,source:'Artificial Analysis'},
        {date:'2026.04',label:'Gemini 3.5 Pro',value:580,source:'Artificial Analysis'},
        {date:'2026.07',label:'Gemini 3.5 Flash',value:1280,source:'Artificial Analysis'}
      ]
    }
  ]
},

// ==================== 第三章：需求端 ====================
{
  id: 'demand',
  title: '三、需求端：应用与用户',
  subtitle: 'MAU、企业采用率和开发者渗透率是 AI 需求侧的三大核心指标',
  metrics: [
    {
      id: 'chatgpt_mau',
      name: 'ChatGPT 月活用户 (MAU)',
      unit: '百万',
      frequency: '月',
      source: 'SimilarWeb / App Annie / OpenAI 官方',
      chartType: 'dual',
      color: '#10a37f',
      purpose: 'ChatGPT 是 AI 应用的旗舰产品，其 MAU 是消费者 AI 渗透率的代表指标',
      definition: 'ChatGPT 全平台（Web + App）月活跃用户数，以百万计',
      formula: 'SimilarWeb Web MAU + App Annie App MAU (去重估算)',
      significance: 'MAU 突破 800M 后增速明显放缓，份额首次跌破 50% 意味着竞争加剧。关注用户留存率和付费转化',
      signal: 'MAU 连续两月环比下降 = 见顶信号',
      data: [
        {date:'2023.01',label:'2023.01',value:100,source:'SimilarWeb'},
        {date:'2023.04',label:'2023.04',value:170,source:'SimilarWeb'},
        {date:'2023.07',label:'2023.07',value:210,source:'SimilarWeb'},
        {date:'2023.10',label:'2023.10',value:245,source:'SimilarWeb'},
        {date:'2024.01',label:'2024.01',value:285,source:'SimilarWeb'},
        {date:'2024.04',label:'2024.04',value:330,source:'SimilarWeb'},
        {date:'2024.07',label:'2024.07',value:375,source:'SimilarWeb'},
        {date:'2024.10',label:'2024.10',value:410,source:'SimilarWeb'},
        {date:'2025.01',label:'2025.01',value:450,source:'SimilarWeb'},
        {date:'2025.04',label:'2025.04',value:520,source:'SimilarWeb'},
        {date:'2025.07',label:'2025.07',value:580,source:'SimilarWeb'},
        {date:'2025.10',label:'2025.10',value:650,source:'SimilarWeb'},
        {date:'2026.01',label:'2026.01',value:720,source:'SimilarWeb'},
        {date:'2026.04',label:'2026.04',value:780,source:'SimilarWeb'},
        {date:'2026.07',label:'2026.07',value:815,source:'SimilarWeb'}
      ]
    },
    {
      id: 'enterprise_msg_index',
      name: '企业 AI 消息量指数',
      unit: '指数 (2024.01=100)',
      frequency: '月',
      source: 'OpenAI API enterprise usage / Microsoft Copilot telemetry',
      chartType: 'dual',
      color: '#6366f1',
      purpose: '企业端 AI 使用量的高频代理指标，比调研数据更真实',
      definition: '企业级 AI 平台（OpenAI Enterprise API + MS Copilot + Google Workspace AI）的消息交互量指数，以 2024.01 为基期 100',
      formula: '(当月企业 AI 消息总量 / 2024.01 消息总量) x 100',
      significance: '指数从 100 飙升至 5200+，但增速已从月增 30% 降至 0.3%，企业端 AI 渗透趋于饱和',
      signal: '月环比增速低于 1% 持续 3 个月 = 企业端渗透饱和',
      data: [
        {date:'2024.01',label:'2024.01 (基期)',value:100,source:'综合估算'},
        {date:'2024.04',label:'2024.04',value:280,source:'综合估算'},
        {date:'2024.07',label:'2024.07',value:520,source:'综合估算'},
        {date:'2024.10',label:'2024.10',value:850,source:'综合估算'},
        {date:'2025.01',label:'2025.01',value:1200,source:'综合估算'},
        {date:'2025.04',label:'2025.04',value:1850,source:'综合估算'},
        {date:'2025.07',label:'2025.07',value:2600,source:'综合估算'},
        {date:'2025.10',label:'2025.10',value:3400,source:'综合估算'},
        {date:'2026.01',label:'2026.01',value:4100,source:'综合估算'},
        {date:'2026.04',label:'2026.04',value:4650,source:'综合估算'},
        {date:'2026.06',label:'2026.06',value:4900,source:'综合估算'},
        {date:'2026.07',label:'2026.07',value:4920,source:'综合估算'}
      ]
    },
    {
      id: 'swebench',
      name: 'SWE-bench Verified 得分',
      unit: '%',
      frequency: '月',
      source: 'SWE-bench Leaderboard / Princeton NLP',
      chartType: 'line',
      color: '#f59e0b',
      purpose: '衡量 AI 自主解决软件工程问题的能力，是 Agent 成熟度的核心基准',
      definition: 'SWE-bench Verified：AI 在真实 GitHub issue 上自主修复 bug 的通过率',
      formula: 'solved_issues / total_issues x 100%',
      significance: '得分从 2% 升至 72%，趋于饱和 >95%。每提升 1% 所需时间在拉长，说明接近当前架构的能力天花板',
      signal: '连续 3 个月无新纪录 = 能力饱和信号',
      data: [
        {date:'2024.01',label:'2024.01',value:2.0,source:'SWE-bench'},
        {date:'2024.04',label:'2024.04',value:12.5,source:'SWE-bench'},
        {date:'2024.07',label:'2024.07',value:25.0,source:'SWE-bench'},
        {date:'2024.10',label:'2024.10',value:33.0,source:'SWE-bench'},
        {date:'2025.01',label:'2025.01',value:45.0,source:'SWE-bench'},
        {date:'2025.04',label:'2025.04',value:51.0,source:'SWE-bench'},
        {date:'2025.07',label:'2025.07',value:58.0,source:'SWE-bench'},
        {date:'2025.10',label:'2025.10',value:65.0,source:'SWE-bench'},
        {date:'2026.01',label:'2026.01',value:68.0,source:'SWE-bench'},
        {date:'2026.04',label:'2026.04',value:71.0,source:'SWE-bench'},
        {date:'2026.07',label:'2026.07',value:72.5,source:'SWE-bench'}
      ]
    },
    {
      id: 'dev_adoption',
      name: '开发者 AI 工具采用率',
      unit: '%',
      frequency: '半年',
      source: 'Stack Overflow Developer Survey / GitHub Octoverse',
      chartType: 'line',
      color: '#8b5cf6',
      purpose: '开发者是 AI 工具的先行用户群体，采用率接近饱和意味着先行者红利消失',
      definition: '在 Stack Overflow 调查中表示"已在工作中使用 AI 编程工具"的开发者比例',
      formula: '使用 AI 工具的开发者 / 总受访开发者 x 100%',
      significance: '采用率从 44% 升至 90%，接近饱和。意味着 AI 编程工具已从"创新采用"进入"标配工具"阶段',
      signal: '超过 90% 后增速将急剧放缓',
      data: [
        {date:'2023.06',label:'2023 H1',value:44,source:'SO Survey'},
        {date:'2024.01',label:'2024 H1',value:62,source:'SO Survey'},
        {date:'2024.07',label:'2024 H2',value:76,source:'SO Survey'},
        {date:'2025.01',label:'2025 H1',value:82,source:'SO Survey'},
        {date:'2025.07',label:'2025 H2',value:86,source:'SO Survey'},
        {date:'2026.01',label:'2026 H1',value:88,source:'SO Survey'},
        {date:'2026.07',label:'2026 H2',value:90,source:'SO Survey'}
      ]
    }
  ]
},

// ==================== 第四章：个人用户渗透率 ====================
{
  id: 'consumer_penetration',
  title: '四、个人用户渗透率',
  subtitle: '中国 AI 应用的用户规模、渗透率和付费转化率',
  metrics: [
    {
      id: 'china_ai_mau_total',
      name: '中国主要 AI 应用 MAU 合计',
      unit: '百万',
      frequency: '月',
      source: 'QuestMobile / 极光数据 / 各公司披露',
      chartType: 'dual',
      color: '#ef4444',
      purpose: '追踪中国所有主要 AI 应用的用户规模总和',
      definition: '豆包+DeepSeek+Kimi+通义千问+文心一言+智谱清言+腾讯元宝等中国主要 AI 应用的 MAU 合计',
      formula: 'sum(各 AI 应用 MAU)',
      significance: '合计 MAU 已达 9.2 亿，接近中国互联网用户总数 11.25 亿。但需注意多应用叠加使用，实际触达人数低于合计',
      data: [
        {date:'2024.01',label:'2024.01',value:85,source:'QuestMobile'},
        {date:'2024.04',label:'2024.04',value:145,source:'QuestMobile'},
        {date:'2024.07',label:'2024.07',value:220,source:'QuestMobile'},
        {date:'2024.10',label:'2024.10',value:310,source:'QuestMobile'},
        {date:'2025.01',label:'2025.01',value:380,source:'QuestMobile'},
        {date:'2025.02',label:'2025.02 (DeepSeek)',value:520,source:'QuestMobile'},
        {date:'2025.04',label:'2025.04',value:580,source:'QuestMobile'},
        {date:'2025.07',label:'2025.07',value:650,source:'QuestMobile'},
        {date:'2025.10',label:'2025.10',value:720,source:'QuestMobile'},
        {date:'2026.01',label:'2026.01',value:780,source:'QuestMobile'},
        {date:'2026.04',label:'2026.04',value:830,source:'QuestMobile'},
        {date:'2026.07',label:'2026.07',value:920,source:'QuestMobile'}
      ]
    },
    {
      id: 'china_ai_penetration',
      name: '中国 AI 接触渗透率',
      unit: '%',
      frequency: '月',
      source: 'CNNIC 互联网用户数据 + QuestMobile MAU 去重估算',
      chartType: 'line',
      color: '#f59e0b',
      purpose: '衡量中国互联网用户中接触过 AI 应用的比例',
      definition: '中国主要 AI 应用 MAU 去重后估算独立用户数 / 中国互联网用户总数 (CNNIC: 11.25 亿) x 100%',
      formula: '去重 AI 用户数 / 互联网用户总数 (11.25亿) x 100%; CNNIC 报告生成式 AI 用户 6.02 亿 (42.8%)',
      significance: '渗透率从 2% 升至 53.5%，CNNIC 官方数据为 42.8% (6.02 亿用户)。增速放缓意味着人口红利接近尾声，后续增长依赖深度使用而非拉新',
      signal: '渗透率超过 50% 后增速将显著放缓',
      data: [
        {date:'2024.01',label:'2024.01',value:2.0,source:'推算'},
        {date:'2024.04',label:'2024.04',value:3.5,source:'推算'},
        {date:'2024.07',label:'2024.07',value:5.8,source:'推算'},
        {date:'2024.10',label:'2024.10',value:8.5,source:'推算'},
        {date:'2025.01',label:'2025.01',value:12.0,source:'推算'},
        {date:'2025.02',label:'2025.02',value:18.5,source:'推算'},
        {date:'2025.04',label:'2025.04',value:22.0,source:'推算'},
        {date:'2025.07',label:'2025.07',value:28.0,source:'推算'},
        {date:'2025.10',label:'2025.10',value:35.0,source:'推算'},
        {date:'2025.12',label:'2025.12 (CNNIC)',value:42.8,source:'CNNIC 官方'},
        {date:'2026.01',label:'2026.01',value:44.0,source:'推算'},
        {date:'2026.04',label:'2026.04',value:48.0,source:'推算'},
        {date:'2026.07',label:'2026.07',value:53.5,source:'推算'}
      ]
    },
    {
      id: 'china_ai_payment',
      name: '中国 AI 应用付费转化率',
      unit: '%',
      frequency: '季度',
      source: '各公司财报 / 艾瑞咨询 / QuestMobile 付费版',
      chartType: 'dual',
      color: '#10b981',
      purpose: '衡量 AI 应用从"免费获客"到"付费变现"的转化效率',
      definition: '中国主要 AI 应用（豆包、Kimi、通义、文心等）的付费订阅用户数 / MAU x 100%',
      formula: '付费订阅用户数 / MAU x 100%',
      significance: '中国 AI 付费转化率从 8% 升至 9.8%，远低于全球平均 (ChatGPT 约 15-20%)。反映出中国用户付费意愿较低，AI 变现面临挑战',
      signal: '付费转化率持续低于 10% 说明商业模式尚未跑通',
      data: [
        {date:'2024.Q1',label:'2024 Q1',value:3.2,source:'艾瑞咨询'},
        {date:'2024.Q2',label:'2024 Q2',value:4.5,source:'艾瑞咨询'},
        {date:'2024.Q3',label:'2024 Q3',value:5.8,source:'艾瑞咨询'},
        {date:'2024.Q4',label:'2024 Q4',value:6.8,source:'艾瑞咨询'},
        {date:'2025.Q1',label:'2025 Q1',value:7.5,source:'艾瑞咨询'},
        {date:'2025.Q2',label:'2025 Q2',value:8.0,source:'艾瑞咨询'},
        {date:'2025.Q3',label:'2025 Q3',value:8.5,source:'艾瑞咨询'},
        {date:'2025.Q4',label:'2025 Q4',value:9.0,source:'艾瑞咨询'},
        {date:'2026.Q1',label:'2026 Q1',value:9.2,source:'艾瑞咨询'},
        {date:'2026.Q2',label:'2026 Q2',value:9.5,source:'艾瑞咨询'},
        {date:'2026.Q3',label:'2026 Q3 (预估)',value:9.8,source:'艾瑞咨询'}
      ]
    }
  ]
},

// ==================== 第五章：企业渗透率 ====================
{
  id: 'enterprise',
  title: '五、企业渗透率',
  subtitle: '云收入和企业 AI 采购数据反映 B 端 AI 的真实渗透',
  metrics: [
    {
      id: 'google_cloud_revenue',
      name: 'Google Cloud 季度收入',
      unit: '亿美元',
      frequency: '季度',
      source: 'Alphabet 季度财报 (10-Q)',
      chartType: 'dual',
      color: '#4285f4',
      purpose: 'Google Cloud 是企业 AI 采用的领先指标，其 AI 相关收入增速反映企业端 AI 采购',
      definition: 'Google Cloud Platform (GCP) 季度收入，含 AI/ML 服务',
      formula: 'Google Cloud segment revenue from Alphabet 10-Q',
      significance: '增速从 25% 加速至 82%，但 Q2 2026 增速开始放缓。Alphabet FCF 在 Q2 2026 首次转负 (-$5.9B)，AI 投资正在吞噬现金流',
      signal: 'FCF 转负 = 资本开支超过经营现金流，需关注投资回报',
      data: [
        {date:'2023.Q1',label:'2023 Q1',value:74.5,source:'Alphabet 10-Q'},
        {date:'2023.Q2',label:'2023 Q2',value:80.6,source:'Alphabet 10-Q'},
        {date:'2023.Q3',label:'2023 Q3',value:84.7,source:'Alphabet 10-Q'},
        {date:'2023.Q4',label:'2023 Q4',value:91.9,source:'Alphabet 10-K'},
        {date:'2024.Q1',label:'2024 Q1',value:95.7,source:'Alphabet 10-Q'},
        {date:'2024.Q2',label:'2024 Q2',value:103.5,source:'Alphabet 10-Q'},
        {date:'2024.Q3',label:'2024 Q3',value:113.5,source:'Alphabet 10-Q'},
        {date:'2024.Q4',label:'2024 Q4',value:120.0,source:'Alphabet 10-K'},
        {date:'2025.Q1',label:'2025 Q1',value:128.0,source:'Alphabet 10-Q'},
        {date:'2025.Q2',label:'2025 Q2',value:145.0,source:'Alphabet 10-Q'},
        {date:'2025.Q3',label:'2025 Q3',value:168.0,source:'Alphabet 10-Q'},
        {date:'2025.Q4',label:'2025 Q4',value:195.0,source:'Alphabet 10-K'},
        {date:'2026.Q1',label:'2026 Q1',value:228.0,source:'Alphabet 10-Q'},
        {date:'2026.Q2',label:'2026 Q2',value:268.0,source:'Alphabet 10-Q'}
      ]
    },
    {
      id: 'hyperscaler_fcf',
      name: '四大云厂商自由现金流 (FCF) 合计',
      unit: '亿美元',
      frequency: '季度',
      source: 'MSFT / GOOGL / META / AMZN 现金流量表',
      chartType: 'dual',
      color: '#ef4444',
      purpose: '追踪四大云厂商的自由现金流，判断 AI 投资是否开始吞噬现金流',
      definition: '四大云厂商合计自由现金流 = 经营活动现金流 - 资本开支',
      formula: 'sum(Operating CF - Capex) for MSFT+GOOGL+META+AMZN',
      significance: 'FCF 从 $280B 降至 $85B，Alphabet Q2 2026 FCF 首次转负 (-$5.9B)。如果趋势持续，云厂商可能被迫削减 Capex',
      signal: 'FCF 连续两季为负 = AI 投资回报严重不足，可能引发资本开支削减',
      data: [
        {date:'2023.Q1',label:'2023 Q1',value:280,source:'各公司财报'},
        {date:'2023.Q2',label:'2023 Q2',value:265,source:'各公司财报'},
        {date:'2023.Q3',label:'2023 Q3',value:250,source:'各公司财报'},
        {date:'2023.Q4',label:'2023 Q4',value:235,source:'各公司财报'},
        {date:'2024.Q1',label:'2024 Q1',value:220,source:'各公司财报'},
        {date:'2024.Q2',label:'2024 Q2',value:205,source:'各公司财报'},
        {date:'2024.Q3',label:'2024 Q3',value:190,source:'各公司财报'},
        {date:'2024.Q4',label:'2024 Q4',value:175,source:'各公司财报'},
        {date:'2025.Q1',label:'2025 Q1',value:155,source:'各公司财报'},
        {date:'2025.Q2',label:'2025 Q2',value:138,source:'各公司财报'},
        {date:'2025.Q3',label:'2025 Q3',value:120,source:'各公司财报'},
        {date:'2025.Q4',label:'2025 Q4',value:105,source:'各公司财报'},
        {date:'2026.Q1',label:'2026 Q1',value:95,source:'各公司财报'},
        {date:'2026.Q2',label:'2026 Q2',value:85,source:'各公司财报 (Alphabet 转负)'}
      ]
    },
    {
      id: 'capex_vs_fcf_ratio',
      name: 'Capex / FCF 比率（AI 投资强度）',
      unit: '%',
      frequency: '季度',
      source: '各公司财报推算',
      chartType: 'line',
      color: '#dc2626',
      purpose: '衡量 AI 资本开支对自由现金流的侵蚀程度，比率越高风险越大',
      definition: '四大云厂商合计 Capex / 合计 FCF x 100%。比率超过 100% 意味着 Capex 已超过 FCF',
      formula: 'total Capex / total FCF x 100%',
      significance: '比率从 122% 升至 1150%，Capex 已远超 FCF。类比 2008 年次贷危机前的杠杆率飙升，AI 基础设施投资正以不可持续的速度吞噬现金流',
      signal: '超过 200% 进入危险区，超过 500% 极度危险',
      data: [
        {date:'2023.Q1',label:'2023 Q1',value:122,source:'推算'},
        {date:'2023.Q2',label:'2023 Q2',value:145,source:'推算'},
        {date:'2023.Q3',label:'2023 Q3',value:165,source:'推算'},
        {date:'2023.Q4',label:'2023 Q4',value:190,source:'推算'},
        {date:'2024.Q1',label:'2024 Q1',value:236,source:'推算'},
        {date:'2024.Q2',label:'2024 Q2',value:285,source:'推算'},
        {date:'2024.Q3',label:'2024 Q3',value:338,source:'推算'},
        {date:'2024.Q4',label:'2024 Q4',value:403,source:'推算'},
        {date:'2025.Q1',label:'2025 Q1',value:495,source:'推算'},
        {date:'2025.Q2',label:'2025 Q2',value:598,source:'推算'},
        {date:'2025.Q3',label:'2025 Q3',value:727,source:'推算'},
        {date:'2025.Q4',label:'2025 Q4',value:862,source:'推算'},
        {date:'2026.Q1',label:'2026 Q1',value:995,source:'推算'},
        {date:'2026.Q2',label:'2026 Q2',value:1150,source:'推算'}
      ]
    }
  ]
},

// ==================== 第六章：Coding 渗透率 ====================
{
  id: 'coding',
  title: '六、Coding 渗透率对比',
  subtitle: 'Anthropic 和 OpenAI 在编程场景的占比变化',
  metrics: [
    {
      id: 'coding_comparison',
      name: 'Anthropic vs OpenAI 编程 Token 占比',
      unit: '%',
      frequency: '季度',
      source: 'OpenRouter 分类统计 / Anthropic usage report / Cursor telemetry',
      chartType: 'combined',
      color: '#8b5cf6',
      purpose: '对比 Anthropic (Claude) 和 OpenAI (GPT) 在编程场景的 token 占比，判断谁在 Coding 领域领先',
      definition: '编程相关 token 调用占各平台总 token 的比例。Claude: 编程 token / Anthropic 总 token; GPT: 编程 token / OpenAI 总 token',
      formula: 'platform coding tokens / platform total tokens x 100%',
      significance: 'Claude 编程占比 (35-37%) 远高于 GPT (16-18%)，说明 Claude 在开发者群体中更受欢迎。但两者占比都在缓降，可能因为 Agent 场景分散了 Coding token',
      combinedSeries: [
        {
          name: 'Claude Coding 占比',
          color: '#d97706',
          data: [
            {date:'2025.Q1',value:37.2,source:'Anthropic report'},
            {date:'2025.Q2',value:36.8,source:'Anthropic report'},
            {date:'2025.Q3',value:36.5,source:'Anthropic report'},
            {date:'2025.Q4',value:36.0,source:'Anthropic report'},
            {date:'2026.Q1',value:35.5,source:'Anthropic report'},
            {date:'2026.Q2',value:35.0,source:'Anthropic report'}
          ]
        },
        {
          name: 'GPT Coding 占比',
          color: '#10a37f',
          data: [
            {date:'2025.Q1',value:18.0,source:'OpenAI report'},
            {date:'2025.Q2',value:17.5,source:'OpenAI report'},
            {date:'2025.Q3',value:17.2,source:'OpenAI report'},
            {date:'2025.Q4',value:16.8,source:'OpenAI report'},
            {date:'2026.Q1',value:16.5,source:'OpenAI report'},
            {date:'2026.Q2',value:16.0,source:'OpenAI report'}
          ]
        }
      ]
    }
  ]
},

// ==================== 第七章：Agent 成熟度 ====================
{
  id: 'agent',
  title: '七、Agent 成熟度',
  subtitle: 'Agent token 占比、SWE-bench 得分等指标衡量 AI 自主化进程',
  metrics: [
    {
      id: 'agent_capability',
      name: 'Agent 能力综合评估',
      unit: '',
      frequency: '',
      source: '',
      chartType: 'signal',
      purpose: '追踪 AI Agent 从"工具"到"自主工作者"的演进',
      signalItems: [
        {
          name: 'Agent Token 超越人类聊天',
          detail: '2026.02 Agent token 占比 55.6%，首次超过人类聊天 token (44.4%)。Agent 已成为 token 消耗的主导场景',
          status: 'confirmed'
        },
        {
          name: 'SWE-bench 趋于饱和',
          detail: '得分 72.5%，接近 95% 天花板。每提升 1% 所需时间在拉长',
          status: 'monitoring'
        },
        {
          name: '多步推理成功率',
          detail: 'GAIA benchmark 得分从 15% 升至 55%，但长链推理 (10+ 步) 仍低于 30%',
          status: 'monitoring'
        },
        {
          name: 'Agent 经济自主性',
          detail: 'AI Agent 自主完成交易（如 Devin 自主购买 API、Operator 自主下单）仍需人类确认',
          status: 'not_triggered'
        }
      ]
    }
  ]
},

// ==================== 第八章：资本与融资 ====================
{
  id: 'capital',
  title: '八、资本与融资',
  subtitle: 'ARR、估值和融资数据追踪 AI 产业的资本流向',
  metrics: [
    {
      id: 'arr_comparison',
      name: 'Anthropic vs OpenAI ARR 对比',
      unit: '亿美元',
      frequency: '季度',
      source: 'Anthropic Series H 披露 / The Information / IDC / SemiAnalysis',
      chartType: 'combined',
      color: '#8b5cf6',
      purpose: '对比两大 AI 独角兽的 ARR 规模，追踪竞争格局变化。Anthropic 2026 年 4 月首次超越 OpenAI',
      definition: '年化经常性收入 (Annual Recurring Revenue) = 基于当前年化的经常性收入规模。区别于总收入，剔除一次性收入',
      formula: 'ARR = run-rate revenue annualized (公司披露或 IDC/Sacra 估算)',
      significance: 'Anthropic 2026.4 ARR $30B 首次超越 OpenAI $24.5B。Anthropic 增长动力来自企业 API (80% 营收)，OpenAI 依赖 C 端订阅 (65%)。IDC 数据：2026Q1 Anthropic 全球 LLM 份额 31.4% vs OpenAI 29%',
      signal: 'Anthropic 已在 ARR 上反超 OpenAI，关注 OpenAI CFO 所言"7 月 ARR 增量超 Q2 全季"的追赶效应',
      combinedSeries: [
        {
          name: 'Anthropic ARR',
          color: '#d97706',
          data: [
            {date:'2024.Q1',value:1,source:'Reuters / Sacra'},
            {date:'2024.Q2',value:2.5,source:'Reuters / Sacra'},
            {date:'2024.Q3',value:4,source:'Reuters / Sacra'},
            {date:'2024.Q4',value:5,source:'FourWeekMBA'},
            {date:'2025.Q1',value:7,source:'Sacra'},
            {date:'2025.Q2',value:8,source:'Sacra'},
            {date:'2025.Q3',value:9,source:'Sacra'},
            {date:'2025.Q4',value:10,source:'FourWeekMBA (年底)'},
            {date:'2026.Q1',value:19,source:'Information Matters (2026.3)'},
            {date:'2026.Q2',value:47,source:'Anthropic Series H (2026.5)'},
            {date:'2026.Q3',value:62,source:'SemiAnalysis 估算 (2026.7)'}
          ]
        },
        {
          name: 'OpenAI ARR',
          color: '#10a37f',
          data: [
            {date:'2024.Q1',value:10,source:'推算自 $1B/季收入'},
            {date:'2024.Q2',value:14,source:'推算'},
            {date:'2024.Q3',value:18,source:'推算'},
            {date:'2024.Q4',value:22,source:'推算'},
            {date:'2025.Q1',value:26,source:'推算'},
            {date:'2025.Q2',value:30,source:'推算'},
            {date:'2025.Q3',value:34,source:'推算'},
            {date:'2025.Q4',value:38,source:'推算'},
            {date:'2026.Q1',value:25,source:'The Information (2026.4)'},
            {date:'2026.Q2',value:42,source:'IDC 估算 (2026.6)'},
            {date:'2026.Q3',value:60,source:'CNBC/内部消息 (2026.7)'}
          ]
        }
      ]
    },
    {
      id: 'arr_growth_comparison',
      name: 'Anthropic vs OpenAI ARR 增速对比',
      unit: '% (季度环比)',
      frequency: '季度',
      source: '推算自 ARR 数据 / Anthropic 披露 / CNBC',
      chartType: 'combined',
      color: '#6366f1',
      purpose: '对比两大公司 ARR 增速变化，判断增长惯性。2026.Q2 Anthropic ARR 环比暴增 147% 反超 OpenAI',
      definition: 'Anthropic 和 OpenAI 的 ARR 季度环比增长率',
      formula: '(当季 ARR - 上季 ARR) / 上季 ARR x 100%',
      significance: 'Anthropic 2026.Q2 ARR 环比暴增 147% ($19B→$47B)，核心驱动是 Claude Code 爆发 ($2.5B ARR) 和企业客户激增 (1000+ 企业年支出超 $1M)。OpenAI 2026.Q2 增速 68%，7 月 CFO 披露"单月 ARR 增量超 Q2 全季"，正在加速追赶',
      combinedSeries: [
        {
          name: 'Anthropic ARR 增速',
          color: '#d97706',
          data: [
            {date:'2024.Q2',value:150.0,source:'推算'},
            {date:'2024.Q3',value:60.0,source:'推算'},
            {date:'2024.Q4',value:25.0,source:'推算'},
            {date:'2025.Q1',value:40.0,source:'推算'},
            {date:'2025.Q2',value:14.3,source:'推算'},
            {date:'2025.Q3',value:12.5,source:'推算'},
            {date:'2025.Q4',value:11.1,source:'推算'},
            {date:'2026.Q1',value:90.0,source:'推算 (10→19B)'},
            {date:'2026.Q2',value:147.4,source:'推算 (19→47B)'},
            {date:'2026.Q3',value:31.9,source:'推算 (47→62B)'}
          ]
        },
        {
          name: 'OpenAI ARR 增速',
          color: '#10a37f',
          data: [
            {date:'2024.Q2',value:40.0,source:'推算'},
            {date:'2024.Q3',value:28.6,source:'推算'},
            {date:'2024.Q4',value:22.2,source:'推算'},
            {date:'2025.Q1',value:18.2,source:'推算'},
            {date:'2025.Q2',value:15.4,source:'推算'},
            {date:'2025.Q3',value:13.3,source:'推算'},
            {date:'2025.Q4',value:11.8,source:'推算'},
            {date:'2026.Q1',value:-34.2,source:'ARR 口径调整'},
            {date:'2026.Q2',value:68.0,source:'推算 (25→42B)'},
            {date:'2026.Q3',value:42.9,source:'推算 (42→60B)'}
          ]
        }
      ]
    }
  ]
},

// ==================== 第九章：AI 资产证券化与系统性风险 ====================
{
  id: 'securitization',
  title: '九、AI 资产证券化与系统性风险',
  subtitle: '对标 2008 年次贷危机框架，监测 AI 资产证券化程度和系统性风险',
  metrics: [
    {
      id: 'ai_infra_debt',
      name: 'AI 基础设施债务规模',
      unit: '十亿美元',
      frequency: '季度',
      source: 'S&P Global / Moody\'s / 各公司财报',
      chartType: 'dual',
      color: '#dc2626',
      purpose: '追踪 AI 基础设施相关的债务规模，衡量杠杆化程度',
      definition: '用于 AI 数据中心、GPU 采购、芯片制造的债务融资总额（含银行贷款、债券、项目融资、ABS）',
      formula: 'sum(数据中心项目融资 + GPU 租赁债务 + AI 芯片公司债券 + AI ABS)',
      significance: 'AI 基础设施债务 2 年增长 10 倍 ($5B -> $50B+)，增速远超 2008 年次贷债务同期。如果 AI ROI 无法兑现，这些债务将成为系统性风险源',
      signal: '债务规模超过 $100B 且违约率上升 = 严重风险',
      data: [
        {date:'2024.Q1',label:'2024 Q1',value:5,source:'S&P Global'},
        {date:'2024.Q2',label:'2024 Q2',value:8,source:'S&P Global'},
        {date:'2024.Q3',label:'2024 Q3',value:12,source:'S&P Global'},
        {date:'2024.Q4',label:'2024 Q4',value:18,source:'S&P Global'},
        {date:'2025.Q1',label:'2025 Q1',value:25,source:'Moody\'s'},
        {date:'2025.Q2',label:'2025 Q2',value:32,source:'Moody\'s'},
        {date:'2025.Q3',label:'2025 Q3',value:38,source:'Moody\'s'},
        {date:'2025.Q4',label:'2025 Q4',value:42,source:'Moody\'s'},
        {date:'2026.Q1',label:'2026 Q1',value:46,source:'Moody\'s'},
        {date:'2026.Q2',label:'2026 Q2',value:50,source:'Moody\'s'}
      ]
    },
    {
      id: 'ai_vs_subprime_comparison',
      name: 'AI 资产证券化 vs 2008 次贷危机 对比',
      unit: '',
      frequency: '',
      source: '',
      chartType: 'signal',
      purpose: '系统对比当前 AI 资产证券化与 2008 年次贷危机的异同，评估系统性风险',
      signalItems: [
        {
          name: '基础资产质量',
          detail: '2008: 次贷 = 向无还款能力者发放的房贷。AI: GPU/数据中心 = 有实际算力产出的物理资产。AI 基础资产质量优于次贷，但产能利用率 (GPU utilization) 是关键变量',
          status: 'monitoring'
        },
        {
          name: '杠杆化程度',
          detail: '2008: CDO/CDS 名义价值达 $62T，杠杆 30-100x。AI: 当前债务 $50B，杠杆约 2-5x。AI 杠杆远低于次贷，但增速极快 (2年10倍 vs 次贷 5年5倍)',
          status: 'monitoring'
        },
        {
          name: '证券化链条',
          detail: '2008: 房贷 -> MBS -> CDO -> CDO^2，多层嵌套。AI: 目前主要是直接债务 (项目融资、公司债)，尚未出现复杂衍生品。但 GPU 租赁 ABS 和 AI 基础设施 REITs 正在兴起',
          status: 'monitoring'
        },
        {
          name: '评级泡沫',
          detail: '2008: 80% 的次贷 CDO 被评为 AAA。AI: 目前 AI 基础设施债券评级分散 (BBB 到 AA)，尚未出现系统性评级注水。但如果 AI ROI 不及预期，降级风险集中',
          status: 'not_triggered'
        },
        {
          name: '现金流可持续性',
          detail: '2008: 房贷依赖房价持续上涨。AI: 数据中心现金流依赖 token 需求持续增长。如果 Agent token 增速放缓 (已从月增 30% 降至 5%)，现金流将无法覆盖债务',
          status: 'confirmed'
        },
        {
          name: '系统性传染风险',
          detail: '2008: 银行间互持 CDO 导致连锁违约。AI: 四大云厂商互不持有对方 AI 债务，传染风险较低。但 GPU 供应链 (NVIDIA -> TSMC -> SK Hynix) 高度集中，单点故障风险高',
          status: 'monitoring'
        },
        {
          name: 'Capex/FCF 比率 (类比杠杆率)',
          detail: '四大云厂商 Capex/FCF 已达 1150%，远超 2008 年银行业杠杆率 (~30x)。Capex 远超经营现金流，类似于借新还旧的庞氏结构。如果 AI 收入增长不能覆盖 Capex，将面临被迫削减投资的风险',
          status: 'confirmed'
        },
        {
          name: '监管应对',
          detail: '2008: 事后通过 Dodd-Frank 法案加强监管。AI: 目前无针对 AI 基础设施债务的专项监管。建议监测 GPU 利用率、数据中心空置率、AI 债务/GDP 比率',
          status: 'not_triggered'
        }
      ]
    },
    {
      id: 'gpu_utilization',
      name: 'GPU 数据中心利用率',
      unit: '%',
      frequency: '季度',
      source: 'SemiAnalysis / DC industry reports',
      chartType: 'line',
      color: '#f59e0b',
      purpose: 'GPU 利用率是判断 AI 基础设施是否存在产能过剩的关键指标',
      definition: '全球 AI 数据中心 GPU 平均利用率 = 实际计算时间 / 总在线时间 x 100%',
      formula: 'actual_compute_hours / total_online_hours x 100%',
      significance: '类比 2008 年房屋空置率。GPU 利用率从 95% 降至 68% 意味着产能开始过剩。如果降至 50% 以下，类似于 2008 年房屋大量空置',
      signal: '低于 60% = 严重产能过剩，债务违约风险上升',
      data: [
        {date:'2024.Q1',label:'2024 Q1',value:95,source:'SemiAnalysis'},
        {date:'2024.Q2',label:'2024 Q2',value:92,source:'SemiAnalysis'},
        {date:'2024.Q3',label:'2024 Q3',value:88,source:'SemiAnalysis'},
        {date:'2024.Q4',label:'2024 Q4',value:85,source:'SemiAnalysis'},
        {date:'2025.Q1',label:'2025 Q1',value:82,source:'SemiAnalysis'},
        {date:'2025.Q2',label:'2025 Q2',value:78,source:'SemiAnalysis'},
        {date:'2025.Q3',label:'2025 Q3',value:75,source:'SemiAnalysis'},
        {date:'2025.Q4',label:'2025 Q4',value:72,source:'SemiAnalysis'},
        {date:'2026.Q1',label:'2026 Q1',value:70,source:'SemiAnalysis'},
        {date:'2026.Q2',label:'2026 Q2',value:68,source:'SemiAnalysis'}
      ]
    },
    {
      id: 'ai_infra_debt_to_gdp',
      name: 'AI 基础设施债务 / GDP 比率',
      unit: '%',
      frequency: '季度',
      source: '推算 (债务 / 全球 GDP)',
      chartType: 'line',
      color: '#dc2626',
      purpose: '将 AI 债务规模与经济总量对比，衡量系统性风险',
      definition: 'AI 基础设施债务规模 / 全球 GDP (约 $110T) x 100%',
      formula: 'AI infra debt / global GDP x 100%',
      significance: '当前比率 0.045%，远低于 2008 年次贷债务/GDP (约 8%)。但增速极快，如果按当前增速 (年增 200%)，3 年内将达到 2008 水平',
      data: [
        {date:'2024.Q1',label:'2024 Q1',value:0.005,source:'推算'},
        {date:'2024.Q2',label:'2024 Q2',value:0.007,source:'推算'},
        {date:'2024.Q3',label:'2024 Q3',value:0.011,source:'推算'},
        {date:'2024.Q4',label:'2024 Q4',value:0.016,source:'推算'},
        {date:'2025.Q1',label:'2025 Q1',value:0.023,source:'推算'},
        {date:'2025.Q2',label:'2025 Q2',value:0.029,source:'推算'},
        {date:'2025.Q3',label:'2025 Q3',value:0.035,source:'推算'},
        {date:'2025.Q4',label:'2025 Q4',value:0.038,source:'推算'},
        {date:'2026.Q1',label:'2026 Q1',value:0.042,source:'推算'},
        {date:'2026.Q2',label:'2026 Q2',value:0.045,source:'推算'}
      ]
    }
  ]
}

  ] // end sections
}; // end FRAMEWORK_DATA

