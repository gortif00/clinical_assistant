// frontend/js/app.js

const API_URL = "/api/v1/analyze";
const STATUS_URL = "/api/v1/get_status";

// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const caseText = document.getElementById("caseText");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const autoClassify = document.getElementById("autoClassify");
const pathology = document.getElementById("pathology");
const manualPathologyGroup = document.getElementById("manualPathologyGroup");
const exampleButtons = document.querySelectorAll(".example-btn");
const executionDevice = document.getElementById("executionDevice");
const historySidebar = document.getElementById("historySidebar");
const historyList = document.getElementById("historyList");
const toggleHistoryBtn = document.getElementById("toggleHistoryBtn");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const exportBtn = document.getElementById("exportBtn");
const darkModeToggle = document.getElementById("darkModeToggle");

// History storage
const HISTORY_KEY = 'clinical_assistant_history';
const DARK_MODE_KEY = 'clinical_assistant_dark_mode';
let caseHistory = loadHistory();
let lastAnalysisData = null;

// Event Listeners
analyzeBtn.addEventListener("click", analyzeCase);
clearBtn.addEventListener("click", clearChat);
autoClassify.addEventListener("change", toggleManualMode);
caseText.addEventListener("keydown", handleTextareaKeydown);
toggleHistoryBtn.addEventListener("click", toggleHistory);
clearHistoryBtn.addEventListener("click", clearHistory);
exportBtn.addEventListener("click", exportResults);
darkModeToggle.addEventListener("click", toggleDarkMode);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  renderHistory();
  loadExecutionDevice();
  loadDarkMode();
});

// Handle example buttons
exampleButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const exampleType = btn.getAttribute("data-example");
    const exampleText = document.querySelector(`#exampleTexts [data-example="${exampleType}"]`);
    if (exampleText) {
      caseText.value = exampleText.textContent.trim();
      caseText.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
});

// Toggle manual pathology selection
function toggleManualMode() {
  manualPathologyGroup.style.display = autoClassify.checked ? "none" : "block";
}

// Handle Ctrl/Cmd + Enter to submit
function handleTextareaKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    analyzeCase();
  }
}

// Clear chat history
function clearChat() {
  chatMessages.innerHTML = `
    <div class="welcome-message">
      <p><strong>👨‍⚕️ Welcome to the Clinical Mental Health Assistant</strong></p>
      <p>Enter patient clinical observations or case descriptions to receive:</p>
      <ul>
        <li>🔍 Automated condition classification</li>
        <li>💊 Evidence-based treatment recommendations</li>
      </ul>
    </div>
  `;
  caseText.value = "";
}

// Add user message to chat
function addUserMessage(text) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message user-message";
  messageDiv.innerHTML = `
    <div class="message-avatar">👨‍⚕️</div>
    <div class="message-content">
      <div class="message-text">${escapeHtml(text)}</div>
    </div>
  `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Add bot message to chat
function addBotMessage(html, className = "") {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message bot-message ${className}`;
  messageDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="message-text">${html}</div>
    </div>
  `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
  return messageDiv;
}

// Update existing bot message
function updateBotMessage(messageDiv, html) {
  const contentDiv = messageDiv.querySelector(".message-text");
  if (contentDiv) {
    contentDiv.innerHTML = html;
    scrollToBottom();
  }
}

// Add loading message with detailed progress
function addLoadingMessage() {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message loading-message";
  messageDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="message-text">
        <div class="progress-container">
          <div class="progress-stages">
            <div class="stage" data-stage="classify">
              <span class="stage-icon">🔍</span>
              <span class="stage-label">Classifying</span>
              <span class="stage-status">⏳</span>
            </div>
            <div class="stage" data-stage="summarize">
              <span class="stage-icon">📋</span>
              <span class="stage-label">Summarizing</span>
              <span class="stage-status">⏳</span>
            </div>
            <div class="stage" data-stage="generate">
              <span class="stage-icon">💊</span>
              <span class="stage-label">Generating</span>
              <span class="stage-status">⏳</span>
            </div>
          </div>
          <div class="progress-bar-outer">
            <div class="progress-bar-inner" style="width: 0%"></div>
          </div>
          <div class="progress-text">Starting analysis...</div>
        </div>
      </div>
    </div>
  `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
  return messageDiv;
}

// Update progress stage
function updateProgress(messageDiv, stage, progress, text) {
  const progressBar = messageDiv.querySelector('.progress-bar-inner');
  const progressText = messageDiv.querySelector('.progress-text');
  const stages = messageDiv.querySelectorAll('.stage');
  
  if (progressBar) progressBar.style.width = `${progress}%`;
  if (progressText) progressText.textContent = text;
  
  // Update stage indicators
  stages.forEach(stageEl => {
    const stageName = stageEl.getAttribute('data-stage');
    const statusEl = stageEl.querySelector('.stage-status');
    
    if (stageName === stage) {
      stageEl.classList.add('active');
      statusEl.textContent = '⏳';
    } else if (progress > getStageProgress(stageName)) {
      stageEl.classList.add('completed');
      statusEl.textContent = '✅';
    }
  });
  
  scrollToBottom();
}

function getStageProgress(stage) {
  const stages = { classify: 0, summarize: 33, generate: 66 };
  return stages[stage] || 0;
}

// Scroll chat to bottom
function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Format classification results
function formatClassification(classification) {
  const { pathology, confidence, all_probabilities } = classification;
  
  let html = `<div class="classification-result">`;
  html += `<h3>✅ Diagnostic Classification Complete</h3>`;
  html += `<p><strong>Primary Diagnosis:</strong> ${pathology}</p>`;
  
  if (confidence !== null) {
    html += `<p><strong>Confidence Level:</strong> ${(confidence * 100).toFixed(1)}%</p>`;
    html += `<h4>Differential Diagnosis Probabilities:</h4>`;
    html += `<div class="probabilities">`;
    
    const sortedProbs = Object.entries(all_probabilities)
      .sort((a, b) => b[1] - a[1]);
    
    for (const [label, prob] of sortedProbs) {
      const percentage = (prob * 100).toFixed(1);
      const barWidth = Math.max(prob * 100, 2);
      html += `
        <div class="prob-item">
          <span class="prob-label">${label}</span>
          <div class="prob-bar-container">
            <div class="prob-bar" style="width: ${barWidth}%"></div>
          </div>
          <span class="prob-value">${percentage}%</span>
        </div>
      `;
    }
    
    html += `</div>`;
  } else {
    html += `<p><em>ℹ️ Manual diagnosis selection mode</em></p>`;
  }
  
  html += `</div>`;
  return html;
}

// Format summary
function formatSummary(summary) {
  return `
    <div class="summary-result">
      <h3>📋 Clinical Summary</h3>
      <p>${escapeHtml(summary)}</p>
    </div>
  `;
}

// Format recommendation
function formatRecommendation(recommendation) {
  return `
    <div class="recommendation-result">
      <h3>💊 Treatment Recommendations</h3>
      <div class="recommendation-text">${escapeHtml(recommendation).replace(/\n/g, '<br>')}</div>
      <div class="disclaimer-box">
        <strong>⚠️ Professional Disclaimer:</strong><br>
        This AI-assisted analysis is intended as a clinical decision support tool. Final diagnosis and treatment planning should incorporate comprehensive clinical assessment, patient history, and professional clinical judgment. This system is designed to augment, not replace, professional expertise.
      </div>
    </div>
  `;
}

// Main analyze function
async function analyzeCase() {
  const text = caseText.value.trim();
  
  // Validate input
  if (!text) {
    addBotMessage(`
      <div class="error-message">
        ⚠️ <strong>Input Required:</strong><br>
        Please enter patient clinical observations to analyze.
      </div>
    `);
    return;
  }
  
  if (text.length < 50) {
    addBotMessage(`
      <div class="error-message">
        ⚠️ <strong>Insufficient Information:</strong><br>
        Please provide more detailed clinical observations (minimum 50 characters) for accurate analysis.
      </div>
    `);
    return;
  }
  
  // Disable button during analysis
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";
  
  // Add user message
  addUserMessage(text);
  
  // Clear input
  caseText.value = "";
  
  // Add loading message with progress
  const loadingMsg = addLoadingMessage();
  
  // Prepare payload
  const payload = {
    text,
    auto_classify: autoClassify.checked,
    pathology: autoClassify.checked ? null : pathology.value,
  };
  
  try {
    // Simulate progress stages
    updateProgress(loadingMsg, 'classify', 10, 'Loading classification model...');
    await simulateDelay(500);
    
    updateProgress(loadingMsg, 'classify', 25, 'Analyzing symptoms and patterns...');
    
    // Call API
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      loadingMsg.remove();
      const errorData = await response.json();
      throw new Error(errorData.detail || "API request failed");
    }
    
    updateProgress(loadingMsg, 'summarize', 50, 'Extracting clinical summary...');
    await simulateDelay(300);
    
    updateProgress(loadingMsg, 'generate', 75, 'Generating treatment recommendations...');
    await simulateDelay(500);
    
    const data = await response.json();
    
    updateProgress(loadingMsg, 'generate', 100, 'Analysis complete!');
    await simulateDelay(300);
    
    // Remove loading message
    loadingMsg.remove();
    
    // Show classification with animation
    if (autoClassify.checked) {
      const classMsg = addBotMessage(formatClassification(data.classification));
      classMsg.style.opacity = '0';
      setTimeout(() => {
        classMsg.style.transition = 'opacity 0.3s';
        classMsg.style.opacity = '1';
      }, 50);
    }
    
    // Show recommendation with streaming effect
    await simulateDelay(400);
    await streamRecommendation(data.recommendation);
    
    // Save to history
    lastAnalysisData = {
      text,
      classification: data.classification,
      recommendation: data.recommendation,
      timestamp: new Date().toISOString()
    };
    
    addToHistory(lastAnalysisData);
    exportBtn.disabled = false;
    
  } catch (error) {
    // Remove loading message
    loadingMsg.remove();
    
    // Show error
    addBotMessage(`
      <div class="error-message">
        ❌ <strong>Analysis Error:</strong><br>
        ${escapeHtml(error.message)}<br><br>
        <strong>Action Required:</strong> Please review case description and retry, or contact technical support.
      </div>
    `);
    
    console.error("Analysis error:", error);
  } finally {
    // Re-enable button
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze Case 🔬";
  }
}

// Simulate delay for better UX
function simulateDelay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Stream recommendation text with typing effect
async function streamRecommendation(text) {
  const messageDiv = addBotMessage(`
    <div class="recommendation-result">
      <h3>💊 Treatment Recommendations</h3>
      <div class="recommendation-text streaming"></div>
      <div class="disclaimer-box">
        <strong>⚠️ Professional Disclaimer:</strong><br>
        This AI-assisted analysis is intended as a clinical decision support tool. Final diagnosis and treatment planning should incorporate comprehensive clinical assessment, patient history, and professional clinical judgment. This system is designed to augment, not replace, professional expertise.
      </div>
    </div>
  `);
  
  const textDiv = messageDiv.querySelector('.recommendation-text');
  const words = text.split(' ');
  let currentText = '';
  
  for (let i = 0; i < words.length; i++) {
    currentText += (i > 0 ? ' ' : '') + words[i];
    textDiv.innerHTML = escapeHtml(currentText).replace(/\n/g, '<br>') + '<span class="cursor">▋</span>';
    scrollToBottom();
    
    // Variable speed based on word length
    const delay = words[i].length > 8 ? 40 : 25;
    await simulateDelay(delay);
  }
  
  // Remove cursor
  textDiv.innerHTML = escapeHtml(currentText).replace(/\n/g, '<br>');
  textDiv.classList.remove('streaming');
}

// Get device icon based on device type
function getDeviceIcon(device) {
  switch (device) {
    case 'cuda':
      return '⚡ GPU (CUDA)';
    case 'mps':
      return '🍎 GPU (Apple Silicon)';
    case 'cpu':
    default:
      return '🐢 CPU';
  }
}

// ==================== HISTORY MANAGEMENT ====================

// Load history from localStorage
function loadHistory() {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (e) {
    console.error('Error loading history:', e);
    return [];
  }
}

// Save history to localStorage
function saveHistory() {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(caseHistory));
  } catch (e) {
    console.error('Error saving history:', e);
  }
}

// Add case to history
function addToHistory(caseData) {
  const historyItem = {
    id: Date.now(),
    timestamp: new Date().toISOString(),
    text: caseData.text.substring(0, 100) + (caseData.text.length > 100 ? '...' : ''),
    fullText: caseData.text,
    pathology: caseData.classification?.pathology || 'Unknown',
    confidence: caseData.classification?.confidence || null,
    recommendation: caseData.recommendation
  };
  
  caseHistory.unshift(historyItem);
  
  // Keep only last 20 items
  if (caseHistory.length > 20) {
    caseHistory = caseHistory.slice(0, 20);
  }
  
  saveHistory();
  renderHistory();
}

// Render history list
function renderHistory() {
  if (caseHistory.length === 0) {
    historyList.innerHTML = '<p class="empty-history">No previous cases</p>';
    return;
  }
  
  historyList.innerHTML = caseHistory.map(item => `
    <div class="history-item" data-id="${item.id}">
      <div class="history-header-item">
        <span class="history-pathology">${item.pathology}</span>
        ${item.confidence ? `<span class="history-confidence">${(item.confidence * 100).toFixed(0)}%</span>` : ''}
      </div>
      <p class="history-text">${escapeHtml(item.text)}</p>
      <span class="history-time">${formatTimestamp(item.timestamp)}</span>
    </div>
  `).join('');
  
  // Add click handlers
  document.querySelectorAll('.history-item').forEach(item => {
    item.addEventListener('click', () => {
      const id = parseInt(item.getAttribute('data-id'));
      loadHistoryItem(id);
    });
  });
}

// Load a history item into chat
function loadHistoryItem(id) {
  const item = caseHistory.find(h => h.id === id);
  if (!item) return;
  
  clearChat();
  addUserMessage(item.fullText);
  
  if (item.pathology !== 'Unknown') {
    addBotMessage(formatClassification({
      pathology: item.pathology,
      confidence: item.confidence,
      all_probabilities: {}
    }));
  }
  
  addBotMessage(formatRecommendation(item.recommendation));
}

// Toggle history sidebar
function toggleHistory() {
  historySidebar.classList.toggle('collapsed');
  toggleHistoryBtn.textContent = historySidebar.classList.contains('collapsed') ? '▶' : '◀';
}

// Clear all history
function clearHistory() {
  if (confirm('Are you sure you want to clear all case history?')) {
    caseHistory = [];
    saveHistory();
    renderHistory();
  }
}

// Format timestamp
function formatTimestamp(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
}

// ==================== EXPORT FUNCTIONALITY ====================

// Export results
function exportResults() {
  if (!lastAnalysisData) {
    alert('No analysis available to export. Please analyze a case first.');
    return;
  }
  
  const menu = document.createElement('div');
  menu.className = 'export-menu';
  menu.innerHTML = `
    <div class="export-menu-content">
      <h3>Export Analysis</h3>
      <button class="export-option" data-format="json">📄 Export as JSON</button>
      <button class="export-option" data-format="txt">📝 Export as Text</button>
      <button class="export-option" data-format="pdf">📕 Export as PDF (Simple)</button>
      <button class="export-cancel">✖ Cancel</button>
    </div>
  `;
  
  document.body.appendChild(menu);
  
  menu.querySelectorAll('.export-option').forEach(btn => {
    btn.addEventListener('click', () => {
      const format = btn.getAttribute('data-format');
      performExport(format);
      menu.remove();
    });
  });
  
  menu.querySelector('.export-cancel').addEventListener('click', () => {
    menu.remove();
  });
}

// Perform export in specified format
function performExport(format) {
  const data = lastAnalysisData;
  const timestamp = new Date(data.timestamp).toLocaleString();
  
  switch (format) {
    case 'json':
      exportAsJSON(data, timestamp);
      break;
    case 'txt':
      exportAsText(data, timestamp);
      break;
    case 'pdf':
      exportAsPDF(data, timestamp);
      break;
  }
}

// Export as JSON
function exportAsJSON(data, timestamp) {
  const exportData = {
    timestamp,
    patient_input: data.text,
    classification: data.classification,
    recommendation: data.recommendation,
    metadata: {
      exported: new Date().toISOString(),
      system: 'Clinical Mental Health Assistant v1.0'
    }
  };
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  downloadFile(blob, `clinical_analysis_${Date.now()}.json`);
}

// Export as Text
function exportAsText(data, timestamp) {
  let content = `CLINICAL MENTAL HEALTH ASSISTANT\nAnalysis Report\n\n`;
  content += `${'='.repeat(60)}\n\n`;
  content += `Timestamp: ${timestamp}\n\n`;
  content += `${'='.repeat(60)}\n\n`;
  
  content += `PATIENT OBSERVATIONS:\n${'-'.repeat(60)}\n`;
  content += `${data.text}\n\n`;
  
  if (data.classification) {
    content += `${'='.repeat(60)}\n\n`;
    content += `DIAGNOSTIC CLASSIFICATION:\n${'-'.repeat(60)}\n`;
    content += `Primary Diagnosis: ${data.classification.pathology}\n`;
    if (data.classification.confidence) {
      content += `Confidence Level: ${(data.classification.confidence * 100).toFixed(1)}%\n\n`;
      
      if (data.classification.all_probabilities) {
        content += `Differential Diagnosis Probabilities:\n`;
        const sorted = Object.entries(data.classification.all_probabilities)
          .sort((a, b) => b[1] - a[1]);
        sorted.forEach(([label, prob]) => {
          content += `  - ${label}: ${(prob * 100).toFixed(1)}%\n`;
        });
      }
    }
  }
  
  content += `\n${'='.repeat(60)}\n\n`;
  content += `TREATMENT RECOMMENDATIONS:\n${'-'.repeat(60)}\n`;
  content += `${data.recommendation}\n\n`;
  
  content += `${'='.repeat(60)}\n\n`;
  content += `PROFESSIONAL DISCLAIMER:\n${'-'.repeat(60)}\n`;
  content += `This AI-assisted analysis is intended as a clinical decision support\n`;
  content += `tool. Final diagnosis and treatment planning should incorporate\n`;
  content += `comprehensive clinical assessment, patient history, and professional\n`;
  content += `clinical judgment. This system is designed to augment, not replace,\n`;
  content += `professional expertise.\n\n`;
  content += `${'='.repeat(60)}\n`;
  content += `Generated by Clinical Mental Health Assistant\n`;
  content += `Export Date: ${new Date().toLocaleString()}\n`;
  
  const blob = new Blob([content], { type: 'text/plain' });
  downloadFile(blob, `clinical_analysis_${Date.now()}.txt`);
}

// Export as PDF (simple HTML-based)
function exportAsPDF(data, timestamp) {
  let html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Clinical Analysis Report</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
    h1 { color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
    h2 { color: #1e293b; margin-top: 30px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }
    .meta { color: #64748b; font-size: 0.9em; margin-bottom: 30px; }
    .section { margin: 20px 0; padding: 15px; background: #f8fafc; border-left: 4px solid #2563eb; }
    .disclaimer { background: #fef3c7; border-left-color: #f59e0b; padding: 15px; margin-top: 30px; }
    .prob-list { margin-left: 20px; }
    .prob-item { margin: 5px 0; }
  </style>
</head>
<body>
  <h1>🧠 Clinical Mental Health Assistant</h1>
  <p class="meta">Analysis Report | ${timestamp}</p>
  
  <h2>Patient Observations</h2>
  <div class="section">${escapeHtml(data.text)}</div>
  `;
  
  if (data.classification) {
    html += `
  <h2>Diagnostic Classification</h2>
  <div class="section">
    <p><strong>Primary Diagnosis:</strong> ${data.classification.pathology}</p>
    `;
    
    if (data.classification.confidence) {
      html += `<p><strong>Confidence Level:</strong> ${(data.classification.confidence * 100).toFixed(1)}%</p>`;
      
      if (data.classification.all_probabilities) {
        html += `<p><strong>Differential Diagnosis Probabilities:</strong></p><div class="prob-list">`;
        const sorted = Object.entries(data.classification.all_probabilities)
          .sort((a, b) => b[1] - a[1]);
        sorted.forEach(([label, prob]) => {
          html += `<div class="prob-item">• ${label}: ${(prob * 100).toFixed(1)}%</div>`;
        });
        html += `</div>`;
      }
    }
    html += `</div>`;
  }
  
  html += `
  <h2>Treatment Recommendations</h2>
  <div class="section">${escapeHtml(data.recommendation).replace(/\n/g, '<br>')}</div>
  
  <div class="disclaimer">
    <strong>⚠️ Professional Disclaimer:</strong><br><br>
    This AI-assisted analysis is intended as a clinical decision support tool. 
    Final diagnosis and treatment planning should incorporate comprehensive clinical 
    assessment, patient history, and professional clinical judgment. This system is 
    designed to augment, not replace, professional expertise.
  </div>
  
  <p style="text-align: center; color: #64748b; margin-top: 40px; font-size: 0.9em;">
    Generated by Clinical Mental Health Assistant | Export Date: ${new Date().toLocaleString()}
  </p>
</body>
</html>
  `;
  
  const blob = new Blob([html], { type: 'text/html' });
  downloadFile(blob, `clinical_analysis_${Date.now()}.html`);
  
  // Auto-open for print dialog
  const url = URL.createObjectURL(blob);
  const win = window.open(url, '_blank');
  if (win) {
    win.onload = () => {
      setTimeout(() => win.print(), 500);
    };
  }
}

// Download file utility
function downloadFile(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ==================== DARK MODE ====================

// Load dark mode preference
function loadDarkMode() {
  const isDark = localStorage.getItem(DARK_MODE_KEY) === 'true';
  if (isDark) {
    document.body.classList.add('dark-mode');
    darkModeToggle.textContent = '☀️';
  }
}

// Toggle dark mode
function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  const isDark = document.body.classList.contains('dark-mode');
  localStorage.setItem(DARK_MODE_KEY, isDark);
  darkModeToggle.textContent = isDark ? '☀️' : '🌙';
  
  // Smooth transition
  document.body.style.transition = 'background-color 0.3s, color 0.3s';
  setTimeout(() => {
    document.body.style.transition = '';
  }, 300);
}

// Load execution device status
async function loadExecutionDevice() {
  try {
    const response = await fetch(STATUS_URL);
    const data = await response.json();

    if (response.ok && data.device) {
      executionDevice.textContent = getDeviceIcon(data.device.toLowerCase());
      executionDevice.className = `device-${data.device.toLowerCase()}`;
    } else {
      executionDevice.textContent = 'Server not responding';
    }
  } catch (error) {
    executionDevice.textContent = 'Server disconnected';
    console.error("Error loading device status:", error);
  }
}

// Initialize
toggleManualMode();
loadExecutionDevice(); // Load device status on startup