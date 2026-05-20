# 📚 Web School Library

Sistema completo de gerenciamento de biblioteca escolar desenvolvido como projeto full stack, unindo interface moderna, API robusta e banco de dados relacional.

---

## 📋 Sobre o Projeto

O **Web School Library** é uma aplicação web desenvolvida para simular o funcionamento de um sistema real de biblioteca escolar. O projeto foi construído com foco em segurança, organização de código e experiência do usuário, aplicando conhecimentos de desenvolvimento full stack com tecnologias modernas.

A aplicação oferece funcionalidades como gerenciamento de livros e alunos, controle de empréstimos e devoluções, autenticação segura de usuários e sistema de notificações automáticas.

---

## 🚀 Funcionalidades

- ✅ Login e cadastro de usuários
- ✅ Recuperação de senha
- ✅ Catálogo de livros
- ✅ Cadastro de livros e alunos
- ✅ Registro e controle de empréstimos
- ✅ Prazo automático de devolução (15 dias)
- ✅ Renovação de empréstimos
- ✅ Verificação de disponibilidade dos livros
- ✅ Controle de permissões e níveis de acesso (aluno, ex-aluno, funcionário, administrador)
- ✅ Sistema de notificações automáticas de devolução
- 🔜 Integração com WhatsApp para notificações
- 🔜 Verificação de e-mail
- 🔜 Criptografia de senhas

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Front-end | HTML5, CSS3 |
| Back-end | Python, Django |
| Banco de Dados | MySQL |
| Autenticação | Django Auth (sessões, permissões) |

---

## 🗂️ Estrutura do Projeto

```
web-school-library/
├── frontend/        # Interface visual (HTML5 + CSS3)
├── backend/         # API e lógica do sistema (Django)
├── database/        # Modelagem e scripts do banco de dados (MySQL)
├── auth/            # Sistema de autenticação e controle de acesso
└── docs/            # Documentação do projeto
```

---

## 👥 Equipe e Responsabilidades

| Integrante | Área |
|---|---|
| **Jefté Pedro** | Front-end, Back-end (API) & Documentação |
| **Alesson Passos** | Banco de Dados |
| **Luiz Alexandre** | Back-end (API) & Documentação |
| **João Erick** | Back-end (API) |
| **Lázaro Antonio** | Back-end (API) & Documentação |
| **Daniel Santos** | Autenticação  |
| **Matheus da Silva** |  Notificações & Documentação |

---

## 🗄️ Banco de Dados

O banco de dados foi modelado no **MySQL** com tabelas relacionais para:

- Livros
- Alunos
- Usuários
- Empréstimos
- Controle de devoluções

A estrutura foi planejada para garantir integridade, desempenho e escalabilidade, com suporte a importação de dados via planilhas para preenchimento inicial do catálogo.

---

## 🔒 Autenticação e Segurança

O sistema de autenticação diferencia os perfis de acesso na plataforma:

- **Aluno** — acesso ao catálogo e empréstimos próprios
- **Ex-aluno** — acesso limitado
- **Funcionário** — gerenciamento de empréstimos
- **Administrador** — acesso completo ao sistema

Funcionalidades de segurança planejadas incluem criptografia de senhas, verificação de e-mail, controle de sessões e proteção contra tentativas indevidas de acesso.

---

## 🔔 Sistema de Notificações

O módulo de notificações foi desenvolvido para automatizar a comunicação com os usuários, enviando avisos sobre:

- Prazos de devolução próximos
- Empréstimos vencidos
- Renovações realizadas
- Atualizações importantes na plataforma

Está prevista a integração com **WhatsApp** para envio de mensagens automáticas diretamente no celular do usuário.

---

## 🎯 Objetivos do Projeto

Este projeto foi desenvolvido com os seguintes objetivos:

- Aplicar conhecimentos de desenvolvimento full stack em um cenário real
- Praticar integração entre front-end, back-end e banco de dados
- Desenvolver habilidades em criação de APIs REST com Django
- Entender arquitetura e organização de sistemas web escaláveis
- Compor portfólio acadêmico e profissional

---

## 📄 Licença

Este projeto está licenciado sob uma **licença proprietária restrita**.

O código-fonte, a estrutura e os recursos deste sistema **não são de uso livre**. É proibido copiar, redistribuir, modificar ou utilizar qualquer parte deste projeto sem autorização prévia e expressa da equipe responsável pelo desenvolvimento.

A exibição pública deste repositório não implica liberação de uso, cópia ou distribuição do código. Todo o conteúdo aqui presente é de propriedade dos desenvolvedores envolvidos no projeto.

Para dúvidas, parcerias ou autorizações, entre em contato com a equipe.
