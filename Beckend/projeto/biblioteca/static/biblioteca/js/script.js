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

/* ===== UTILITÁRIO: CSRF ===== */

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

/* ===== CARREGAR HTML ===== */

document.addEventListener("DOMContentLoaded", () => {
  /* ===== TRANSIÇÃO SUAVE ENTRE PÁGINAS ===== */

  const mainEl = document.querySelector("main");

  mainEl.style.opacity = "0";
  mainEl.style.transition = "opacity 0.25s ease";
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

  /* ===== SISTEMA DE IDIOMA ===== */

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

  /* ===== SIDEBAR - SCROLL E RESPONSIVA ===== */

  const sidebar = document.querySelector(".sidebar");
  const menuBtn = document.getElementById("menu-toggle");

  if (sidebar) {
    document.body.setAttribute("tabindex", "-1");
    document.body.focus({ preventScroll: true });

    sidebar.querySelectorAll(".btn-sidebar").forEach((link) => {
      link.addEventListener(
        "focus",
        () => {
          const pos = sessionStorage.getItem("sidebar-scroll");
          if (pos) sidebar.scrollTop = parseInt(pos);
        },
        true,
      );
    });

    const restaurar = () => {
      const pos = sessionStorage.getItem("sidebar-scroll");
      if (pos) sidebar.scrollTop = parseInt(pos);
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
          menuBtn.querySelector("i").classList.replace("fa-times", "fa-bars");
        }
      });
    });
  }

  /* ===== ACESSIBILIDADE - FONTE ===== */

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

  /* ===== ABA ATIVA NO ACERVO ===== */

  const abaAtiva = document.querySelector(".conteudo-pag.ativo");
  if (abaAtiva) {
    document
      .querySelectorAll(".conteudo-pag")
      .forEach((p) => (p.style.display = "none"));
    abaAtiva.style.display = "block";
  }

  /* ===== CARROSSEL - INICIALIZAÇÃO ===== */

  const listaCarrossel = document.getElementById("lista-livros");
  if (listaCarrossel) {
    listaCarrossel.addEventListener("scroll", gerenciarEstadoDasSetas);
    gerenciarEstadoDasSetas();

    listaCarrossel.addEventListener(
      "touchstart",
      () => {
        pararTudo();
      },
      { passive: true },
    );
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

  /* ===== BUSCA DE LIVROS ===== */

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

  /* ===== MODAL DE LISTA ===== */

  const btnAbrirModal = document.getElementById("btn-abrir-modal");
  const btnConfirmarLista = document.getElementById("btn-confirmar-lista");
  const inputNomeLista = document.getElementById("input-nome-lista");
  const containerListas = document.getElementById("conteudo-dinamico-lista");

  if (btnAbrirModal) {
    btnAbrirModal.onclick = () => {
      document.getElementById("modal-lista").classList.add("aberto");
      inputNomeLista.focus();
    };
  }

  if (btnConfirmarLista) {
    btnConfirmarLista.onclick = async () => {
      const nome = inputNomeLista.value.trim();
      if (!nome) {
        alert("Digite um nome para a lista.");
        return;
      }

      const response = await fetch("/acervo/lista/criar/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ nome }),
      });

      if (response.ok) {
        const lista = await response.json();
        fecharModal();

        const msgVazia = document.getElementById("msg-sem-listas");
        if (msgVazia) msgVazia.remove();

        const div = document.createElement("div");
        div.className = "card-lista";
        div.dataset.listaId = lista.id;
        div.innerHTML = `
          <div class="info-lista" style="cursor:pointer; flex-grow: 1;">
            <h3>${lista.nome}</h3>
            <span class="qtd-livros">${lista.qtd_livros} livros</span>
          </div>
          <button class="btn-add-livro" onclick="event.stopPropagation();">
            <i class="fa-solid fa-plus"></i>
          </button>
          <button class="btn-deletar-lista" onclick="deletarLista(${lista.id}, this)" style="margin-left:8px;">
            <i class="fa-solid fa-trash"></i>
          </button>
        `;
        containerListas.appendChild(div);
      } else {
        alert("Erro ao criar lista.");
      }
    };
  }

  // NOTA: O modal de empréstimo é gerenciado pelo próprio emp-livro.html
  // Não há código de empréstimo aqui para evitar conflitos.
}); // <- fecha o DOMContentLoaded

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
      lista.scrollTo({ left: 0, behavior: "smooth" });
    } else {
      const primeiroCard = lista.querySelector(".card-livro");
      if (primeiroCard) {
        const largura =
          (primeiroCard.offsetWidth + 15) * (window.innerWidth <= 768 ? 1 : 2);
        lista.scrollBy({ left: largura, behavior: "smooth" });
      }
    }
  }, tempoEspera);
}

/* ===== LIVROS - CARREGAR E BUSCAR ===== */

async function carregarLivros() {
  const lista = document.getElementById("lista-livros");
  if (!lista) return;

  lista.innerHTML = '<p style="padding:20px;">Carregando livros...</p>';

  try {
    const response = await fetch("/api/livros/");
    if (!response.ok) throw new Error("Erro ao buscar livros");

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
    lista.innerHTML =
      '<p style="padding:20px; color:red;">Erro ao carregar livros.</p>';
    console.error(err);
  }
}

async function buscarLivros(termo) {
  const lista = document.getElementById("lista-livros");
  if (!lista) return;

  pararTudo();
  lista.innerHTML = '<p style="padding:20px;">Buscando...</p>';

  try {
    const response = await fetch(
      `/api/livros/?search=${encodeURIComponent(termo)}`,
    );
    if (!response.ok) throw new Error("Erro na busca");

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
    lista.innerHTML =
      '<p style="padding:20px; color:red;">Erro ao buscar livros.</p>';
    console.error(err);
  }
}

function criarCardLivro(livro) {
  const card = document.createElement("div");
  card.className = "card-livro";
  card.style.cursor = "pointer";
  card.innerHTML = `
    <img src="${livro.capa || ""}" alt="${livro.titulo}" onerror="this.style.display='none'">
    <p>${livro.titulo}</p>
    <span>${livro.autor}</span>
  `;
  card.addEventListener("click", () => abrirLivro(livro.id));
  return card;
}

/* ===== PÁGINA DO LIVRO ===== */

async function abrirLivro(id) {
  const pagina = document.getElementById("pag-livro");

  if (!pagina) {
    window.location.href = `/livro/${id}/`;
    return;
  }

  try {
    const response = await fetch(`/api/livros/${id}/`);
    if (!response.ok) throw new Error("Livro não encontrado");

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

    const statusEl = document.getElementById("livro-status");
    if (statusEl) {
      statusEl.textContent = livro.disponivel
        ? "✓ Disponível"
        : "✗ Indisponível";
      statusEl.style.color = livro.disponivel ? "green" : "red";
    }

    const statusEmp = document.getElementById("livro-status-Emprestado");
    if (statusEmp) {
      statusEmp.textContent = livro.disponivel
        ? ""
        : "Este livro está emprestado no momento.";
    }
  } catch (err) {
    console.error(err);
    alert("Erro ao carregar detalhes do livro.");
    pagina.style.display = "none";
  }
}

function voltarPagina() {
  const pagina = document.getElementById("pag-livro");
  if (pagina) pagina.style.display = "none";
}


/* ===== DELETAR LISTA ===== */

async function deletarLista(id, btn) {
  if (!confirm("Tem certeza que deseja deletar esta lista?")) return;

  const response = await fetch(`/acervo/lista/deletar/${id}/`, {
    method: "POST",
    headers: { "X-CSRFToken": getCookie("csrftoken") },
  });

  if (response.ok) {
    const card = btn.closest(".card-lista");
    if (card) card.remove();
  } else {
    alert("Erro ao deletar lista.");
  }
}

/* ===== EMPRÉSTIMOS - RENOVAR E DEVOLVER (fallback para outras páginas) ===== */
// Estas funções são sobrescritas pelo emp-livro.html quando estiver nessa página.
// Aqui ficam apenas como fallback para evitar erros em outras páginas.

if (typeof renovarEmprestimo === "undefined") {
  async function renovarEmprestimo(pk) {
    if (!confirm("Confirmar renovação deste empréstimo?")) return;
    const response = await fetch(`/biblioteca/emprestimos/renovar/${pk}/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
    });
    if (response.ok) {
      const data = await response.json();
      const card = document.getElementById(`emp-${pk}`);
      if (card) {
        card.querySelectorAll(".qtd-livros").forEach((s) => {
          if (s.textContent.includes("Devolução prevista")) {
            s.textContent = s.textContent.replace(
              /Devolução prevista: [\d-]+/,
              `Devolução prevista: ${data.nova_data}`,
            );
          }
        });
      }
    } else {
      const err = await response.json();
      alert(err.erro || "Erro ao renovar.");
    }
  }
}

if (typeof devolverEmprestimo === "undefined") {
  async function devolverEmprestimo(pk) {
    if (!confirm("Confirmar devolução?")) return;
    const response = await fetch(`/biblioteca/emprestimos/devolver/${pk}/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
    });
    if (response.ok) {
      const card = document.getElementById(`emp-${pk}`);
      if (card) card.remove();
    } else {
      alert("Erro ao registrar devolução.");
    }
  }
}
