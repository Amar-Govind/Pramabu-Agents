const state = {
  sessionId: localStorage.getItem("parambuChatSession") || "",
  files: [],
  agents: [],
  activeAgent: "Parambu Assistant",
};

const messagesEl = document.getElementById("messages");
const agentListEl = document.getElementById("agentList");
const formEl = document.getElementById("chatForm");
const inputEl = document.getElementById("messageInput");
const fileInputEl = document.getElementById("fileInput");
const filePillsEl = document.getElementById("filePills");
const dropzoneEl = document.getElementById("dropzone");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const modePill = document.getElementById("modePill");
const statusDot = document.getElementById("statusDot");
const setupBanner = document.getElementById("setupBanner");
const activeAgentName = document.getElementById("activeAgentName");
const activeAgentRole = document.getElementById("activeAgentRole");
const activeAgentBadge = document.getElementById("activeAgentBadge");
const modePillWrap = modePill?.parentElement;

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderMarkdown(text) {
  const escaped = escapeHtml(text || "");
  return escaped
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h3>$1</h3>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(?:<li>.*<\/li>\n?)+/g, (block) => `<ul>${block}</ul>`)
    .replace(/\n{2,}/g, "<br><br>")
    .replace(/\n/g, "<br>");
}

function setActiveAgent(name, role = "", badge = "") {
  state.activeAgent = name || "Parambu Assistant";
  activeAgentName.textContent = state.activeAgent;
  if (role) activeAgentRole.textContent = role;
  else {
    const found = state.agents.find((a) => a.name === state.activeAgent);
    activeAgentRole.textContent = found?.role || "Brand knowledge + specialist tools";
  }
  if (badge) activeAgentBadge.textContent = badge;
  [...agentListEl.querySelectorAll("li")].forEach((li) => {
    li.classList.toggle("active", li.dataset.name === state.activeAgent);
  });
}

function addMessage({ role, text, files = [], uploads = [], meta = "" }) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  if (meta) {
    const metaEl = document.createElement("div");
    metaEl.className = "meta";
    metaEl.textContent = meta;
    div.appendChild(metaEl);
  }
  const body = document.createElement("div");
  body.className = "md";
  if (role === "assistant" || role === "system") body.innerHTML = renderMarkdown(text);
  else body.textContent = text;
  div.appendChild(body);

  if (uploads.length) {
    const up = document.createElement("div");
    up.className = "uploads";
    up.textContent = "Attached: " + uploads.join(", ");
    div.appendChild(up);
  }

  if (files.length) {
    const wrap = document.createElement("div");
    wrap.className = "files";
    for (const file of files) {
      const a = document.createElement("a");
      a.className = "file-chip";
      a.href = file.url;
      a.download = file.name;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = `⬇ ${file.name}`;
      wrap.appendChild(a);
    }
    div.appendChild(wrap);
  }

  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderFilePills() {
  filePillsEl.innerHTML = "";
  state.files.forEach((file, index) => {
    const pill = document.createElement("span");
    pill.className = "file-pill";
    pill.innerHTML = `<span>${file.name}</span>`;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.setAttribute("aria-label", "Remove file");
    btn.textContent = "×";
    btn.addEventListener("click", () => {
      state.files.splice(index, 1);
      renderFilePills();
    });
    pill.appendChild(btn);
    filePillsEl.appendChild(pill);
  });
}

function addFiles(fileList) {
  for (const file of fileList) {
    if (![...state.files].some((f) => f.name === file.name && f.size === file.size)) {
      state.files.push(file);
    }
  }
  renderFilePills();
}

async function loadStatus() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    if (data.llm_enabled) {
      modePill.textContent = `LLM · ${data.model || "ready"}`;
      modePillWrap?.classList.add("ok");
      modePillWrap?.classList.remove("warn");
      setupBanner?.classList.add("hidden");
      activeAgentBadge.textContent = "LLM ready";
    } else {
      modePill.textContent = "Knowledge mode · add API key";
      modePillWrap?.classList.add("warn");
      modePillWrap?.classList.remove("ok");
      setupBanner?.classList.remove("hidden");
      activeAgentBadge.textContent = "Knowledge mode";
    }
  } catch {
    modePill.textContent = "Server offline";
    modePillWrap?.classList.add("warn");
  }
}

async function loadAgents() {
  try {
    const res = await fetch("/api/agents");
    const data = await res.json();
    state.agents = data.agents || [];
    agentListEl.innerHTML = "";
    for (const agent of state.agents) {
      const li = document.createElement("li");
      li.dataset.name = agent.name;
      li.innerHTML = `<strong>${agent.name}</strong><span>${agent.role}</span>`;
      li.style.cursor = "pointer";
      li.addEventListener("click", () => {
        setActiveAgent(agent.name, agent.role, "Selected");
        if (agent.key === "assistant") {
          inputEl.value = "";
          inputEl.placeholder = "Ask anything about Parambu…";
        } else if (agent.name === "Poster Production") {
          inputEl.value = "Create posters for Rose Soap";
        } else if (agent.key === "weekly" || agent.name === "Orchestrator") {
          inputEl.value = "Run a weekly campaign focused on soap";
        } else {
          inputEl.value = `Please run the ${agent.name} agent and summarize the plan`;
        }
        inputEl.focus();
      });
      agentListEl.appendChild(li);
    }
    setActiveAgent("Parambu Assistant", "Brand knowledge + specialist tools", "Ready");
  } catch {
    agentListEl.innerHTML = "<li><strong>Could not load agents</strong><span>Is the server running?</span></li>";
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;

  addMessage({
    role: "user",
    text: message,
    uploads: state.files.map((f) => f.name),
    meta: "You",
  });

  const form = new FormData();
  form.append("message", message);
  if (state.sessionId) form.append("session_id", state.sessionId);
  for (const file of state.files) form.append("files", file);

  inputEl.value = "";
  state.files = [];
  renderFilePills();
  sendBtn.disabled = true;
  modePill.textContent = "Thinking…";
  activeAgentBadge.textContent = "Thinking…";

  try {
    const res = await fetch("/api/chat", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Chat request failed");

    state.sessionId = data.session_id;
    localStorage.setItem("parambuChatSession", state.sessionId);

    const agent = data.agent || "Parambu Assistant";
    const found = state.agents.find((a) => a.name === agent);
    setActiveAgent(
      agent,
      found?.role || "Brand knowledge + specialist tools",
      `${data.mode || "knowledge"} · ${data.intent || "chat"}`
    );
    if (data.mode === "LLM") {
      modePill.textContent = `LLM · ${agent}`;
      modePillWrap?.classList.add("ok");
      modePillWrap?.classList.remove("warn");
    } else {
      modePill.textContent = `Knowledge · ${agent}`;
      modePillWrap?.classList.add("warn");
      modePillWrap?.classList.remove("ok");
    }

    addMessage({
      role: "assistant",
      text: data.reply,
      files: data.files || [],
      meta: agent,
    });

    if (data.llm && data.llm.ok === false && data.llm.error && data.intent === "chat") {
      // Keep quiet for normal knowledge answers; banner already explains setup.
    }
  } catch (err) {
    addMessage({
      role: "system",
      text: err.message || "Something went wrong.",
    });
    modePill.textContent = "Error";
    activeAgentBadge.textContent = "Error";
  } finally {
    sendBtn.disabled = false;
  }
});

clearBtn.addEventListener("click", () => {
  state.sessionId = "";
  localStorage.removeItem("parambuChatSession");
  state.files = [];
  renderFilePills();
  messagesEl.innerHTML = "";
  setActiveAgent("Parambu Assistant", "Brand knowledge + specialist tools", "Ready");
  addMessage({
    role: "system",
    text: "New chat started. Ask me about Parambu products, voice, or campaigns — or upload a brief.",
  });
  modePill.textContent = "Ready";
});

fileInputEl.addEventListener("change", () => {
  addFiles(fileInputEl.files);
  fileInputEl.value = "";
});

["dragenter", "dragover"].forEach((evt) => {
  dropzoneEl.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzoneEl.classList.add("dragover");
  });
});
["dragleave", "drop"].forEach((evt) => {
  dropzoneEl.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzoneEl.classList.remove("dragover");
  });
});
dropzoneEl.addEventListener("drop", (e) => {
  if (e.dataTransfer?.files?.length) addFiles(e.dataTransfer.files);
});

// Enter to send, Shift+Enter for newline
inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});

addMessage({
  role: "system",
  text: "Hi — I’m **Parambu Assistant**. I use your brand bible, product catalog, and any files you upload as my knowledge base.\n\nAsk naturally, like chatting with an LLM. Example: “What’s special about Rose Soap?” or “Create posters for neem soap”.",
});
loadStatus();
loadAgents();
