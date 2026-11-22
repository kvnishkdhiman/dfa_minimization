/**
 * DFA-Min Main Application Controller.
 * Manages UI state, stepper execution, API communication, and visualizations.
 */

// Application State
const appState = {
  currentDfa: null,
  minimizationData: null,
  currentStepIndex: 0,
  isPlaying: false,
  playTimer: null,
  playSpeedMs: 1200,
  originalViz: null,
  minimizedViz: null,
  comparisonOrigViz: null,
  comparisonMinViz: null,
};

document.addEventListener("DOMContentLoaded", () => {
  initVisualizers();
  initNavigationTabs();
  initEventListeners();
  loadPreset("textbook_6_state");
});

function initVisualizers() {
  appState.originalViz = new DFAVisualizer("cy-original");
  appState.minimizedViz = new DFAVisualizer("cy-minimized");
  appState.comparisonOrigViz = new DFAVisualizer("cy-comp-orig");
  appState.comparisonMinViz = new DFAVisualizer("cy-comp-min");
}

function initNavigationTabs() {
  const navBtns = document.querySelectorAll(".nav-btn");
  navBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      navBtns.forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((tab) => tab.classList.remove("active"));

      btn.classList.add("active");
      const targetTabId = btn.getAttribute("data-tab");
      const targetTab = document.getElementById(targetTabId);
      if (targetTab) {
        targetTab.classList.add("active");
      }

      // Re-fit cytoscape graphs when switching tabs to ensure proper dimensions
      setTimeout(() => {
        if (appState.originalViz) appState.originalViz.fit();
        if (appState.minimizedViz) appState.minimizedViz.fit();
        if (appState.comparisonOrigViz) appState.comparisonOrigViz.fit();
        if (appState.comparisonMinViz) appState.comparisonMinViz.fit();
      }, 150);
    });
  });
}

function initEventListeners() {
  // Preset selector
  const presetSelect = document.getElementById("preset-select");
  if (presetSelect) {
    presetSelect.addEventListener("change", (e) => {
      loadPreset(e.target.value);
    });
  }

  // Input changes triggering matrix regeneration
  const statesInput = document.getElementById("input-states");
  const alphabetInput = document.getElementById("input-alphabet");
  if (statesInput) statesInput.addEventListener("blur", updateFormOptionsAndMatrix);
  if (alphabetInput) alphabetInput.addEventListener("blur", updateFormOptionsAndMatrix);

  // Validate DFA button
  const validateBtn = document.getElementById("btn-validate-dfa");
  if (validateBtn) validateBtn.addEventListener("click", validateAndRenderDFA);

  // Run Minimization button
  const minimizeBtn = document.getElementById("btn-run-minimize");
  if (minimizeBtn) minimizeBtn.addEventListener("click", runMinimization);

  // Stepper buttons
  const btnPrev = document.getElementById("btn-step-prev");
  const btnNext = document.getElementById("btn-step-next");
  const btnPlay = document.getElementById("btn-step-play");
  const btnReset = document.getElementById("btn-step-reset");
  const btnEnd = document.getElementById("btn-step-end");
  const speedRange = document.getElementById("stepper-speed");

  if (btnPrev) btnPrev.addEventListener("click", stepPrev);
  if (btnNext) btnNext.addEventListener("click", stepNext);
  if (btnPlay) btnPlay.addEventListener("click", togglePlay);
  if (btnReset) btnReset.addEventListener("click", stepReset);
  if (btnEnd) btnEnd.addEventListener("click", stepJumpEnd);
  if (speedRange) {
    speedRange.addEventListener("input", (e) => {
      appState.playSpeedMs = parseInt(e.target.value, 10);
    });
  }

  // Distinguishing strings buttons
  const btnDistinguish = document.getElementById("btn-find-distinguishing");
  if (btnDistinguish) btnDistinguish.addEventListener("click", findDistinguishingString);

  const btnDistTable = document.getElementById("btn-compute-dist-table");
  if (btnDistTable) btnDistTable.addEventListener("click", computeDistinguishTable);

  // String testing simulation button
  const btnSimulate = document.getElementById("btn-run-simulation");
  if (btnSimulate) btnSimulate.addEventListener("click", runDualSimulation);

  // Formal equivalence verification button
  const btnFormalProof = document.getElementById("btn-run-formal-proof");
  if (btnFormalProof) btnFormalProof.addEventListener("click", runFormalVerification);

  // Graph toolbar buttons
  document.querySelectorAll("[data-viz-action]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const action = e.currentTarget.getAttribute("data-viz-action");
      const targetGraph = e.currentTarget.getAttribute("data-target-graph");
      handleGraphAction(targetGraph, action);
    });
  });
}

function handleGraphAction(target, action) {
  let viz = appState.originalViz;
  if (target === "minimized") viz = appState.minimizedViz;
  if (target === "comp-orig") viz = appState.comparisonOrigViz;
  if (target === "comp-min") viz = appState.comparisonMinViz;

  if (!viz) return;

  if (action === "fit") viz.fit();
  if (action === "zoom-in") viz.zoomIn();
  if (action === "zoom-out") viz.zoomOut();
  if (action === "layout-circle") viz.applyLayout("circle");
  if (action === "layout-cose") viz.applyLayout("cose");
  if (action === "layout-breadth") viz.applyLayout("breadthfirst");
}

function loadPreset(presetKey) {
  const preset = DFA_PRESETS[presetKey];
  if (!preset) return;

  document.getElementById("input-states").value = preset.states.join(", ");
  document.getElementById("input-alphabet").value = preset.alphabet.join(", ");

  updateFormOptionsAndMatrix(() => {
    document.getElementById("input-initial").value = preset.initial_state;

    // Accepting states
    const acceptSelect = document.getElementById("input-accepting");
    if (acceptSelect) {
      Array.from(acceptSelect.options).forEach((opt) => {
        opt.selected = preset.accepting_states.includes(opt.value);
      });
    }

    // Set transition matrix cells
    preset.states.forEach((s) => {
      preset.alphabet.forEach((sym) => {
        const cell = document.getElementById(`delta_${s}_${sym}`);
        if (cell && preset.transitions[s] && preset.transitions[s][sym]) {
          cell.value = preset.transitions[s][sym];
        }
      });
    });

    validateAndRenderDFA();
  });
}

function parseDFAFromForm() {
  const statesRaw = document.getElementById("input-states").value.split(",");
  const states = statesRaw.map((s) => s.trim()).filter((s) => s.length > 0);

  const alphabetRaw = document.getElementById("input-alphabet").value.split(",");
  const alphabet = alphabetRaw.map((a) => a.trim()).filter((a) => a.length > 0);

  const initial_state = document.getElementById("input-initial").value.trim();

  const acceptSelect = document.getElementById("input-accepting");
  const accepting_states = Array.from(acceptSelect.selectedOptions).map((o) => o.value.trim());

  const transitions = {};
  states.forEach((s) => {
    transitions[s] = {};
    alphabet.forEach((sym) => {
      const cell = document.getElementById(`delta_${s}_${sym}`);
      transitions[s][sym] = cell ? cell.value.trim() : "";
    });
  });

  return {
    states,
    alphabet,
    initial_state,
    accepting_states,
    transitions,
  };
}

function updateFormOptionsAndMatrix(callback) {
  const statesRaw = document.getElementById("input-states").value.split(",");
  const states = statesRaw.map((s) => s.trim()).filter((s) => s.length > 0);

  const alphabetRaw = document.getElementById("input-alphabet").value.split(",");
  const alphabet = alphabetRaw.map((a) => a.trim()).filter((a) => a.length > 0);

  // Update initial state dropdown
  const initSelect = document.getElementById("input-initial");
  const prevInit = initSelect.value;
  initSelect.innerHTML = "";
  states.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    initSelect.appendChild(opt);
  });
  if (states.includes(prevInit)) initSelect.value = prevInit;

  // Update accepting states multi-select
  const acceptSelect = document.getElementById("input-accepting");
  const prevAccepting = Array.from(acceptSelect.selectedOptions).map((o) => o.value);
  acceptSelect.innerHTML = "";
  states.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    if (prevAccepting.includes(s)) opt.selected = true;
    acceptSelect.appendChild(opt);
  });

  // Update state selectors in Distinguishing tab
  const statePSelect = document.getElementById("select-state-p");
  const stateQSelect = document.getElementById("select-state-q");
  if (statePSelect && stateQSelect) {
    statePSelect.innerHTML = "";
    stateQSelect.innerHTML = "";
    states.forEach((s, idx) => {
      const optP = document.createElement("option");
      optP.value = s;
      optP.textContent = `State ${s}`;
      statePSelect.appendChild(optP);

      const optQ = document.createElement("option");
      optQ.value = s;
      optQ.textContent = `State ${s}`;
      if (idx === 1) optQ.selected = true;
      stateQSelect.appendChild(optQ);
    });
  }

  // Generate Matrix Table
  const matrixContainer = document.getElementById("matrix-container");
  if (states.length === 0 || alphabet.length === 0) {
    matrixContainer.innerHTML = '<p class="form-hint">Enter states and alphabet to build transition table.</p>';
    return;
  }

  let html = '<table class="matrix-table"><thead><tr><th>δ(q, a)</th>';
  alphabet.forEach((sym) => {
    html += `<th>${sym}</th>`;
  });
  html += "</tr></thead><tbody>";

  states.forEach((s) => {
    html += `<tr><td class="state-cell">${s}</td>`;
    alphabet.forEach((sym) => {
      html += `<td><select class="matrix-select" id="delta_${s}_${sym}">`;
      states.forEach((targetState) => {
        html += `<option value="${targetState}">${targetState}</option>`;
      });
      html += `</select></td>`;
    });
    html += "</tr>";
  });
  html += "</tbody></table>";

  matrixContainer.innerHTML = html;

  if (typeof callback === "function") {
    callback();
  }
}

async function validateAndRenderDFA() {
  const dfa = parseDFAFromForm();
  const alertBox = document.getElementById("validation-alert");

  try {
    const res = await fetch("/api/dfa/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dfa),
    });

    const data = await res.json();
    if (!data.success) {
      alertBox.className = "step-explanation-box badge-danger";
      alertBox.style.display = "block";
      alertBox.innerHTML = `⚠️ <strong>Validation Error:</strong> ${data.error}`;
      return;
    }

    appState.currentDfa = data.dfa;
    alertBox.style.display = "none";

    // Reachability Alert
    const reachAlert = document.getElementById("reachability-alert");
    if (data.unreachable_states && data.unreachable_states.length > 0) {
      reachAlert.className = "step-explanation-box badge-warning";
      reachAlert.style.display = "block";
      reachAlert.innerHTML = `⚠️ <strong>Unreachable States Detected:</strong> [${data.unreachable_states.join(", ")}]. These states cannot be reached from initial state <code>${data.dfa.initial_state}</code> and will be pruned during minimization.`;
    } else {
      reachAlert.style.display = "none";
    }

    // Render Original DFA in Cytoscape
    appState.originalViz.loadElements(data.elements);

    // Auto-run minimization
    await runMinimization();
  } catch (err) {
    alertBox.className = "step-explanation-box badge-danger";
    alertBox.style.display = "block";
    alertBox.innerHTML = `⚠️ Network/Validation Error: ${err.message}`;
  }
}

async function runMinimization() {
  const dfa = parseDFAFromForm();

  try {
    const res = await fetch("/api/dfa/minimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dfa),
    });

    const data = await res.json();
    if (!data.success) {
      console.error("Minimization error:", data.error);
      return;
    }

    appState.minimizationData = data;
    appState.currentStepIndex = 0;

    // Update Comparison metrics
    document.getElementById("metric-orig-states").textContent = data.original_states_count;
    document.getElementById("metric-reach-states").textContent = data.reachable_states_count;
    document.getElementById("metric-min-states").textContent = data.minimized_states_count;

    const reductionPct = Math.round(
      ((data.original_states_count - data.minimized_states_count) / data.original_states_count) * 100
    );
    document.getElementById("metric-reduction").textContent = `${Math.max(0, reductionPct)}%`;

    // Render Minimized DFA Graph
    if (data.minimized_elements) {
      appState.minimizedViz.loadElements(data.minimized_elements);
      appState.comparisonMinViz.loadElements(data.minimized_elements);
    }
    if (data.original_elements) {
      appState.comparisonOrigViz.loadElements(data.original_elements);
    }

    renderCurrentStep();
    updateEquivalentPairsUI();
  } catch (err) {
    console.error("Error executing minimization:", err);
  }
}

function renderCurrentStep() {
  const data = appState.minimizationData;
  if (!data || !data.steps) return;

  const step = data.steps[appState.currentStepIndex];
  const stepCount = data.steps.length;

  // Update step indicators
  document.getElementById("step-counter").textContent = `Step ${appState.currentStepIndex + 1} of ${stepCount}`;
  const statusBadge = document.getElementById("step-status-badge");
  if (step.is_stable) {
    statusBadge.className = "badge badge-success";
    statusBadge.textContent = "Stable Fixed Point Reached";
  } else {
    statusBadge.className = "badge badge-gold";
    statusBadge.textContent = `Partition Refinement Round ${appState.currentStepIndex}`;
  }

  // Update 5-Stage Lifecycle Tracker
  updateLifecycleStages(step, appState.currentStepIndex, stepCount);

  // Update partitions visualization
  const pContainer = document.getElementById("partition-blocks-container");
  pContainer.innerHTML = "";

  const partitionMap = {};

  step.partitions.forEach((block, bIdx) => {
    const blockEl = document.createElement("div");
    blockEl.className = "p-block";
    blockEl.style.borderTop = `3px solid ${PARTITION_COLORS[bIdx % PARTITION_COLORS.length]}`;

    const title = document.createElement("div");
    title.className = "p-block-title";
    title.textContent = `Block P${bIdx} (${block.length})`;
    blockEl.appendChild(title);

    const statesList = document.createElement("div");
    statesList.className = "p-block-states";
    block.forEach((s) => {
      partitionMap[s] = bIdx;
      const chip = document.createElement("span");
      chip.className = "state-chip";
      chip.textContent = s;
      statesList.appendChild(chip);
    });
    blockEl.appendChild(statesList);
    pContainer.appendChild(blockEl);
  });

  // Render Textbook Successor-Block Signature Analysis Table
  renderSignatureAnalysisTable(step, appState.currentStepIndex);

  // Color original graph nodes according to current step's partition
  if (appState.originalViz) {
    appState.originalViz.applyPartitionColors(partitionMap);
  }

  // Explanation box
  document.getElementById("step-explanation").textContent = step.explanation;

  // Split details list
  const splitDetailsEl = document.getElementById("step-split-details");
  if (step.splits && step.splits.length > 0) {
    let splitHtml = '<div style="margin-top: 0.5rem; font-size: 0.85rem;"><strong>Splits triggered in this step:</strong><ul style="margin-left: 1.25rem; margin-top: 0.35rem;">';
    step.splits.forEach((sp) => {
      splitHtml += `<li>${sp.description}</li>`;
    });
    splitHtml += "</ul></div>";
    splitDetailsEl.innerHTML = splitHtml;
  } else {
    splitDetailsEl.innerHTML = "";
  }
}

function updateLifecycleStages(step, currentIdx, totalSteps) {
  const data = appState.minimizationData;
  const sReach = document.getElementById("stage-reachability");
  const sInit = document.getElementById("stage-init");
  const sSig = document.getElementById("stage-signatures");
  const sFix = document.getElementById("stage-fixedpoint");
  const sQuot = document.getElementById("stage-quotient");

  if (!sReach) return;

  // Reset stage classes
  [sReach, sInit, sSig, sFix, sQuot].forEach((el) => {
    el.className = "stage-step";
  });

  // Stage 1: Reachability is always analyzed
  const unreach = data.unreachable_states || [];
  sReach.classList.add("completed");
  const reachText = sReach.querySelector(".stage-text");
  if (reachText) {
    reachText.textContent = unreach.length > 0 ? `Reachability (${unreach.length} pruned)` : "Reachability (100%)";
  }

  // Stage 2: Initial P0
  if (currentIdx === 0) {
    sInit.classList.add("active");
  } else {
    sInit.classList.add("completed");
  }

  // Stage 3: Signature Refinement
  if (currentIdx > 0 && !step.is_stable) {
    sSig.classList.add("active");
  } else if (currentIdx > 0 && step.is_stable) {
    sSig.classList.add("completed");
  }

  // Stage 4: Fixed Point & Stage 5: Quotient DFA
  if (step.is_stable) {
    sFix.classList.add("active");
    sQuot.classList.add("active");
    sQuot.classList.add("completed");
  }
}

function renderSignatureAnalysisTable(step, currentIdx) {
  const container = document.getElementById("signature-table-container");
  const content = document.getElementById("signature-tables-content");
  const roundNumEl = document.getElementById("sig-round-num");
  if (!container || !content) return;

  const alphabet = (step.alphabet && step.alphabet.length > 0)
    ? step.alphabet
    : (appState.currentDfa && appState.currentDfa.alphabet ? appState.currentDfa.alphabet : ["0", "1"]);

  if (currentIdx === 0) {
    // Stage 2 / Step 0: Initial P0 epsilon-separation explanation
    container.style.display = "block";
    if (roundNumEl) roundNumEl.textContent = "0 (Initial P₀)";

    let p0Html = `
      <div class="sig-p0-box">
        <div class="sig-p0-title"><strong>Initial Partition P₀ by Empty String ε Distinguishability:</strong></div>
        <p style="margin: 0.4rem 0; font-size: 0.85rem; color: var(--text-secondary);">
          At string length 0 (input <code>w = ε</code>), accepting states and non-accepting states produce strictly opposite acceptance outcomes:
        </p>
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 0.5rem;">
          <div class="sig-p0-pill" style="border-left: 3px solid #2563eb;">
            <span class="p0-pill-badge" style="background: #2563eb; color: #fff;">Block P₀</span>
            <strong>Non-Accepting (Q \\ F):</strong> [${step.partitions[0] ? step.partitions[0].join(", ") : ""}]
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">δ*(q, ε) ∉ F → Rejected (Single Border)</div>
          </div>
          ${step.partitions.length > 1 ? `
          <div class="sig-p0-pill" style="border-left: 3px solid #10b981;">
            <span class="p0-pill-badge" style="background: #10b981; color: #fff;">Block P₁</span>
            <strong>Accepting (F):</strong> [${step.partitions[1].join(", ")}]
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">δ*(q, ε) ∈ F → Accepted (Double Circle)</div>
          </div>` : ""}
        </div>
      </div>
    `;
    content.innerHTML = p0Html;
    return;
  }

  // Step > 0: Signature tables for each block analyzed
  if (!step.signatures || Object.keys(step.signatures).length === 0) {
    if (step.is_stable) {
      container.style.display = "block";
      if (roundNumEl) roundNumEl.textContent = `${currentIdx} (Stable)`;
      content.innerHTML = `
        <div class="sig-stable-banner">
          <span style="font-size: 1.25rem;">✅</span>
          <div>
            <strong>Fixed-Point Convergence Reached:</strong> All states in every partition block possess identical transition signatures on every alphabet symbol. No further splits are possible!
          </div>
        </div>
      `;
    } else {
      container.style.display = "none";
    }
    return;
  }

  container.style.display = "block";
  if (roundNumEl) roundNumEl.textContent = `${currentIdx}`;

  let html = "";
  const sigBlocks = step.signatures;

  for (const [blkKey, blkData] of Object.entries(sigBlocks)) {
    const origBlock = blkData.original_block || [];
    if (origBlock.length <= 1) continue; // single state blocks don't need signature table

    const blkIdx = blkData.block_index !== undefined ? blkData.block_index : blkKey.replace("Block_", "");
    const didSplit = blkData.did_split;
    const subBlocks = blkData.sub_blocks || [];

    html += `
      <div class="sig-block-wrapper">
        <div class="sig-block-header">
          <span class="sig-block-tag" style="background: ${PARTITION_COLORS[blkIdx % PARTITION_COLORS.length]};">Block P${blkIdx}</span>
          <span style="font-weight: 700; color: #fff;">States {${origBlock.join(", ")}}</span>
          <span class="sig-status-badge ${didSplit ? 'badge-split' : 'badge-match'}">
            ${didSplit ? `⚠️ SPLITS into ${subBlocks.length} Sub-blocks` : '✓ STABLE (Identical Signatures)'}
          </span>
        </div>

        <table class="sig-table">
          <thead>
            <tr>
              <th>State q</th>
              ${alphabet.map((sym) => `<th>δ(q, ${sym}) → Target</th>`).join("")}
              <th>Signature Vector</th>
              <th>Outcome</th>
            </tr>
          </thead>
          <tbody>
    `;

    const stateDetails = blkData.state_details || {};
    origBlock.forEach((s) => {
      const sInfo = stateDetails[s];
      if (!sInfo) return;

      const sigLabel = sInfo.signature_label || (sInfo.targets ? `(${sInfo.targets.map(t => 'P' + t).join(', ')})` : '-');

      // Find which sub-block this state landed in if split
      let outcomeBadge = "";
      if (didSplit) {
        const subIdx = subBlocks.findIndex((sb) => sb.includes(s));
        outcomeBadge = `<span class="sig-subblock-chip">Sub-block ${subIdx + 1} {${subBlocks[subIdx] ? subBlocks[subIdx].join(", ") : s}}</span>`;
      } else {
        outcomeBadge = `<span class="sig-unified-chip">Unified in P${blkIdx}</span>`;
      }

      html += `
        <tr class="sig-row" onmouseenter="if(appState.originalViz) appState.originalViz.highlightState('${s}')" onmouseleave="if(appState.originalViz) appState.originalViz.resetHighlights()">
          <td class="sig-state-cell"><span class="state-chip">${s}</span></td>
      `;

      alphabet.forEach((sym) => {
        const dest = (sInfo.by_symbol && sInfo.by_symbol[sym]) || {};
        const tgtState = dest.target_state || "-";
        const tgtBlk = dest.target_block_idx !== undefined ? dest.target_block_idx : "-";
        const blkColor = tgtBlk !== "-" ? PARTITION_COLORS[tgtBlk % PARTITION_COLORS.length] : "#334155";
        html += `
          <td>
            <code>${tgtState}</code>
            <span class="sig-target-pill" style="border-color: ${blkColor}; color: ${blkColor};">P${tgtBlk}</span>
          </td>
        `;
      });

      html += `
          <td class="sig-vector-cell"><code>${sigLabel}</code></td>
          <td>${outcomeBadge}</td>
        </tr>
      `;
    });

    html += `
          </tbody>
        </table>
      </div>
    `;
  }

  content.innerHTML = html;
}

function stepNext() {
  if (!appState.minimizationData) return;
  if (appState.currentStepIndex < appState.minimizationData.steps.length - 1) {
    appState.currentStepIndex++;
    renderCurrentStep();
  } else {
    stopPlay();
  }
}

function stepPrev() {
  if (!appState.minimizationData) return;
  if (appState.currentStepIndex > 0) {
    appState.currentStepIndex--;
    renderCurrentStep();
  }
}

function stepReset() {
  stopPlay();
  appState.currentStepIndex = 0;
  renderCurrentStep();
}

function stepJumpEnd() {
  stopPlay();
  if (!appState.minimizationData) return;
  appState.currentStepIndex = appState.minimizationData.steps.length - 1;
  renderCurrentStep();
}

function togglePlay() {
  if (appState.isPlaying) {
    stopPlay();
  } else {
    startPlay();
  }
}

function startPlay() {
  if (!appState.minimizationData) return;
  appState.isPlaying = true;
  const playBtn = document.getElementById("btn-step-play");
  if (playBtn) playBtn.innerHTML = "⏸️ Pause";

  if (appState.currentStepIndex >= appState.minimizationData.steps.length - 1) {
    appState.currentStepIndex = 0;
    renderCurrentStep();
  }

  appState.playTimer = setInterval(() => {
    if (appState.currentStepIndex < appState.minimizationData.steps.length - 1) {
      stepNext();
    } else {
      stopPlay();
    }
  }, appState.playSpeedMs);
}

function stopPlay() {
  appState.isPlaying = false;
  if (appState.playTimer) clearInterval(appState.playTimer);
  const playBtn = document.getElementById("btn-step-play");
  if (playBtn) playBtn.innerHTML = "▶️ Play";
}

function updateEquivalentPairsUI() {
  const data = appState.minimizationData;
  if (!data) return;

  const eqList = document.getElementById("equivalent-pairs-list");
  if (!eqList) return;

  if (!data.equivalent_pairs || data.equivalent_pairs.length === 0) {
    eqList.innerHTML = '<span class="badge badge-info">No equivalent states detected. Automaton is already minimal.</span>';
    return;
  }

  let html = "";
  data.equivalent_pairs.forEach((pair) => {
    html += `<span class="badge badge-success" style="font-size: 0.85rem; padding: 0.35rem 0.65rem; margin-right: 0.5rem; margin-bottom: 0.5rem;">${pair[0]} ≡ ${pair[1]}</span>`;
  });
  eqList.innerHTML = html;
}

// ----------------------------------------------------
// Distinguishing String Feature
// ----------------------------------------------------
async function findDistinguishingString() {
  const stateP = document.getElementById("select-state-p").value;
  const stateQ = document.getElementById("select-state-q").value;
  const resultCard = document.getElementById("distinguishing-result-card");

  const dfa = parseDFAFromForm();

  try {
    const res = await fetch("/api/dfa/distinguish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dfa, state_p: stateP, state_q: stateQ }),
    });

    const data = await res.json();
    if (!data.success) {
      alert("Error: " + data.error);
      return;
    }

    const r = data.result;
    resultCard.style.display = "block";

    const badge = document.getElementById("dist-status-badge");
    const stringDisplay = document.getElementById("dist-string-val");
    const explanationEl = document.getElementById("dist-explanation-text");

    if (r.distinguishable) {
      badge.className = "badge badge-danger";
      badge.textContent = `Distinguishable (Length ${r.length})`;
      stringDisplay.textContent = r.display_string || '""';
      explanationEl.textContent = r.explanation;

      // Render Traces
      renderDistTrace("trace-p-container", stateP, r.trace_p, r.accepted_p);
      renderDistTrace("trace-q-container", stateQ, r.trace_q, r.accepted_q);
    } else {
      badge.className = "badge badge-success";
      badge.textContent = "Equivalent States (p ≡ q)";
      stringDisplay.textContent = "None (No distinguishing string exists)";
      explanationEl.textContent = r.explanation;
      document.getElementById("trace-p-container").innerHTML = '<p class="form-hint">States exhibit identical language acceptance behavior.</p>';
      document.getElementById("trace-q-container").innerHTML = '<p class="form-hint">States belong to the same equivalence class.</p>';
    }
  } catch (err) {
    console.error("Error finding distinguishing string:", err);
  }
}

function renderDistTrace(containerId, startState, trace, isAccepted) {
  const container = document.getElementById(containerId);
  if (!container || !trace) return;

  let html = `<div style="font-weight: 700; margin-bottom: 0.5rem; color: #fff;">Trace from State ${startState}:</div>`;
  html += '<div class="trace-steps">';

  trace.forEach((step, idx) => {
    if (idx > 0) {
      html += `<div class="trace-arrow">── (${step.symbol}) ──▶</div>`;
    }
    const isFinal = idx === trace.length - 1;
    const borderStyle = isFinal
      ? (isAccepted ? "border-color: #10b981; color: #6ee7b7;" : "border-color: #ef4444; color: #fca5a5;")
      : "";
    html += `<div class="trace-node" style="${borderStyle}">${step.state}</div>`;
  });

  html += "</div>";
  html += `<div style="margin-top: 0.5rem; font-size: 0.8rem; font-weight: 600;">Status: <span style="color: ${isAccepted ? "#10b981" : "#ef4444"};">${isAccepted ? "ACCEPTING ✓" : "REJECTING ✗"}</span></div>`;

  container.innerHTML = html;
}

async function computeDistinguishTable() {
  const dfa = parseDFAFromForm();
  const tableContainer = document.getElementById("dist-matrix-container");

  try {
    const res = await fetch("/api/dfa/distinguish-all", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dfa }),
    });

    const data = await res.json();
    if (!data.success) return;

    const states = data.table.states;
    const table = data.table.table;

    let html = '<table class="matrix-table" style="font-size: 0.8rem;"><thead><tr><th>p \\ q</th>';
    states.forEach((s) => {
      html += `<th>${s}</th>`;
    });
    html += "</tr></thead><tbody>";

    states.forEach((p) => {
      html += `<tr><td class="state-cell">${p}</td>`;
      states.forEach((q) => {
        if (p === q) {
          html += '<td style="background: rgba(31, 41, 55, 0.4); color: #6b7280;">-</td>';
        } else if (table[p] && table[p][q]) {
          const entry = table[p][q];
          const color = entry.distinguishable ? "#fca5a5" : "#6ee7b7";
          const label = entry.distinguishable ? (entry.string || "ε") : "≡";
          html += `<td style="color: ${color}; font-weight: 700;" title="${entry.explanation}">${label}</td>`;
        } else if (table[q] && table[q][p]) {
          const entry = table[q][p];
          const color = entry.distinguishable ? "#fca5a5" : "#6ee7b7";
          const label = entry.distinguishable ? (entry.string || "ε") : "≡";
          html += `<td style="color: ${color}; font-weight: 700;" title="${entry.explanation}">${label}</td>`;
        } else {
          html += "<td>-</td>";
        }
      });
      html += "</tr>";
    });

    html += "</tbody></table>";
    tableContainer.innerHTML = html;
  } catch (err) {
    console.error("Error computing distinguish table:", err);
  }
}

// ----------------------------------------------------
// String Testing & Simulation Studio
// ----------------------------------------------------
async function runDualSimulation() {
  const inputString = document.getElementById("test-string-input").value.trim();
  const resultsContainer = document.getElementById("sim-results-container");

  if (!appState.minimizationData || !appState.minimizationData.minimized_dfa) {
    alert("Please run minimization first to generate the minimized DFA.");
    return;
  }

  const payload = {
    original_dfa: parseDFAFromForm(),
    minimized_dfa: appState.minimizationData.minimized_dfa,
    input_string: inputString,
  };

  try {
    const res = await fetch("/api/dfa/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!data.success) {
      alert("Simulation error: " + data.error);
      return;
    }

    resultsContainer.style.display = "block";

    // Result match banner
    const matchBanner = document.getElementById("sim-match-banner");
    if (data.match) {
      matchBanner.className = "badge badge-success";
      matchBanner.innerHTML = `✅ Output Equivalent: Both automata produce matching acceptance for string "${data.test_string}".`;
    } else {
      matchBanner.className = "badge badge-danger";
      matchBanner.innerHTML = `❌ Output Discrepancy detected for string "${data.test_string}".`;
    }

    // Render Original Simulation Details
    renderSimDetail("sim-orig-details", "Original DFA", data.original_result);
    renderSimDetail("sim-min-details", "Minimized DFA", data.minimized_result);

    // Animate traces on the graphs
    if (data.original_result.path) {
      appState.comparisonOrigViz.animatePath(data.original_result.path);
    }
    if (data.minimized_result.path) {
      appState.comparisonMinViz.animatePath(data.minimized_result.path);
    }
  } catch (err) {
    console.error("Error during simulation:", err);
  }
}

function renderSimDetail(containerId, title, result) {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (!result.valid) {
    el.innerHTML = `<div class="badge badge-danger">Error: ${result.error}</div>`;
    return;
  }

  const statusColor = result.accepted ? "#10b981" : "#ef4444";
  const statusText = result.accepted ? "ACCEPTED" : "REJECTED";

  let html = `<div style="font-weight: 700; color: #fff; margin-bottom: 0.35rem;">${title}:</div>`;
  html += `<div style="font-size: 0.85rem; margin-bottom: 0.5rem;">Result: <span style="font-weight: 700; color: ${statusColor};">${statusText}</span> (Final state: <code>${result.final_state}</code>)</div>`;

  html += '<div style="font-size: 0.8rem; color: #9ca3af; margin-bottom: 0.25rem;">Execution Path:</div>';
  html += '<div class="trace-steps" style="font-size: 0.8rem;">';
  result.path.forEach((state, idx) => {
    if (idx > 0) {
      const sym = result.steps[idx - 1].symbol;
      html += `<div class="trace-arrow">── (${sym}) ──▶</div>`;
    }
    html += `<div class="trace-node" style="padding: 0.2rem 0.45rem;">${state}</div>`;
  });
  html += "</div>";

  el.innerHTML = html;
}

// ----------------------------------------------------
// Level 2: Formal Language Equivalence Verification
// ----------------------------------------------------
async function runFormalVerification() {
  if (!appState.minimizationData || !appState.minimizationData.minimized_dfa) {
    alert("Please run minimization first to generate the minimized DFA.");
    return;
  }

  const certContainer = document.getElementById("formal-proof-container");

  const payload = {
    dfa1: parseDFAFromForm(),
    dfa2: appState.minimizationData.minimized_dfa,
  };

  try {
    const res = await fetch("/api/dfa/verify-equivalence", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!data.success) {
      alert("Verification error: " + data.error);
      return;
    }

    const v = data.verification;
    certContainer.style.display = "block";

    const certTitle = document.getElementById("cert-status-title");
    const certStatement = document.getElementById("cert-statement");
    const certMath = document.getElementById("cert-math");
    const certExpl = document.getElementById("cert-explanation");

    if (v.is_equivalent) {
      certTitle.innerHTML = "🏆 Formal Mathematical Proof Certificate: EQUIVALENCE VERIFIED";
      certTitle.style.color = "#34d399";
      certStatement.innerHTML = "Theorem Proved: <strong>L(Original DFA) ≡ L(Minimized DFA)</strong>";
      certMath.innerHTML = `Explored Reachable Product Space: <strong>${v.states_explored}</strong> pairs out of theoretical upper bound <strong>${v.max_product_states}</strong> states.<br>
      Symmetric Difference Condition: <code>L(M1) △ L(M2) = ∅</code> strictly holds.<br>
      No counterexample string exists across Σ*.`;
      certExpl.textContent = v.explanation;
    } else {
      certTitle.innerHTML = "❌ Formal Verification: NOT EQUIVALENT";
      certTitle.style.color = "#f87171";
      certStatement.innerHTML = `Disproved with Counterexample: <code>"${v.counterexample}"</code>`;
      certMath.innerHTML = `Counterexample string "${v.counterexample}" produces differing acceptance in M1 vs M2.`;
      certExpl.textContent = v.explanation;
    }
  } catch (err) {
    console.error("Error running formal verification:", err);
  }
}
