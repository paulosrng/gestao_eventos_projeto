## Participantes:
                Paulo Sérgio Reis Neto Ra:22409324
                Augusto Ramos Ra:22401009
                Rodrigo Passos Ra:22405821

# Gestão de Eventos

Uma aplicação web para gerenciar eventos — incluindo cadastro de eventos, participantes, controle de presenças, relatórios e outras funcionalidades típicas de uma plataforma de gestão de eventos.

---

## 🗂️ Sumário

- [Visão Geral](#visão-geral)  
- [Funcionalidades](#funcionalidades)  
- [Tecnologias Utilizadas](#tecnologias-utilizadas)  
- [Instalação e Uso](#instalação-e-uso)  
  - [Pré-requisitos](#pré-requisitos)  
  - [Setup do ambiente](#setup-do-ambiente)  
  - [Executando a aplicação](#executando-a-aplicação)  
- [Estrutura do Projeto](#estrutura-do-projeto)  
- [Rotas / Endpoints](#rotas--endpoints)  
- [Contribuição](#contribuição)  
- [Licença](#licença)  
- [Autor / Contato](#autor--contato)

---

## Visão Geral

Este projeto tem como objetivo oferecer uma plataforma completa para gerenciamento de eventos, focando em:

- Cadastro e edição de eventos (nome, data, local, descrição).  
- Cadastro e gestão de participantes.  
- Registro de presença em cada evento.  
- Emissão de relatórios (listas de participantes, estatísticas de participação, eventos futuros).  
- Interface web amigável para administradores e usuários.  

Ele pode servir como base para um sistema real de gestão de conferências, palestras, workshops, shows etc.

---

## Funcionalidades

- Autenticação e controle de acesso (login, logout)  
- CRUD completo para eventos  
- CRUD para participantes  
- Associação de participantes a eventos  
- Registro de inscrição 
- Interface web com páginas responsivas  
- Validações de dados (datas, campos obrigatórios etc.)  

---

## Tecnologias Utilizadas

Aqui estão as principais tecnologias e ferramentas usadas no projeto:

| Tipo | Tecnologia / Ferramenta |
|------|--------------------------|
| Linguagem Principal | Python |
| Framework Web |Django|
| Banco de Dados |SQLite|
| Front-end / Templates | HTML, CSS, JavaScript |
| Ambiente Virtual | venv |
| Outros | biblioteca ReportLab |

---

## Instalação e Uso

### Pré-requisitos

- Python 3.x instalado  
- (Opcional) PostgreSQL / MySQL ou outro banco de dados, se você não usar SQLite  
- Git
- Biblioteca ReportLab instalada (pip install ReportLab)
- Entrar na pasta venv (venv\\Scripts\\activate)

### Setup do ambiente

1. Clone este repositório:

   ```bash
   git clone https://github.com/paulosrng/gestao_eventos_projeto.git
   cd gestao_eventos_projeto

## Executando a aplicação:
```bash
python manage.py runserver 
```
- Crie um superusuário para aceder à [área de administração:](http://127.0.0.1:8000/admin/)

 ```bash
python manage.py createsuperuser
 ```
Criamos no banco:
- Usuário: paulo.sn
- Senha: vasco123


## Documentos(Caso de uso e tabela sqlite)

- [Sistema de Gestão de Eventos Acadêmicos (SGEA) - Requisitos e Casos de Uso..pdf](https://github.com/user-attachments/files/22970619/Sistema.de.Gestao.de.Eventos.Academicos.SGEA.-.Requisitos.e.Casos.de.Uso.pdf)

- [tabela sqlite.pdf](https://github.com/user-attachments/files/22970617/tabela.sqlite.pdf)
