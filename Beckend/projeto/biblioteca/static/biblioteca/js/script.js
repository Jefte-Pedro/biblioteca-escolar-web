/* ===== TRADUÇÕES ===== */

const traducoes = {
  pt: {
    idioma: "Português",
    inicio: "Início",
    lista: "Minha Lista",
    reservados: "Livros Reservados",
    lidos: "Livros Lidos",
    prazos: "Meus Prazos",
    busca: "Digite o nome do livro ou autor(a) que deseja buscar",
    sugestoes: "Sugestões de leitura",
    descricao:
      "Escolha livros que deseja ler e armazene em sua lista para acessar rapidamente quando precisar.",
  },
  en: {
    idioma: "English",
    inicio: "Home",
    lista: "My List",
    reservados: "Reserved Books",
    lidos: "Read Books",
    prazos: "My Deadlines",
    busca: "Type the book or author name you want to search",
    sugestoes: "Reading Suggestions",
    descricao:
      "Choose books you want to read and store them in your list for quick access.",
  },
  es: {
    idioma: "Español",
    inicio: "Inicio",
    lista: "Mi Lista",
    reservados: "Libros Reservados",
    lidos: "Libros Leídos",
    prazos: "Mis Plazos",
    busca: "Escribe el nombre del libro o autor que deseas buscar",
    sugestoes: "Sugerencias de lectura",
    descricao:
      "Elige libros que deseas leer y guárdalos en tu lista para acceder rápidamente.",
  },
};

/* ===== SISTEMA DE TEMA (DARK MODE) ===== */
const botaoTema = document.getElementById("alternar-tema");
const temaSalvo = localStorage.getItem("tema");

if (temaSalvo === "dark") {
  document.body.classList.add("dark");
}

if (botaoTema) {
  botaoTema.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    localStorage.setItem(
      "tema",
      document.body.classList.contains("dark") ? "dark" : "light",
    );
  });
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

  /* ===== SIDEBAR - SCROLL E RESPONSIVA (UNIFICADO) ===== */

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
      document.getElementById("nav-inicio").textContent =
        traducoes[lang].inicio;
      document.getElementById("nav-lista").textContent = traducoes[lang].lista;
      document.getElementById("nav-reservados").textContent =
        traducoes[lang].reservados;
      document.getElementById("nav-lidos").textContent = traducoes[lang].lidos;
      document.getElementById("busca-texto").placeholder =
        traducoes[lang].busca;

      const sugestoes = document.getElementById("sugestoes");
      if (sugestoes) sugestoes.textContent = traducoes[lang].sugestoes;

      document.querySelectorAll("#descricao").forEach((d) => {
        d.textContent = traducoes[lang].descricao;
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

  /* ===== ACESSIBILIDADE - FONTE ===== */

  const btnAumentar = document.getElementById("aumentar-fonte");
  const btnDiminuir = document.getElementById("diminuir-fonte");
  let tamanhoFonte = localStorage.getItem("fonte") || 16;

  document.documentElement.style.fontSize = tamanhoFonte + "px";

  if (btnAumentar) {
    btnAumentar.addEventListener("click", () => {
      tamanhoFonte++;
      document.documentElement.style.fontSize = tamanhoFonte + "px";
      localStorage.setItem("fonte", tamanhoFonte);
    });
  }

  if (btnDiminuir) {
    btnDiminuir.addEventListener("click", () => {
      tamanhoFonte--;
      document.documentElement.style.fontSize = tamanhoFonte + "px";
      localStorage.setItem("fonte", tamanhoFonte);
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

  /* ===== CARROSSEL - SETAS ===== */

  const lista = document.getElementById("lista-livros");
  if (lista) {
    lista.addEventListener("scroll", gerenciarEstadoDasSetas);
    gerenciarEstadoDasSetas();
    iniciarAutoPlay();

    lista.addEventListener(
      "touchstart",
      () => {
        pararTudo();
      },
      { passive: true },
    );
    lista.addEventListener(
      "touchend",
      () => {
        clearTimeout(inatividadeTimer);
        inatividadeTimer = setTimeout(iniciarAutoPlay, tempoRetorno);
      },
      { passive: true },
    );

    lista.addEventListener("mouseenter", pararTudo);
    lista.addEventListener("mouseleave", () => {
      if (!inatividadeTimer) {
        inatividadeTimer = setTimeout(iniciarAutoPlay, 2000);
      }
    });
  }
}); // <- fecha o DOMContentLoaded corretamente

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
