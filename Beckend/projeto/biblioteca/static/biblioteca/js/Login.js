// Custom Select (Cargo)
const selectWrapper = document.querySelector(".custom-select-wrapper");
if (selectWrapper) {
  selectWrapper.addEventListener("click", function () {
    this.classList.toggle("open");
  });

  for (const option of document.querySelectorAll(".custom-option")) {
    option.addEventListener("click", function () {
      if (!this.classList.contains("selected")) {
        const parent = this.closest(".custom-select-wrapper");
        const realSelect = document.getElementById("Cargo");
        parent.querySelector(".custom-select-trigger span").textContent =
          this.textContent;
        realSelect.value = this.getAttribute("data-value");
        parent
          .querySelectorAll(".custom-option")
          .forEach((el) => el.classList.remove("selected"));
        this.classList.add("selected");
      }
    });
  }

  window.addEventListener("click", function (e) {
    if (!selectWrapper.contains(e.target)) {
      selectWrapper.classList.remove("open");
    }
  });
}

// Tema Dark Mode
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

const alternar = document.getElementById("alternar-contato");
if (alternar) {
  alternar.addEventListener("click", function (e) {
    e.preventDefault();
    const campoEmail = document.getElementById("campo-email");
    const campoNumero = document.getElementById("campo-numero");
    const metodo = document.getElementById("metodo-contato"); // só existe no cadastro

    if (campoNumero.style.display === "none") {
      campoEmail.style.display = "none";
      campoNumero.style.display = "block";
      alternar.textContent = "Usar email";
      if (metodo) metodo.value = "numero"; // só atualiza se existir
    } else {
      campoEmail.style.display = "block";
      campoNumero.style.display = "none";
      alternar.textContent = "Usar número";
      if (metodo) metodo.value = "email"; // só atualiza se existir
    }
  });
}