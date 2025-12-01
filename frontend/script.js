// 全局变量
let currentSection = 'dashboard';
let apiStatus = 'unknown';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadSettings();
    updateStats();
    checkApiStatus();
});

// 初始化应用
function initializeApp() {
    // 设置导航点击事件
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1);
            showSection(target);
        });
    });

    // 测试后端状态
    const testStatusBtn = document.getElementById('test-status-btn');
    const statusOutput = document.getElementById('status-output');

    if (testStatusBtn) {
        testStatusBtn.addEventListener('click', async () => {
            statusOutput.textContent = '检测中...';
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                statusOutput.textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                statusOutput.textContent = 'Error: ' + err.message;
            }
        });
    }

    // 开始分析
    const startAnalysisBtn = document.getElementById('start-analysis-btn');
    const logDirInput = document.getElementById('log-dir-input');
    const enableAiCheckbox = document.getElementById('enable-ai-checkbox');
    const analysisOutput = document.getElementById('analysis-output');
    const runDiagnoseBtn = document.getElementById('run-diagnose-btn');
    const issueTimeInput = document.getElementById('issue-time-input');
    const issueDescInput = document.getElementById('issue-desc-input');
    const diagnoseWindowInput = document.getElementById('diagnose-window-input');
    const diagnoseOutput = document.getElementById('diagnose-output');

    if (startAnalysisBtn) {
        startAnalysisBtn.addEventListener('click', async () => {
            if (!logDirInput || !analysisOutput) return;
            
            // 显示加载状态和禁用按钮
            analysisOutput.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>正在进行深度分析，请稍候...</p>
                    <div class="progress-bar">
                        <div class="progress-fill" id="analysis-progress"></div>
                    </div>
                    <div class="progress-steps">
                        <span class="step active">🔍 扫描日志文件</span>
                        <span class="step">📊 执行综合分析</span>
                        <span class="step">🤖 AI增强处理</span>
                        <span class="step">📋 生成报告</span>
                    </div>
                </div>
            `;
            
            startAnalysisBtn.disabled = true;
            
            // 修复的进度条更新
            let progress = 0;
            let step = 0;
            const steps = [0, 33, 66, 100]; // 四个关键进度点，对应四个步骤
            
            // 更新进度条和步骤显示
            const updateProgress = () => {
                const progressFill = document.getElementById('analysis-progress');
                const progressSteps = document.querySelectorAll('.progress-steps .step');
                
                if (progressFill) {
                    progressFill.style.width = `${progress}%`;
                }
                
                // 更新步骤状态
                progressSteps.forEach((stepEl, index) => {
                    if (index < step) {
                        stepEl.classList.add('completed');
                        stepEl.classList.remove('active');
                    } else if (index === step) {
                        stepEl.classList.add('active');
                        stepEl.classList.remove('completed');
                    } else {
                        stepEl.classList.remove('active', 'completed');
                    }
                });
            };
            
            // 平滑的进度更新
            const progressInterval = setInterval(() => {
                // 逐步增加进度
                progress += Math.random() * 8 + 2; // 每次增加2-10%
                
                // 确保进度不超过100%
                if (progress > 100) {
                    progress = 100;
                    clearInterval(progressInterval);
                }
                
                // 更新步骤
                if (progress >= steps[step + 1] && step < steps.length - 1) {
                    step++;
                }
                
                // 更新进度条和步骤
                updateProgress();
            }, 400);
            
            try {
                // 获取报告类型选择
                const reportTypeSelect = document.getElementById('report-type-select');
                const reportType = reportTypeSelect ? reportTypeSelect.value : 'enhanced';
                
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        log_directory: logDirInput.value || './logs',
                        enable_ai: enableAiCheckbox ? enableAiCheckbox.checked : true, // 默认启用AI
                        report_type: reportType // 使用选择的报告类型
                    })
                });
                
                clearInterval(progressInterval);
                startAnalysisBtn.disabled = false;
                
                // 完成进度条
                const progressFill = document.getElementById('analysis-progress');
                if (progressFill) {
                    progressFill.style.width = '100%';
                }
                
                const data = await res.json();
                
                // 更新进度步骤
                const steps = document.querySelectorAll('.progress-steps .step');
                steps.forEach(step => step.classList.remove('active'));
                
                if (data.status === 'success') {
                    // 分析成功，显示丰富的结果
                    const summaryInfo = data.summary || {};
                    const detailsInfo = data.analysis_details || {};
                    
                    analysisOutput.innerHTML = `
                        <div class="result-success">
                            <div class="success-header">
                                <h4>🎉 ${data.message || '综合分析完成'}</h4>
                                <div class="analysis-type-badge ${data.analysis_type}">${data.analysis_type.toUpperCase()}</div>
                            </div>
                            
                            <div class="summary-grid">
                                <div class="summary-card">
                                    <div class="card-icon">📁</div>
                                    <div class="card-content">
                                        <div class="card-value">${detailsInfo.log_files_analyzed || 0}</div>
                                        <div class="card-label">分析日志文件</div>
                                    </div>
                                </div>
                                
                                <div class="summary-card">
                                    <div class="card-icon">⚠️</div>
                                    <div class="card-content">
                                        <div class="card-value">${detailsInfo.anomalies_detected || 0}</div>
                                        <div class="card-label">检测到异常</div>
                                    </div>
                                </div>
                                
                                <div class="summary-card">
                                    <div class="card-icon">🔧</div>
                                    <div class="card-content">
                                        <div class="card-value">${detailsInfo.task_segments_found || 0}</div>
                                        <div class="card-label">任务分段</div>
                                    </div>
                                </div>
                                
                                <div class="summary-card">
                                    <div class="card-icon">🤖</div>
                                    <div class="card-content">
                                        <div class="card-value">${detailsInfo.ai_enhanced ? '已启用' : '未启用'}</div>
                                        <div class="card-label">AI增强</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="report-section">
                                <h5>📋 生成的分析报告</h5>
                                <div class="report-links">
                                    ${data.paths.json ? `
                                        <a href="/api/report?path=${encodeURIComponent(data.paths.json)}" target="_blank" class="report-link">
                                            📄 集成JSON报告
                                        </a>
                                    ` : ''}
                                    
                                    ${data.paths.html ? `
                                        <button onclick="openHtmlReport('${encodeURIComponent(data.paths.html)}')" class="report-link html-report">
                                            🌐 可视化HTML报告
                                        </button>
                                    ` : ''}
                                    
                                    ${data.paths.deepseek_html ? `
                                        <button onclick="openHtmlReport('${encodeURIComponent(data.paths.deepseek_html)}')" class="report-link deepseek-report">
                                            🤖 DeepSeek增强报告
                                        </button>
                                    ` : ''}
                                    
                                    ${data.paths.comprehensive_json ? `
                                        <a href="/api/report?path=${encodeURIComponent(data.paths.comprehensive_json)}" target="_blank" class="report-link">
                                            📊 综合分析报告
                                        </a>
                                    ` : ''}
                                    
                                    ${data.paths.historical_json ? `
                                        <a href="/api/report?path=${encodeURIComponent(data.paths.historical_json)}" target="_blank" class="report-link">
                                            📈 历史追溯报告
                                        </a>
                                    ` : ''}
                                    
                                    ${data.paths.complaint_json ? `
                                        <a href="/api/report?path=${encodeURIComponent(data.paths.complaint_json)}" target="_blank" class="report-link complaint-report">
                                            🗣️ 投诉分析报告
                                        </a>
                                    ` : ''}
                                </div>
                            </div>
                            
                            <div class="analysis-metadata">
                                <p><strong>报告ID:</strong> ${data.report_id}</p>
                                <p><strong>分析时间:</strong> ${new Date().toLocaleString('zh-CN')}</p>
                                <p><strong>日志目录:</strong> ${logDirInput.value || './logs'}</p>
                            </div>
                        </div>
                    `;
                    
                    // 刷新报告列表
                    loadReports();
                    
                } else {
                    // 分析失败
                    analysisOutput.innerHTML = `
                        <div class="result-error">
                            <h4>❌ 分析失败</h4>
                            <p>${data.message || '未知错误'}</p>
                            ${data.error_details ? `
                                <div class="error-details">
                                    <h5>详细信息:</h5>
                                    <pre>${JSON.stringify(data.error_details, null, 2)}</pre>
                                </div>
                            ` : ''}
                        </div>
                    `;
                }
            } catch (err) {
                clearInterval(progressInterval);
                startAnalysisBtn.disabled = false;
                
                analysisOutput.innerHTML = `
                    <div class="result-error">
                        <h4>🚫 网络错误</h4>
                        <p>无法连接到分析服务: ${err.message}</p>
                        <div class="error-suggestions">
                            <p><strong>建议:</strong></p>
                            <ul>
                                <li>检查网络连接</li>
                                <li>确认后端服务是否正常运行</li>
                                <li>验证日志目录是否存在</li>
                            </ul>
                        </div>
                    </div>
                `;
            }
        });
    }

    if (runDiagnoseBtn && diagnoseOutput) {
        runDiagnoseBtn.addEventListener('click', async () => {
            if (!issueTimeInput) return;

            const issueTime = issueTimeInput.value.trim();
            if (!issueTime) {
                diagnoseOutput.innerHTML = `<p class="badge warning">⚠️ 请先输入问题时间 (YYYY-MM-DD HH:MM:SS)</p>`;
                issueTimeInput.focus();
                return;
            }

            const windowMinutes = parseInt((diagnoseWindowInput && diagnoseWindowInput.value) || '10', 10) || 10;
            const description = issueDescInput ? issueDescInput.value.trim() : '';

            runDiagnoseBtn.disabled = true;
            diagnoseOutput.innerHTML = `
                <div class="diagnose-loading">
                    <div class="spinner"></div>
                    <p>正在检索日志并请求AI诊断，请稍候...</p>
                </div>
            `;

            try {
                const res = await fetch('/api/diagnose', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        issue_time: issueTime,
                        description,
                        window: windowMinutes
                    })
                });

                const data = await res.json();

                if (data.status === 'success') {
                    const logsBlock = data.logs_preview ? `
                        <details class="logs-preview" ${data.logs_found ? 'open' : ''}>
                            <summary>相关日志片段 (${data.logs_found ? '已匹配' : '未匹配'})</summary>
                            <pre>${escapeHtml(data.logs_preview)}</pre>
                        </details>
                    ` : `<p class="text-muted">未匹配到相关日志，请检查时间是否正确。</p>`;

                    const ai = data.ai_analysis || {};
                    const aiBlock = ai.error ? `
                        <div class="ai-response">
                            <p class="badge warning">🤖 AI调用失败</p>
                            <pre>${escapeHtml(ai.error)}</pre>
                        </div>
                    ` : `
                        <div class="ai-response">
                            <p class="badge success">🤖 AI诊断完成</p>
                            <pre>${escapeHtml(ai.raw || '（模型未返回内容）')}</pre>
                        </div>
                    `;

                    diagnoseOutput.innerHTML = `
                        <div class="diagnose-result">
                            <div>
                                <span class="badge success">⏱ 问题时间: ${issueTime}</span>
                                <span class="badge success">🕑 时间窗口: ±${windowMinutes} 分钟</span>
                            </div>
                            ${logsBlock}
                            ${aiBlock}
                        </div>
                    `;
                } else {
                    diagnoseOutput.innerHTML = `
                        <div class="diagnose-result">
                            <p class="badge warning">❌ 诊断失败</p>
                            <pre>${escapeHtml(data.message || '未知错误')}</pre>
                        </div>
                    `;
                }
            } catch (err) {
                diagnoseOutput.innerHTML = `
                    <div class="diagnose-result">
                        <p class="badge warning">🚫 网络错误</p>
                        <pre>${escapeHtml(err.message)}</pre>
                        <p class="text-muted">请检查后端服务是否运行、网络是否可用。</p>
                    </div>
                `;
            } finally {
                runDiagnoseBtn.disabled = false;
            }
        });
    }

    // 刷新报告列表
    const refreshReportsBtn = document.getElementById('refresh-reports-btn');
    const reportsList = document.getElementById('reports-list');
    const noReportsDiv = document.getElementById('no-reports');

    if (refreshReportsBtn) {
        refreshReportsBtn.addEventListener('click', async () => {
            if (!reportsList) return;
            
            reportsList.innerHTML = '<li class="loading">加载中...</li>';
            try {
                const res = await fetch('/api/reports');
                const data = await res.json();
                reportsList.innerHTML = '';
                
                if (data.length === 0) {
                    if (noReportsDiv) noReportsDiv.style.display = 'block';
                } else {
                    if (noReportsDiv) noReportsDiv.style.display = 'none';
                    data.forEach(item => {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <div class="report-info">
                                <span class="report-name">${item.name}</span>
                                <span class="report-meta">${item.size} | ${item.type}</span>
                            </div>
                            <div class="report-actions">
                                <button class="report-btn view" onclick="viewReport('${item.id}')">
                                    <i class="fas fa-eye"></i> 查看
                                </button>
                                <button class="report-btn download" onclick="downloadReport('${item.id}')">
                                    <i class="fas fa-download"></i> 下载
                                </button>
                            </div>
                        `;
                        reportsList.appendChild(li);
                    });
                }
            } catch (err) {
                reportsList.innerHTML = `<li class="error">Error: ${err.message}</li>`;
            }
        });
    }

    // API设置管理
    const apiProvider = document.getElementById('api-provider');
    const apiKey = document.getElementById('api-key');
    const baseUrl = document.getElementById('base-url');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const settingsOutput = document.getElementById('settings-output');

    // 初始化时从 localStorage 读取
    const savedProvider = localStorage.getItem('api_provider');
    const savedKey = localStorage.getItem('api_key');
    const savedBaseUrl = localStorage.getItem('base_url');

    if (savedProvider && apiProvider) apiProvider.value = savedProvider;
    if (savedKey && apiKey) apiKey.value = savedKey;
    if (savedBaseUrl && baseUrl) baseUrl.value = savedBaseUrl;

    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', async () => {
            if (!apiProvider || !apiKey || !baseUrl) return;
            
            const payload = {
                api_provider: apiProvider.value,
                api_key: apiKey.value,
                base_url: baseUrl.value
            };
            
            // 先存 localStorage
            localStorage.setItem('api_provider', payload.api_provider);
            localStorage.setItem('api_key', payload.api_key);
            localStorage.setItem('base_url', payload.base_url);

            // 再同步到后端
            try {
                const res = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (settingsOutput) {
                    settingsOutput.textContent = JSON.stringify(data, null, 2);
                }
            } catch (err) {
                if (settingsOutput) {
                    settingsOutput.textContent = 'Error: ' + err.message;
                }
            }
        });
    }

    // 设置Provider切换事件
    if (apiProvider) {
        apiProvider.addEventListener('change', function() {
            const provider = this.value;
            const baseUrlInput = document.getElementById('base-url');
            if (baseUrlInput) {
                if (provider === 'openai') {
                    baseUrlInput.value = 'https://api.openai.com/v1';
                } else if (provider === 'deepseek') {
                    baseUrlInput.value = 'https://api.deepseek.com/v1';
                }
            }
        });
    }
}

// 显示指定区域
function showSection(sectionId) {
    // 隐藏所有区域
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // 更新导航链接状态
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // 显示目标区域
    const targetSection = document.getElementById(sectionId);
    const targetLink = document.querySelector(`[href="#${sectionId}"]`);
    
    if (targetSection) targetSection.classList.add('active');
    if (targetLink) targetLink.classList.add('active');

    currentSection = sectionId;

    // 特定区域的初始化
    if (sectionId === 'reports') {
        loadReports();
    } else if (sectionId === 'dashboard') {
        updateStats();
    }
}

// 检查API状态
async function checkApiStatus() {
    const statusElement = document.getElementById('apiStatus');
    if (!statusElement) return;

    statusElement.textContent = '检测中...';
    statusElement.className = 'status-badge';

    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'success') {
            statusElement.textContent = '已连接';
            statusElement.className = 'status-badge connected';
            apiStatus = 'connected';
        } else {
            statusElement.textContent = '连接失败';
            statusElement.className = 'status-badge disconnected';
            apiStatus = 'disconnected';
        }
    } catch (error) {
        statusElement.textContent = '连接错误';
        statusElement.className = 'status-badge disconnected';
        apiStatus = 'error';
    }

    // 更新AI状态
    const aiStatusElement = document.getElementById('aiStatus');
    if (aiStatusElement) {
        aiStatusElement.textContent = apiStatus === 'connected' ? '就绪' : '离线';
    }
}

// 加载设置
function loadSettings() {
    // 从后端加载当前设置
    fetch('/api/settings')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success' && data.settings) {
                const apiProvider = document.getElementById('api-provider');
                const baseUrl = document.getElementById('base-url');
                
                if (apiProvider && !localStorage.getItem('api_provider')) {
                    apiProvider.value = data.settings.api_provider || 'openai';
                }
                if (baseUrl && !localStorage.getItem('base_url')) {
                    baseUrl.value = data.settings.base_url || 'https://api.openai.com/v1';
                }
            }
        })
        .catch(err => console.log('加载设置失败:', err));
}

// 更新统计信息
function updateStats() {
    // 更新日志文件数量
    const logCountElement = document.getElementById('logCount');
    if (logCountElement) {
        // 这里可以添加真实的日志文件计数逻辑
        logCountElement.textContent = '25';
    }

    // 更新异常检测数量
    const anomalyCountElement = document.getElementById('anomalyCount');
    if (anomalyCountElement) {
        // 这里可以添加真实的异常计数逻辑
        anomalyCountElement.textContent = '3';
    }

    // 更新报告数量
    const reportCountElement = document.getElementById('reportCount');
    if (reportCountElement) {
        fetch('/api/reports')
            .then(res => res.json())
            .then(data => {
                if (reportCountElement) {
                    reportCountElement.textContent = data.length || '0';
                }
            })
            .catch(() => {
                if (reportCountElement) {
                    reportCountElement.textContent = '0';
                }
            });
    }
}

// 加载报告列表
function loadReports() {
    const refreshBtn = document.getElementById('refresh-reports-btn');
    if (refreshBtn) {
        refreshBtn.click();
    }
}

// 查看报告
function viewReport(reportId) {
    // 根据报告ID构建完整的文件路径
    const reportPath = `./reports/${reportId}.html`;
    
    // 检查是否存在HTML报告，如果存在则打开HTML报告
    fetch(`/api/report?path=${encodeURIComponent(reportPath)}`)
        .then(response => {
            if (response.ok) {
                // HTML报告存在，打开可视化报告
                openHtmlReport(encodeURIComponent(reportPath));
            } else {
                // HTML报告不存在，尝试打开JSON报告
                const jsonPath = `./temp_reports/${reportId}.json`;
                fetch(`/api/report?path=${encodeURIComponent(jsonPath)}`)
                    .then(jsonResponse => {
                        if (jsonResponse.ok) {
                            // 在新标签页打开JSON报告
                            window.open(`/api/report?path=${encodeURIComponent(jsonPath)}`, '_blank');
                        } else {
                            // 尝试其他可能的JSON文件路径
                            const alternativePaths = [
                                `./temp_reports/integrated_${reportId}.json`,
                                `./temp_reports/comprehensive_${reportId}.json`,
                                `./temp_reports/historical_trace_${reportId}.json`
                            ];
                            
                            let found = false;
                            alternativePaths.forEach(path => {
                                if (!found) {
                                    fetch(`/api/report?path=${encodeURIComponent(path)}`)
                                        .then(altResponse => {
                                            if (altResponse.ok) {
                                                window.open(`/api/report?path=${encodeURIComponent(path)}`, '_blank');
                                                found = true;
                                            }
                                        });
                                }
                            });
                            
                            if (!found) {
                                alert(`无法找到报告文件: ${reportId}`);
                            }
                        }
                    });
            }
        })
        .catch(error => {
            console.error('查看报告失败:', error);
            alert(`查看报告失败: ${error.message}`);
        });
}

// 下载报告
function downloadReport(reportId) {
    // 这里可以实现报告下载功能
    window.open(`/api/reports/${reportId}/download`, '_blank');
}

// 打开HTML报告弹出窗口
function openHtmlReport(encodedPath) {
    const reportPath = decodeURIComponent(encodedPath);
    
    // 创建弹出窗口
    const popupWidth = 1200;
    const popupHeight = 800;
    const left = (screen.width - popupWidth) / 2;
    const top = (screen.height - popupHeight) / 2;
    
    const popup = window.open('', 'htmlReportPopup', 
        `width=${popupWidth},height=${popupHeight},left=${left},top=${top},resizable=yes,scrollbars=yes`);
    
    if (popup) {
        // 设置弹出窗口内容
        popup.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>机器人详细分析报告</title>
                <style>
                    body { 
                        margin: 0; 
                        padding: 20px; 
                        font-family: Arial, sans-serif; 
                        background: #f5f5f5;
                    }
                    .container { 
                        max-width: 100%; 
                        margin: 0 auto; 
                        background: white; 
                        border-radius: 10px; 
                        box-shadow: 0 0 10px rgba(0,0,0,0.1); 
                        overflow: hidden;
                    }
                    .header { 
                        background: #007bff; 
                        color: white; 
                        padding: 20px; 
                        text-align: center; 
                    }
                    .loading { 
                        text-align: center; 
                        padding: 100px; 
                        font-size: 18px; 
                    }
                    iframe { 
                        width: 100%; 
                        height: calc(100vh - 80px); 
                        border: none; 
                    }
                    .spinner {
                        width: 40px;
                        height: 40px;
                        margin: 0 auto 1rem;
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #667eea;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    .error-message {
                        color: red;
                        margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>机器人详细分析报告</h1>
                        <p>正在加载增强版详细报告...</p>
                    </div>
                    <iframe src="/api/report?path=${encodedPath}" 
                            onload="this.style.display='block'; document.querySelector('.loading').style.display='none';" 
                            onerror="document.querySelector('.error-message').style.display='block'; document.querySelector('.loading').style.display='none';" 
                            style="display:none;"></iframe>
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>正在加载报告内容，请稍候...</p>
                        <div class="error-message" style="display:none;">
                            <p>报告加载失败，请检查网络连接或报告路径是否正确。</p>
                            <p>报告路径: /api/report?path=${encodedPath}</p>
                            <button onclick="window.location.reload();">重试</button>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        `);
        popup.document.close(); // 确保文档被正确关闭，以便onload事件触发
    } else {
        // 如果弹出窗口被阻止，在新标签页打开
        window.open(`/api/report?path=${encodedPath}`, '_blank');
    }
}

function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

// ==================== 智能Agent诊断功能 ====================

/**
 * 初始化Agent诊断功能
 */
function initAgentDiagnose() {
    const runAgentBtn = document.getElementById('run-agent-diagnose-btn');
    const showKnowledgeBtn = document.getElementById('show-log-knowledge-btn');
    const closeKnowledgeBtn = document.getElementById('close-knowledge-modal');
    const knowledgeModal = document.getElementById('log-knowledge-modal');
    
    if (runAgentBtn) {
        runAgentBtn.addEventListener('click', runAgentDiagnose);
    }
    
    if (showKnowledgeBtn) {
        showKnowledgeBtn.addEventListener('click', showLogKnowledge);
    }
    
    if (closeKnowledgeBtn) {
        closeKnowledgeBtn.addEventListener('click', () => {
            knowledgeModal.style.display = 'none';
        });
    }
    
    // 点击模态框外部关闭
    if (knowledgeModal) {
        knowledgeModal.addEventListener('click', (e) => {
            if (e.target === knowledgeModal) {
                knowledgeModal.style.display = 'none';
            }
        });
    }
}

/**
 * 执行Agent智能诊断
 */
async function runAgentDiagnose() {
    const problemInput = document.getElementById('agent-problem-input');
    const timeInput = document.getElementById('agent-time-input');
    const windowInput = document.getElementById('agent-window-input');
    const maxLinesInput = document.getElementById('agent-max-lines-input');
    const runBtn = document.getElementById('run-agent-diagnose-btn');
    
    const reasoningSection = document.getElementById('agent-reasoning-section');
    const selectedLogsSection = document.getElementById('agent-selected-logs-section');
    const resultSection = document.getElementById('agent-result-section');
    const reasoningSteps = document.getElementById('agent-reasoning-steps');
    const selectedLogs = document.getElementById('agent-selected-logs');
    const analysisContent = document.getElementById('agent-analysis-content');
    
    const problemDesc = problemInput?.value.trim();
    
    if (!problemDesc) {
        alert('请输入问题描述');
        problemInput?.focus();
        return;
    }
    
    // 显示加载状态
    runBtn.disabled = true;
    runBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 诊断中...';
    
    // 重置显示区域
    reasoningSection.style.display = 'block';
    selectedLogsSection.style.display = 'none';
    resultSection.style.display = 'none';
    
    // 显示思考中的动画
    reasoningSteps.innerHTML = `
        <div class="agent-loading">
            <div class="spinner"></div>
            <p>Agent 正在分析问题并选择相关日志...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/agent/diagnose', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                description: problemDesc,
                issue_time: timeInput?.value.trim() || '',
                window: parseInt(windowInput?.value) || 15,
                max_lines_per_file: parseInt(maxLinesInput?.value) || 500
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'error') {
            throw new Error(data.message || '诊断失败');
        }
        
        // 渲染推理过程
        renderReasoningSteps(data.reasoning, reasoningSteps);
        
        // 渲染选中的日志文件
        if (data.selected_logs && data.selected_logs.length > 0) {
            selectedLogsSection.style.display = 'block';
            renderSelectedLogs(data.selected_logs, selectedLogs);
        }
        
        // 渲染AI分析结果
        if (data.ai_analysis) {
            resultSection.style.display = 'block';
            renderAgentAnalysis(data.ai_analysis, analysisContent);
        }
        
    } catch (error) {
        reasoningSteps.innerHTML = `
            <div class="error-message" style="color: #ff6b6b; padding: 1rem;">
                <i class="fas fa-exclamation-triangle"></i> 诊断失败: ${escapeHtml(error.message)}
            </div>
        `;
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = '<i class="fas fa-magic"></i> 智能诊断';
    }
}

/**
 * 渲染Agent推理步骤
 */
function renderReasoningSteps(reasoning, container) {
    if (!reasoning || reasoning.length === 0) {
        container.innerHTML = '<p style="color: #808080;">未获取到推理过程</p>';
        return;
    }
    
    const stepsHtml = reasoning.map((step, index) => `
        <div class="reasoning-step">
            <span class="step-number">${index + 1}</span>
            <span class="step-content">${escapeHtml(step)}</span>
        </div>
    `).join('');
    
    container.innerHTML = stepsHtml;
}

/**
 * 渲染选中的日志文件
 */
function renderSelectedLogs(logs, container) {
    if (!logs || logs.length === 0) {
        container.innerHTML = '<p style="color: #808080;">未选择任何日志文件</p>';
        return;
    }
    
    const logsHtml = logs.map(log => `
        <div class="selected-log-item">
            <i class="fas fa-file-alt"></i>
            <span class="log-name">${escapeHtml(log.file || log.name || log)}</span>
            ${log.reason ? `<span class="log-reason">- ${escapeHtml(log.reason)}</span>` : ''}
        </div>
    `).join('');
    
    container.innerHTML = logsHtml;
}

/**
 * 渲染Agent分析结果
 */
function renderAgentAnalysis(analysis, container) {
    if (!analysis) {
        container.innerHTML = '<p style="color: #808080;">未获取到分析结果</p>';
        return;
    }
    
    // 如果是字符串，直接渲染（可能包含markdown）
    if (typeof analysis === 'string') {
        container.innerHTML = markdownToHtml(analysis);
        return;
    }
    
    // 如果有raw字段（来自AI返回）
    if (analysis.raw) {
        container.innerHTML = markdownToHtml(analysis.raw);
        return;
    }
    
    // 如果有error字段
    if (analysis.error) {
        container.innerHTML = `
            <div style="color: #ff6b6b;">
                <i class="fas fa-exclamation-circle"></i> ${escapeHtml(analysis.error)}
            </div>
        `;
        return;
    }
    
    // 结构化结果
    let html = '';
    
    if (analysis.summary) {
        html += `<h5>📋 总结</h5><p>${escapeHtml(analysis.summary)}</p>`;
    }
    
    if (analysis.root_cause) {
        html += `<h5>🔍 根因分析</h5><p>${escapeHtml(analysis.root_cause)}</p>`;
    }
    
    if (analysis.key_findings && analysis.key_findings.length > 0) {
        html += `<h5>💡 关键发现</h5><ul>`;
        analysis.key_findings.forEach(finding => {
            html += `<li>${escapeHtml(finding)}</li>`;
        });
        html += `</ul>`;
    }
    
    if (analysis.suggestions && analysis.suggestions.length > 0) {
        html += `<h5>🛠️ 建议操作</h5><ul>`;
        analysis.suggestions.forEach(suggestion => {
            html += `<li>${escapeHtml(suggestion)}</li>`;
        });
        html += `</ul>`;
    }
    
    container.innerHTML = html || '<p>分析完成，但无具体内容</p>';
}

/**
 * 简单的Markdown转HTML
 */
function markdownToHtml(text) {
    if (!text) return '';
    
    // 转义HTML
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // 标题
    html = html.replace(/^### (.+)$/gm, '<h5>$1</h5>');
    html = html.replace(/^## (.+)$/gm, '<h5>$1</h5>');
    html = html.replace(/^# (.+)$/gm, '<h5>$1</h5>');
    
    // 粗体
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // 斜体
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // 行内代码
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // 代码块
    html = html.replace(/```[\w]*\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // 列表项
    html = html.replace(/^[\-\*] (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    
    // 数字列表
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    
    // 换行
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    // 包装段落
    if (!html.startsWith('<')) {
        html = '<p>' + html + '</p>';
    }
    
    return html;
}

/**
 * 显示日志知识库
 */
async function showLogKnowledge() {
    const modal = document.getElementById('log-knowledge-modal');
    const content = document.getElementById('log-knowledge-content');
    
    modal.style.display = 'flex';
    content.innerHTML = `
        <div class="agent-loading">
            <div class="spinner"></div>
            <p>加载知识库...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/agent/logs-info');
        const data = await response.json();
        
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        
        const knowledge = data.knowledge_base || {};
        
        let html = `<p style="margin-bottom: 1rem; color: #a0a0a0;">
            共 ${data.log_types_count || Object.keys(knowledge).length} 种日志类型
        </p>`;
        
        for (const [pattern, info] of Object.entries(knowledge)) {
            html += `
                <div class="knowledge-item">
                    <div class="log-pattern">${escapeHtml(pattern)}</div>
                    <div class="log-description">${escapeHtml(info.description || info)}</div>
                    ${info.keywords ? `
                        <div class="log-keywords">
                            ${info.keywords.map(kw => `<span class="keyword-tag">${escapeHtml(kw)}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        content.innerHTML = html;
        
    } catch (error) {
        content.innerHTML = `
            <div style="color: #ff6b6b; padding: 1rem;">
                <i class="fas fa-exclamation-triangle"></i> 加载失败: ${escapeHtml(error.message)}
            </div>
        `;
    }
}

// 页面加载时初始化Agent功能
document.addEventListener('DOMContentLoaded', function() {
    initAgentDiagnose();
});
