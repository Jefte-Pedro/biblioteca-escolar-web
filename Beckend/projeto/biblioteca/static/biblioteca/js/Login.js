/* ══════════════════════════════════════════
   THEME
══════════════════════════════════════════ */
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute("data-theme") === "dark";
  html.setAttribute("data-theme", isDark ? "light" : "dark");
  const moon = document.getElementById("ico-moon");
  const sun = document.getElementById("ico-sun");
  if (moon) moon.style.display = isDark ? "none" : "block";
  if (sun) sun.style.display = isDark ? "block" : "none";
  localStorage.setItem("theme", isDark ? "light" : "dark");
}

/* Restore saved theme on load */
(function () {
  const saved = localStorage.getItem("theme");
  if (saved) {
    document.documentElement.setAttribute("data-theme", saved);
    const moon = document.getElementById("ico-moon");
    const sun = document.getElementById("ico-sun");
    if (moon) moon.style.display = saved === "dark" ? "block" : "none";
    if (sun) sun.style.display = saved === "dark" ? "none" : "block";
  }
})();

/* ══════════════════════════════════════════
   LOGIN — role toggle
══════════════════════════════════════════ */
function setRole(role) {
  const btnAluno = document.getElementById("btn-aluno");
  const btnFunc = document.getElementById("btn-func");
  const roleField = document.getElementById("role-field");
  const hint = document.getElementById("mat-hint");
  if (btnAluno) btnAluno.classList.toggle("active", role === "aluno");
  if (btnFunc) btnFunc.classList.toggle("active", role === "funcionario");
  if (roleField) roleField.value = role;
  if (hint)
    hint.textContent =
      role === "funcionario"
        ? "Número de matrícula do servidor"
        : "Apenas números · 7 dígitos";
}

/* ══════════════════════════════════════════
   LOGIN — password eye toggle
══════════════════════════════════════════ */
function togglePwd(inputId, eyeOffId, eyeOnId) {
  inputId = inputId || "senha";
  eyeOffId = eyeOffId || "eye-off";
  eyeOnId = eyeOnId || "eye-on";
  const inp = document.getElementById(inputId);
  if (!inp) return;
  const isHidden = inp.type === "password";
  inp.type = isHidden ? "text" : "password";
  const off = document.getElementById(eyeOffId);
  const on = document.getElementById(eyeOnId);
  if (off) off.style.display = isHidden ? "none" : "block";
  if (on) on.style.display = isHidden ? "block" : "none";
}

/* ══════════════════════════════════════════
   CADASTRO — state
══════════════════════════════════════════ */
const CAD = {
  step: 1, // current step (1|2|3)
  identity: null, // { name, turma, matricula } when found
  pwdOk: false,
  channelOk: false,
};

/* ── Step navigation ── */
function cadGoStep(n) {
  CAD.step = n;
  _cadRenderStepper();
  _cadRenderCols();
}

function _cadRenderStepper() {
  const subLabels = {
    1: { done: "Confirmada", active: "Em andamento", next: "Pendente" },
    2: { done: "Concluída", active: "Em andamento", next: "Próximo" },
    3: { done: "Concluído", active: "Em andamento", next: "Próximo" },
  };
  [1, 2, 3].forEach((i) => {
    const circle = document.getElementById("step-circle-" + i);
    const label = document.getElementById("step-label-" + i);
    const sub = document.getElementById("step-sub-" + i);
    const line = document.getElementById("step-line-" + i);
    if (!circle) return;

    circle.className = "step-circle";
    label.className = "step-label";
    if (sub) sub.className = "step-sub";

    if (i < CAD.step) {
      circle.classList.add("done");
      label.classList.add("done");
      if (sub) {
        sub.classList.add("done");
        sub.textContent = subLabels[i].done;
      }
      circle.innerHTML = _checkSVG();
      if (line) line.classList.add("done");
    } else if (i === CAD.step) {
      circle.classList.add("active");
      label.classList.add("active");
      circle.textContent = i;
      if (sub) {
        sub.classList.add("active");
        sub.textContent = subLabels[i].active;
      }
      if (line) line.classList.remove("done");
    } else {
      circle.textContent = i;
      if (sub) sub.textContent = subLabels[i].next;
      if (line) line.classList.remove("done");
    }
  });
}

function _cadRenderCols() {
  [1, 2, 3].forEach((i) => {
    const col = document.getElementById("cad-col-" + i);
    if (!col) return;
    col.className = "cad-col";
    if (i === CAD.step) col.classList.add("current");
    else col.classList.add("inactive");
  });
}

function _checkSVG() {
  return '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
}

/* ── Etapa 1: identity lookup ── */
function cadCheckIdentity() {
  const val = (document.getElementById("cad-matricula") || {}).value || "";
  const mat = val.trim();
  const resultEl = document.getElementById("cad-id-result");
  if (!mat || mat.length < 4) return;

  /* Simula busca — em produção isso vira um fetch ao Django */
  /* Substitua esta lógica pelo retorno real do backend       */
  const mockDB = [
    {
      matricula: "2024089",
      name: "Maria Silva Costa",
      turma: "3º A",
      initials: "MS",
    },
  ];
  const found = mockDB.find((u) => u.matricula === mat);

  if (found) {
    CAD.identity = found;
    resultEl.innerHTML = `
      <div class="id-result-card found">
        <div class="id-avatar">${found.initials}</div>
        <div>
          <div class="id-result-name">${found.name}</div>
          <div class="id-result-meta">${found.turma} · Matrícula ${found.matricula}</div>
        </div>
        <div class="id-check">${_checkSVG()}</div>
      </div>
      <div class="id-not-me">Se não for você, fale com a bibliotecária</div>`;
    document.getElementById("cad-next-1").disabled = false;
    document.getElementById("cad-next-1").classList.remove("submit-btn");
    document.getElementById("cad-next-1").className = "submit-btn";
  } else {
    CAD.identity = null;
    resultEl.innerHTML = `
      <div class="id-result-card not-found">
        <div style="font-size:12px;color:#EF4444">Matrícula não encontrada. Verifique o número ou fale com a bibliotecária.</div>
      </div>`;
    document.getElementById("cad-next-1").disabled = true;
  }
}

/* ── Etapa 2: password validation ── */
function cadCheckPwd() {
  const pwd = (document.getElementById("cad-pwd") || {}).value || "";
  const conf = (document.getElementById("cad-conf") || {}).value || "";

  const hasMin = pwd.length >= 8;
  const hasLetter = /[a-zA-Z]/.test(pwd);
  const hasNumber = /\d/.test(pwd);
  const matches = pwd === conf && pwd.length > 0;

  _setPwdCheck("chk-min", hasMin);
  _setPwdCheck("chk-letter", hasLetter && hasNumber);
  _setPwdCheck("chk-match", matches);

  /* Strength bar */
  const score = [hasMin, hasLetter, hasNumber, pwd.length >= 12].filter(
    Boolean,
  ).length;
  const fill = document.getElementById("pwd-fill");
  const lbl = document.getElementById("pwd-strength-lbl");
  const count = document.getElementById("pwd-char-count");
  if (fill) {
    const map = { 0: "0%", 1: "25%", 2: "55%", 3: "80%", 4: "100%" };
    const col = {
      0: "#EF4444",
      1: "#F59E0B",
      2: "#F59E0B",
      3: "#22C55E",
      4: "#22C55E",
    };
    fill.style.width = map[score];
    fill.style.background = col[score];
  }
  if (lbl) {
    const labels = {
      0: "",
      1: "Fraca",
      2: "Média",
      3: "Forte",
      4: "Muito forte",
    };
    lbl.textContent = labels[score];
    lbl.style.color =
      score >= 3 ? "#22C55E" : score >= 2 ? "#F59E0B" : "#EF4444";
  }
  if (count) count.textContent = pwd.length + " caracteres";

  const confInput = document.getElementById("cad-conf");
  if (confInput && conf.length > 0) {
    confInput.classList.toggle("valid", matches);
    confInput.classList.toggle("invalid", !matches);
  }

  CAD.pwdOk = hasMin && hasLetter && hasNumber && matches;
  const btn = document.getElementById("cad-next-2");
  if (btn) btn.disabled = !CAD.pwdOk;
}

function _setPwdCheck(id, ok) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle("ok", ok);
  const dot = el.querySelector(".pwd-check-dot");
  if (dot) dot.innerHTML = ok ? _checkSVG() : "";
}

/* ── Etapa 3: channels ── */
function cadToggleChannel(name) {
  const card = document.getElementById("ch-card-" + name);
  const wrap = document.getElementById("ch-input-" + name);
  const check = document.getElementById("ch-check-" + name);
  if (!card || !check) return;
  const selected = check.checked;
  card.classList.toggle("selected", selected);
  if (wrap) wrap.style.display = selected ? "block" : "none";
  _cadUpdateFinalizar();
}

function _cadUpdateFinalizar() {
  const emailChk = document.getElementById("ch-check-email");
  const waChk = document.getElementById("ch-check-wa");
  const anySelected =
    (emailChk && emailChk.checked) || (waChk && waChk.checked);
  CAD.channelOk = anySelected;
  const btn = document.getElementById("finalizar-btn");
  if (btn) btn.classList.toggle("ready", anySelected);
}
