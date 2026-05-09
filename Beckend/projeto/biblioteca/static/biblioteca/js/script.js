/* ===== TEMA ===== */
// Única fonte de verdade para tema em todo o projeto.
// Chave localStorage: "theme"  |  Valores: "dark" | "light" | "auto"

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
}

/**
 * toggleTheme()
 * Alterna dark ↔ light
 */
function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  setTheme(current === "dark" ? "light" : "dark");
}

/* Restaurar tema salvo */
(function () {
  const saved = localStorage.getItem("theme") || "dark";
  _applyTheme(saved);
})();

/* ===== CSRF ===== */

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

/* ===== DOM READY ===== */

document.addEventListener("DOMContentLoaded", () => {
  /* ===== TRANSIÇÃO ENTRE PÁGINAS ===== */

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

  /* ===== IDIOMA ===== */

  const botaoIdioma = document.querySelector(".idioma");
  const menuIdioma = document.querySelector(".idioma-menu");
  const idiomaTexto = document.getElementById("idioma-texto");

  if (botaoIdioma && menuIdioma) {
    botaoIdioma.addEventListener("click", () => {
      menuIdioma.classList.toggle("ativo");
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".idioma-container")) {
        menuIdioma.classList.remove("ativo");
      }
    });

    function trocarIdioma(lang) {
      idiomaTexto.textContent = traducoes[lang].idioma;

      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const chave = el.dataset.i18n;

        if (traducoes[lang][chave]) {
          el.textContent = traducoes[lang][chave];
        }
      });

      document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
        const chave = el.dataset.i18nPlaceholder;

        if (traducoes[lang][chave]) {
          el.placeholder = traducoes[lang][chave];
        }
      });

      localStorage.setItem("idioma", lang);
    }

    document.querySelectorAll(".idioma-menu button").forEach((btn) => {
      btn.addEventListener("click", () => {
        trocarIdioma(btn.dataset.lang);
        menuIdioma.classList.remove("ativo");
      });
    });

    const idiomaSalvo = localStorage.getItem("idioma") || "pt";
    trocarIdioma(idiomaSalvo);
  }

  /* ===== SIDEBAR ===== */

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

  /* ===== FONTE ===== */

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

  /* ===== CARROSSEL ===== */

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

  /* ===== BUSCA ===== */

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

  /* ===== MODAIS ===== */

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

/* ===== CARROSSEL ===== */

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

/* ===== LIVROS ===== */

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

  card.addEventListener("click", () => abrirLivro(livro.id));

  return card;
}

/* ===== DETALHE LIVRO ===== */

async function abrirLivro(id) {
  const pagina = document.getElementById("pag-livro");

  if (!pagina) {
    window.location.href = `${BASE_URL}/livro/${id}/`;

    return;
  }

  try {
    const response = await fetch(`${BASE_URL}/api/livros/${id}/`);

    if (!response.ok) {
      throw new Error("Livro não encontrado");
    }

    const livro = await response.json();

    document.getElementById("livro-titulo").textContent = livro.titulo;

    document.getElementById("livro-autor").textContent = livro.autor;

    document.getElementById("livro-genero").textContent = livro.genero;

    document.getElementById("livro-editora").textContent = livro.editora;

    document.getElementById("livro-sinopse").textContent = livro.sinopse;

    document.getElementById("livro-prateleira").textContent =
      `Prateleira: ${livro.endereco_prateleira}`;

    document.getElementById("livro-unidades").textContent =
      `Unidades disponíveis: ${livro.quantidade}`;

    document.getElementById("livro-codigo").textContent =
      `Edição: ${livro.edicao}`;

    const capa = document.getElementById("livro-capa");

    if (livro.capa) {
      capa.src = livro.capa;
      capa.style.display = "block";
    } else {
      capa.style.display = "none";
    }
  } catch (err) {
    console.error(err);

    alert("Erro ao carregar detalhes do livro.");
  }
}

/* ===== EMPRÉSTIMOS ===== */

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
