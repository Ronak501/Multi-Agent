function toPct(value) {
  return `${(Number(value || 0) * 100).toFixed(2)}%`;
}

function scrollToSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (section) {
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function setOutput(id, text) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = text;
  }
}

function bindClick(id, handler) {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener("click", handler);
  }
}

function setHtml(id, html) {
  const el = document.getElementById(id);
  if (el) {
    el.innerHTML = html;
  }
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Request failed (${res.status}) for ${url}`);
  }
  return res.json();
}

function renderResults(payload) {
  const body = document.getElementById("resultsBody");
  const winner = document.getElementById("winner");
  body.innerHTML = "";

  (payload.results || []).forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.name}</td>
      <td>${toPct(item.final_accuracy)}</td>
      <td>${toPct(item.early_avg)}</td>
      <td>${toPct(item.late_avg)}</td>
      <td>${toPct(item.improvement)}</td>
    `;
    body.appendChild(tr);
  });

  if (payload.best_approach) {
    winner.textContent = `Best approach: ${payload.best_approach.name} (${toPct(payload.best_approach.final_accuracy)})`;
  } else {
    winner.textContent = "No result available.";
  }
}

async function runExperiment(event) {
  if (event) {
    event.preventDefault();
  }
  try {
    const episodes = document.getElementById("episodes")?.value || "30";
    const length = document.getElementById("length")?.value || "10";
    const payload = await fetchJson(
      `/api/experiments/?episodes=${episodes}&length=${length}`,
    );
    renderResults(payload);
  } catch (error) {
    setOutput("winner", `Experiment failed: ${error.message}`);
  }
}

async function loadDemo() {
  setHtml(
    "demoChatFlow",
    '<div class="flow-card"><h4>Preparing demo...</h4><p>Fetching speaker and listener messages.</p></div>',
  );
  setOutput("speakerOutput", "Generating...");
  setOutput("listenerOutput", "Generating...");
  try {
    const payload = await fetchJson("/api/demo/");

    const speakerChoices = (
      payload.speaker_agent?.generated_descriptions ||
      payload.descriptions ||
      []
    )
      .slice(0, 4)
      .map((d) => `<p>- ${escapeHtml(d)}</p>`)
      .join("");
    const chosen =
      payload.speaker_agent?.chosen_description ||
      payload.best_description ||
      "N/A";
    const selectedImage =
      payload.listener_agent?.selected_image || payload.selected || {};
    const confidence = payload.listener_agent?.confidence ?? payload.confidence;
    const isCorrect = payload.listener_agent?.is_correct ?? payload.success;

    setHtml(
      "demoChatFlow",
      `
      <div class="chat-row speaker">
        <div class="bubble">
          <h4>User -> Speaker</h4>
          <p>Describe the target image so the listener can identify it.</p>
          <div class="meta-line">Target: ${escapeHtml(JSON.stringify(payload.target || {}))}</div>
        </div>
      </div>
      <div class="chat-row speaker">
        <div class="bubble">
          <h4>Speaker -> Listener</h4>
          <p><strong>Chosen Message:</strong> ${escapeHtml(chosen)}</p>
          <div class="meta-line">Generated options:</div>
          ${speakerChoices || "<p>- No options</p>"}
        </div>
      </div>
      <div class="chat-row listener">
        <div class="bubble">
          <h4>Listener Response</h4>
          <p>Selected image: ${escapeHtml(JSON.stringify(selectedImage))}</p>
          <div class="meta-line">Confidence: ${escapeHtml(confidence)} | Correct: ${isCorrect ? "Yes" : "No"}</div>
        </div>
      </div>
      `,
    );

    setOutput(
      "speakerOutput",
      JSON.stringify(
        {
          target: payload.target,
          candidates: payload.candidates,
          generated_descriptions:
            payload.speaker_agent?.generated_descriptions ||
            payload.descriptions,
          chosen_description:
            payload.speaker_agent?.chosen_description ||
            payload.best_description,
        },
        null,
        2,
      ),
    );

    setOutput(
      "listenerOutput",
      JSON.stringify(
        {
          selected_image:
            payload.listener_agent?.selected_image || payload.selected,
          confidence: payload.listener_agent?.confidence ?? payload.confidence,
          is_correct: payload.listener_agent?.is_correct ?? payload.success,
        },
        null,
        2,
      ),
    );
  } catch (error) {
    setOutput("speakerOutput", `Demo failed: ${error.message}`);
    setOutput("listenerOutput", `Demo failed: ${error.message}`);
  }
}

async function loadImmacDemo() {
  setHtml(
    "immacFlow",
    '<div class="flow-card"><h4>Preparing IMMAC flow...</h4><p>Scoring surprise and routing messages.</p></div>',
  );
  setOutput("immacOutput", "Generating...");
  try {
    const payload = await fetchJson("/api/immac-demo/");
    const sent = (payload.messages_sent || [])
      .map(
        (m, i) => `
        <div class="flow-card">
          <h4>Message ${i + 1}: Agent ${escapeHtml(m.sender_id)}</h4>
          <p>Intrinsic value: ${escapeHtml(m.intrinsic_value)}</p>
          <div class="meta-line">Observation: ${escapeHtml(JSON.stringify(m.observation || {}))}</div>
        </div>
      `,
      )
      .join("");

    const ranked = (payload.top_attention || [])
      .map(
        (m, i) => `
        <div class="flow-card">
          <h4>Top Attention ${i + 1}: Agent ${escapeHtml(m.sender_id)}</h4>
          <p>Weight: ${escapeHtml(m.attention_weight)} | Intrinsic: ${escapeHtml(m.intrinsic_value)}</p>
        </div>
      `,
      )
      .join("");

    setHtml(
      "immacFlow",
      `
      <div class="flow-card">
        <h4>Step 1: Observe Environment</h4>
        <p>Total observations: ${(payload.observations || []).length}</p>
      </div>
      <div class="flow-card">
        <h4>Step 2: Intrinsic Gating</h4>
        <p>Gate threshold: ${escapeHtml(payload.gate_threshold)}</p>
      </div>
      ${sent || '<div class="flow-card"><h4>No sent messages</h4><p>No observation passed the gate.</p></div>'}
      <div class="flow-card">
        <h4>Step 3: Attention Routing</h4>
        <p>Top important messages selected for communication.</p>
      </div>
      ${ranked || '<div class="flow-card"><h4>No ranked messages</h4><p>Nothing to prioritize.</p></div>'}
      `,
    );
    setOutput("immacOutput", JSON.stringify(payload, null, 2));
  } catch (error) {
    setOutput("immacOutput", `IMMAC demo failed: ${error.message}`);
    setHtml(
      "immacFlow",
      `<div class="flow-card"><h4>IMMAC Demo Failed</h4><p>${escapeHtml(error.message)}</p></div>`,
    );
  }
}

async function loadA2aDemo() {
  setHtml(
    "a2aFlow",
    '<div class="flow-card"><h4>Preparing A2A flow...</h4><p>Client and remote agent are exchanging tasks.</p></div>',
  );
  setOutput("a2aOutput", "Generating...");
  try {
    const payload = await fetchJson("/api/a2a-demo/");
    const sync = payload.sync_flow || {};
    const asyncFlow = payload.async_flow || {};
    const events = asyncFlow.events || [];

    const syncUserIntent = sync.user_intent || "Unknown request";
    const syncArtifact = sync.rpc_response?.result?.artifact || {};
    const syncOutput = syncArtifact.output || {};

    const asyncUserIntent = asyncFlow.user_intent || "Unknown request";

    // Extract async output from the last completed event
    const completedEvent =
      events.find((ev) => ev.event === "task.completed") || {};
    const asyncArtifact = completedEvent.artifact || {};
    const asyncOutput = asyncArtifact.output || {};

    const eventHtml = events
      .map((ev) => {
        const eventType = ev.event || "unknown";
        let label = "";
        if (eventType === "task.created") {
          label = `✓ Created: ${escapeHtml(ev.task_type || "Task")}`;
        } else if (eventType === "task.running") {
          label = `▶ Running: Client Agent executing task`;
        } else if (eventType === "task.completed") {
          label = `✓ Completed: Task finished successfully`;
        } else {
          label = eventType;
        }
        return `
        <div class="flow-card">
          <p>${label}</p>
        </div>
      `;
      })
      .join("");

    const syncResultHtml = Object.entries(syncOutput)
      .map(
        ([key, val]) =>
          `<strong>${escapeHtml(key)}:</strong> ${escapeHtml(JSON.stringify(val))}`,
      )
      .join("<br>");

    const asyncResultHtml = Object.entries(asyncOutput)
      .map(
        ([key, val]) =>
          `<strong>${escapeHtml(key)}:</strong> ${escapeHtml(JSON.stringify(val))}`,
      )
      .join("<br>");

    setHtml(
      "a2aFlow",
      `
      <div class="flow-card" style="background: #f0f4ff; border-left: 4px solid #2563eb;">
        <h4>👥 Agents Involved: 2</h4>
        <p><strong>1. Client Agent</strong> - Orchestrates tasks<br>
           <strong>2. Remote Agent</strong> - Executes skills</p>
      </div>

      <div class="flow-card" style="background: #fef3c7; border-left: 4px solid #f59e0b;">
        <h4>❓ What User Asked (Sync)</h4>
        <p>${escapeHtml(syncUserIntent)}</p>
      </div>

      <div class="flow-card" style="background: #ecfdf5; border-left: 4px solid #10b981;">
        <h4>✓ Answer (Sync)</h4>
        <div style="font-size: 0.9em; line-height: 1.6;">${syncResultHtml || "No result"}</div>
      </div>

      <div class="flow-card" style="background: #fef3c7; border-left: 4px solid #f59e0b;">
        <h4>❓ What User Asked (Async)</h4>
        <p>${escapeHtml(asyncUserIntent)}</p>
      </div>

      <div class="flow-card" style="background: #ecfdf5; border-left: 4px solid #10b981;">
        <h4>✓ Answer (Async)</h4>
        <div style="font-size: 0.9em; line-height: 1.6;">${asyncResultHtml || "No result"}</div>
      </div>

      <div class="flow-card">
        <h4>⏱ Events Timeline</h4>
        ${eventHtml || "<p>No events recorded</p>"}
      </div>
      `,
    );
    setOutput("a2aOutput", JSON.stringify(payload, null, 2));
  } catch (error) {
    setOutput("a2aOutput", `A2A demo failed: ${error.message}`);
    setHtml(
      "a2aFlow",
      `<div class="flow-card"><h4>A2A Demo Failed</h4><p>${escapeHtml(error.message)}</p></div>`,
    );
  }
}

async function runAllDemos() {
  const btn = document.getElementById("runAllBtn");
  if (btn) {
    btn.textContent = "Running...";
  }
  await runExperiment();
  await loadDemo();
  await loadImmacDemo();
  await loadA2aDemo();
  if (btn) {
    btn.textContent = "Run All Demos";
  }
  scrollToSection("experiments");
}

(function init() {
  try {
    const initialEl = document.getElementById("initialData");
    if (initialEl?.textContent) {
      const initialPayload = JSON.parse(initialEl.textContent);
      renderResults(initialPayload);
    }

    const experimentForm = document.getElementById("experimentForm");
    if (experimentForm) {
      experimentForm.addEventListener("submit", runExperiment);
    }

    bindClick("demoBtn", loadDemo);
    bindClick("immacBtn", loadImmacDemo);
    bindClick("a2aBtn", loadA2aDemo);
    bindClick("goExperimentBtn", () => {
      runExperiment();
      scrollToSection("experiments");
    });
    bindClick("goDemoBtn", () => {
      loadDemo();
      scrollToSection("speaker-listener");
    });
    bindClick("goImmacBtn", () => {
      loadImmacDemo();
      scrollToSection("immac");
    });
    bindClick("goA2aBtn", () => {
      loadA2aDemo();
      scrollToSection("a2a");
    });
    bindClick("runAllBtn", runAllDemos);

    setOutput("speakerOutput", "Click Step 2 or Generate Demo");
    setOutput("listenerOutput", "Click Step 2 or Generate Demo");
    setOutput("immacOutput", "Click Step 3 or Run IMMAC Demo");
    setOutput("a2aOutput", "Click Step 4 or Run A2A Demo");
    setHtml(
      "demoChatFlow",
      '<div class="flow-card"><h4>Demo Chat View</h4><p>Click Step 2 or Generate Demo to see chat flow.</p></div>',
    );
    setHtml(
      "immacFlow",
      '<div class="flow-card"><h4>IMMAC Visual Flow</h4><p>Click Step 3 or Run IMMAC Demo to visualize gating and attention.</p></div>',
    );
    setHtml(
      "a2aFlow",
      '<div class="flow-card"><h4>A2A Visual Flow</h4><p>Click Step 4 or Run A2A Demo to view client-agent lifecycle.</p></div>',
    );
  } catch (error) {
    setOutput("immacOutput", `Page init failed: ${error.message}`);
    setOutput("a2aOutput", `Page init failed: ${error.message}`);
  }
})();
