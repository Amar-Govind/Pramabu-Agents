const state = {
  sessionId: localStorage.getItem("parambuChatSession") || "",
  files: [],
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
    agentListEl.innerHTML = "";
    for (const agent of data.agents || []) {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${agent.name}</strong><span>${agent.role}</span>`;
      li.style.cursor = "pointer";
      li.addEventListener("click", () => {
        inputEl.value = `Run ${agent.name} agent`;
        inputEl.focus();
      });
      agentListEl.appendChild(li);
    }
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

  try {
    const res = await fetch("/api/chat", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Chat request failed");

    state.sessionId = data.session_id;
    localStorage.setItem("parambuChatSession", state.sessionId);
    modePill.textContent = `${data.mode || "template"} · ${data.intent || "chat"}`;

    addMessage({
      role: "assistant",
      text: data.reply,
      files: data.files || [],
      meta: "Parambu Agents",
    });
  } catch (err) {
    addMessage({
      role: "system",
      text: err.message || "Something went wrong.",
    });
    modePill.textContent = "Error";
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
  addMessage({
    role: "system",
    text: "New chat started. Upload a brief or ask for a weekly campaign.",
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
  text: "Welcome. Ask any agent for help, or upload images/documents as input context. Generated posters and reports will appear as download chips.",
});
loadAgents();
