// Personal Finance Advisor Bot - Advanced Frontend Script

// ---------------- 1. Category Definitions & Icons ---------------- //
const CATEGORY_MAP = {
  expense: [
    { value: "Food", label: "🍔 Food & Dining" },
    { value: "Rent", label: "🏠 Rent & Housing" },
    { value: "Transport", label: "🚗 Transport & Fuel" },
    { value: "Shopping", label: "🛍️ Shopping & Apparel" },
    { value: "Utilities", label: "⚡ Utilities & Bills" },
    { value: "Entertainment", label: "🎬 Entertainment & Fun" },
    { value: "Healthcare", label: "🏥 Healthcare & Meds" },
    { value: "Education", label: "🎓 Education & Books" },
    { value: "Bills", label: "📄 Recurring Bills" },
    { value: "Other", label: "🏷️ Other Expense" }
  ],
  income: [
    { value: "Salary", label: "💰 Monthly Salary" },
    { value: "Freelance", label: "💻 Freelance & Contract" },
    { value: "Investment", label: "📈 Investment Dividend" },
    { value: "Other", label: "🏷️ Other Inflow" }
  ]
};

function updateCategoryOptions(kind) {
  const catSelect = document.getElementById("category");
  if (!catSelect) return;

  const currentVal = catSelect.value;
  const list = CATEGORY_MAP[kind] || CATEGORY_MAP.expense;

  catSelect.innerHTML = "";
  list.forEach(item => {
    const opt = document.createElement("option");
    opt.value = item.value;
    opt.textContent = item.label;
    if (item.value === currentVal) opt.selected = true;
    catSelect.appendChild(opt);
  });
}

function onModalKindChange(kind) {
  const modalCat = document.getElementById("modalCategory");
  if (!modalCat) return;

  const list = CATEGORY_MAP[kind] || CATEGORY_MAP.expense;
  modalCat.innerHTML = "";
  list.forEach(item => {
    const opt = document.createElement("option");
    opt.value = item.value;
    opt.textContent = item.label;
    modalCat.appendChild(opt);
  });
}

// ---------------- 2. Live Header Clock ---------------- //
function updateLiveClock() {
  const clockElem = document.getElementById("liveClock");
  if (!clockElem) return;

  const textElem = clockElem.querySelector(".clock-text");
  if (!textElem) return;

  const now = new Date();
  const options = {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  };
  textElem.textContent = now.toLocaleDateString('en-IN', options);
}

// ---------------- 3. Dark / Light Theme Toggle ---------------- //
function initTheme() {
  const savedTheme = localStorage.getItem("fa_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
  const nextTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", nextTheme);
  localStorage.setItem("fa_theme", nextTheme);
}

// ---------------- 4. Quick Add Modal Functions ---------------- //
function openTxModal() {
  const overlay = document.getElementById("txModalOverlay");
  const modal = document.getElementById("txModalCard");
  if (!overlay || !modal) return;

  overlay.classList.add("active");
  const amtInput = document.getElementById("modalAmount");
  if (amtInput) {
    amtInput.value = "";
    setTimeout(() => amtInput.focus(), 150);
  }
}

function closeTxModal(e) {
  if (e && e.target && e.target.id !== "txModalOverlay") return;
  const overlay = document.getElementById("txModalOverlay");
  if (overlay) overlay.classList.remove("active");
}

function setQuickAmount(amt) {
  const input = document.getElementById("modalAmount");
  if (!input) return;
  const current = parseFloat(input.value) || 0;
  input.value = (current + amt).toFixed(0);
}

// ---------------- 5. Live Instant Client-Side Search ---------------- //
function initLiveSearch() {
  const searchBox = document.getElementById("liveSearchInput");
  const table = document.getElementById("txTable");
  if (!searchBox || !table) return;

  searchBox.addEventListener("input", function() {
    const query = this.value.toLowerCase().trim();
    const rows = table.querySelectorAll("tbody tr.tx-row");

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(query) ? "" : "none";
    });
  });
}

// ---------------- 6. Refresh AI Quick Advice ---------------- //
async function getAIAdvice() {
  const box = document.getElementById("advice");
  if (!box) return;

  box.innerHTML = '<div class="insight-row insight-loading"><span class="typing-dots"><span>.</span><span>.</span><span>.</span></span> AI Advisor analyzing records...</div>';
  try {
    const res = await fetch("/api/ai-advice");
    const data = await res.json();
    const adviceList = data.advice || [];

    if (adviceList.length === 0) {
      box.innerHTML = '<div class="insight-row"><div class="insight-icon-dot">💡</div><div class="insight-content">Keep logging transactions to receive personalized tips.</div></div>';
      return;
    }

    const tipsHtml = adviceList.map(item => `
      <div class="insight-row">
        <div class="insight-icon-dot">💡</div>
        <div class="insight-content">${escapeHtml(item)}</div>
      </div>
    `).join("");

    box.innerHTML = tipsHtml;
  } catch (err) {
    box.innerHTML = '<div class="insight-row"><div class="insight-icon-dot">⚠️</div><div class="insight-content">Unable to refresh insights right now. Please try again.</div></div>';
  }
}

// ---------------- 7. Interactive Conversational Chatbot ---------------- //
function toggleChatDrawer(open) {
  const drawer = document.getElementById("chatDrawer");
  const overlay = document.getElementById("chatOverlay");
  if (!drawer || !overlay) return;

  if (open) {
    drawer.classList.add("open");
    overlay.classList.add("open");
    const input = document.getElementById("chatInput");
    if (input) setTimeout(() => input.focus(), 250);
  } else {
    drawer.classList.remove("open");
    overlay.classList.remove("open");
  }
}

function clearChatHistory() {
  const container = document.getElementById("chatMessages");
  if (!container) return;
  container.innerHTML = `
    <div class="chat-msg bot">
      <div class="msg-avatar">🤖</div>
      <div class="msg-bubble">
        Chat cleared! How can I help you with your budget or financial goals today?
      </div>
    </div>
  `;
}

function sendSuggestedQuery(text) {
  const input = document.getElementById("chatInput");
  if (!input) return;
  input.value = text;
  handleChatSubmit(new Event("submit"));
}

async function handleChatSubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("chatInput");
  const messagesContainer = document.getElementById("chatMessages");
  const sendBtn = document.getElementById("chatSendBtn");
  if (!input || !messagesContainer) return;

  const text = input.value.trim();
  if (!text) return;

  // Append user bubble
  appendMessage("user", text);
  input.value = "";

  // Append loading bubble
  const loadingId = "msg-loading-" + Date.now();
  appendMessage("bot", '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span> Analyzing your finances...', loadingId);
  if (sendBtn) sendBtn.disabled = true;

  try {
    const res = await fetch("/api/ai-chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    const reply = data.reply || "I couldn't process that question. Please try asking in a different way!";

    const loadingElem = document.getElementById(loadingId);
    if (loadingElem) {
      const bubble = loadingElem.querySelector(".msg-bubble");
      if (bubble) bubble.innerHTML = formatMarkdown(reply);
    }
  } catch (err) {
    const loadingElem = document.getElementById(loadingId);
    if (loadingElem) {
      const bubble = loadingElem.querySelector(".msg-bubble");
      if (bubble) bubble.innerHTML = "Sorry, I had trouble connecting. Please try again shortly!";
    }
  } finally {
    if (sendBtn) sendBtn.disabled = false;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}

function appendMessage(sender, htmlContent, elementId = null) {
  const container = document.getElementById("chatMessages");
  if (!container) return;

  const msgDiv = document.createElement("div");
  msgDiv.className = `chat-msg ${sender}`;
  if (elementId) msgDiv.id = elementId;

  if (sender === "bot") {
    const avatar = document.createElement("div");
    avatar.className = "msg-avatar";
    avatar.textContent = "🤖";
    msgDiv.appendChild(avatar);
  }

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = sender === "user" ? escapeHtml(htmlContent) : htmlContent;

  msgDiv.appendChild(bubble);
  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

// ---------------- 8. Markdown Formatter ---------------- //
function formatMarkdown(str) {
  if (!str) return "";
  let text = escapeHtml(str);

  text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
  text = text.replace(/^\s*[•\-\*]\s+(.*)$/gm, "<li>$1</li>");
  text = text.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");
  text = text.replace(/\n\n/g, "<br><br>");
  text = text.replace(/\n/g, "<br>");

  return text;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, m => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }[m]));
}

// ---------------- 9. Initialize Everything On Load ---------------- //
document.addEventListener("DOMContentLoaded", function() {
  initTheme();
  updateLiveClock();
  setInterval(updateLiveClock, 30000); // Update clock every 30s
  initLiveSearch();

  // Toast auto-dismissal
  setTimeout(() => {
    document.querySelectorAll(".toast").forEach(toast => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      setTimeout(() => toast.remove(), 400);
    });
  }, 4000);
});
