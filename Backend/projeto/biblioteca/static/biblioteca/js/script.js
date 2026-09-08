/* ══════════════════════════════════════════
   TEMA
   Única fonte de verdade para tema em todo o projeto.
   Chave localStorage: "theme"  |  Valores: "dark" | "light" | "auto"
══════════════════════════════════════════ */

const BASE_URL = "/biblioteca";

function _applyTheme(value) {
  const html = document.documentElement;

  let resolved = value;

  if (value === "auto") {
    resolved = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  html.setAttribute("data-theme", resolved);

  const moon = document.getElementById("ico-moon");
  const sun = document.getElementById("ico-sun");

  if (moon) moon.style.display = resolved === "dark" ? "block" : "none";
  if (sun) sun.style.display = resolved === "dark" ? "none" : "block";
}

/**
 * setTheme(value)
 * Usado pelas configurações: "dark" | "light" | "auto"
 */
function setTheme(value) {
  localStorage.setItem("theme", value);
  _applyTheme(value);
  window.dispatchEvent(new CustomEvent("themeChanged", { detail: value }));
}

/**
 * toggleTheme()
 * Alterna dark ↔ light
 */
function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  setTheme(current === "dark" ? "light" : "dark");
}

/* Restaurar tema salvo — com migração da chave antiga "tema" */
(function () {
  const old = localStorage.getItem("tema");
  if (old && !localStorage.getItem("theme")) {
    localStorage.setItem("theme", old);
    localStorage.removeItem("tema");
  }

  const saved = localStorage.getItem("theme") || "dark";
  _applyTheme(saved);
})();

/* ══════════════════════════════════════════
   IDIOMA
   Funções no escopo global para os onclick do HTML funcionarem.
══════════════════════════════════════════ */

const _langLabels = { pt: "PT", en: "EN", es: "ES" };

function toggleLangMenu() {
  const menu = document.getElementById("lang-menu");
  const btn = document.getElementById("lang-btn");

  if (!menu || !btn) return;

  const isOpen = menu.classList.contains("open");

  if (!isOpen) {
    const rect = btn.getBoundingClientRect();
    menu.style.top = rect.bottom + 8 + "px";
    menu.style.right = window.innerWidth - rect.right + "px";
    menu.style.left = "auto";
  }

  menu.classList.toggle("open");
}

function setLang(lang) {
  localStorage.setItem("idioma", lang);
  const el = document.getElementById("lang-texto");
  if (el) el.textContent = _langLabels[lang] || "PT";
  document.getElementById("lang-menu")?.classList.remove("open");

  if (typeof traducoes !== "undefined" && traducoes[lang]) {
    document.querySelectorAll("[data-i18n]").forEach((elT) => {
      if (traducoes[lang][elT.dataset.i18n]) {
        elT.textContent = traducoes[lang][elT.dataset.i18n];
      }
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((elT) => {
      if (traducoes[lang][elT.dataset.i18nPlaceholder]) {
        elT.placeholder = traducoes[lang][elT.dataset.i18nPlaceholder];
      }
    });
  }

  window.dispatchEvent(new CustomEvent("langChanged", { detail: lang }));
}

/* ══════════════════════════════════════════
   CSRF
══════════════════════════════════════════ */

function getCookie(name) {
  let cookieValue = null;

  if (document.cookie && document.cookie !== "") {
    document.cookie.split(";").forEach((cookie) => {
      cookie = cookie.trim();

      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
      }
    });
  }

  return cookieValue;
}

/* ══════════════════════════════════════════
   ZOOM DE FOCO (mobile)
   Navegadores mobile dão zoom automático ao focar um input/textarea/select
   com font-size menor que 16px. Esse zoom NÃO volta sozinho quando o campo
   perde o foco — o usuário precisa fazer o gesto de pinça manualmente.
   Aqui a gente força a volta: ao sair do campo, trava o zoom por um
   instante (obrigando o navegador a resetar a escala) e libera de novo
   logo em seguida, sem travar o pinça-zoom manual do usuário.
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

  // "focusout" (em vez de "blur") borbulha no DOM, então funciona pra
  // qualquer input/textarea/select da página — inclusive os que aparecem
  // depois, dentro de modais carregados dinamicamente.
  document.addEventListener("focusout", (e) => {
    const tag = e.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") {
      resetarZoomDeFoco();
    }
  });
})();

/* ══════════════════════════════════════════
   DOM READY
══════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
  /* ── Transição entre páginas ── */

  const mainEl = document.querySelector("main");

  if (mainEl) {
    mainEl.style.opacity = "0";
    mainEl.style.transition = "opacity .25s ease";

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        mainEl.style.opacity = "1";
      });
    });

    document.querySelectorAll(".btn-sidebar").forEach((link) => {
      link.addEventListener("click", function (e) {
        if (this.classList.contains("ativo")) return;

        e.preventDefault();

        const destino = this.href;

        mainEl.style.opacity = "0";

        setTimeout(() => {
          window.location.href = destino;
        }, 250);
      });
    });
  }

  /* ── Idioma — fechar ao clicar fora ── */

  document.addEventListener("click", function (e) {
    if (!e.target.closest("#lang-container")) {
      document.getElementById("lang-menu")?.classList.remove("open");
    }
  });

  /* ── Idioma — restaurar ao carregar ── */

  const salvoIdioma = localStorage.getItem("idioma") || "pt";
  const elLang = document.getElementById("lang-texto");
  if (elLang) elLang.textContent = _langLabels[salvoIdioma] || "PT";
  if (typeof traducoes !== "undefined" && traducoes[salvoIdioma]) {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      if (traducoes[salvoIdioma][el.dataset.i18n]) {
        el.textContent = traducoes[salvoIdioma][el.dataset.i18n];
      }
    });
  }

  /* ── Sidebar ── */

  const sidebar = document.querySelector(".sidebar");
  const menuBtn = document.getElementById("menu-toggle");

  if (sidebar) {
    document.body.setAttribute("tabindex", "-1");
    document.body.focus({ preventScroll: true });

    const restaurar = () => {
      const pos = sessionStorage.getItem("sidebar-scroll");

      if (pos) {
        sidebar.scrollTop = parseInt(pos);
      }
    };

    restaurar();
    setTimeout(restaurar, 0);
    setTimeout(restaurar, 100);

    sidebar.addEventListener("scroll", () => {
      sessionStorage.setItem("sidebar-scroll", sidebar.scrollTop);
    });

    window.addEventListener("beforeunload", () => {
      sessionStorage.setItem("sidebar-scroll", sidebar.scrollTop);
    });
  }

  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("aberta");

      const icon = menuBtn.querySelector("i");

      if (!icon) return;

      if (sidebar.classList.contains("aberta")) {
        icon.classList.replace("fa-bars", "fa-times");
      } else {
        icon.classList.replace("fa-times", "fa-bars");
      }
    });

    document.querySelectorAll(".btn-sidebar").forEach((link) => {
      link.addEventListener("click", () => {
        if (window.innerWidth <= 1024) {
          sidebar.classList.remove("aberta");

          const icon = menuBtn.querySelector("i");

          if (icon) {
            icon.classList.replace("fa-times", "fa-bars");
          }
        }
      });
    });
  }

  /* ── Fonte ── */

  const btnAumentar = document.getElementById("aumentar-fonte");
  const btnDiminuir = document.getElementById("diminuir-fonte");

  let tamanhoFonte = parseInt(localStorage.getItem("fonte")) || 16;

  const FONTE_PADRAO = 16;
  const FONTE_MIN = 12;
  const FONTE_MAX = 24;

  function aplicarFonte(tamanho) {
    const escala = tamanho / FONTE_PADRAO;

    document.documentElement.style.fontSize = tamanho + "px";

    document.documentElement.style.setProperty("--escala-fonte", escala);
  }

  function atualizarEstadoBotoesFonte() {
    const isPadrao = tamanhoFonte === FONTE_PADRAO;

    if (btnAumentar) {
      btnAumentar.classList.toggle("fonte-alterada", !isPadrao);
      btnAumentar.classList.toggle("fonte-padrao", isPadrao);
      btnAumentar.disabled = tamanhoFonte >= FONTE_MAX;
    }

    if (btnDiminuir) {
      btnDiminuir.classList.toggle("fonte-alterada", !isPadrao);
      btnDiminuir.classList.toggle("fonte-padrao", isPadrao);
      btnDiminuir.disabled = tamanhoFonte <= FONTE_MIN;
    }
  }

  aplicarFonte(tamanhoFonte);
  atualizarEstadoBotoesFonte();

  if (btnAumentar) {
    btnAumentar.addEventListener("click", () => {
      if (tamanhoFonte >= FONTE_MAX) return;

      tamanhoFonte++;

      localStorage.setItem("fonte", tamanhoFonte);

      aplicarFonte(tamanhoFonte);
      atualizarEstadoBotoesFonte();
    });
  }

  if (btnDiminuir) {
    btnDiminuir.addEventListener("click", () => {
      if (tamanhoFonte <= FONTE_MIN) return;

      tamanhoFonte--;

      localStorage.setItem("fonte", tamanhoFonte);

      aplicarFonte(tamanhoFonte);
      atualizarEstadoBotoesFonte();
    });
  }

  /* ── Carrossel ── */

  const listaCarrossel = document.getElementById("lista-livros");

  if (listaCarrossel) {
    listaCarrossel.addEventListener("scroll", gerenciarEstadoDasSetas);

    gerenciarEstadoDasSetas();

    listaCarrossel.addEventListener("touchstart", pararTudo, { passive: true });

    listaCarrossel.addEventListener(
      "touchend",
      () => {
        clearTimeout(inatividadeTimer);

        inatividadeTimer = setTimeout(iniciarAutoPlay, tempoRetorno);
      },
      { passive: true },
    );

    listaCarrossel.addEventListener("mouseenter", pararTudo);

    listaCarrossel.addEventListener("mouseleave", () => {
      if (!inatividadeTimer) {
        inatividadeTimer = setTimeout(iniciarAutoPlay, 2000);
      }
    });

    carregarLivros();
  }

  /* ── Busca ── */

  const inputBusca = document.getElementById("busca-texto");

  if (inputBusca) {
    let timerBusca;

    inputBusca.addEventListener("input", () => {
      clearTimeout(timerBusca);

      timerBusca = setTimeout(() => {
        const termo = inputBusca.value.trim();

        if (termo.length === 0) {
          carregarLivros();
        } else {
          buscarLivros(termo);
        }
      }, 400);
    });
  }

  /* ── Modais ── */

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;

    document.querySelectorAll(".modal-overlay").forEach((modal) => {
      if (modal.style.display !== "none") {
        modal.style.display = "none";
      }
    });
  });

  document.addEventListener("click", (e) => {
    if (!e.target.classList.contains("modal-overlay")) return;

    e.target.style.display = "none";
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;

    const input = e.target;

    if (!input.matches(".modal-overlay input, .modal-overlay textarea")) {
      return;
    }

    const modal = input.closest(".modal-overlay");

    if (!modal) return;

    const btnConfirm = modal.querySelector(
      ".modal-btn-confirm:not([disabled])",
    );

    if (btnConfirm) {
      btnConfirm.click();
    }
  });
});

/* ══════════════════════════════════════════
   CARROSSEL
══════════════════════════════════════════ */

let autoPlayInterval;
let inatividadeTimer;

const tempoEspera = 4000;
const tempoRetorno = 15000;

function pararTudo() {
  clearInterval(autoPlayInterval);
  clearTimeout(inatividadeTimer);
}

function scrollCarrossel(direcao) {
  const lista = document.getElementById("lista-livros");

  if (!lista) return;

  const primeiroCard = lista.querySelector(".card-livro");

  pararTudo();

  if (primeiroCard) {
    const larguraDoCard = primeiroCard.offsetWidth + 15;

    const multiplicador = window.innerWidth <= 768 ? 1 : 2;

    lista.scrollBy({
      left: direcao * (larguraDoCard * multiplicador),
      behavior: "smooth",
    });
  }

  inatividadeTimer = setTimeout(iniciarAutoPlay, tempoRetorno);
}

function gerenciarEstadoDasSetas() {
  const lista = document.getElementById("lista-livros");
  const setaEsq = document.querySelector(".seta-carrossel.esquerda");
  const setaDir = document.querySelector(".seta-carrossel.direita");

  if (!lista || !setaEsq || !setaDir) return;

  const scrollEsquerda = lista.scrollLeft;
  const scrollMaximo = lista.scrollWidth - lista.clientWidth;

  setaEsq.style.opacity = scrollEsquerda <= 10 ? "0.2" : "1";
  setaEsq.style.pointerEvents = scrollEsquerda <= 10 ? "none" : "auto";

  setaDir.style.opacity = scrollEsquerda >= scrollMaximo - 10 ? "0.2" : "1";

  setaDir.style.pointerEvents =
    scrollEsquerda >= scrollMaximo - 10 ? "none" : "auto";
}

function iniciarAutoPlay() {
  pararTudo();

  autoPlayInterval = setInterval(() => {
    const lista = document.getElementById("lista-livros");

    if (!lista) return;

    const scrollMaximo = lista.scrollWidth - lista.clientWidth;

    if (lista.scrollLeft >= scrollMaximo - 10) {
      lista.scrollTo({
        left: 0,
        behavior: "smooth",
      });
    } else {
      const primeiroCard = lista.querySelector(".card-livro");

      if (primeiroCard) {
        const largura =
          (primeiroCard.offsetWidth + 15) * (window.innerWidth <= 768 ? 1 : 2);

        lista.scrollBy({
          left: largura,
          behavior: "smooth",
        });
      }
    }
  }, tempoEspera);
}

/* ══════════════════════════════════════════
   LIVROS
══════════════════════════════════════════ */

async function carregarLivros() {
  const lista = document.getElementById("lista-livros");

  if (!lista) return;

  lista.innerHTML = '<p style="padding:20px;">Carregando livros...</p>';

  try {
    const response = await fetch(`${BASE_URL}/api/livros/`);

    if (!response.ok) {
      throw new Error("Erro ao buscar livros");
    }

    const livros = await response.json();

    livros.sort(() => Math.random() - 0.5);

    lista.innerHTML = "";

    if (livros.length === 0) {
      lista.innerHTML =
        '<p style="padding:20px;">Nenhum livro cadastrado ainda.</p>';

      return;
    }

    livros.forEach((livro) => {
      const card = criarCardLivro(livro);

      lista.appendChild(card);
    });

    gerenciarEstadoDasSetas();
    iniciarAutoPlay();
  } catch (err) {
    console.error(err);

    lista.innerHTML =
      '<p style="padding:20px;color:red;">Erro ao carregar livros.</p>';
  }
}

async function buscarLivros(termo) {
  const lista = document.getElementById("lista-livros");

  if (!lista) return;

  pararTudo();

  lista.innerHTML = '<p style="padding:20px;">Buscando...</p>';

  try {
    const response = await fetch(
      `${BASE_URL}/api/livros/?search=${encodeURIComponent(termo)}`,
    );

    if (!response.ok) {
      throw new Error("Erro na busca");
    }

    const livros = await response.json();

    lista.innerHTML = "";

    if (livros.length === 0) {
      lista.innerHTML = '<p style="padding:20px;">Nenhum livro encontrado.</p>';

      return;
    }

    livros.forEach((livro) => {
      const card = criarCardLivro(livro);

      lista.appendChild(card);
    });

    gerenciarEstadoDasSetas();
  } catch (err) {
    console.error(err);

    lista.innerHTML =
      '<p style="padding:20px;color:red;">Erro ao buscar livros.</p>';
  }
}

function criarCardLivro(livro) {
  const card = document.createElement("div");

  card.className = "card-livro";
  card.style.cursor = "pointer";

  card.innerHTML = `
    <img src="${livro.capa || ""}" alt="${livro.titulo}"
         onerror="this.style.display='none'">

    <p>${livro.titulo}</p>

    <span>${livro.autor || "Autor desconhecido"}</span>
  `;

  // A página de detalhe do livro é renderizada pelo Django (server-side),
  // então aqui é só navegar direto pra URL — sem SPA, sem fetch extra.
  card.addEventListener("click", () => {
    window.location.href = `${BASE_URL}/livro/${livro.id}/`;
  });

  return card;
}

/* ══════════════════════════════════════════
   EMPRÉSTIMOS
══════════════════════════════════════════ */

window.renovarEmprestimo =
  window.renovarEmprestimo ||
  async function (pk) {
    if (!confirm("Confirmar renovação deste empréstimo?")) {
      return;
    }

    const response = await fetch(`${BASE_URL}/emprestimos/renovar/${pk}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    if (response.ok) {
      window.location.reload();
    } else {
      const err = await response.json();

      alert(err.erro || "Erro ao renovar.");
    }
  };

window.devolverEmprestimo =
  window.devolverEmprestimo ||
  async function (pk) {
    if (!confirm("Confirmar devolução?")) {
      return;
    }

    const response = await fetch(`${BASE_URL}/emprestimos/devolver/${pk}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    if (response.ok) {
      window.location.reload();
    } else {
      alert("Erro ao registrar devolução.");
    }
  };
