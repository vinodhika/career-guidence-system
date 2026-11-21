/* Career Guidance & Recommendation System Interactive JS */

// Helper: Get CSRF token from cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// ==========================================
// 1. AI CHAT MODULE (Screen 1 CareerWithinU)
// ==========================================
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const messagesContainer = document.getElementById('chat-messages-container');

if (chatForm && chatInput && messagesContainer) {
  // Scroll to bottom initially
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  chatForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    // Render User Message immediately
    appendUserMessage(message);
    chatInput.value = '';

    // Render Typing Indicator
    const typingId = appendTypingIndicator();
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      const response = await fetch('/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ message: message })
      });

      const data = await response.json();
      removeTypingIndicator(typingId);

      if (data.status === 'success') {
        appendAssistantMessage(data.reply, data.cards, data.is_redirected, data.timestamp);
      } else {
        appendAssistantMessage("I can help with career-related questions. Would you like to explore a career or improve a skill?", [], true);
      }
    } catch (err) {
      removeTypingIndicator(typingId);
      appendAssistantMessage("I can help with career-related questions. Would you like to explore a career or improve a skill?", [], true);
    }

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  });
}

function appendUserMessage(text) {
  const msgDiv = document.createElement('div');
  msgDiv.className = 'message-row user-row';
  msgDiv.innerHTML = `
    <div class="message-bubble user-bubble">
      <p>${escapeHtml(text)}</p>
      <span class="message-time">Just now</span>
    </div>
    <div class="chat-avatar user-avatar-badge">You</div>
  `;
  messagesContainer.appendChild(msgDiv);
}

function appendAssistantMessage(text, cards = [], isRedirected = false, timeStr = 'Just now') {
  const msgDiv = document.createElement('div');
  msgDiv.className = 'message-row assistant-row';

  let cardsHtml = '';
  if (cards && cards.length > 0) {
    cardsHtml = `
      <div class="chat-cards-grid">
        ${cards.map(c => `
          <div class="chat-career-card">
            <div class="card-icon-title">
              <span class="card-icon">⚡</span>
              <div>
                <strong>${escapeHtml(c.title)}</strong>
                <span class="card-meta">${escapeHtml(c.category || 'Career Path')}</span>
              </div>
            </div>
            <div class="card-action-bar">
              <span class="match-badge">${escapeHtml(c.match || 'High Match')}</span>
              <a href="/careers/" class="explore-btn">Explore</a>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  // Format markdown style bold and bullets in text
  let formattedText = formatSimpleMarkdown(text);

  let redirectNotice = '';
  if (isRedirected) {
    redirectNotice = `<div class="redirect-notice"><small>🛡️ Guided by strict career scope boundaries</small></div>`;
  }

  msgDiv.innerHTML = `
    <div class="chat-avatar asst-avatar-badge">CW</div>
    <div class="message-bubble assistant-bubble">
      <div class="msg-text">${formattedText}</div>
      ${cardsHtml}
      ${redirectNotice}
      <span class="message-time">${timeStr}</span>
    </div>
  `;
  messagesContainer.appendChild(msgDiv);
}

function appendTypingIndicator() {
  const id = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.id = id;
  div.className = 'message-row assistant-row typing-row';
  div.innerHTML = `
    <div class="chat-avatar asst-avatar-badge">CW</div>
    <div class="message-bubble assistant-bubble typing-bubble">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>
  `;
  messagesContainer.appendChild(div);
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function sendPresetPrompt(text) {
  if (chatInput) {
    chatInput.value = text;
    chatInput.focus();
    if (chatForm) {
      chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
    }
  }
}

// ==========================================
// 2. GAMIFIED ROADMAP MODULE (Screen 2 Ascento)
// ==========================================
async function toggleMilestoneStatus(milestoneId, currentStatus) {
  let nextStatus = 'in_progress';
  if (currentStatus === 'not_started') nextStatus = 'in_progress';
  else if (currentStatus === 'in_progress') nextStatus = 'completed';
  else if (currentStatus === 'completed') nextStatus = 'not_started';

  try {
    const res = await fetch('/api/milestone/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ milestone_id: milestoneId, status: nextStatus })
    });
    const data = await res.json();
    if (data.status === 'success') {
      // Reload or update DOM
      window.location.reload();
    }
  } catch (e) {
    console.error(e);
  }
}

// ==========================================
// 3. CAREER FAVORITING & BINNING (Screen 3)
// ==========================================
async function toggleFavoriteCareer(careerId, btnElement) {
  try {
    const res = await fetch('/api/career/save/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ career_id: careerId, action: 'favorite' })
    });
    const data = await res.json();
    if (data.status === 'success') {
      if (data.is_favorited) {
        btnElement.classList.add('favorited');
        btnElement.innerHTML = '❤️';
      } else {
        btnElement.classList.remove('favorited');
        btnElement.innerHTML = '🤍';
      }
    }
  } catch (err) {
    console.error(err);
  }
}

async function binCareer(careerId, cardElementId) {
  if (!confirm("Hide this career from your active recommendations?")) return;
  try {
    const res = await fetch('/api/career/save/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ career_id: careerId, action: 'bin' })
    });
    const data = await res.json();
    if (data.status === 'success') {
      const card = document.getElementById(cardElementId);
      if (card) {
        card.style.opacity = '0';
        setTimeout(() => card.remove(), 300);
      }
    }
  } catch (err) {
    console.error(err);
  }
}

// ==========================================
// 4. CV UPLOAD & MOCK INTERVIEW (Screen 4 Aivance)
// ==========================================
function triggerCvUpload() {
  const fileInput = document.getElementById('cv-file-input');
  if (fileInput) fileInput.click();
}

async function handleCvFileSelected(input) {
  if (!input.files || input.files.length === 0) return;
  const file = input.files[0];
  const formData = new FormData();
  formData.append('cv_file', file);

  const statusEl = document.getElementById('cv-upload-status');
  if (statusEl) statusEl.innerText = "Analyzing CV with Career Engine...";

  try {
    const res = await fetch('/api/cv/upload/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken },
      body: formData
    });
    const data = await res.json();
    if (data.status === 'success') {
      if (statusEl) statusEl.innerHTML = `✅ <strong>${data.filename}</strong> analyzed! Extracted: ${data.extracted_skills}`;
    }
  } catch (err) {
    if (statusEl) statusEl.innerText = "CV Upload completed.";
  }
}

async function scheduleMockInterviewPrompt() {
  const role = prompt("Enter target role for your mock interview (e.g. Software Engineer, Data Scientist):", "Software Engineer");
  if (!role) return;

  try {
    const res = await fetch('/api/interview/schedule/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ role: role, time_slot: 'Tomorrow, 3:00 PM' })
    });
    const data = await res.json();
    alert(data.message || `Mock interview scheduled for ${role}!`);
    window.location.reload();
  } catch (e) {
    console.error(e);
  }
}

// ==========================================
// Utilities
// ==========================================
function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatSimpleMarkdown(txt) {
  // Bold **text**
  let output = txt.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Bullets • or *
  output = output.replace(/^[•*]\s*(.*)$/gm, '<li>$1</li>');
  output = output.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  // Linebreaks
  output = output.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');
  return output;
}
