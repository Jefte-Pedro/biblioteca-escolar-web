/* ══════════════════════════════════════════
   ZOOM DE FOCO (mobile)
   Navegadores mobile dão zoom automático ao focar um campo com font-size
   menor que 16px, e não desfazem esse zoom sozinhos. Aqui a gente força
   a volta ao sair do campo, sem travar o pinça-zoom manual do usuário.
══════════════════════════════════════════ */

(function () {
  const viewport = document.querySelector('meta[name="viewport"]');
  if (!viewport) return;

  const conteudoOriginal = viewport.getAttribute("content");

  function resetarZoomDeFoco() {
    viewport.setAttribute("content", conteudoOriginal + ", maximum-scale=1.0");

    setTimeout(() => {
      viewport.setAttribute("content", conteudoOriginal);
    }, 300);
  }

  document.addEventListener("focusout", (e) => {
    const tag = e.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") {
      resetarZoomDeFoco();
    }
  });
})();

/* ══════════════════════════════════════════
   TEMA
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

/* Restaurar tema salvo ao carregar */
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
   LOGIN — alternar tipo de usuário (aluno / funcionário)
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
   LOGIN — mostrar/ocultar senha
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
   CADASTRO — estado das etapas
   OBS: a identidade (nome, série, matrícula) já vem pronta do Django —
   o campo de matrícula no cadastro.html é "readonly" e não dispara
   nenhuma verificação por JS. Por isso não existe mais uma função de
   "buscar identidade" aqui: isso é resolvido 100% no backend antes da
   página carregar. Esse objeto CAD cuida só da navegação entre as
   3 etapas visuais (identidade → senha → canais).
══════════════════════════════════════════ */

const CAD = {
  step: 1, // etapa atual (1|2|3)
  pwdOk: false,
  channelOk: false,
};

/* ── Navegação entre etapas ── */

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

/* ── Etapa 2: validação de senha ── */

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

/* ── Etapa 3: canais de contato ── */

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
