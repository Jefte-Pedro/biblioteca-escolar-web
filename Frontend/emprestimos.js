// =============================================================
// BANCO FAKE DE EMPRÉSTIMOS
// Este array simula o banco de dados enquanto o backend não está pronto.
// Django: será substituído pelos dados vindos da view através do
// contexto: emprestimos = Emprestimo.objects.all()
// =============================================================

let emprestimos = [];

// =============================================================
// ABRIR E FECHAR FORMULÁRIO
// JS: controlado por display none/block via JavaScript.
// Django: o formulário será um ModelForm do Django (forms.py),
// submetido via POST para uma view chamada 'criar_emprestimo'
// =============================================================

function abrirFormEmprestimo() {
  document.getElementById("form-emprestimo").style.display = "block";

  // JS: preenche a data de hoje automaticamente via JS.
  // Django: a view pode passar {{ today }} no contexto e o campo já vem preenchido
  const hoje = new Date().toISOString().split("T")[0];
  document.getElementById("emp-data").value = hoje;
}

function fecharFormEmprestimo() {
  document.getElementById("form-emprestimo").style.display = "none";
  limparForm();
}

function limparForm() {
  document.getElementById("emp-livro").value = "";
  document.getElementById("emp-aluno").value = "";
  document.getElementById("emp-turma").value = "";
  document.getElementById("emp-data").value = "";
  document.getElementById("emp-devolucao").value = "";
}

// =============================================================
// CONFIRMAR EMPRÉSTIMO
// JS: salva no array local (memória do navegador, some ao recarregar).
// Django: será uma view que recebe o POST do formulário,
// valida com o ModelForm e salva com emprestimo.save() no banco
// =============================================================

function confirmarEmprestimo() {
  const livro = document.getElementById("emp-livro").value.trim();
  const aluno = document.getElementById("emp-aluno").value.trim();
  const turma = document.getElementById("emp-turma").value.trim();
  const dataEmp = document.getElementById("emp-data").value;
  let dataDev = document.getElementById("emp-devolucao").value;

  // Validação básica
  // Django: a validação será feita pelo ModelForm com is_valid()
  if (!livro || !aluno || !turma || !dataEmp) {
    alert("Preencha todos os campos obrigatórios!");
    return;
  }

  // JS: calcula +15 dias aqui no front quando a data é omitida.
  // Django: o backend faz esse cálculo no save() do model ou na view,
  // antes de salvar: if not data_devolucao: data_devolucao = data_emprestimo + timedelta(days=15)
  if (!dataDev) {
    const dataBase = new Date(dataEmp);
    dataBase.setDate(dataBase.getDate() + 15);
    dataDev = dataBase.toISOString().split("T")[0];
  }

  // JS: objeto simples guardado no array.
  // Django: será uma instância do model Emprestimo salva no banco
  const novoEmprestimo = {
    id: Date.now(),
    livro: livro,
    aluno: aluno,
    turma: turma,
    dataEmprestimo: dataEmp,
    dataDevolucao: dataDev,
    devolvido: false,
  };

  emprestimos.push(novoEmprestimo);
  fecharFormEmprestimo();
  renderizarEmprestimos();
}

// =============================================================
// RENDERIZAR OS CARDS
// JS: percorre o array local e gera HTML dinamicamente.
// Django: será substituído por um {% for emp in emprestimos %}
// diretamente no template, sem precisar desse JavaScript
// =============================================================

function renderizarEmprestimos() {
  const container = document.getElementById("lista-emprestimos");

  if (emprestimos.length === 0) {
    container.innerHTML =
      '<p class="msg-vazia">Nenhum empréstimo registrado ainda.</p>';
    return;
  }

  container.innerHTML = "";

  emprestimos.forEach((emp) => {
    // JS: calcula o atraso comparando datas no front.
    // Django: o model pode ter uma @property chamada 'esta_atrasado'
    // que faz essa comparação: return not self.devolvido and self.data_devolucao < date.today()
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    const devDate = new Date(emp.dataDevolucao + "T00:00:00");
    const atrasado = !emp.devolvido && devDate < hoje;

    const empFormatado = formatarData(emp.dataEmprestimo);
    const devFormatado = formatarData(emp.dataDevolucao);

    // JS: classe CSS definida aqui no JS baseada no estado.
    // Django: será {{ emp.esta_atrasado|yesno:"vermelho,verde" }} direto no template
    const corBolinha = atrasado
      ? "vermelho"
      : emp.devolvido
        ? "cinza"
        : "verde";

    container.innerHTML += `
            <div class="card-emprestimo ${emp.devolvido ? "devolvido" : ""}">

                <!-- Bolinha de status -->
                <!-- Django: a cor virá de {{ emp.esta_atrasado|yesno:"vermelho,verde" }} -->
                <div class="status-bolinha ${corBolinha}"></div>

                <div class="info-emprestimo">
                    <h3>${emp.livro}</h3>
                    <p><strong>Aluno:</strong> ${emp.aluno} — <strong>Turma:</strong> ${emp.turma}</p>
                    <p><strong>Empréstimo:</strong> ${empFormatado}</p>
                    <p><strong>Devolução prevista:</strong> ${devFormatado}</p>
                    ${atrasado ? '<p class="aviso-atraso">⚠️ Em atraso!</p>' : ""}
                    ${emp.devolvido ? '<p class="aviso-devolvido">✅ Devolvido</p>' : ""}
                </div>

                <div class="acoes-emprestimo">
                    <!-- JS: onclick chama função JS que edita o array.           -->
                    <!-- Django: será um link/form POST para a view 'renovar_emprestimo' com o ID real -->
                    <button class="btn-renovar"
                            onclick="renovarEmprestimo(${emp.id})"
                            ${emp.devolvido ? "disabled" : ""}>
                        <i class="fa-solid fa-rotate-right"></i> Renovar
                    </button>

                    <!-- JS: onclick chama função JS que marca devolvido no array. -->
                    <!-- Django: será um form POST para a view 'devolver_emprestimo' com o ID real -->
                    <button class="btn-devolver"
                            onclick="devolverEmprestimo(${emp.id})"
                            ${emp.devolvido ? "disabled" : ""}>
                        <i class="fa-solid fa-check"></i> Devolver
                    </button>
                </div>

            </div>
        `;
  });
}

// =============================================================
// RENOVAR (+15 DIAS)
// JS: edita o objeto diretamente no array local.
// Django: será uma view que recebe o ID do empréstimo via POST,
// busca no banco com get_object_or_404 e soma timedelta(days=15)
// =============================================================

function renovarEmprestimo(id) {
  const emp = emprestimos.find((e) => e.id === id);
  if (!emp) return;

  const dataAtual = new Date(emp.dataDevolucao + "T00:00:00");
  dataAtual.setDate(dataAtual.getDate() + 15);
  emp.dataDevolucao = dataAtual.toISOString().split("T")[0];

  renderizarEmprestimos();
}

// =============================================================
// DEVOLVER
// JS: apenas marca devolvido: true no objeto do array.
// Django: será uma view que busca o empréstimo pelo ID e salva
// emprestimo.devolvido = True, emprestimo.save()
// =============================================================

function devolverEmprestimo(id) {
  const emp = emprestimos.find((e) => e.id === id);
  if (!emp) return;

  emp.devolvido = true;
  renderizarEmprestimos();
}

// =============================================================
// FORMATAR DATA (DD/MM/AAAA)
// JS: necessário porque o input type=date retorna AAAA-MM-DD.
// Django: não precisará disso, pois o template filter
// {{ emp.data_emprestimo|date:"d/m/Y" }} já formata direto
// =============================================================

function formatarData(dataISO) {
  const [ano, mes, dia] = dataISO.split("-");
  return `${dia}/${mes}/${ano}`;
}
