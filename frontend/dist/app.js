let diagnosticResults = [];
let isRunning = false;
let showAll = false;
let selectedFilters = ["all"];

const TASK_NAMES = {
    "step1": { name: "网络配置检测", details: ["检测本机IP地址", "检测网关连通性", "检测网卡和DHCP状态"] },
    "step2": { name: "DNS与域名检测", details: ["解析github.com", "解析baidu.com", "检测公共DNS服务器"] },
    "step3": { name: "端口与代理检测", details: ["检测443端口连通性", "检测代理端口状态", "检测系统代理配置"] },
    "step4": { name: "高级网络检测", details: ["检测WiFi信号", "检测MTU设置", "检测防火墙和连接状态"] },
    "step5": { name: "综合分析", details: ["分析诊断结果", "计算健康评分", "生成修复建议"] }
};

function setStepDone(stepId) {
    const step = document.getElementById(stepId);
    step.className = "step-item done";
    step.querySelector(".step-icon").textContent = "✓";
}

function setStepActive(stepId) {
    const step = document.getElementById(stepId);
    step.className = "step-item active";
}

function resetSteps() {
    for (let i = 1; i <= 5; i++) {
        const step = document.getElementById("step" + i);
        step.className = "step-item pending";
        step.querySelector(".step-icon").textContent = i;
    }
}

function showCurrentTask(stepId, detailIndex) {
    const taskInfo = TASK_NAMES[stepId];
    if (taskInfo) {
        document.getElementById("currentTask").style.display = "block";
        document.getElementById("currentTaskName").textContent = taskInfo.name;
        document.getElementById("currentTaskDetail").textContent = taskInfo.details[detailIndex] || "";
    }
}

function hideCurrentTask() {
    document.getElementById("currentTask").style.display = "none";
}

function updateProgress(percent) {
    document.getElementById("progressPercent").textContent = percent + "%";
    document.getElementById("progressFill").style.width = percent + "%";
}

function updateScore(score) {
    document.getElementById("healthScore").textContent = score;
    const circumference = 2 * Math.PI * 65;
    const offset = circumference - (score / 100) * circumference;
    document.getElementById("scoreProgress").style.strokeDashoffset = offset;
}

function updateStatus(id, value, isOk) {
    const el = document.getElementById(id);
    el.textContent = value;
    el.style.color = isOk ? "#22c55e" : "#ef4444";
}

function setButtonsDisabled(disabled) {
    document.getElementById("btnStart").disabled = disabled;
    document.getElementById("btnFix").disabled = disabled;
}

function toggleCard(element) {
    element.classList.toggle("expanded");
}

function renderResults(results, filter) {
    const list = document.getElementById("resultsList");
    
    if (!results || results.length === 0) {
        list.innerHTML = '<div class="empty-state"><div class="empty-icon">...</div><div class="empty-title">尚未执行诊断</div><div class="empty-desc">点击上方开始检测按钮</div></div>';
        document.getElementById("resultsCount").textContent = "";
        return;
    }

    let filtered = results;
    if (!selectedFilters.includes("all")) {
        filtered = results.filter(function(r) {
            if (selectedFilters.indexOf("error") !== -1 && (r.status === "严重" || r.status === "致命")) {
                return true;
            }
            if (selectedFilters.indexOf("warning") !== -1 && r.status === "警告") {
                return true;
            }
            if (selectedFilters.indexOf("success") !== -1 && (r.status === "通过" || r.status === "正常")) {
                return true;
            }
            return false;
        });
    }

    document.getElementById("resultsCount").textContent = "(" + filtered.length + ")";

    if (filtered.length === 0) {
        list.innerHTML = '<div class="empty-state"><div class="empty-icon">-</div><div class="empty-title">没有符合条件的结果</div></div>';
        return;
    }

    const badgeMap = {"致命": "!", "严重": "x", "警告": "/", "正常": "v", "通过": "v", "信息": "i"};
    const severityClass = {"致命": "critical", "严重": "error", "警告": "warning", "正常": "success", "通过": "success", "信息": "info"};
    const displayItems = showAll ? filtered : filtered.slice(0, 12);
    
    let html = "";
    for (let i = 0; i < displayItems.length; i++) {
        const r = displayItems[i];
        const sevClass = severityClass[r.status] || "info";
        const badge = badgeMap[r.status] || "i";
        html += '<div class="result-card ' + sevClass + '" onclick="toggleCard(this)">';
        html += '<div class="result-card-header"><div class="result-badge">' + badge + '</div><div class="result-card-title">' + r.test_name + '</div></div>';
        html += '<div class="result-card-component">' + r.component + '</div>';
        html += '<div class="result-card-message">' + r.message + '</div>';
        if (r.suggestion) {
            html += '<div class="result-card-tip">' + r.suggestion + '</div>';
        }
        html += '</div>';
    }
    list.innerHTML = html;

    if (!showAll && filtered.length > 12) {
        list.innerHTML += '<button class="show-more" onclick="toggleShowAll()">显示全部 ' + filtered.length + ' 项</button>';
    }
}

function toggleShowAll() {
    showAll = !showAll;
    renderResults(diagnosticResults, selectedFilters);
}

function toggleFilter(btn) {
    const filter = btn.dataset.filter;
    
    if (filter === "all") {
        selectedFilters = ["all"];
        const allBtns = document.querySelectorAll(".tab-btn");
        for (let i = 0; i < allBtns.length; i++) {
            allBtns[i].classList.remove("selected");
        }
        const allBtn = document.querySelector('.tab-btn[data-filter="all"]');
        if (allBtn) {
            allBtn.classList.add("selected");
        }
    } else {
        const idx = selectedFilters.indexOf("all");
        if (idx !== -1) {
            selectedFilters.splice(idx, 1);
        }
        
        if (btn.classList.contains("selected")) {
            btn.classList.remove("selected");
            const fIdx = selectedFilters.indexOf(filter);
            if (fIdx !== -1) {
                selectedFilters.splice(fIdx, 1);
            }
            if (selectedFilters.length === 0) {
                selectedFilters = ["all"];
                const allBtn = document.querySelector('.tab-btn[data-filter="all"]');
                if (allBtn) {
                    allBtn.classList.add("selected");
                }
            }
        } else {
            btn.classList.add("selected");
            if (selectedFilters.indexOf(filter) === -1) {
                selectedFilters.push(filter);
            }
        }
    }
    
    renderResults(diagnosticResults, selectedFilters);
    renderFixes();
}

function renderFixes() {
    const fixesList = document.getElementById("fixesList");
    const fixesCount = document.getElementById("fixesCount");
    
    const problems = [];
    for (let i = 0; i < diagnosticResults.length; i++) {
        const r = diagnosticResults[i];
        if (r.status === "严重" || r.status === "警告" || r.status === "致命") {
            problems.push(r);
        }
    }
    
    if (problems.length === 0) {
        fixesList.innerHTML = '<div class="fixes-empty">未检测到问题</div>';
        fixesCount.textContent = "";
        return;
    }
    
    fixesCount.textContent = problems.length + "个问题";
    
    let html = "";
    for (let i = 0; i < problems.length; i++) {
        const p = problems[i];
        const fixInfo = getFixSolution(p);
        const typeClass = (p.status === "严重" || p.status === "致命") ? "error" : "warning";
        const icon = (p.status === "严重" || p.status === "致命") ? "x" : "/";
        html += '<div class="fix-item ' + typeClass + '">';
        html += '<div class="fix-item-header"><div class="fix-icon">' + icon + '</div><div class="fix-title">' + p.test_name + '</div></div>';
        html += '<div class="fix-problem">' + p.message + '</div>';
        html += '<div class="fix-solution">' + fixInfo + '</div>';
        html += '</div>';
    }
    fixesList.innerHTML = html;
}

function getFixSolution(result) {
    const solutions = {
        "本机IP地址": "<b>解决方案:</b> 运行 <code class=\"fix-cmd\">ipconfig /release && ipconfig /renew</code> 获取新IP",
        "网关连通性": "<b>解决方案:</b> 1. 检查网线连接 2. 重启路由器 3. 运行 <code class=\"fix-cmd\">netsh winsock reset</code>",
        "DNS": "<b>解决方案:</b> 1. 运行 <code class=\"fix-cmd\">ipconfig /flushdns</code> 2. 更换DNS <code class=\"fix-cmd\">223.5.5.5</code>",
        "端口": "<b>解决方案:</b> 1. 检查防火墙 2. 确认代理软件运行",
        "Git代理": "<b>解决方案:</b> 运行 <code class=\"fix-cmd\">git config --global --unset http.proxy</code> 清除代理",
        "Git SSL": "<b>解决方案:</b> 临时方案 <code class=\"fix-cmd\">git config --global http.sslVerify false</code>",
        "代理端口": "<b>解决方案:</b> 1. 启动代理软件 2. 检查端口配置",
        "WiFi信号": "<b>解决方案:</b> 1. 靠近路由器 2. 切换5GHz频段 3. 重置WiFi适配器",
        "MTU": "<b>解决方案:</b> 运行 <code class=\"fix-cmd\">netsh interface ipv4 set subinterface \"以太网\" mtu=1500 store=persistent</code>",
        "防火墙": "<b>解决方案:</b> 运行 <code class=\"fix-cmd\">netsh advfirewall set allprofiles state on</code> 启用防火墙",
        "CLOSE_WAIT": "<b>解决方案:</b> 1. 检查应用程序连接管理 2. 运行 <code class=\"fix-cmd\">netsh winsock reset</code>",
        "SYN_SENT": "<b>解决方案:</b> 1. 检查防火墙规则 2. 检查网络连通性",
        "IP地址冲突": "<b>解决方案:</b> 运行 <code class=\"fix-cmd\">ipconfig /release && ipconfig /renew</code> 重新获取IP",
        "DHCP": "<b>解决方案:</b> 运行 <code class=\"fix-cmd\">ipconfig /renew</code> 重新获取IP配置",
        "网卡": "<b>解决方案:</b> 1. 检查网线连接 2. 启用网络适配器 3. 更新驱动",
        "网线": "<b>解决方案:</b> 检查网线是否插好，或尝试更换网线",
        "hosts文件": "<b>解决方案:</b> 检查 <code class=\"fix-cmd\">C:\\Windows\\System32\\drivers\\etc\\hosts</code> 中的自定义配置",
        "系统代理": "<b>解决方案:</b> 关闭系统代理或确认代理软件正在运行",
        "SSL": "<b>解决方案:</b> 1. 检查系统时间 2. 运行 <code class=\"fix-cmd\">git config --global http.sslVerify true</code>"
    };
    
    for (const key in solutions) {
        if (result.test_name.indexOf(key) !== -1 || result.component.indexOf(key) !== -1 || result.message.indexOf(key) !== -1) {
            return solutions[key];
        }
    }
    
    return result.suggestion || "<b>解决方案:</b> 查看详细日志获取更多信息";
}

async function runDiagnostic() {
    if (isRunning) return;
    isRunning = true;
    showAll = false;
    
    resetSteps();
    hideCurrentTask();
    setButtonsDisabled(true);
    document.getElementById("scanTime").textContent = new Date().toLocaleTimeString("zh-CN");
    
    try {
        setStepActive("step1");
        updateProgress(20);
        showCurrentTask("step1", 0);
        await sleep(400);
        showCurrentTask("step1", 1);
        await sleep(400);
        showCurrentTask("step1", 2);
        await sleep(400);
        
        setStepDone("step1");
        setStepActive("step2");
        updateProgress(40);
        showCurrentTask("step2", 0);
        await sleep(400);
        showCurrentTask("step2", 1);
        await sleep(400);
        showCurrentTask("step2", 2);
        await sleep(400);
        
        setStepDone("step2");
        setStepActive("step3");
        updateProgress(60);
        showCurrentTask("step3", 0);
        await sleep(400);
        showCurrentTask("step3", 1);
        await sleep(400);
        showCurrentTask("step3", 2);
        
        const resp = await fetch("/api/diagnostic", {method: "POST"});
        const data = await resp.json();
        
        setStepDone("step3");
        setStepActive("step4");
        updateProgress(80);
        showCurrentTask("step4", 0);
        await sleep(400);
        showCurrentTask("step4", 1);
        await sleep(400);
        showCurrentTask("step4", 2);
        
        diagnosticResults = data.results;
        
        setStepDone("step4");
        setStepActive("step5");
        updateProgress(100);
        
        updateScore(data.summary.health_score);
        document.getElementById("passCount").textContent = data.summary.success;
        document.getElementById("warningCount").textContent = data.summary.warning;
        document.getElementById("errorCount").textContent = data.summary.error;
        document.getElementById("criticalCount").textContent = data.summary.critical;
        
        updateStatus("localIP", data.status.local_ip || "-", data.status.local_ip !== "检测失败");
        updateStatus("gatewayStatus", data.status.gateway || "-", data.status.gateway_status);
        updateStatus("publicStatus", data.status.public_net || "-", data.status.public_net_status);
        updateStatus("latencyStatus", data.status.latency || "-", data.status.latency !== "-");
        updateStatus("dnsServer", data.status.dns_server || "-", data.status.dns_server !== "-");
        updateStatus("proxyStatus", data.status.proxy_status || "无代理", data.status.proxy_status !== "已配置");
        updateStatus("gitSSLStatus", data.status.git_ssl || "-", data.status.git_ssl === "已启用");
        updateStatus("proxyPortStatus", data.status.proxy_ports || "无", data.status.proxy_ports !== "-" && data.status.proxy_ports !== "无");
        
        hideCurrentTask();
        renderResults(diagnosticResults, selectedFilters);
        renderFixes();
        updateFixBanner(data.summary);
        setStepDone("step5");
        
    } catch (err) {
        console.error("诊断失败:", err);
        updateProgress(0);
        hideCurrentTask();
    } finally {
        isRunning = false;
        setButtonsDisabled(false);
    }
}

function sleep(ms) {
    return new Promise(function(resolve) {
        setTimeout(resolve, ms);
    });
}

function updateFixBanner(summary) {
    const banner = document.getElementById("fixBanner");
    const title = document.getElementById("fixBannerTitle");
    const desc = document.getElementById("fixBannerDesc");
    const btn = document.getElementById("btnOneClickFix");
    const problemCount = (summary.error || 0) + (summary.critical || 0) + (summary.warning || 0);

    if (problemCount > 0) {
        banner.style.display = "flex";
        btn.disabled = false;
        if (summary.critical > 0) {
            banner.className = "fix-banner critical";
            title.textContent = "检测到 " + problemCount + " 个问题（含 " + summary.critical + " 个致命）";
            desc.textContent = "建议立即一键修复，解决致命错误和网络异常";
        } else if (summary.error > 0) {
            banner.className = "fix-banner error";
            title.textContent = "检测到 " + problemCount + " 个问题（含 " + summary.error + " 个错误）";
            desc.textContent = "点击一键修复，自动解决检测到的网络问题";
        } else {
            banner.className = "fix-banner warning";
            title.textContent = "检测到 " + problemCount + " 个警告";
            desc.textContent = "部分配置可能影响网络体验，建议一键修复";
        }
    } else {
        banner.style.display = "none";
    }
}

async function runAutoFix() {
    if (isRunning) return;
    isRunning = true;

    const btnOneClick = document.getElementById("btnOneClickFix");
    const btnFix = document.getElementById("btnFix");
    if (btnOneClick) btnOneClick.disabled = true;
    if (btnFix) btnFix.disabled = true;

    if (btnOneClick) {
        btnOneClick.innerHTML = '<span class="fix-spinner"></span> 修复中...';
    }

    try {
        updateProgress(30);
        const resp = await fetch('/api/fix', {method: 'POST'});
        const data = await resp.json();

        updateProgress(70);

        if (data.success) {
            const successCount = data.success_count || 0;
            const failCount = data.fail_count || 0;
            const msgList = data.messages || [];
            let msgText = '';
            for (let i = 0; i < msgList.length; i++) {
                msgText += msgList[i] + '\n';
            }

            showFixResult(true, successCount, failCount, msgText);

            updateProgress(90);
            setTimeout(async function() {
                await runDiagnostic();
            }, 2000);
        } else {
            showFixResult(false, 0, 0, data.message || '未知错误');
            updateProgress(0);
        }
    } catch (err) {
        console.error('修复失败:', err);
        showFixResult(false, 0, 0, err.message);
        updateProgress(0);
    } finally {
        isRunning = false;
        if (btnOneClick) {
            btnOneClick.disabled = false;
            btnOneClick.innerHTML = '一键修复';
        }
        if (btnFix) btnFix.disabled = false;
    }
}

function showFixResult(success, successCount, failCount, message) {
    let existing = document.getElementById("fixResultOverlay");
    if (existing) existing.remove();

    const overlay = document.createElement("div");
    overlay.id = "fixResultOverlay";
    overlay.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:2000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);";

    const icon = success ? "✓" : "✗";
    const iconColor = success ? "#22c55e" : "#ef4444";
    const title = success ? "修复完成" : "修复失败";
    const detail = success ? "成功: " + successCount + " 项, 失败: " + failCount + " 项" : "";

    overlay.innerHTML = '<div style="background:#1e293b;border-radius:16px;padding:32px;max-width:420px;width:90%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.5);">' +
        '<div style="width:56px;height:56px;border-radius:50%;background:' + iconColor + '20;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:28px;color:' + iconColor + ';">' + icon + '</div>' +
        '<div style="font-size:18px;font-weight:700;color:#f1f5f9;margin-bottom:8px;">' + title + '</div>' +
        (detail ? '<div style="font-size:14px;color:#94a3b8;margin-bottom:12px;">' + detail + '</div>' : '') +
        '<div style="font-size:13px;color:#64748b;max-height:120px;overflow-y:auto;text-align:left;background:#0f172a;border-radius:8px;padding:12px;margin-bottom:16px;white-space:pre-wrap;">' + (message || '') + '</div>' +
        (success ? '<div style="font-size:13px;color:#38bdf8;margin-bottom:16px;">即将自动重新检测...</div>' : '') +
        '<button onclick="document.getElementById(\'fixResultOverlay\').remove()" style="padding:10px 32px;background:#3b82f6;color:#fff;border:none;border-radius:8px;font-size:14px;cursor:pointer;">确定</button>' +
        '</div>';

    document.body.appendChild(overlay);

    if (success) {
        setTimeout(function() {
            if (document.getElementById("fixResultOverlay")) {
                document.getElementById("fixResultOverlay").remove();
            }
        }, 3000);
    }
}

let kbCurrentCategory = null;
let kbCurrentTerm = null;

function openKnowledgeBase() {
    document.getElementById("kbOverlay").classList.add("active");
    document.body.style.overflow = "hidden";
    renderKBSidebar();
}

function closeKnowledgeBase(event) {
    if (event && event.target !== document.getElementById("kbOverlay")) return;
    document.getElementById("kbOverlay").classList.remove("active");
    document.body.style.overflow = "";
}

function renderKBSidebar() {
    const sidebar = document.getElementById("kbSidebar");
    let html = "";
    const categories = KNOWLEDGE_BASE.categories;
    for (let i = 0; i < categories.length; i++) {
        const cat = categories[i];
        const isActive = kbCurrentCategory === cat.id;
        html += '<div class="kb-category' + (isActive ? " active" : "") + '">';
        html += '<div class="kb-category-header" onclick="selectKBCategory(\'' + cat.id + '\')">';
        html += '<span class="kb-category-icon">' + cat.icon + '</span>';
        html += '<span class="kb-category-name">' + cat.name + '</span>';
        html += '<span class="kb-category-count">' + cat.items.length + '</span>';
        html += '</div>';
        if (isActive) {
            html += '<div class="kb-category-items">';
            for (let j = 0; j < cat.items.length; j++) {
                const item = cat.items[j];
                const isTermActive = kbCurrentTerm === item.term;
                html += '<div class="kb-term-item' + (isTermActive ? " active" : "") + '" onclick="selectKBTerm(\'' + cat.id + '\',\'' + escapeTerm(item.term) + '\')">';
                html += item.term;
                html += '</div>';
            }
            html += '</div>';
        }
        html += '</div>';
    }
    sidebar.innerHTML = html;
}

function escapeTerm(term) {
    return term.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function selectKBCategory(catId) {
    if (kbCurrentCategory === catId) {
        kbCurrentCategory = null;
        kbCurrentTerm = null;
    } else {
        kbCurrentCategory = catId;
        kbCurrentTerm = null;
    }
    renderKBSidebar();
    if (kbCurrentCategory) {
        renderKBContent();
    } else {
        renderKBWelcome();
    }
}

function selectKBTerm(catId, term) {
    kbCurrentCategory = catId;
    kbCurrentTerm = term;
    renderKBSidebar();
    renderKBContent();
}

function renderKBWelcome() {
    document.getElementById("kbContent").innerHTML = '<div class="kb-welcome"><div class="kb-welcome-icon">?</div><div class="kb-welcome-title">选择一个分类开始探索</div><div class="kb-welcome-desc">涵盖网络协议、安全、硬件、诊断等核心知识</div></div>';
}

function renderKBContent() {
    const content = document.getElementById("kbContent");
    if (!kbCurrentCategory) {
        renderKBWelcome();
        return;
    }
    const cat = findCategory(kbCurrentCategory);
    if (!cat) return;

    if (kbCurrentTerm) {
        const item = findTerm(cat, kbCurrentTerm);
        if (item) {
            renderKBTermDetail(item, cat);
            return;
        }
    }

    let html = '<div class="kb-category-view">';
    html += '<div class="kb-category-view-header">';
    html += '<span class="kb-category-view-icon">' + cat.icon + '</span>';
    html += '<h3>' + cat.name + '</h3>';
    html += '</div>';
    html += '<div class="kb-term-grid">';
    for (let i = 0; i < cat.items.length; i++) {
        const item = cat.items[i];
        html += '<div class="kb-term-card" onclick="selectKBTerm(\'' + cat.id + '\',\'' + escapeTerm(item.term) + '\')">';
        html += '<div class="kb-term-card-title">' + item.term + '</div>';
        html += '<div class="kb-term-card-full">' + item.fullForm + '</div>';
        html += '<div class="kb-term-card-desc">' + truncateText(item.description, 80) + '</div>';
        html += '</div>';
    }
    html += '</div>';
    html += '</div>';
    content.innerHTML = html;
}

function renderKBTermDetail(item, cat) {
    const content = document.getElementById("kbContent");
    let html = '<div class="kb-detail">';
    html += '<div class="kb-detail-breadcrumb">';
    html += '<span class="kb-breadcrumb-link" onclick="kbCurrentTerm=null;renderKBSidebar();renderKBContent();">' + cat.name + '</span>';
    html += '<span class="kb-breadcrumb-sep">/</span>';
    html += '<span>' + item.term + '</span>';
    html += '</div>';
    html += '<div class="kb-detail-header">';
    html += '<h2>' + item.term + '</h2>';
    html += '<div class="kb-detail-full">' + item.fullForm + '</div>';
    html += '</div>';
    html += '<div class="kb-detail-section">';
    html += '<div class="kb-detail-section-title">概述</div>';
    html += '<p class="kb-detail-desc">' + item.description + '</p>';
    html += '</div>';
    html += '<div class="kb-detail-section">';
    html += '<div class="kb-detail-section-title">详细说明</div>';
    html += '<ul class="kb-detail-list">';
    for (let i = 0; i < item.details.length; i++) {
        html += '<li>' + item.details[i] + '</li>';
    }
    html += '</ul>';
    html += '</div>';
    if (item.relatedTerms && item.relatedTerms.length > 0) {
        html += '<div class="kb-detail-section">';
        html += '<div class="kb-detail-section-title">相关术语</div>';
        html += '<div class="kb-related-terms">';
        for (let i = 0; i < item.relatedTerms.length; i++) {
            const related = findTermGlobal(item.relatedTerms[i]);
            if (related) {
                html += '<span class="kb-related-tag" onclick="selectKBTerm(\'' + related.catId + '\',\'' + escapeTerm(related.item.term) + '\')">' + item.relatedTerms[i] + '</span>';
            } else {
                html += '<span class="kb-related-tag disabled">' + item.relatedTerms[i] + '</span>';
            }
        }
        html += '</div>';
        html += '</div>';
    }
    html += '</div>';
    content.innerHTML = html;
    content.scrollTop = 0;
}

function searchKnowledge(query) {
    if (!query || query.trim() === "") {
        kbCurrentCategory = null;
        kbCurrentTerm = null;
        renderKBSidebar();
        renderKBWelcome();
        return;
    }
    query = query.toLowerCase().trim();
    const results = [];
    const categories = KNOWLEDGE_BASE.categories;
    for (let i = 0; i < categories.length; i++) {
        const cat = categories[i];
        for (let j = 0; j < cat.items.length; j++) {
            const item = cat.items[j];
            if (item.term.toLowerCase().indexOf(query) !== -1 ||
                item.fullForm.toLowerCase().indexOf(query) !== -1 ||
                item.description.toLowerCase().indexOf(query) !== -1) {
                results.push({ catId: cat.id, catName: cat.name, catIcon: cat.icon, item: item });
            }
        }
    }
    renderSearchResults(results, query);
}

function renderSearchResults(results, query) {
    const content = document.getElementById("kbContent");
    const sidebar = document.getElementById("kbSidebar");
    sidebar.innerHTML = "";
    if (results.length === 0) {
        content.innerHTML = '<div class="kb-welcome"><div class="kb-welcome-icon">0</div><div class="kb-welcome-title">未找到相关术语</div><div class="kb-welcome-desc">尝试其他关键词搜索</div></div>';
        return;
    }
    let html = '<div class="kb-search-results">';
    html += '<div class="kb-search-results-header">找到 ' + results.length + ' 个相关结果</div>';
    html += '<div class="kb-term-grid">';
    for (let i = 0; i < results.length; i++) {
        const r = results[i];
        html += '<div class="kb-term-card" onclick="selectKBTerm(\'' + r.catId + '\',\'' + escapeTerm(r.item.term) + '\');document.getElementById(\'kbSearch\').value=\'\';">';
        html += '<div class="kb-term-card-cat">' + r.catName + '</div>';
        html += '<div class="kb-term-card-title">' + highlightText(r.item.term, query) + '</div>';
        html += '<div class="kb-term-card-full">' + highlightText(r.item.fullForm, query) + '</div>';
        html += '<div class="kb-term-card-desc">' + highlightText(truncateText(r.item.description, 100), query) + '</div>';
        html += '</div>';
    }
    html += '</div>';
    html += '</div>';
    content.innerHTML = html;
}

function highlightText(text, query) {
    if (!query) return text;
    const regex = new RegExp("(" + query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
    return text.replace(regex, "<mark>$1</mark>");
}

function truncateText(text, maxLen) {
    if (text.length <= maxLen) return text;
    return text.substring(0, maxLen) + "...";
}

function findCategory(catId) {
    const categories = KNOWLEDGE_BASE.categories;
    for (let i = 0; i < categories.length; i++) {
        if (categories[i].id === catId) return categories[i];
    }
    return null;
}

function findTerm(cat, term) {
    for (let i = 0; i < cat.items.length; i++) {
        if (cat.items[i].term === term) return cat.items[i];
    }
    return null;
}

function findTermGlobal(termName) {
    const categories = KNOWLEDGE_BASE.categories;
    for (let i = 0; i < categories.length; i++) {
        const cat = categories[i];
        for (let j = 0; j < cat.items.length; j++) {
            if (cat.items[j].term === termName) {
                return { catId: cat.id, item: cat.items[j] };
            }
        }
    }
    return null;
}

document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
        const overlay = document.getElementById("kbOverlay");
        if (overlay.classList.contains("active")) {
            closeKnowledgeBase();
        }
    }
});

async function quickFix(type) {
    if (isRunning) return;
    isRunning = true;
    
    const fixNames = {
        'proxy': '清除Git代理',
        'github': '修复GitHub连接',
        'dns': '刷新DNS缓存',
        'git_reset': '重置Git网络'
    };
    
    try {
        updateProgress(30);
        const resp = await fetch('/api/quick-fix', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type: type})
        });
        const data = await resp.json();
        
        updateProgress(100);
        
        if (data.success) {
            alert(`${fixNames[type] || '修复'}成功！\n\n${data.message}`);
        } else {
            alert(`${fixNames[type] || '修复'}失败: ${data.message}`);
        }
        
        setTimeout(function() { updateProgress(0); }, 2000);
    } catch (err) {
        console.error('快速修复失败:', err);
        alert('请求失败');
        updateProgress(0);
    } finally {
        isRunning = false;
    }
}