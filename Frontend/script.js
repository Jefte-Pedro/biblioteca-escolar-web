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
        descricao: "Escolha livros que deseja ler e armazene em sua lista para acessar rapidamente quando precisar."
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
        descricao: "Choose books you want to read and store them in your list for quick access."
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
        descricao: "Elige libros que deseas leer y guárdalos en tu lista para acceder rápidamente."
    }
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

            document.getElementById("nav-inicio").textContent = traducoes[lang].inicio;
            document.getElementById("nav-lista").textContent = traducoes[lang].lista;
            document.getElementById("nav-reservados").textContent = traducoes[lang].reservados;
            document.getElementById("nav-lidos").textContent = traducoes[lang].lidos;

            document.getElementById("busca-texto").placeholder = traducoes[lang].busca;
            document.getElementById("sugestoes").textContent = traducoes[lang].sugestoes;

            const descricoes = document.querySelectorAll("#descricao");
            descricoes.forEach(d => d.textContent = traducoes[lang].descricao);

            localStorage.setItem("idioma", lang);
        }

        document.querySelectorAll(".idioma-menu button").forEach(btn => {
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
    /* ===== INICIALIZAÇÃO INTELIGENTE ===== */
    const paginaSalva = localStorage.getItem("paginaAtual") || "pag-inicio";

    if (paginaSalva === "pag-livro") {
        const idLivroSalvo = localStorage.getItem("livroAbertoID");
        if (idLivroSalvo) {
            // Se estava na página do livro, recarrega os dados dele
            abrirLivro(parseInt(idLivroSalvo));
        } else {
            mostrarPagina("pag-inicio");
        }
    } else {
        mostrarPagina(paginaSalva);
    }

});


/* ===== SISTEMA DE PÁGINAS ===== */

function mostrarPagina(idPagina) {
    const paginaAtual = localStorage.getItem("paginaAtual");

    // Só salva como anterior se realmente estivermos mudando de uma página válida
    if (paginaAtual && paginaAtual !== idPagina) {
        localStorage.setItem("paginaAnterior", paginaAtual);
    }

    localStorage.setItem("paginaAtual", idPagina);

    // Esconde todas as páginas
    const paginas = document.querySelectorAll(".conteudo-pag");
    paginas.forEach(p => p.style.display = "none");

    // Mostra a página solicitada
    const pagina = document.getElementById(idPagina);
    if (pagina) {
        pagina.style.display = "block";
    }

    // --- SINCRONIZAÇÃO DA SIDEBAR ---
    // Remove o "ativo" de todos os botões da lateral
    const botoesSidebar = document.querySelectorAll(".sidebar button");
    botoesSidebar.forEach(btn => btn.classList.remove("ativo"));

    // Procura na sidebar qual botão tem o onclick que chama essa página específica
    const botaoParaAtivar = document.querySelector(`.sidebar button[onclick*="'${idPagina}'"]`);

    if (botaoParaAtivar) {
        botaoParaAtivar.classList.add("ativo");
    }
}


/* ===== BOTÃO VOLTAR ===== */

function voltarPagina() {
    const paginaAnterior = localStorage.getItem("paginaAnterior");

    if (paginaAnterior && paginaAnterior !== "pag-livro") {
        mostrarPagina(paginaAnterior);
    } else {
        mostrarPagina("pag-inicio");
    }
}


/* ===== MOSTRAR LIVROS ===== */

function mostrarLivro() {

    const container = document.getElementById("lista-livros");

    if (!container) return;

    container.innerHTML = "";

    livros.forEach(livro => {

        container.innerHTML += `
        <div class="card-livro">

            <img 
                src="${livro.capa}" 
                alt="${livro.titulo}" 
                onclick="abrirLivro(${livro.id})"
                class="capa-livro"
            >

            <h3>${livro.titulo}</h3>

            <p><strong>Autor:</strong> ${livro.autor}</p>

        </div>
        `;

    });

}


function abrirLivro(idLivro) {
    const livro = livros.find(l => l.id === idLivro);
    if (!livro) return;

    // Preenche os dados na tela
    document.getElementById("livro-titulo").textContent = livro.titulo;
    document.getElementById("livro-capa").src = livro.capa;
    document.getElementById("livro-autor").textContent = livro.autor;
    document.getElementById("livro-editora").textContent = livro.editora;
    document.getElementById("livro-prateleira").textContent = "Prateleira: " + livro.prateleira;
    document.getElementById("livro-unidades").textContent = "Unidades: " + livro.unidades;
    document.getElementById("livro-codigo").textContent = "Codigo: " + livro.codigo;
    document.getElementById("livro-status").textContent = livro.disponivel ? "Disponível" : "Emprestado";
    document.getElementById("livro-sinopse").innerText = livro.sinopse || "Sinopse não disponível.";

    // --- LOGICA DE MEMÓRIA ---
    const paginaAtual = localStorage.getItem("paginaAtual");
    
    if (paginaAtual && paginaAtual !== "pag-livro") {
        localStorage.setItem("paginaAnterior", paginaAtual);
    }


    localStorage.setItem("livroAbertoID", idLivro);

    const elementoStatus = document.getElementById("livro-status");


elementoStatus.textContent = livro.disponivel ? "Disponível" : "Emprestado";


if (livro.disponivel) {
    elementoStatus.classList.add("disponivel");
    elementoStatus.classList.remove("emprestado");
} else {
    elementoStatus.classList.add("emprestado");
    elementoStatus.classList.remove("disponivel");
}

    mostrarPagina("pag-livro");
}



let totalAvaliacoes = 0
let somaAvaliacoes = 0

const estrelas = document.querySelectorAll("#estrelas-avaliacao .estrela")
const media = document.getElementById("media-avaliacao")

estrelas.forEach(estrela => {

    estrela.addEventListener("click", () => {

        let valor = parseInt(estrela.dataset.valor)

        somaAvaliacoes += valor
        totalAvaliacoes++

        let mediaFinal = (somaAvaliacoes / totalAvaliacoes).toFixed(1)

        media.textContent = mediaFinal + " / 5"

        estrelas.forEach(e => {
            e.classList.remove("ativa")

            if (e.dataset.valor <= valor) {
                e.classList.add("ativa")
            }
        })

    })

})

function scrollCarrossel(direcao) {
    const lista = document.getElementById('lista-livros');
    // Calcula quanto deve rolar (largura de 2 cards aproximadamente)
    const larguraCard = 230; 
    lista.scrollBy({
        left: direcao * (larguraCard * 2),
        behavior: 'smooth'
    });
}

/* ===== INICIAR SISTEMA ===== */

console.log("mostrarLivros foi chamada");

mostrarLivro();


// ==========================================
// LÓGICA DE CRIAR LISTAS PERSONALIZADAS
// ==========================================

const modalLista = document.getElementById('modal-lista');
const btnAbrirModal = document.getElementById('btn-abrir-modal');
const btnConfirmarLista = document.getElementById('btn-confirmar-lista');
const inputNomeLista = document.getElementById('input-nome-lista');
const containerListas = document.getElementById('conteudo-dinamico-lista');

// Array para guardar os dados (simulando um banco de dados)
let colecaoDeListas = [];

// 1. Abrir e Fechar Modal
if (btnAbrirModal) {
    btnAbrirModal.onclick = () => {
        modalLista.style.display = 'block';
        inputNomeLista.focus(); // Já coloca o cursor piscando pro usuário digitar
    };
}

function fecharModal() {
    modalLista.style.display = 'none';
    inputNomeLista.value = ''; // Limpa o texto que estava lá
}

// 2. Criar a Lista de Fato
if (btnConfirmarLista) {
    btnConfirmarLista.onclick = () => {
        const nomeDaLista = inputNomeLista.value.trim();
        
        if (nomeDaLista !== "") {
            // Cria um objeto para a nova lista
            const novaLista = {
                id: Date.now(), // Gera um ID único baseado na data/hora
                nome: nomeDaLista,
                livros: [] // Começa sem livros
            };
            
            colecaoDeListas.push(novaLista); // Salva na nossa coleção
            fecharModal();
            renderizarListasNaTela();
        } else {
            alert("Por favor, digite um nome para a lista.");
        }
    };
}

// 3. Desenhar as listas no HTML
function renderizarListasNaTela() {
    containerListas.innerHTML = ''; // Apaga a mensagem de "vazio"
    
    colecaoDeListas.forEach(lista => {
        const divLista = document.createElement('div');
        divLista.className = 'card-lista'; // Usando aquele CSS que você já tem
        
        // Note o onclick="abrirLista(...)" na div inteira!
        divLista.innerHTML = `
            <div class="info-lista" onclick="abrirLista(${lista.id})" style="cursor:pointer; flex-grow: 1;">
                <h3>${lista.nome}</h3>
                <span class="qtd-livros">${lista.livros.length} livros</span>
            </div>
            <button class="btn-add-livro" onclick="event.stopPropagation(); alert('Em breve: abrir janela para escolher livros!')">
                <i class="fa-solid fa-plus"></i>
            </button>
        `;
        
        containerListas.appendChild(divLista);
    });
}

// 4. Entrar na Lista (O que você pediu!)
function abrirLista(idDaLista) {
    const listaSelecionada = colecaoDeListas.find(l => l.id === idDaLista);
    
    // Por enquanto, apenas um console.log e um alert para testar se achou a lista certa
    console.log("Abrindo a lista:", listaSelecionada.nome);
    alert(`Você entrou na lista: ${listaSelecionada.nome}. \nAqui no futuro faremos a tela mudar para mostrar os livros dela!`);
}