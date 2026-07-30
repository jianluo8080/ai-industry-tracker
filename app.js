// ============================================================
// 全球 AI 产业跟踪框架 - 时间序列仪表盘 v4
// 核心改进：
// 1. localStorage v4 - 新增 guidance/agent/penetration 等指标
// 2. chartType "dual" - 柱状图(量) + 曲线(增速/二阶导)
// 3. chartType "combined" - 多指标同坐标对比
// 4. chartType "guidance" - 实际值 vs 指引 vs 一致预期
// 5. 总览仪表盘单列布局，增加数据定义/来源信息
// 6. 每个指标展示数据来源、定义/公式、监测意义
// ============================================================

let appData = null;
let charts = {};
let currentSectionId = 'overview';

// ==================== 初始化 ====================

function init() {
  // v3: 强制使用新数据模型，清除旧缓存
  const STORAGE_KEY = 'aiTrackerData_v5';
  const saved = localStorage.getItem(STORAGE_KEY);
  const savedVersion = localStorage.getItem('aiTrackerData_version');

  if (saved && savedVersion === '5.0') {
    try {
      appData = JSON.parse(saved);
      if (!appData.sections || appData.sections.length === 0) {
        appData = deepClone(FRAMEWORK_DATA);
      }
    } catch (e) {
      appData = deepClone(FRAMEWORK_DATA);
    }
  } else {
    // 新版本或首次使用：加载最新数据模型
    appData = deepClone(FRAMEWORK_DATA);
    localStorage.setItem('aiTrackerData_version', '5.0');
  }

  buildSidebar();
  renderSection('overview');

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal();
    }
  });
}

function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function saveData() {
  localStorage.setItem('aiTrackerData_v5', JSON.stringify(appData));
  localStorage.setItem('aiTrackerData_version', '5.0');
}

// ==================== 侧边栏 ====================

function buildSidebar() {
  const nav = document.getElementById('sidebarNav');
  let html = '<div class="nav-item ' + (currentSectionId === 'overview' ? 'active' : '') + '" onclick="renderSection(\'overview\')">\u{1F4CA} \u603B\u89C8\u4EEA\u8868\u76D8</div>';

  appData.sections.forEach(function(sec) {
    var chartCount = sec.metrics.filter(function(m) {
      return (m.data && m.data.length > 0) || m.chartType === 'combined' || m.chartType === 'signal' || m.chartType === 'guidance';
    }).length;
    html += '<div class="nav-item ' + (currentSectionId === sec.id ? 'active' : '') + '" onclick="renderSection(\'' + sec.id + '\')">' +
      '<span>' + sec.title.replace(/^[一二三四五六七八九十]+、\s*/, '') + '</span>' +
      '<span class="nav-badge">' + chartCount + '</span>' +
    '</div>';
  });

  nav.innerHTML = html;

  var footer = document.getElementById('sidebarFooter');
  footer.innerHTML =
    '<button class="btn btn-outline" onclick="exportJSON()">\u5BFC\u51FA JSON</button>' +
    '<button class="btn btn-outline" onclick="exportAllCSV()">\u5BFC\u51FA CSV</button>' +
    '<button class="btn btn-outline" onclick="document.getElementById(\'importFile\').click()">\u5BFC\u5165\u6570\u636E</button>' +
    '<input type="file" id="importFile" accept=".json" style="display:none" onchange="importJSON(event)">' +
    '<button class="btn btn-danger" onclick="resetData()">\u91CD\u7F6E\u6570\u636E</button>';
}

// ==================== 渲染 ====================

function renderSection(sectionId) {
  currentSectionId = sectionId;
  charts = {};

  document.querySelectorAll('.nav-item').forEach(function(el) { el.classList.remove('active'); });

  var content = document.getElementById('mainContent');

  if (sectionId === 'overview') {
    renderOverview(content);
    var navItems = document.querySelectorAll('.nav-item');
    if (navItems[0]) navItems[0].classList.add('active');
    return;
  }

  var section = appData.sections.find(function(s) { return s.id === sectionId; });
  if (!section) return;

  document.querySelectorAll('.nav-item').forEach(function(el) {
    if (el.textContent.includes(section.title.replace(/^[一二三四五六七八九十]+、\s*/, ''))) {
      el.classList.add('active');
    }
  });

  var html =
    '<div class="section-header">' +
      '<h1>' + section.title + '</h1>' +
      '<p class="section-subtitle">' + section.subtitle + '</p>' +
    '</div>' +
    '<div class="metrics-grid">';

  section.metrics.forEach(function(metric) {
    html += renderMetricCard(metric);
  });

  html += '</div>';
  content.innerHTML = html;

  section.metrics.forEach(function(metric) {
    if (metric.chartType === 'signal') {
      renderSignalCard(metric);
    } else if (metric.chartType === 'combined') {
      renderCombinedChart(metric);
    } else if (metric.chartType === 'guidance') {
      renderGuidanceChart(metric);
    } else if (metric.data && metric.data.length > 0) {
      renderChart(metric);
    }
  });
}

// ==================== 总览仪表盘 ====================

function renderOverview(container) {
  var allMetrics = appData.sections.flatMap(function(s) { return s.metrics; });
  var totalMetrics = allMetrics.length;
  var tsMetrics = allMetrics.filter(function(m) { return m.data && m.data.length > 0; });
  var totalDataPoints = tsMetrics.reduce(function(s, m) { return s + m.data.length; }, 0);
  var signalMetrics = allMetrics.filter(function(m) { return m.chartType === 'signal'; });
  var confirmedSignals = signalMetrics.flatMap(function(m) { return m.signalItems || []; }).filter(function(s) { return s.status === 'confirmed'; }).length;

  var html =
    '<div class="section-header">' +
      '<h1>\u{1F4CA} \u603B\u89C8\u4EEA\u8868\u76D8</h1>' +
      '<p class="section-subtitle">\u5168\u7403 AI \u4EA7\u4E1A\u65F6\u95F4\u5E8F\u5217\u8D8B\u52BF\u8FFD\u8E2A \u00B7 \u66F4\u65B0\u65E5\u671F ' + appData.meta.updateDate + ' \u00B7 v' + appData.meta.version + '</p>' +
    '</div>' +
    '<div class="stats-row">' +
      '<div class="stat-card"><div class="stat-value">' + totalMetrics + '</div><div class="stat-label">\u8DDF\u8E2A\u6307\u6807</div></div>' +
      '<div class="stat-card"><div class="stat-value">' + tsMetrics.length + '</div><div class="stat-label">\u6709\u5386\u53F2\u6570\u636E</div></div>' +
      '<div class="stat-card"><div class="stat-value">' + totalDataPoints + '</div><div class="stat-label">\u6570\u636E\u70B9\u603B\u6570</div></div>' +
      '<div class="stat-card stat-alert"><div class="stat-value">' + confirmedSignals + '</div><div class="stat-label">\u5DF2\u786E\u8BA4\u89C1\u9876\u4FE1\u53F7</div></div>' +
    '</div>' +
    '<div class="overview-charts">';

  var keyMetrics = [
    { id: 'openrouter_weekly_tokens', title: 'OpenRouter \u5468\u5EA6 Token \u6D88\u8017\u91CF', note: '\u4E24\u5E7493\u500D', def: 'OpenRouter \u5E73\u53F0\u6BCF\u5468\u5904\u7406\u7684 token \u603B\u91CF\uFF0C\u9700\u6C42\u7AEF\u6700\u9AD8\u9891\u6307\u6807', src: 'OpenRouter Dashboard' },
    { id: 'global_weekly_tokens', title: '\u5168\u7403\u5468\u5EA6 Token \u6D88\u8017\u91CF\uFF08\u4F30\u7B97\uFF09', note: 'OpenRouter \u5360\u5168\u7403 ~15%', def: '\u5168\u7403\u4E3B\u8981 LLM \u5E73\u53F0\u6BCF\u5468 token \u6D88\u8017\u603B\u91CF\u4F30\u7B97', src: 'Artificial Analysis \u4F30\u7B97' },
    { id: 'china_daily_tokens', title: '\u4E2D\u56FD\u65E5\u5747 Token \u6D88\u8017\u91CF', note: 'DeepSeek \u6548\u5E94', def: '\u4E2D\u56FD\u4E3B\u8981\u5927\u6A21\u578B\u5E73\u53F0\u65E5\u5747 token \u6D88\u8017\u603B\u91CF', src: '\u5404\u5E73\u53F0\u62AB\u9732' },
    { id: 'agent_token_share', title: 'Agent Token \u8C03\u7528\u5360\u6BD4', note: '63.5%\uFF0C\u9996\u8D85\u4EBA\u7C7B\u804A\u5929', def: 'AI Agent \u53D1\u8D77\u7684 token \u8C03\u7528\u5360\u603B\u91CF\u7684\u6BD4\u4F8B\uFF0C\u8861\u91CF Agent \u751F\u6001\u6210\u719F\u5EA6', src: 'OpenRouter \u5206\u7C7B\u7EDF\u8BA1' },
    { id: 'arr_comparison', title: 'Anthropic vs OpenAI ARR', note: '\u5355\u4F4D: \u5341\u4EBF\u7F8E\u5143 (B)', def: '\u4E24\u5927 AI \u72EC\u89D2\u89D2 ARR \u5BF9\u6BD4\u3002Anthropic $47B vs OpenAI $42B (2026.Q2)\u3002\u6570\u636E\u5355\u4F4D\uFF1A\u5341\u4EBF\u7F8E\u5143 (Billion USD)', src: 'Anthropic Series H / IDC / The Information / Sacra' },
    { id: 'arr_growth_comparison', title: 'Anthropic vs OpenAI ARR \u589E\u901F', note: 'Q2 \u73AF\u6BD4: Anthropic 147% vs OpenAI 68%', def: 'ARR \u5B63\u5EA6\u73AF\u5BF9\u6BD4 (%)\u3002\u57FA\u4E8E\u5341\u4EBF\u7F8E\u5143\u53E3\u5F84\u8BA1\u7B97\u3002Anthropic \u4F01\u4E1A API \u9A71\u52A8\uFF0COpenAI C \u7AEF\u8FFD\u8D76', src: 'Anthropic \u62AB\u9732 / CNBC / IDC' },
    { id: 'coding_comparison', title: 'Claude vs GPT Coding \u5360\u6BD4', note: 'Claude 35% vs GPT 16%', def: '\u7F16\u7A0B\u76F8\u5173 token \u5360\u5404\u5E73\u53F0\u603B token \u7684\u6BD4\u4F8B', src: 'Anthropic / OpenAI report' },
    { id: 'nvidia_dc_revenue', title: '\u82F1\u4F1F\u8FBE\u6570\u636E\u4E2D\u5FC3\u6536\u5165', note: 'GPU \u4F9B\u9700\u6838\u5FC3', def: 'NVIDIA \u6570\u636E\u4E2D\u5FC3\u4E1A\u52A1\u5B63\u5EA6\u6536\u5165\uFF0C\u76F4\u63A5\u53CD\u6620 AI \u7B97\u529B\u9700\u6C42', src: 'NVIDIA 10-Q/10-K' },
    { id: 'hyperscaler_capex', title: '\u56DB\u5927\u4E91 Capex', note: '2026 \u5168\u5E74 $725B+', def: 'MSFT+GOOGL+META+AMZN \u5B63\u5EA6\u8D44\u672C\u5F00\u652F\u5408\u8BA1', src: '\u5404\u516C\u53F8\u8D22\u62A5' },
    { id: 'hyperscaler_capex_guidance', title: 'Capex: \u5B9E\u9645 vs \u6307\u5F15 vs \u9884\u671F', note: '\u8D85\u9884\u671F\u6301\u7EED', def: '\u5B9E\u9645 Capex vs \u516C\u53F8\u6307\u5F15 vs \u5206\u6790\u5E08\u4E00\u81F4\u9884\u671F', src: '\u5404\u516C\u53F8 guidance + Bloomberg' },
    { id: 'cowos_capacity', title: 'CoWoS \u5148\u8FDB\u5C01\u88C5\u4EA7\u80FD', note: '\u8D8A\u6269\u8D8A\u7F3A\u6096\u8BBA', def: '\u53F0\u79EF\u7535 CoWoS \u6708\u5EA6\u7B49\u6548\u4EA7\u80FD\uFF0C\u51B3\u5B9A GPU \u51FA\u8D27\u4E0A\u9650', src: 'TSMC / TrendForce' },
    { id: 'cowos_gpu_conversion', title: 'CoWoS \u8F6C\u5316\u4E3A GPU/ASIC \u7247\u6570', note: '\u82AF\u7247\u9762\u79EF\u589E\u5927\u5BFC\u81F4\u7247\u6570\u964D', def: '\u57FA\u4E8E CoWoS \u4EA7\u80FD\u548C\u82AF\u7247\u9762\u79EF\u4F30\u7B97\u7684\u5B9E\u9645\u82AF\u7247\u4EA7\u51FA', src: 'TrendForce / J.P. Morgan' },
    { id: 'chatgpt_mau', title: 'ChatGPT MAU', note: '\u589E\u901F\u653E\u7F13', def: 'ChatGPT \u5168\u5E73\u53F0\u6708\u6D3B\u7528\u6237\u6570', src: 'SimilarWeb' },
    { id: 'china_ai_mau_total', title: '\u4E2D\u56FD AI \u5E94\u7528 MAU \u5408\u8BA1', note: '\u63A5\u8FD1 9.2 \u4EBF', def: '\u4E2D\u56FD\u4E3B\u8981 AI \u5E94\u7528 MAU \u5408\u8BA1\uFF08\u8C46\u5305+DeepSeek+Kimi \u7B49\uFF09', src: 'QuestMobile' },
    { id: 'china_ai_penetration', title: '\u4E2D\u56FD AI \u63A5\u89E6\u6E17\u900F\u7387', note: '53.5% (CNNIC 42.8%)', def: '\u53BB\u91CD AI \u7528\u6237\u6570 / \u4E92\u8054\u7F51\u7528\u6237\u603B\u6570 (11.25\u4EBF) x 100%', src: 'CNNIC + QuestMobile' },
    { id: 'china_ai_payment', title: '\u4E2D\u56FD AI \u4ED8\u8D39\u8F6C\u5316\u7387', note: '\u8FDC\u4F4E\u4E8E\u5168\u7403 (9.8%)', def: '\u4E2D\u56FD AI \u5E94\u7528\u4ED8\u8D39\u8BA2\u9605\u7528\u6237 / MAU x 100%', src: '\u827E\u745E\u54A8\u8BE2' },
    { id: 'enterprise_msg_index', title: '\u4F01\u4E1A AI \u6D88\u606F\u91CF\u6307\u6570', note: '\u589E\u901F\u964D\u81F3 0.3%', def: '\u4F01\u4E1A\u7EA7 AI \u5E73\u53F0\u6D88\u606F\u4EA4\u4E92\u91CF\u6307\u6570 (2024.01=100)', src: '\u7EFC\u5408\u4F30\u7B97' },
    { id: 'swebench', title: 'SWE-bench Verified', note: '\u8D8B\u4E8E\u9971\u548C 72.5%', def: 'AI \u5728\u771F\u5B9E GitHub issue \u4E0A\u81EA\u4E3B\u4FEE\u590D bug \u7684\u901A\u8FC7\u7387', src: 'SWE-bench Leaderboard' },
    { id: 'dev_adoption', title: '\u5F00\u53D1\u8005 AI \u5DE5\u5177\u91C7\u7528\u7387', note: '\u63A5\u8FD1\u9971\u548C 90%', def: '\u5DF2\u5728\u5DE5\u4F5C\u4E2D\u4F7F\u7528 AI \u7F16\u7A0B\u5DE5\u5177\u7684\u5F00\u53D1\u8005\u6BD4\u4F8B', src: 'Stack Overflow Survey' },
    { id: 'hyperscaler_fcf', title: '\u56DB\u5927\u4E91 FCF \u5408\u8BA1', note: 'Alphabet \u9996\u6B21\u8F6C\u8D1F', def: '\u56DB\u5927\u4E91\u5382\u5546\u81EA\u7531\u73B0\u91D1\u6D41\u5408\u8BA1 = \u7ECF\u8425 CF - Capex', src: '\u5404\u516C\u53F8\u8D22\u62A5' },
    { id: 'capex_vs_fcf_ratio', title: 'Capex/FCF \u6BD4\u7387\uFF08AI \u6295\u8D44\u5F3A\u5EA6\uFF09', note: '1150%\uFF0C\u6781\u5EA6\u5371\u9669', def: 'Capex / FCF x 100%\uFF0C\u8861\u91CF AI \u6295\u8D44\u5BF9\u73B0\u91D1\u6D41\u7684\u4FB5\u8680\u7A0B\u5EA6', src: '\u63A8\u7B97' },
    { id: 'ai_infra_debt', title: 'AI \u57FA\u7840\u8BBE\u65BD\u503A\u52A1\u89C4\u6A21', note: '2\u5E7410\u500D $50B', def: 'AI \u6570\u636E\u4E2D\u5FC3\u3001GPU \u91C7\u8D2D\u7B49\u76F8\u5173\u503A\u52A1\u878D\u8D44\u603B\u989D', src: 'S&P Global / Moody\'s' },
    { id: 'gpu_utilization', title: 'GPU \u6570\u636E\u4E2D\u5FC3\u5229\u7528\u7387', note: '95%\u219268%\uFF0C\u4EA7\u80FD\u8FC7\u5269', def: '\u5168\u7403 AI \u6570\u636E\u4E2D\u5FC3 GPU \u5E73\u5747\u5229\u7528\u7387\uFF0C\u7C7B\u6BD4 2008 \u623F\u5C4B\u7A7A\u7F6E\u7387', src: 'SemiAnalysis' },
    { id: 'google_cloud_revenue', title: 'Google Cloud \u6536\u5165', note: '\u4F01\u4E1A AI \u6E17\u900F\u9886\u5148\u6307\u6807', def: 'Google Cloud Platform \u5B63\u5EA6\u6536\u5165\uFF0C\u542B AI/ML \u670D\u52A1', src: 'Alphabet 10-Q' },
    { id: 'openrouter_china_share', title: '\u4E2D\u56FD\u6A21\u578B OpenRouter \u4EFD\u989D', note: '4.5%\u219245.5%', def: '\u4E2D\u56FD\u5927\u6A21\u578B\u5728 OpenRouter \u5E73\u53F0 token \u6D88\u8017\u4E2D\u7684\u5360\u6BD4', src: 'OpenRouter' },
    { id: 'gemini_token_rate', title: 'Gemini Token \u901F\u7387', note: '\u63A8\u7406\u6548\u7387\u63D0\u5347', def: 'Gemini \u6A21\u578B\u5728\u6807\u51C6\u6D4B\u8BD5\u6761\u4EF6\u4E0B\u7684 token \u8F93\u51FA\u901F\u7387', src: 'Artificial Analysis' }
  ];

  keyMetrics.forEach(function(km) {
    var metric = allMetrics.find(function(m) { return m.id === km.id; });
    if (metric && ((metric.data && metric.data.length > 0) || metric.chartType === 'combined' || metric.chartType === 'guidance')) {
      html +=
        '<div class="overview-chart-card">' +
          '<div class="overview-chart-header">' +
            '<h3>' + km.title + '</h3>' +
            '<span class="chart-note">' + km.note + '</span>' +
          '</div>' +
          (km.def ? '<div class="overview-chart-def">' + km.def + '</div>' : '') +
          (km.src ? '<div class="overview-chart-src">\u6765\u6E90: ' + km.src + '</div>' : '') +
          '<div class="chart-container" id="overview_chart_' + km.id + '"></div>' +
        '</div>';
    }
  });

  html += '</div>';

  // 见顶信号摘要
  html += '<div class="signals-overview"><h2>\u89C1\u9876\u4FE1\u53F7\u72B6\u6001</h2><div class="signals-grid">';
  signalMetrics.forEach(function(sm) {
    (sm.signalItems || []).forEach(function(item) {
      var statusClass = item.status === 'confirmed' ? 'signal-confirmed' :
                          item.status === 'monitoring' ? 'signal-monitoring' : 'signal-not-triggered';
      var statusText = item.status === 'confirmed' ? '\u5DF2\u786E\u8BA4' :
                         item.status === 'monitoring' ? '\u76D1\u63A7\u4E2D' : '\u672A\u89E6\u53D1';
      html += '<div class="signal-pill ' + statusClass + '">' +
        '<span class="signal-status-dot"></span>' +
        '<div><div class="signal-name">' + item.name + '</div><div class="signal-detail">' + item.detail + '</div></div>' +
        '<span class="signal-badge">' + statusText + '</span>' +
      '</div>';
    });
  });
  html += '</div></div>';

  container.innerHTML = html;

  keyMetrics.forEach(function(km) {
    var metric = allMetrics.find(function(m) { return m.id === km.id; });
    if (metric && ((metric.data && metric.data.length > 0) || metric.chartType === 'combined' || metric.chartType === 'guidance')) {
      if (metric.chartType === 'combined') {
        renderCombinedChart(metric, 'overview_chart_' + km.id, true);
      } else if (metric.chartType === 'guidance') {
        renderGuidanceChart(metric, 'overview_chart_' + km.id, true);
      } else {
        renderChart(metric, 'overview_chart_' + km.id, true);
      }
    }
  });
}

// ==================== 指标卡片 ====================

function renderMetricCard(metric) {
  var dataInfo = '';
  if (metric.data && metric.data.length > 0) {
    var first = metric.data[0];
    var last = metric.data[metric.data.length - 1];
    dataInfo = metric.data.length + ' \u4E2A\u6570\u636E\u70B9 \u00B7 ' + first.date + ' \u81F3 ' + last.date;
  } else if (metric.chartType === 'combined' && metric.combinedSeries) {
    var totalPoints = metric.combinedSeries.reduce(function(s, series) {
      return s + (series.data ? series.data.length : 0);
    }, 0);
    dataInfo = totalPoints + ' \u4E2A\u6570\u636E\u70B9 (\u591A\u7CFB\u5217\u5BF9\u6BD4)';
  }

  var hasSignal = metric.signal ? true : false;
  var signalBadge = hasSignal ? '<span class="signal-tag" title="' + (metric.signal || '') + '">\u26A0 \u4FE1\u53F7</span>' : '';

  // 定义/公式/意义信息块
  var definitionHtml = '';
  if (metric.definition || metric.formula || metric.significance) {
    definitionHtml = '<div class="metric-info-block">';
    if (metric.definition) {
      definitionHtml += '<div class="info-row"><span class="info-label">\u{1F4D6} \u5B9A\u4E49</span><span class="info-text">' + metric.definition + '</span></div>';
    }
    if (metric.formula) {
      definitionHtml += '<div class="info-row"><span class="info-label">\u{1F9EE} \u516C\u5F0F</span><span class="info-text formula-text">' + metric.formula + '</span></div>';
    }
    if (metric.significance) {
      definitionHtml += '<div class="info-row"><span class="info-label">\u{1F3AF} \u76D1\u6D4B\u610F\u4E49</span><span class="info-text">' + metric.significance + '</span></div>';
    }
    definitionHtml += '</div>';
  }

  var chartContent = '';
  if (metric.chartType === 'signal') {
    chartContent = '<div class="signal-list" id="signal_list_' + metric.id + '"></div>';
  } else if (metric.chartType === 'combined') {
    chartContent = '<div class="chart-container" id="chart_' + metric.id + '"></div>';
  } else if (metric.chartType === 'guidance') {
    chartContent = '<div class="chart-container" id="chart_' + metric.id + '"></div>';
  } else if (metric.data && metric.data.length > 0) {
    var dualBadge = metric.chartType === 'dual' ? '<span class="meta-tag dual-badge">\u6881+\u7EBF(\u4E8C\u9636\u5BFC)</span>' : '';
    chartContent = '<div class="chart-container" id="chart_' + metric.id + '"></div>' +
      '<div class="data-table-wrap" id="table_' + metric.id + '"></div>';
    // 在 meta 中添加 dual 标记
  } else {
    chartContent = '<div class="no-data">\u6682\u65E0\u5386\u53F2\u6570\u636E \u2014 \u70B9\u51FB\u300C+ \u6DFB\u52A0\u6570\u636E\u300D\u5F00\u59CB\u8FFD\u8E2A</div>';
  }

  var dualBadge = metric.chartType === 'dual' ? '<span class="meta-tag dual-badge">\u6881+\u7EBF (\u4E8C\u9636\u5BFC)</span>' : '';
  var combinedBadge = metric.chartType === 'combined' ? '<span class="meta-tag combined-badge">\u591A\u7CFB\u5217\u5BF9\u6BD4</span>' : '';
  var guidanceBadge = metric.chartType === 'guidance' ? '<span class="meta-tag guidance-badge">\u5B9E\u9645 vs \u6307\u5F15 vs \u9884\u671F</span>' : '';

  return '<div class="metric-card" id="card_' + metric.id + '">' +
    '<div class="metric-header">' +
      '<div>' +
        '<h3 class="metric-name">' + metric.name + signalBadge + '</h3>' +
        '<div class="metric-meta">' +
          '<span class="meta-tag">\u9891\u7387: ' + metric.frequency + '</span>' +
          '<span class="meta-tag">\u5355\u4F4D: ' + (metric.unit || '\u2014') + '</span>' +
          '<span class="meta-tag">\u6765\u6E90: ' + metric.source + '</span>' +
          dualBadge + combinedBadge + guidanceBadge +
        '</div>' +
      '</div>' +
      (metric.chartType !== 'signal' && metric.chartType !== 'combined' && metric.chartType !== 'guidance' ? '<button class="btn-add" onclick="openDataModal(\'' + metric.id + '\')">+ \u6DFB\u52A0\u6570\u636E</button>' : '') +
    '</div>' +
    '<p class="metric-purpose">' + metric.purpose + '</p>' +
    definitionHtml +
    (dataInfo ? '<div class="metric-data-info">' + dataInfo + '</div>' : '') +
    (hasSignal ? '<div class="metric-signal-text">\u26A0 ' + metric.signal + '</div>' : '') +
    chartContent +
  '</div>';
}

// ==================== 图表渲染 ====================

function renderChart(metric, containerId, compact) {
  var id = containerId || ('chart_' + metric.id);
  var container = document.getElementById(id);
  if (!container) return;

  var data = metric.data;
  if (!data || data.length === 0) return;

  var labels = data.map(function(d) { return d.label || d.date; });
  var values = data.map(function(d) { return d.value; });
  var color = metric.color || '#3b82f6';
  var isBar = metric.chartType === 'bar';
  var isDual = metric.chartType === 'dual';
  var canvasId = id + '_canvas';
  var height = compact ? '200px' : '340px';
  container.innerHTML = '<canvas id="' + canvasId + '" style="max-height:' + height + '"></canvas>';

  var ctx = document.getElementById(canvasId);
  if (!ctx) return;

  // 趋势信息
  var trendHtml = '';
  if (values.length >= 2) {
    var last = values[values.length - 1];
    var prev = values[values.length - 2];
    if (prev !== 0 && last !== 0) {
      var change = ((last - prev) / Math.abs(prev) * 100);
      var arrow = change > 0 ? '\u2191' : change < 0 ? '\u2193' : '\u2192';
      var colorClass = change > 0 ? 'trend-up' : change < 0 ? 'trend-down' : 'trend-flat';
      trendHtml = '<span class="trend-indicator ' + colorClass + '">' + arrow + ' ' + Math.abs(change).toFixed(1) + '%</span>';
    }
  }

  var overallHtml = '';
  if (values.length >= 2) {
    var firstV = values[0];
    var lastV = values[values.length - 1];
    if (firstV !== 0 && lastV !== 0) {
      var changeAll = ((lastV - firstV) / Math.abs(firstV) * 100);
      var multiplier = (lastV / firstV).toFixed(1);
      overallHtml = '<span class="overall-change">\u5168\u7A0B: ' + firstV + ' \u2192 ' + lastV + ' (' + (changeAll > 0 ? '+' : '') + changeAll.toFixed(0) + '%, ' + multiplier + 'x)</span>';
    }
  }

  if (!compact && (trendHtml || overallHtml)) {
    var chartCard = container.parentElement;
    var existing = chartCard.querySelector('.chart-trend-info');
    if (!existing) {
      var div = document.createElement('div');
      div.className = 'chart-trend-info';
      div.innerHTML = trendHtml + ' ' + overallHtml;
      container.parentNode.insertBefore(div, container);
    }
  }

  var datasets = [];
  var scalesConfig = {
    y: {
      beginAtZero: isBar || (values.every(function(v) { return v >= 0; })),
      grid: { color: 'rgba(0,0,0,0.06)' },
      ticks: { font: { size: 11 } }
    },
    x: {
      grid: { display: false },
      ticks: {
        font: { size: 10 },
        maxRotation: compact ? 0 : 45,
        autoSkip: true,
        maxTicksLimit: compact ? 6 : 14
      }
    }
  };

  if (isDual) {
    // 二阶导图表：柱状图(量) + 曲线(增速)
    var growthRates = [];
    for (var i = 0; i < values.length; i++) {
      if (i === 0) {
        growthRates.push(null);
      } else {
        var prevVal = values[i - 1];
        if (prevVal !== 0) {
          growthRates.push(((values[i] - prevVal) / Math.abs(prevVal)) * 100);
        } else {
          growthRates.push(null);
        }
      }
    }

    datasets.push({
      type: 'bar',
      label: metric.name + ' (\u91CF)',
      data: values,
      backgroundColor: color + '70',
      borderColor: color,
      borderWidth: 1,
      yAxisID: 'y',
      order: 2
    });

    datasets.push({
      type: 'line',
      label: metric.name + ' (\u73AF\u6BD4\u589E\u901F%)',
      data: growthRates,
      borderColor: '#ef4444',
      backgroundColor: 'rgba(239,68,68,0.1)',
      borderWidth: 2.5,
      fill: false,
      tension: 0.3,
      pointBackgroundColor: '#ef4444',
      pointBorderColor: '#fff',
      pointBorderWidth: 1.5,
      pointRadius: compact ? 3 : 5,
      pointHoverRadius: 7,
      yAxisID: 'y1',
      order: 1
    });

    scalesConfig.y1 = {
      type: 'linear',
      position: 'right',
      grid: { drawOnChartArea: false },
      ticks: {
        font: { size: 11 },
        callback: function(value) { return value + '%'; }
      },
      title: {
        display: !compact,
        text: '\u73AF\u6BD4\u589E\u901F (%)',
        font: { size: 11 }
      }
    };

    scalesConfig.y.title = {
      display: !compact,
      text: metric.unit || '',
      font: { size: 11 }
    };
  } else {
    // 普通折线图或柱状图
    datasets.push({
      type: isBar ? 'bar' : 'line',
      label: metric.name,
      data: values,
      borderColor: color,
      backgroundColor: isBar ? color + '80' : color + '15',
      borderWidth: 2,
      fill: !isBar,
      tension: 0.3,
      pointBackgroundColor: color,
      pointBorderColor: '#fff',
      pointBorderWidth: 1.5,
      pointRadius: compact ? 3 : 5,
      pointHoverRadius: 7
    });
  }

  var config = {
    type: isDual ? 'bar' : (isBar ? 'bar' : 'line'),
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          display: isDual,
          position: 'top',
          labels: { font: { size: 11 }, boxWidth: 12 }
        },
        tooltip: {
          backgroundColor: 'rgba(0,0,0,0.85)',
          titleFont: { size: 13 },
          bodyFont: { size: 12 },
          padding: 10,
          callbacks: {
            label: function(ctx) {
              var dp = data[ctx.dataIndex];
              var label = ctx.dataset.label + ': ' + ctx.parsed.y;
              if (ctx.dataset.yAxisID === 'y1') {
                label = ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(1) + '%';
              } else {
                label = ctx.dataset.label + ': ' + dp.value + ' ' + (metric.unit || '');
              }
              if (dp && dp.source) label += '\n\u6765\u6E90: ' + dp.source;
              return label;
            }
          }
        }
      },
      scales: scalesConfig
    }
  };

  charts[id] = new Chart(ctx, config);

  // 渲染数据表格
  if (!compact) {
    renderDataTable(metric, container);
  }
}

// ==================== 组合图表（多指标同坐标） ====================

function renderCombinedChart(metric, containerId, compact) {
  var id = containerId || ('chart_' + metric.id);
  var container = document.getElementById(id);
  if (!container) return;
  if (!metric.combinedSeries || metric.combinedSeries.length === 0) return;

  // 合并所有日期标签
  var allDates = [];
  metric.combinedSeries.forEach(function(series) {
    series.data.forEach(function(d) {
      if (allDates.indexOf(d.date) === -1) allDates.push(d.date);
    });
  });
  allDates.sort();

  var labels = allDates.map(function(d) {
    return d;
  });

  var datasets = [];
  metric.combinedSeries.forEach(function(series) {
    var dataMap = {};
    series.data.forEach(function(d) { dataMap[d.date] = d; });

    var values = allDates.map(function(date) {
      return dataMap[date] ? dataMap[date].value : null;
    });

    datasets.push({
      type: 'line',
      label: series.name,
      data: values,
      borderColor: series.color,
      backgroundColor: series.color + '15',
      borderWidth: 2.5,
      fill: false,
      tension: 0.3,
      pointBackgroundColor: series.color,
      pointBorderColor: '#fff',
      pointBorderWidth: 1.5,
      pointRadius: compact ? 3 : 5,
      pointHoverRadius: 7,
      spanGaps: true
    });
  });

  var height = compact ? '200px' : '380px';
  container.innerHTML = '<canvas id="' + id + '_canvas" style="max-height:' + height + '"></canvas>';
  var ctx = document.getElementById(id + '_canvas');
  if (!ctx) return;

  // 交叉点标注
  var annotationHtml = '';
  if (metric.signal) {
    annotationHtml = '<div class="metric-signal-text" style="margin-top:8px">\u26A0 ' + metric.signal + '</div>';
  }

  var config = {
    type: 'line',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: { font: { size: 12 }, boxWidth: 15 }
        },
        tooltip: {
          backgroundColor: 'rgba(0,0,0,0.85)',
          titleFont: { size: 13 },
          bodyFont: { size: 12 },
          padding: 10,
          callbacks: {
            label: function(ctx) {
              var series = metric.combinedSeries[ctx.datasetIndex];
              var date = allDates[ctx.dataIndex];
              var dp = series.data.find(function(d) { return d.date === date; });
              var label = ctx.dataset.label + ': ' + ctx.parsed.y + ' ' + (metric.unit || '');
              if (dp && dp.source) label += '\n\u6765\u6E90: ' + dp.source;
              return label;
            }
          }
        }
      },
      scales: {
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { font: { size: 11 } },
          title: {
            display: !compact,
            text: metric.unit || '',
            font: { size: 11 }
          }
        },
        x: {
          grid: { display: false },
          ticks: {
            font: { size: 10 },
            maxRotation: compact ? 0 : 45,
            autoSkip: true,
            maxTicksLimit: compact ? 6 : 14
          }
        }
      }
    }
  };

  charts[id] = new Chart(ctx, config);

  if (!compact && metric.signal) {
    var existing = container.parentElement.querySelector('.combined-signal');
    if (!existing) {
      var div = document.createElement('div');
      div.className = 'combined-signal metric-signal-text';
      div.style.marginTop = '8px';
      div.innerHTML = '\u26A0 ' + metric.signal;
      container.parentNode.insertBefore(div, container.nextSibling);
    }
  }
}

// ==================== Guidance 图表（实际 vs 指引 vs 预期） ====================

function renderGuidanceChart(metric, containerId, compact) {
  var id = containerId || ('chart_' + metric.id);
  var container = document.getElementById(id);
  if (!container) return;
  if (!metric.guidanceData || metric.guidanceData.length === 0) return;

  var labels = metric.guidanceData.map(function(d) { return d.date; });

  var datasets = [
    {
      type: 'bar',
      label: '\u5B9E\u9645\u503C',
      data: metric.guidanceData.map(function(d) { return d.actual; }),
      backgroundColor: 'rgba(59,130,246,0.7)',
      borderColor: '#3b82f6',
      borderWidth: 1,
      order: 3
    },
    {
      type: 'line',
      label: '\u516C\u53F8\u6307\u5F15',
      data: metric.guidanceData.map(function(d) { return d.guidance; }),
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245,158,11,0.1)',
      borderWidth: 2.5,
      fill: false,
      tension: 0.3,
      pointBackgroundColor: '#f59e0b',
      pointBorderColor: '#fff',
      pointBorderWidth: 1.5,
      pointRadius: compact ? 3 : 5,
      pointHoverRadius: 7,
      borderDash: [6, 3],
      spanGaps: true,
      order: 2
    },
    {
      type: 'line',
      label: '\u4E00\u81F4\u9884\u671F',
      data: metric.guidanceData.map(function(d) { return d.consensus; }),
      borderColor: '#10b981',
      backgroundColor: 'rgba(16,185,129,0.1)',
      borderWidth: 2.5,
      fill: false,
      tension: 0.3,
      pointBackgroundColor: '#10b981',
      pointBorderColor: '#fff',
      pointBorderWidth: 1.5,
      pointRadius: compact ? 3 : 5,
      pointHoverRadius: 7,
      borderDash: [2, 2],
      spanGaps: true,
      order: 1
    }
  ];

  var height = compact ? '200px' : '380px';
  container.innerHTML = '<canvas id="' + id + '_canvas" style="max-height:' + height + '"></canvas>';
  var ctx = document.getElementById(id + '_canvas');
  if (!ctx) return;

  // 超预期/低于预期标注
  var surpriseHtml = '';
  if (!compact) {
    var lastActual = null;
    var lastConsensus = null;
    var lastDate = '';
    for (var i = metric.guidanceData.length - 1; i >= 0; i--) {
      if (metric.guidanceData[i].actual != null) {
        lastActual = metric.guidanceData[i].actual;
        lastConsensus = metric.guidanceData[i].consensus;
        lastDate = metric.guidanceData[i].date;
        break;
      }
    }
    if (lastActual != null && lastConsensus != null) {
      var surprise = ((lastActual - lastConsensus) / lastConsensus * 100);
      var surpriseText = surprise > 0 ? '\u8D85\u9884\u671F +' + surprise.toFixed(1) + '%' : '\u4F4E\u4E8E\u9884\u671F ' + surprise.toFixed(1) + '%';
      var surpriseColor = surprise > 0 ? '#10b981' : '#ef4444';
      surpriseHtml = '<div style="margin-top:8px;font-size:12px;color:' + surpriseColor + ';font-weight:600">\u6700\u65B0\u5B63\u5EA6 (' + lastDate + '): \u5B9E\u9645 ' + lastActual + ' vs \u9884\u671F ' + lastConsensus + ' = ' + surpriseText + '</div>';
    }
  }

  var config = {
    type: 'bar',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: { font: { size: 12 }, boxWidth: 15 }
        },
        tooltip: {
          backgroundColor: 'rgba(0,0,0,0.85)',
          titleFont: { size: 13 },
          bodyFont: { size: 12 },
          padding: 10,
          callbacks: {
            label: function(ctx) {
              var dp = metric.guidanceData[ctx.dataIndex];
              var label = ctx.dataset.label + ': ';
              if (ctx.parsed.y == null) {
                label += '\u672A\u516C\u5E03';
              } else {
                label += ctx.parsed.y + ' ' + (metric.unit || '');
              }
              if (dp && dp.actual != null && dp.consensus != null) {
                var diff = ((dp.actual - dp.consensus) / dp.consensus * 100).toFixed(1);
                label += ' (\u5DEE\u5F02 ' + (diff > 0 ? '+' : '') + diff + '%)';
              }
              return label;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { font: { size: 11 } },
          title: {
            display: !compact,
            text: metric.unit || '',
            font: { size: 11 }
          }
        },
        x: {
          grid: { display: false },
          ticks: {
            font: { size: 10 },
            maxRotation: compact ? 0 : 45,
            autoSkip: true,
            maxTicksLimit: compact ? 6 : 14
          }
        }
      }
    }
  };

  charts[id] = new Chart(ctx, config);

  if (!compact && surpriseHtml) {
    var existing = container.parentElement.querySelector('.guidance-surprise');
    if (!existing) {
      var div = document.createElement('div');
      div.className = 'guidance-surprise';
      div.innerHTML = surpriseHtml;
      container.parentNode.insertBefore(div, container.nextSibling);
    }
  }
}

// ==================== 数据表格 ====================

function renderDataTable(metric, container) {
  var tableId = 'table_' + metric.id;
  var tableContainer = document.getElementById(tableId);
  if (!tableContainer || !metric.data || metric.data.length === 0) return;

  var html = '<details class="data-table-details"><summary>\u67E5\u770B\u539F\u59CB\u6570\u636E\u8868 (' + metric.data.length + ' \u6761)</summary>' +
    '<div class="data-table-scroll"><table class="data-table"><thead><tr>' +
    '<th>\u65E5\u671F</th><th>\u6570\u503C</th><th>\u5355\u4F4D</th><th>\u6765\u6E90</th><th>\u5907\u6CE8</th><th>\u64CD\u4F5C</th>' +
    '</tr></thead><tbody>';

  // 逆序显示（最新在上）
  var sortedData = metric.data.slice().reverse();
  sortedData.forEach(function(d, idx) {
    var realIndex = metric.data.length - 1 - idx;
    html += '<tr>' +
      '<td>' + (d.date || '') + '</td>' +
      '<td class="num">' + d.value + '</td>' +
      '<td>' + (metric.unit || '') + '</td>' +
      '<td>' + (d.source || metric.source || '') + '</td>' +
      '<td>' + (d.label || '') + '</td>' +
      '<td><button class="btn-del" onclick="deleteDataPoint(\'' + metric.id + '\',' + realIndex + ')">\u5220\u9664</button></td>' +
    '</tr>';
  });

  html += '</tbody></table></div></details>';
  tableContainer.innerHTML = html;
}

// ==================== 信号卡片 ====================

function renderSignalCard(metric) {
  var container = document.getElementById('signal_list_' + metric.id);
  if (!container || !metric.signalItems) return;

  var html = '';
  metric.signalItems.forEach(function(item, idx) {
    var statusClass = item.status === 'confirmed' ? 'signal-confirmed' :
                        item.status === 'monitoring' ? 'signal-monitoring' : 'signal-not-triggered';
    html += '<div class="signal-item ' + statusClass + '">' +
      '<div class="signal-item-header">' +
        '<span class="signal-dot"></span>' +
        '<span class="signal-item-name">' + item.name + '</span>' +
        '<select class="signal-select" onchange="updateSignalStatus(\'' + metric.id + '\',' + idx + ',this.value)">' +
          '<option value="not_triggered" ' + (item.status === 'not_triggered' ? 'selected' : '') + '>\u672A\u89E6\u53D1</option>' +
          '<option value="monitoring" ' + (item.status === 'monitoring' ? 'selected' : '') + '>\u76D1\u63A7\u4E2D</option>' +
          '<option value="confirmed" ' + (item.status === 'confirmed' ? 'selected' : '') + '>\u5DF2\u786E\u8BA4</option>' +
          '<option value="resolved" ' + (item.status === 'resolved' ? 'selected' : '') + '>\u5DF2\u89E3\u9664</option>' +
        '</select>' +
      '</div>' +
      '<div class="signal-item-detail">' + item.detail + '</div>' +
    '</div>';
  });
  container.innerHTML = html;
}

function updateSignalStatus(metricId, index, status) {
  var metric = findMetric(metricId);
  if (metric && metric.signalItems) {
    metric.signalItems[index].status = status;
    saveData();
    renderSignalCard(metric);
    showToast('\u4FE1\u53F7\u72B6\u6001\u5DF2\u66F4\u65B0');
  }
}

// ==================== 数据录入 ====================

function openDataModal(metricId) {
  var metric = findMetric(metricId);
  if (!metric) return;

  var suggestedDate = '';
  if (metric.data && metric.data.length > 0) {
    suggestedDate = metric.data[metric.data.length - 1].date;
  }

  document.getElementById('modalMetricId').value = metricId;
  document.getElementById('modalTitle').textContent = '\u6DFB\u52A0\u6570\u636E\u70B9';
  document.getElementById('modalSubtitle').textContent = metric.name + ' (' + metric.unit + ')';
  document.getElementById('dataDate').value = suggestedDate;
  document.getElementById('dataLabel').value = '';
  document.getElementById('dataValue').value = '';
  document.getElementById('dataSource').value = metric.source || '';

  document.getElementById('dataModal').classList.add('show');
  document.getElementById('dataValue').focus();
}

function closeModal() {
  document.getElementById('dataModal').classList.remove('show');
}

function saveDataPoint() {
  var metricId = document.getElementById('modalMetricId').value;
  var metric = findMetric(metricId);
  if (!metric) return;

  var date = document.getElementById('dataDate').value.trim();
  var value = parseFloat(document.getElementById('dataValue').value);
  var label = document.getElementById('dataLabel').value.trim();
  var source = document.getElementById('dataSource').value.trim();

  if (!date || isNaN(value)) {
    showToast('\u8BF7\u586B\u5199\u65E5\u671F\u548C\u6570\u503C', 'error');
    return;
  }

  var dp = { date: date, value: value, label: label || date, source: source || '' };
  metric.data.push(dp);
  metric.data.sort(function(a, b) { return (a.date || '').localeCompare(b.date || ''); });

  saveData();
  closeModal();
  buildSidebar();
  renderSection(currentSectionId);
  showToast('\u6570\u636E\u5DF2\u4FDD\u5B58');
}

function deleteDataPoint(metricId, index) {
  var metric = findMetric(metricId);
  if (!metric) return;
  metric.data.splice(index, 1);
  saveData();
  buildSidebar();
  renderSection(currentSectionId);
  showToast('\u6570\u636E\u5DF2\u5220\u9664');
}

function findMetric(id) {
  for (var i = 0; i < appData.sections.length; i++) {
    var m = appData.sections[i].metrics.find(function(m) { return m.id === id; });
    if (m) return m;
  }
  return null;
}

// ==================== 导入导出 ====================

function exportJSON() {
  var dataStr = JSON.stringify(appData, null, 2);
  var blob = new Blob([dataStr], { type: 'application/json' });
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = 'ai_industry_timeseries_' + new Date().toISOString().split('T')[0] + '.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('JSON \u5DF2\u5BFC\u51FA');
}

function exportAllCSV() {
  var csv = '\uFEFF\u6307\u6807\u540D\u79F0,\u65E5\u671F,\u6570\u503C,\u5355\u4F4D,\u6765\u6E90,\u5907\u6CE8,\u5B9A\u4E49,\u516C\u5F0F,\u76D1\u6D4B\u610F\u4E49\n';
  appData.sections.forEach(function(sec) {
    sec.metrics.forEach(function(m) {
      if (m.data && m.data.length > 0) {
        m.data.forEach(function(d) {
          csv += '"' + m.name + '","' + (d.date || '') + '","' + d.value + '","' + (m.unit || '') + '","' + (d.source || m.source || '') + '","' + (d.label || '') + '","' + (m.definition || '').replace(/"/g, '""') + '","' + (m.formula || '').replace(/"/g, '""') + '","' + (m.significance || '').replace(/"/g, '""') + '"\n';
        });
      } else if (m.combinedSeries) {
        m.combinedSeries.forEach(function(series) {
          series.data.forEach(function(d) {
            csv += '"' + m.name + ' - ' + series.name + '","' + (d.date || '') + '","' + d.value + '","' + (m.unit || '') + '","' + (d.source || '') + '","' + (d.label || '') + '","","",""\n';
          });
        });
      } else if (m.guidanceData) {
        m.guidanceData.forEach(function(d) {
          csv += '"' + m.name + '","' + (d.date || '') + '","actual=' + (d.actual != null ? d.actual : 'N/A') + ' guidance=' + (d.guidance != null ? d.guidance : 'N/A') + ' consensus=' + (d.consensus != null ? d.consensus : 'N/A') + '","' + (m.unit || '') + '","' + (m.source || '') + '","","","",""\n';
        });
      }
    });
  });

  var blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = 'ai_industry_all_data_' + new Date().toISOString().split('T')[0] + '.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('CSV \u5DF2\u5BFC\u51FA\uFF08\u542B\u5B9A\u4E49/\u516C\u5F0F/\u610F\u4E49\uFF09');
}

function importJSON(event) {
  var file = event.target.files[0];
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function(e) {
    try {
      var imported = JSON.parse(e.target.result);
      if (imported.sections && imported.sections.length > 0) {
        appData = imported;
        saveData();
        charts = {};
        buildSidebar();
        renderSection('overview');
        showToast('\u6570\u636E\u5BFC\u5165\u6210\u529F');
      } else {
        showToast('\u6570\u636E\u683C\u5F0F\u4E0D\u6B63\u786E', 'error');
      }
    } catch (err) {
      showToast('\u5BFC\u5165\u5931\u8D25: ' + err.message, 'error');
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

function resetData() {
  if (!confirm('\u786E\u5B9A\u8981\u91CD\u7F6E\u4E3A\u521D\u59CB\u6570\u636E\uFF1F\u6240\u6709\u624B\u52A8\u6DFB\u52A0\u7684\u6570\u636E\u5C06\u4E22\u5931\u3002')) return;
  appData = deepClone(FRAMEWORK_DATA);
  saveData();
  charts = {};
  buildSidebar();
  renderSection(currentSectionId);
  showToast('\u5DF2\u91CD\u7F6E\u4E3A\u521D\u59CB\u6570\u636E v4');
}

// ==================== Toast ====================

function showToast(msg, type) {
  var toast = document.createElement('div');
  toast.className = 'toast ' + (type === 'error' ? 'toast-error' : 'toast-success');
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(function() { toast.classList.add('show'); }, 10);
  setTimeout(function() {
    toast.classList.remove('show');
    setTimeout(function() { toast.remove(); }, 300);
  }, 2500);
}

// ==================== 启动 ====================
document.addEventListener('DOMContentLoaded', init);
