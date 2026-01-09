// frontend/js/app.js

const API_URL = "/api/v1/analyze";
const STREAM_URL = "/api/v1/analyze_stream";
const STATUS_URL = "/api/v1/get_status";

// Generation states
const State = {
  IDLE: 'idle',
  ANALYZING: 'analyzing',
  STREAMING: 'streaming',
  COMPLETED: 'completed',
  ERROR: 'error'
};

let currentState = State.IDLE;
const ANALYZING_TIMEOUT_MS = 30000; // 30 second failsafe

// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const caseText = document.getElementById("caseText");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const autoClassify = document.getElementById("autoClassify");
const pathology = document.getElementById("pathology");
const exampleButtons = document.querySelectorAll(".example-card");
const executionDevice = document.getElementById("executionDevice");
const sidebar = document.getElementById("sidebar");
const historyList = document.getElementById("historyList");
const sidebarToggle = document.getElementById("sidebarToggle");
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
caseText.addEventListener("input", autoResizeTextarea);
sidebarToggle.addEventListener("click", toggleSidebar);
clearHistoryBtn.addEventListener("click", clearHistory);
exportBtn.addEventListener("click", exportResults);
darkModeToggle.addEventListener("click", toggleDarkMode);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  renderHistory();
  loadExecutionDevice();
  loadDarkMode();
  
  // Auto-hide sidebar on mobile
  if (window.innerWidth <= 768) {
    sidebar.classList.add('hidden');
  }
});

// Handle example buttons
exampleButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const exampleType = btn.getAttribute("data-example");
    const exampleText = document.querySelector(`#exampleTexts [data-example="${exampleType}"]`);
    if (exampleText) {
      caseText.value = exampleText.textContent.trim();
      caseText.focus();
      autoResizeTextarea();
      
      // Hide welcome screen
      const welcomeScreen = document.querySelector('.welcome-screen');
      if (welcomeScreen) {
        welcomeScreen.remove();
      }
    }
  });
});

// Toggle sidebar
function toggleSidebar() {
  sidebar.classList.toggle('hidden');
}

// Toggle manual pathology selection
function toggleManualMode() {
  pathology.style.display = autoClassify.checked ? "none" : "block";
}

// Auto-resize textarea
function autoResizeTextarea() {
  caseText.style.height = 'auto';
  caseText.style.height = Math.min(caseText.scrollHeight, 200) + 'px';
}

// Handle Ctrl/Cmd + Enter to submit
function handleTextareaKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    analyzeCase();
  }
}

// Clear chat history
function clearChat() {
  chatMessages.innerHTML = `
    <div class="welcome-screen">
      <div class="welcome-icon">🧠</div>
      <h2>Clinical Mental Health Assistant</h2>
      <p class="welcome-subtitle">AI-powered diagnostic support for healthcare professionals</p>
      
      <div class="example-prompts">
        <button class="example-card" data-example="depression">
          <div class="example-title">Depression case</div>
          <div class="example-desc">Analyze a patient with depressive symptoms</div>
        </button>
        <button class="example-card" data-example="anxiety">
          <div class="example-title">Anxiety case</div>
          <div class="example-desc">Evaluate anxiety and panic symptoms</div>
        </button>
        <button class="example-card" data-example="bipolar">
          <div class="example-title">Bipolar case</div>
          <div class="example-desc">Assess mood fluctuation patterns</div>
        </button>
      </div>
    </div>
  `;
  caseText.value = "";
  autoResizeTextarea();
  lastAnalysisData = null;
  
  // Re-attach event listeners to example buttons
  document.querySelectorAll(".example-card").forEach(btn => {
    btn.addEventListener("click", () => {
      const exampleType = btn.getAttribute("data-example");
      const exampleText = document.querySelector(`#exampleTexts [data-example="${exampleType}"]`);
      if (exampleText) {
        caseText.value = exampleText.textContent.trim();
        caseText.focus();
        autoResizeTextarea();
        
        // Hide welcome screen
        const welcomeScreen = document.querySelector('.welcome-screen');
        if (welcomeScreen) {
          welcomeScreen.remove();
        }
      }
    });
  });
}

// Add user message to chat
function addUserMessage(text) {
  // Remove welcome screen if it exists
  const welcomeScreen = document.querySelector('.welcome-screen');
  if (welcomeScreen) {
    welcomeScreen.remove();
  }
  
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
      ${html}
    </div>
  `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
  return messageDiv;
}

// Add loading message
function addLoadingMessage() {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message loading-message";
  messageDiv.id = "loadingMessage";
  messageDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="loading">
        <span id="loadingText">Thinking</span>
        <div class="loading-dots">
          <div class="loading-dot"></div>
          <div class="loading-dot"></div>
          <div class="loading-dot"></div>
        </div>
      </div>
    </div>
  `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
  return messageDiv;
}

// Update loading message text
function updateLoadingMessage(text) {
  const loadingText = document.getElementById("loadingText");
  if (loadingText) {
    loadingText.textContent = text;
  }
}

// Remove loading message
function removeLoadingMessage() {
  const loadingMsg = document.getElementById("loadingMessage");
  if (loadingMsg) {
    loadingMsg.remove();
  }
}

// Add streaming message container
function addStreamingMessage() {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message streaming-message";
  messageDiv.id = "streamingMessage";
  messageDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div id="classificationContainer" class="classification-result" style="display:none;"></div>
      <div id="responseContainer" class="response-text"></div>
    </div>
  `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
  return messageDiv;
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

// Main analyze function with streaming support
async function analyzeCase() {
  const text = caseText.value.trim();
  
  // Validate input
  if (!text) {
    addBotMessage(`<div class="error-message">⚠️ Please enter patient clinical observations to analyze.</div>`);
    return;
  }
  
  if (text.length < 50) {
    addBotMessage(`<div class="error-message">⚠️ Please provide more detailed clinical observations (minimum 50 characters).</div>`);
    return;
  }
  
  // Disable button during analysis
  analyzeBtn.disabled = true;
  
  // Add user message
  addUserMessage(text);
  
  // Clear input
  caseText.value = "";
  autoResizeTextarea();
  
  // Start analyzing state
  currentState = State.ANALYZING;
  const loadingMsg = addLoadingMessage();
  
  // Failsafe timeout for analyzing state
  const timeoutId = setTimeout(() => {
    if (currentState === State.ANALYZING) {
      console.warn('Analyzing timeout - transitioning to error state');
      currentState = State.ERROR;
      removeLoadingMessage();
      addBotMessage(`<div class="error-message">⚠️ Analysis timeout. Please try again.</div>`);
      analyzeBtn.disabled = false;
    }
  }, ANALYZING_TIMEOUT_MS);
  
  // Prepare payload
  const payload = {
    text,
    auto_classify: autoClassify.checked,
    pathology: autoClassify.checked ? null : pathology.value,
  };
  
  try {
    // Use streaming endpoint
    const response = await fetch(STREAM_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      clearTimeout(timeoutId);
      removeLoadingMessage();
      const errorData = await response.json();
      throw new Error(errorData.detail || "API request failed");
    }
    
    // Process Server-Sent Events stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let classificationData = null;
    let fullRecommendation = '';
    
    // Create streaming message container (but keep it hidden initially)
    let streamingMsg = null;
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.type === 'classification') {
            // Classification received - transition from analyzing to streaming
            clearTimeout(timeoutId);
            currentState = State.STREAMING;
            removeLoadingMessage();
            
            // Create streaming container
            streamingMsg = addStreamingMessage();
            
            // Store classification data
            classificationData = data.classification;
            
            // Display classification
            const classContainer = document.getElementById('classificationContainer');
            if (classContainer && classificationData) {
              classContainer.style.display = 'block';
              let classHTML = `<h4>🔍 ${escapeHtml(classificationData.pathology)}</h4>`;
              
              if (classificationData.confidence) {
                const confidencePercent = (classificationData.confidence * 100).toFixed(1);
                classHTML += `
                  <p>Confidence: ${confidencePercent}%</p>
                  <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                  </div>
                `;
              }
              classContainer.innerHTML = classHTML;
            }
            
          } else if (data.type === 'text_chunk') {
            // Stream text chunks
            if (currentState === State.STREAMING) {
              fullRecommendation += data.content;
              const responseContainer = document.getElementById('responseContainer');
              if (responseContainer) {
                responseContainer.textContent = fullRecommendation;
                scrollToBottom();
              }
            }
            
          } else if (data.type === 'complete') {
            // Generation complete
            currentState = State.COMPLETED;
            
            // Save to history (without exposing clinical summary)
            lastAnalysisData = {
              text,
              classification: classificationData,
              recommendation: fullRecommendation,
              metadata: data.metadata,
              timestamp: new Date().toISOString()
            };
            addToHistory(lastAnalysisData);
            
          } else if (data.type === 'error') {
            throw new Error(data.error);
          }
        }
      }
    }
    
  } catch (error) {
    clearTimeout(timeoutId);
    removeLoadingMessage();
    currentState = State.ERROR;
    addBotMessage(`<div class="error-message">❌ Error: ${escapeHtml(error.message)}</div>`);
    console.error("Analysis error:", error);
  } finally {
    currentState = State.IDLE;
    analyzeBtn.disabled = false;
  }
}


// ==================== HISTORY MANAGEMENT ====================

function loadHistory() {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (e) {
    return [];
  }
}

function saveHistory() {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(caseHistory));
  } catch (e) {
    console.error('Error saving history:', e);
  }
}

function addToHistory(caseData) {
  const historyItem = {
    id: Date.now(),
    timestamp: new Date().toISOString(),
    preview: caseData.text.substring(0, 60) + '...',
    fullData: caseData
  };
  
  caseHistory.unshift(historyItem);
  
  if (caseHistory.length > 20) {
    caseHistory = caseHistory.slice(0, 20);
  }
  
  saveHistory();
  renderHistory();
}

function renderHistory() {
  if (caseHistory.length === 0) {
    historyList.innerHTML = '<p class="empty-history">No conversations yet</p>';
    return;
  }
  
  historyList.innerHTML = caseHistory.map(item => `
    <button class="history-item" data-id="${item.id}">
      ${escapeHtml(item.preview)}
    </button>
  `).join('');
  
  document.querySelectorAll('.history-item').forEach(item => {
    item.addEventListener('click', () => {
      const id = parseInt(item.getAttribute('data-id'));
      loadHistoryItem(id);
    });
  });
}

function loadHistoryItem(id) {
  const item = caseHistory.find(h => h.id === id);
  if (!item) return;
  
  clearChat();
  addUserMessage(item.fullData.text);
  
  // Redisplay results (without clinical summary)
  const { classification, recommendation } = item.fullData;
  
  // Create a message similar to the streaming result
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message";
  messageDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="classification-result">
        <h4>🔍 ${escapeHtml(classification.pathology)}</h4>
        ${classification.confidence ? `
          <p>Confidence: ${(classification.confidence * 100).toFixed(1)}%</p>
          <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${(classification.confidence * 100).toFixed(1)}%"></div>
          </div>
        ` : ''}
      </div>
      <div class="response-text">${escapeHtml(recommendation)}</div>
    </div>
  `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

function clearHistory() {
  if (confirm('Clear all conversation history?')) {
    caseHistory = [];
    saveHistory();
    renderHistory();
  }
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

function loadDarkMode() {
  const isDark = localStorage.getItem(DARK_MODE_KEY) === 'true';
  if (isDark) {
    document.body.classList.add('dark-mode');
    darkModeToggle.textContent = '☀️';
  }
}

function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  const isDark = document.body.classList.contains('dark-mode');
  localStorage.setItem(DARK_MODE_KEY, isDark);
  darkModeToggle.textContent = isDark ? '☀️' : '🌙';
}

// ==================== DEVICE STATUS ====================

async function loadExecutionDevice() {
  try {
    const response = await fetch(STATUS_URL);
    const data = await response.json();

    if (response.ok && data.device) {
      const deviceMap = {
        'cuda': '⚡ CUDA',
        'mps': '🍎 MPS',
        'cpu': '💻 CPU'
      };
      executionDevice.textContent = deviceMap[data.device.toLowerCase()] || data.device;
    } else {
      executionDevice.textContent = 'Offline';
    }
  } catch (error) {
    executionDevice.textContent = 'Offline';
  }
}
