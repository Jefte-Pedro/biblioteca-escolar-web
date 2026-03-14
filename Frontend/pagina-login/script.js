
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