const state = {
  sessionId: localStorage.getItem("parambuChatSession") || "",
  files: [],
  agents: [],
  activeAgent: "Orchestrator",
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
const activeAgentName = document.getElementById("activeAgentName");
const activeAgentRole = document.getElementById("activeAgentRole");
const activeAgentBadge = document.getElementById("activeAgentBadge");

function setActiveAgent(name, role = "", badge = "") {
  state.activeAgent = name || "Orchestrator";
  activeAgentName.textContent = state.activeAgent;
  if (role) activeAgentRole.textContent = role;
  else {
    const found = state.agents.find((a) => a.name === state.activeAgent);
    activeAgentRole.textContent = found?.role || "Specialist agent";
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
  body.textContent = text;
  div.appendChild(body);

  if (uploads.length) {
    const up = document.createElement("div");
    up.className = "uploads";
    up.textContent = "Uploaded: " + uploads.join(", ");
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
        if (agent.key === "weekly") inputEl.value = "Run weekly campaign";
        else if (agent.name === "Poster Production") inputEl.value = "Create posters";
        else inputEl.value = `Run ${agent.name} agent`;
        inputEl.focus();
      });
      agentListEl.appendChild(li);
    }
    setActiveAgent("Orchestrator", "Full weekly campaign pipeline", "Ready");
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
  modePill.textContent = "Agents working…";
  activeAgentBadge.textContent = "Working…";

  try {
    const res = await fetch("/api/chat", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Chat request failed");

    state.sessionId = data.session_id;
    localStorage.setItem("parambuChatSession", state.sessionId);

    const agent = data.agent || "Orchestrator";
    const found = state.agents.find((a) => a.name === agent);
    setActiveAgent(agent, found?.role || "", `${data.mode || "template"} · ${data.intent || "chat"}`);
    modePill.textContent = agent;

    const focusBits = [];
    if (data.focus?.products?.length) focusBits.push(data.focus.products.join(", "));
    const focusNote = focusBits.length ? ` · Focus: ${focusBits.join(" · ")}` : "";

    addMessage({
      role: "assistant",
      text: data.reply,
      files: data.files || [],
      meta: `${agent}${focusNote}`,
    });
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
  setActiveAgent("Orchestrator", "Full weekly campaign pipeline", "Ready");
  addMessage({
    role: "system",
    text: "New chat started. Select an agent above or ask for a weekly campaign.",
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

addMessage({
  role: "system",
  text: "Welcome. Pick an agent from the left, or type a request. Mentions like “rose soap” or “crm” change the reply.",
});
loadAgents();
