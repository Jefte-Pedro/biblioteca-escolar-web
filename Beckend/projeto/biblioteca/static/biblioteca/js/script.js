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

// 1. Aplica o tema imediatamente ao carregar a página
if (temaSalvo === "dark") {
  document.body.classList.add("dark");
}

// 2. Faz o botão funcionar e salvar a escolha do usuário
if (botaoTema) {
  botaoTema.addEventListener("click", () => {
    document.body.classList.toggle("dark");

    if (document.body.classList.contains("dark")) {
      localStorage.setItem("tema", "dark");
    } else {
      localStorage.setItem("tema", "light");
    }
  });
}

/* ===== CARREGAR HTML ===== */

document.addEventListener("DOMContentLoaded", () => {
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
      document.getElementById("sugestoes").textContent =
        traducoes[lang].sugestoes;

      const descricoes = document.querySelectorAll("#descricao");
      descricoes.forEach((d) => (d.textContent = traducoes[lang].descricao));

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
});

/* ===== LÓGICA DE NAVEGAÇÃO DO CARROSSEL (ESTILO NETFLIX) ===== */

function scrollCarrossel(direcao) {
  const lista = document.getElementById("lista-livros");
  // Busca o primeiro card disponível dentro da lista
  const primeiroCard = lista.querySelector(".card-livro");

  if (primeiroCard) {
    // Pega a largura real do card + o espaço (gap) entre eles
    const larguraDoCard = primeiroCard.offsetWidth + 15;

    // Se for celular (tela < 768px), move apenas 1 card.
    // Se for PC, move 2 para ser mais rápido.
    const multiplicador = window.innerWidth <= 768 ? 1 : 2;

    lista.scrollBy({
      left: direcao * (larguraDoCard * multiplicador),
      behavior: "smooth",
    });
  }
}

// Função para dar o feedback visual de "seta desativada"
function gerenciarEstadoDasSetas() {
  const lista = document.getElementById("lista-livros");
  const setaEsq = document.querySelector(".seta-carrossel.esquerda");
  const setaDir = document.querySelector(".seta-carrossel.direita");

  if (!lista || !setaEsq || !setaDir) return;

  const scrollEsquerda = lista.scrollLeft;
  // Largura total do conteúdo menos a largura visível
  const scrollMaximo = lista.scrollWidth - lista.clientWidth;

  // Lógica para a Seta Esquerda (Início)
  if (scrollEsquerda <= 10) {
    setaEsq.style.opacity = "0.2";
    setaEsq.style.pointerEvents = "none"; // Impede o clique
  } else {
    setaEsq.style.opacity = "1";
    setaEsq.style.pointerEvents = "auto";
  }

  // Lógica para a Seta Direita (Fim)
  if (scrollEsquerda >= scrollMaximo - 10) {
    setaDir.style.opacity = "0.2";
    setaDir.style.pointerEvents = "none";
  } else {
    setaDir.style.opacity = "1";
    setaDir.style.pointerEvents = "auto";
  }
}

// Ativa os ouvintes de evento para as setas
document.addEventListener("DOMContentLoaded", () => {
  const lista = document.getElementById("lista-livros");
  if (lista) {
    // Sempre que o usuário rolar (com o mouse, dedo ou seta), verifica as setas
    lista.addEventListener("scroll", gerenciarEstadoDasSetas);
    // Verifica uma vez ao carregar para a seta esquerda já começar apagada
    gerenciarEstadoDasSetas();
  }
});

/* ===== LÓGICA DA SIDEBAR RESPONSIVA ===== */
const menuBtn = document.getElementById("menu-toggle");
const sidebar = document.querySelector(".sidebar");

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

  // Fecha a sidebar automaticamente ao clicar em qualquer botão dela (melhor UX no mobile)
  const botoesSidebar = document.querySelectorAll(".sidebar button");
  botoesSidebar.forEach((botao) => {
    botao.addEventListener("click", () => {
      if (window.innerWidth <= 1024) {
        sidebar.classList.remove("aberta");
        menuBtn.querySelector("i").classList.replace("fa-times", "fa-bars");
      }
    });
  });
}

// Verifica a URL quando a página carrega e abre a aba correta do acervo
document.addEventListener("DOMContentLoaded", function () {
  // Pega a variável 'aba' que o Django injetou no HTML
  const abaAtiva = document.querySelector(".conteudo-pag.ativo");

  if (abaAtiva) {
    // Se Django mandou uma aba ativa, ignora o localStorage
    const paginas = document.querySelectorAll(".conteudo-pag");
    paginas.forEach((p) => (p.style.display = "none"));
    abaAtiva.style.display = "block";
  }
});

/* ===== SISTEMA DE AUTOPLAY (SCROLL AUTOMÁTICO) ===== */

let autoPlayInterval;
let inatividadeTimer;
const tempoEspera = 4000; // 4 segundos para mudar sozinho
const tempoRetorno = 15000; // 15 segundos de espera após mexer

// 1. Função que limpa TUDO (intervalos e timers)
function pararTudo() {
  clearInterval(autoPlayInterval);
  clearTimeout(inatividadeTimer);
}

// 2. Função Principal de Scroll
function scrollCarrossel(direcao) {
  const lista = document.getElementById("lista-livros");
  const primeiroCard = lista.querySelector(".card-livro");

  // Para o autoplay IMEDIATAMENTE
  pararTudo();

  if (primeiroCard) {
    const larguraDoCard = primeiroCard.offsetWidth + 15;
    const multiplicador = window.innerWidth <= 768 ? 1 : 2;

    lista.scrollBy({
      left: direcao * (larguraDoCard * multiplicador),
      behavior: "smooth",
    });
  }

  // Só reagenda o início do autoplay para daqui a 10 segundos
  inatividadeTimer = setTimeout(iniciarAutoPlay, tempoRetorno);
}

// 3. Função que liga o movimento automático
function iniciarAutoPlay() {
  pararTudo(); // Limpa resíduos antes de começar

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

// 4. Inicialização e Eventos
document.addEventListener("DOMContentLoaded", () => {
  const lista = document.getElementById("lista-livros");

  if (lista) {
    iniciarAutoPlay();

    // 1. Monitora o início do toque (dedo encostou)
    lista.addEventListener(
      "touchstart",
      () => {
        pararTudo(); // Para o autoplay imediatamente
      },
      { passive: true },
    );

    // 2. Monitora o fim do toque (dedo saiu da tela)
    lista.addEventListener(
      "touchend",
      () => {
        // Após soltar o dedo, espera os 10 segundos de inatividade para voltar
        clearTimeout(inatividadeTimer);
        inatividadeTimer = setTimeout(iniciarAutoPlay, tempoRetorno);
      },
      { passive: true },
    );

    // 3. Mantém as regras de mouse para o PC
    lista.addEventListener("mouseenter", pararTudo);
    lista.addEventListener("mouseleave", () => {
      // Se apenas tirou o mouse, volta rápido. Se clicou, o timer do scrollCarrossel (10s) manda.
      if (!inatividadeTimer) {
        inatividadeTimer = setTimeout(iniciarAutoPlay, 2000);
      }
    });

    // 4. Atualiza as setas (opacidade)
    lista.addEventListener("scroll", gerenciarEstadoDasSetas);
    gerenciarEstadoDasSetas();
  }
});
