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

// Event Listeners
analyzeBtn.addEventListener("click", analyzeCase);
clearBtn.addEventListener("click", clearChat);
autoClassify.addEventListener("change", toggleManualMode);
caseText.addEventListener("keydown", handleTextareaKeydown);

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

// Add loading message
function addLoadingMessage() {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message loading-message";
  messageDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="message-text">
        <div class="loading-spinner"></div>
        <span>Analyzing case data...</span>
      </div>
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
  
  // Add loading message
  const loadingMsg = addLoadingMessage();
  
  // Prepare payload
  const payload = {
    text,
    auto_classify: autoClassify.checked,
    pathology: autoClassify.checked ? null : pathology.value,
  };
  
  try {
    // Call API
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    
    // Remove loading message
    loadingMsg.remove();
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "API request failed");
    }
    
    const data = await response.json();
    
    // Show classification
    if (autoClassify.checked) {
      await simulateDelay(500);
      addBotMessage(formatClassification(data.classification));
    }
    
    // Show processing status (summary is processed but not displayed)
    await simulateDelay(300);
    addBotMessage(`
      <div class="info-message">
        ⏳ Generating clinical summary and treatment plan...
      </div>
    `);
    
    // Show recommendation
    await simulateDelay(700);
    addBotMessage(formatRecommendation(data.recommendation));
    
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