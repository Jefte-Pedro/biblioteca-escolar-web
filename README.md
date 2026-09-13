# 📚 Web School Library

Sistema web de gerenciamento de biblioteca escolar, desenvolvido como projeto full stack com **Django, Django REST Framework, MySQL, JavaScript e APScheduler**.

O projeto nasceu a partir de uma necessidade real de uma instituição de ensino e foi posteriormente adaptado para publicação como portfólio, com substituição de nomes, identidade visual e dados sensíveis.

> **Status:** projeto em desenvolvimento contínuo e ainda não disponibilizado em produção.

---

## 📋 Sobre o projeto

O **Web School Library** é uma aplicação web voltada ao gerenciamento de uma biblioteca escolar, reunindo em um único sistema recursos para organização do acervo, usuários, empréstimos, devoluções, reservas e notificações.

A aplicação foi desenvolvida utilizando **Django no back-end**, com renderização tradicional das páginas e integração com **Django REST Framework** para recursos que podem ser acessados de forma programática.

Durante o desenvolvimento, o projeto envolveu não apenas a implementação de funcionalidades, mas também integração entre diferentes partes do sistema, correção de problemas, refatoração, definição de regras de negócio e preocupação com segurança e manutenção.

### Principais recursos

- Autenticação e cadastro de usuários
- Recuperação de senha
- Verificação de e-mail
- Controle de perfis e permissões
- Catálogo de livros com busca e filtros
- Cadastro e gerenciamento de livros
- Gerenciamento de alunos
- Controle de empréstimos e devoluções
- Cálculo automático do prazo de devolução
- Renovação de empréstimos
- Sistema de reservas
- Fila de espera para reservas
- Expiração automática de reservas
- Verificação de disponibilidade dos livros
- Notificações no sistema
- Envio de notificações por e-mail
- Rotinas automatizadas para acompanhamento de prazos
- Testes automatizados para regras de negócio centrais

---

## 🖼️ Demonstração da interface

### Login e acesso

| Login | Home — visitante |
|---|---|
| ![Tela de login](docs/screenshots/login.png) | ![Home deslogado](docs/screenshots/home-deslogado.png) |

### Área do usuário

| Home — usuário logado | Catálogo de livros |
|---|---|
| ![Home logado](docs/screenshots/home-logado.png) | ![Catálogo](docs/screenshots/catalogo.png) |

### Área administrativa

| Painel de empréstimos |
|---|
| ![Empréstimos](docs/screenshots/emprestimos.png) |

---

## 🚀 Funcionalidades

### 👤 Usuários e autenticação

- Cadastro de usuários
- Login e logout
- Recuperação de senha
- Verificação de e-mail
- Autenticação baseada no Django Auth
- Hash seguro de senhas
- Perfis de acesso com permissões específicas

### 📚 Acervo

- Cadastro e gerenciamento de livros
- Cadastro e gerenciamento de alunos
- Busca no catálogo
- Filtros
- Controle de disponibilidade
- Gerenciamento de exemplares

### 📖 Empréstimos

- Registro de empréstimos
- Registro de devoluções
- Prazo automático de devolução de **15 dias**
- Renovação de empréstimos
- Identificação de empréstimos em atraso

### 📌 Reservas

- Criação de reservas
- Controle de disponibilidade
- Expiração automática de reservas
- Liberação do exemplar após expiração
- Fila de espera
- Notificação do próximo usuário da fila

### 🔔 Notificações

O sistema possui uma camada centralizada de notificações responsável por registrar eventos no sistema e enviar comunicações por e-mail.

Entre os eventos tratados estão:

- empréstimos próximos do vencimento;
- empréstimos vencidos;
- reservas expiradas;
- disponibilidade para o próximo usuário da fila.

---

## 🏗️ Arquitetura

O projeto utiliza **Django com renderização tradicional no servidor (SSR)**, mantendo os templates responsáveis pela interface da aplicação.

Em paralelo, o projeto utiliza **Django REST Framework** para disponibilizar recursos por meio de uma API REST.

A organização geral pode ser representada da seguinte forma:

```text
Interface Web
     │
     ▼
Django Views / Regras de negócio
     │
 ┌───┴───────────────┐
 ▼                   ▼
Django ORM       Django REST Framework
 │
 ▼
MySQL
```

As rotinas automatizadas utilizam **APScheduler**, responsável apenas por iniciar as tarefas programadas.

A lógica de negócio permanece nos módulos responsáveis por cada domínio:

```text
APScheduler
    │
    ├──► notifications.py
    │       └── Verificação e criação de notificações
    │
    └──► reservas.py
            └── Expiração e processamento de reservas
```

O scheduler é executado automaticamente duas vezes ao dia:

```text
08:00
20:00
```

utilizando o fuso horário de **America/Recife**.

As mesmas rotinas também podem ser executadas manualmente por meio dos comandos de gerenciamento do Django, facilitando testes, manutenção e depuração.

---

## 🧠 Regras de negócio

O sistema possui diversas regras implementadas diretamente no domínio da aplicação.

Alguns exemplos:

### Prazo de empréstimo

Ao registrar um novo empréstimo, o sistema calcula automaticamente a data prevista de devolução com base em um prazo de **15 dias**.

### Controle de atraso

Os empréstimos são classificados de acordo com sua situação:

- ainda dentro do prazo;
- vencendo;
- vencido;
- devolvido.

Empréstimos já devolvidos não são considerados atrasados.

### Reservas

Quando uma reserva expira:

1. A reserva é marcada como expirada.
2. O exemplar é liberado.
3. O usuário é notificado.
4. O próximo usuário da fila pode ser processado.

Essa separação permite manter as regras de empréstimos, reservas e notificações em seus respectivos módulos.

---

## 🔒 Autenticação e segurança

A autenticação utiliza os recursos nativos do **Django Auth**, incluindo o armazenamento de senhas por hash em vez de texto puro.

O sistema trabalha com quatro perfis principais:

| Perfil | Acesso |
|---|---|
| **Aluno** | Catálogo e recursos relacionados aos próprios empréstimos e reservas |
| **Ex-aluno** | Acesso limitado |
| **Funcionário** | Recursos de gerenciamento de empréstimos |
| **Administrador** | Acesso completo ao sistema |

Também foram utilizadas permissões e regras específicas para controlar quais áreas da aplicação podem ser acessadas por cada tipo de usuário.

### Auditoria de segurança

Antes da publicação do projeto, foi realizada uma revisão de segurança do repositório.

Durante esse processo:

- chaves de APIs que haviam sido expostas durante testes foram removidas;
- as respectivas credenciais foram revogadas junto aos provedores;
- o histórico do Git foi reescrito para remover os segredos expostos;
- arquivos e integrações de teste que não faziam parte da versão final foram removidos.

Essa etapa foi importante para garantir que o repositório público não carregasse credenciais ou experimentos descartados.

---

## 🧪 Testes automatizados

O projeto possui testes automatizados utilizando o sistema de testes do Django.

Atualmente são cobertas regras de negócio centrais relacionadas a:

- normalização de categorias de livros;
- disponibilidade de livros de acordo com seus exemplares;
- cálculo automático do prazo de devolução;
- identificação de empréstimos atrasados;
- comportamento de empréstimos antes do vencimento;
- comportamento no dia do vencimento;
- comportamento após o vencimento;
- empréstimos devolvidos não são contabilizados como atrasados.

Execução:

```bash
python manage.py test biblioteca
```

Resultado atual:

```text
Ran 7 tests
OK
```

---

## 🛠️ Tecnologias utilizadas

| Área | Tecnologia |
|---|---|
| Front-end | HTML5, CSS3, JavaScript |
| Back-end | Python, Django |
| API | Django REST Framework |
| Banco de dados | MySQL |
| Autenticação | Django Auth |
| Agendamento | APScheduler |
| Controle de versão | Git / GitHub |

---

## 🗂️ Estrutura do projeto

```text
web-school-library/
├── Backend/
│   └── projeto/
│       ├── biblioteca/
│       │   ├── migrations/
│       │   ├── templates/
│       │   ├── management/
│       │   ├── models.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── notifications.py
│       │   ├── reservas.py
│       │   ├── scheduler.py
│       │   └── ...
│       │
│       ├── projeto/
│       │   └── settings.py
│       │
│       ├── manage.py
│       └── requirements.txt
│
├── docs/
│   └── screenshots/
│
└── README.md
```

---

## ⚙️ Principais decisões técnicas

Durante o desenvolvimento, algumas decisões foram tomadas a partir de problemas encontrados durante a implementação.

### Centralização das notificações

Inicialmente existiam responsabilidades relacionadas a notificações distribuídas entre diferentes partes do projeto.

A estrutura foi reorganizada para centralizar a criação das notificações e manter o envio de e-mail integrado à mesma lógica.

Com isso, uma notificação pode ser registrada no sistema e enviada por e-mail sem precisar duplicar a mesma implementação em cada funcionalidade.

### Separação entre scheduler e regra de negócio

O **APScheduler** ficou responsável somente pelo agendamento das rotinas.

As regras permanecem nos módulos específicos:

```text
scheduler.py
    │
    ├── notifications.py
    └── reservas.py
```

Essa separação facilita manutenção, testes e execução manual das mesmas rotinas.

### Comandos de gerenciamento

As tarefas automatizadas também possuem comandos próprios do Django, permitindo executar processos manualmente durante desenvolvimento e depuração.

---

## 🧩 Integrações avaliadas e descontinuadas

Nem todas as tentativas de automação foram mantidas na versão final do projeto.

Essas experiências ajudaram a identificar limitações técnicas e operacionais e também influenciaram as decisões posteriores da arquitetura.

### Google Books API

Foi avaliada uma integração para automatizar informações como capas e sinopses dos livros.

Durante os testes, foram observadas inconsistências nos resultados e problemas de confiabilidade para o acervo utilizado.

A integração foi descontinuada e o preenchimento dessas informações passou a ser tratado manualmente.

### WhatsApp / Evolution API

Foi estudada uma integração para envio de notificações de prazo pelo WhatsApp.

A solução dependia de um número institucional dedicado. Como esse recurso não estava disponível e a utilização de um número pessoal não era adequada para o projeto, a integração foi abandonada.

O sistema passou a utilizar o **e-mail** como principal canal externo de comunicação.

### SerpApi

Também foi realizado um experimento separado para automatizar informações de livros.

O teste não apresentou resultados confiáveis para o projeto e o código foi removido da versão final.

Durante a limpeza do repositório, a credencial utilizada no experimento também foi revogada.

---

## 👥 Equipe

O projeto foi desenvolvido originalmente como um trabalho acadêmico em equipe.

| Integrante | Área de contribuição |
|---|---|
| **Jefté Pedro** | Front-end, back-end, integração e documentação |
| **Alesson Passos** | Banco de dados |
| **Luiz Alexandre** | Back-end e documentação |
| **João Erick** | Back-end |
| **Lázaro Antonio** | Back-end e documentação |
| **Daniel Santos** | Autenticação |
| **Matheus da Silva** | Notificações e documentação |

### Minha contribuição

Minha principal participação no projeto esteve relacionada à **integração e evolução do sistema**.

Ao longo do desenvolvimento, atuei na implementação e adaptação de funcionalidades do front-end e back-end, integração entre componentes, aplicação das regras de negócio, integração com banco de dados e API, correção de erros, refatorações e organização do projeto.

O desenvolvimento foi colaborativo, e diferentes partes da base inicial foram construídas por outros integrantes da equipe. A versão publicada representa principalmente a evolução e integração dessas partes ao longo do projeto.

---

## 📈 Aprendizados

O desenvolvimento do projeto proporcionou experiência prática em diferentes áreas do desenvolvimento de software, principalmente:

- desenvolvimento web com Django;
- modelagem e integração com banco de dados relacional;
- criação e consumo de APIs;
- autenticação e controle de permissões;
- implementação de regras de negócio;
- automação de tarefas;
- envio de notificações;
- testes automatizados;
- depuração e correção de problemas;
- refatoração;
- controle de versão com Git;
- trabalho colaborativo em equipe.

Além da implementação das funcionalidades, o projeto também trouxe experiência com decisões que fazem parte do desenvolvimento real, como lidar com integrações que não funcionaram como esperado, remover soluções desnecessárias e revisar o projeto antes de sua publicação.

---

## 📌 Status do projeto

**Em desenvolvimento contínuo.**

O projeto ainda não está em produção e pode receber novas melhorias, correções, testes e funcionalidades futuramente.

A versão disponibilizada neste repositório tem como objetivo demonstrar a evolução técnica do projeto e servir como parte do meu portfólio de desenvolvimento de software.

---

## 📄 Licença

Este repositório foi publicado para fins de **portfólio e avaliação técnica**.

O código não é disponibilizado como software livre e sua utilização, redistribuição ou modificação para outros fins depende de autorização do autor.

---

## 👨‍💻 Autor

**Jefté Pedro**

Estudante de Ciência da Computação e desenvolvedor Full Stack em formação, com foco em desenvolvimento web e construção de aplicações utilizando JavaScript, React.js, Node.js, Python e Django.

🔗 **GitHub:** [Jefte-Pedro](https://github.com/Jefte-Pedro)    