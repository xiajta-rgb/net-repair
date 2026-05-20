let diagnosticResults = [];
let isRunning = false;
let showAll = false;
let selectedFilters = ["all"];

const TASK_NAMES = {
    "step1": { name: "网络配置检测", details: ["检测本机IP地址", "检测网关连通性", "检测公网连通性"] },
    "step2": { name: "DNS解析检测", details: ["解析github.com", "解析baidu.com", "检测公共DNS"] },
    "step3": { name: "端口连通性检测", details: ["检测443端口", "检测代理端口10808", "检测代理端口7890"] },
    "step4": { name: "Git配置检测", details: ["检测Git代理配置", "检测Git SSL验证", "检测Git远程仓库"] }
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
        list.innerHTML = "<div class=\"empty-state\"><div class=\"empty-icon\">...</div><div class=\"empty-title\">尚未执行诊断</div><div class=\"empty-desc\">点击上方开始检测按钮</div></div>";
        document.getElementById("resultsCount").textContent = "";
        return;
    }

    let filtered = results;
    if (!selectedFilters.includes("all")) {
        filtered = results.filter(function(r) {
            if (selectedFilters.indexOf("error") !== -1 && (r.status === "严重" || r.status === "致命")) return true;
            if (selectedFilters.indexOf("warning") !== -1 && r.status === "警告") return true;
            if (selectedFilters.indexOf("success") !== -1 && (r.status === "通过" || r.status === "正常") return true;
            return false;
        });
    }

    document.getElementById("resultsCount").textContent = "(" + filtered.length + ")";

    if (filtered.length === 0) {
        list.innerHTML = "<div class=\"empty-state\"><div class=\"empty-icon\">-</div><div class=\"empty-title\">没有符合条件的结果</div></div>";
        return;
    }

    const badgeMap = {"致命": "!", "严重": "x", "警告": "/", "正常": "v", "通过": "v", "信息": "i"};
    const severityClass = {"致命": "critical", "严重": "error", "警告": "warning", "正常": "success", "通过": "success", "信息": "info"};
    const displayItems = showAll ? filtered : filtered.slice(0, 12);
    
    list.innerHTML = displayItems.map(function(r) {
        return "<div class=\"result-card " + (severityClass[r.status] || "info") + "\" onclick=\"toggleCard(this)\"><div class=\"result-card-header\"><div class=\"result-badge\">" + (badgeMap[r.status] || "i") + "</div><div class=\"result-card-title\">" + r.test_name + "</div></div><div class=\"result-card-component\">" + r.component + "</div><div class=\"result-card-message\">" + r.message + "</div>" + (r.suggestion ? "<div class=\"result-card-tip\">" + r.suggestion + "</div>" : "") + "</div>";
    }).join("");

    if (!showAll && filtered.length > 12) {
        list.innerHTML += "<button class=\"show-more\" onclick=\"toggleShowAll()\">显示全部 " + filtered.length + " 项</button>";
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
        document.querySelectorAll(".tab-btn").forEach(function(b) {
            b.classList.remove("selected");
            if (b.dataset.filter === "all") {
                b.classList.add("selected");
            }
        });
    } else {
        const idx = selectedFilters.indexOf("all");
        if (idx !== -1) selectedFilters.splice(idx, 1);
        
        if (btn.classList.contains("selected")) {
            btn.classList.remove("selected");
            const fIdx = selectedFilters.indexOf(filter);
            if (fIdx !== -1) selectedFilters.splice(fIdx, 1);
            if (selectedFilters.length === 0) {
                selectedFilters = ["all"];
                document.querySelector(".tab-btn[data-filter=\"all\"] && document.querySelector(".tab-btn[data-filter=\"all\").classList.add("selected");
        }
    } else {
        btn.classList.add("selected");
        if (selectedFilters.indexOf(filter) === -1) {
            selectedFilters.push(filter);
        }
    }
    
    renderResults(diagnosticResults, selectedFilters);
    renderFixes();
}

function renderFixes() {
    const fixesList = document.getElementById("fixesList");
    const fixesCount = document.getElementById("fixesCount");
    
    const problems = diagnosticResults.filter(function(r) {
        return r.status === "严重" || r.status === "警告" || r.status === "致命";
    });
    
    if (problems.length === 0) {
        fixesList.innerHTML = "<div class=\"fixes-empty\">未检测到问题</div>";
        fixesCount.textContent = "";
        return;
    }
    
    fixesCount.textContent = problems.length + "个问题";
    
    fixesList.innerHTML = problems.map(function(p) {
        const fixInfo = getFixSolution(p);
        const typeClass = (p.status === "严重" || p.status === "致命") ? "error" : "warning";
        const icon = (p.status === "严重" || p.status === "致命") ? "x" : "/";
        return "<div class=\"fix-item " + typeClass + "\"><div class=\"fix-item-header\"><div class=\"fix-icon\">" + icon + "</div><div class=\"fix-title\">" + p.test_name + "</div></div><div class=\"fix-problem\">" + p.message + "</div><div class=\"fix-solution\">" + fixInfo + "</div></div>";
    }).join("");
}

function getFixSolution(result) {
    const solutions = {
        "本机IP地址": "<b>解决方案:</b> 运行 <code class=\"fix-cmd\">ipconfig /release && ipconfig /renew</code> 获取新IP",
        "网关连通性": "<b>解决方案:</b> 1. 检查网线连接 2. 重启路由器 3. 运行 <code class=\"fix-cmd\">netsh winsock reset</code>",
        "DNS": "<b>解决方案:</b> 1. 运行 <code class=\"fix-cmd\">ipconfig /flushdns</code> 2. 更换DNS <code class=\"fix-cmd\">223.5.5.5</code>",
        "端口": "<b>解决方案:</b> 1. 检查防火墙 2. 确认代理软件运行",
        "Git代理": "<b>解决方案:</b> 运行 <code class=\"fix-cmd\">git config --global --unset http.proxy</code> 清除代理",
        "Git SSL": "<b>解决方案:</b> 临时方案 <code class=\"fix-cmd\">git config --global http.sslVerify false</code>",
        "代理端口": "<b>解决方案:</b> 1. 启动代理软件 2. 检查端口配置"
    };
    
    for (const key in solutions) {
        if (result.test_name.indexOf(key) !== -1 || result.component.indexOf(key) !== -1) {
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
        
        hideCurrentTask();
        renderResults(diagnosticResults, selectedFilters);
        renderFixes();
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

async function runAutoFix() {
    updateProgress(50);
    await sleep(1500);
    updateProgress(100);
    setTimeout(function() { updateProgress(0); }, 2000);
}

async function quickFix(type) {
    updateProgress(50);
    await sleep(1500);
    updateProgress(100);
    setTimeout(function() { updateProgress(0); }, 2000);
}