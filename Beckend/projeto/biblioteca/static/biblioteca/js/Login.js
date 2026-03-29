
function mostrarPagina(idPagina, event) {

    if (event) {
        event.preventDefault();
    }


    const paginas = document.querySelectorAll('.conteudo-pag');


    paginas.forEach(pag => {
        pag.style.display = 'none';


        const formulario = pag.querySelector('form');
        if (formulario) {
            formulario.reset();
        }
    });


    const paginaAlvo = document.getElementById(idPagina);
    if (paginaAlvo) {
        paginaAlvo.style.display = 'block';


        localStorage.setItem('ultimaPagina', idPagina);
    }
}

window.onload = function () {
    const ultimaPagina = localStorage.getItem('ultimaPagina');


    if (ultimaPagina === 'tela-cadastro') {
        mostrarPagina('tela-cadastro');
    } else {
        mostrarPagina('tela-login');
    }
};

document.querySelectorAll('form').forEach(form => {
    form.onsubmit = function (e) {
        e.preventDefault();
        console.log("Formulário enviado com sucesso (simulação)");
    };
});

document.querySelector('.custom-select-wrapper').addEventListener('click', function() {
    this.classList.toggle('open');
});

for (const option of document.querySelectorAll(".custom-option")) {
    option.addEventListener('click', function() {
        if (!this.classList.contains('selected')) {
            const parent = this.closest('.custom-select-wrapper');
            const realSelect = document.getElementById('Cargo');
            
            // Atualiza o texto visível
            parent.querySelector('.custom-select-trigger span').textContent = this.textContent;
            
            // Atualiza o valor no Select escondido (funcionalidade)
            realSelect.value = this.getAttribute('data-value');
            
            // Remove 'selected' dos outros e adiciona neste
            parent.querySelectorAll('.custom-option').forEach(el => el.classList.remove('selected'));
            this.classList.add('selected');
        }
    });
}

// Fecha o menu se clicar fora dele
window.addEventListener('click', function(e) {
    const select = document.querySelector('.custom-select-wrapper');
    if (!select.contains(e.target)) {
        select.classList.remove('open');
    }
});


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