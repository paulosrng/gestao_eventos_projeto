## Participantes:
                Paulo Sérgio Reis Neto Ra:22409324
                Augusto Ramos Ra:22401009
                Rodrigo Passos Ra:22405821

# SGEA - Sistema de Gestão de Eventos Acadêmicos

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Status](https://img.shields.io/badge/Status-Fase%202%20Concluída-success)

O **SGEA** é uma aplicação web robusta para o gerenciamento completo de eventos acadêmicos.  
Na **Fase 2**, o sistema recebeu melhorias significativas como automação de processos, regras de negócio avançadas, API REST, auditoria e geração de certificados.

---

## 🗂️ Sumário

- [Visão Geral](#-visão-geral)
- [Funcionalidades (Fase 2)](#-funcionalidades-fase-2)
- [Perfis de Acesso](#-perfis-de-acesso)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Instalação e Configuração](#%EF%B8%8F-instalação-e-configuração)
- [Guia de Testes (Dados Iniciais)](#-guia-de-testes-dados-iniciais)
- [Documentação da API](#-documentação-da-api)
- [Licença](#-licença)

---

## 🚀 Visão Geral

O SGEA permite o ciclo completo de gestão de eventos, incluindo:

1. **Divulgação:** Cadastro detalhado de eventos com banners personalizados.  
2. **Inscrição:** Alunos e professores podem se inscrever respeitando vagas e períodos.  
3. **Realização:** Controle de presença e gerenciamento da agenda.  
4. **Pós-Evento:** Emissão automática de certificados PDF e registro de logs de auditoria.

---

## ✨ Funcionalidades (Fase 2)

### 🔒 Segurança e Auditoria

- **RBAC — Controle de acesso por perfil:**  
  Permissões diferentes para Alunos, Professores e Organizadores.
- **Auditoria completa:**  
  Registra ações críticas (login, criação, edição e exclusão de eventos).
- **Política de senhas fortes:**  
  Exige números, letras e caracteres especiais.

### 📡 API REST

- Endpoints públicos e privados.
- Endpoints para consulta de eventos e inscrições externas.
- Autenticação via **Token**.
- **Throttling**:  
  - 20 requests/dia para eventos  
  - 50 requests/dia para inscrições  

### 📄 Automação e Documentos

- **Geração automática de certificados PDF** com ReportLab.  
- Certificados liberados apenas para participantes confirmados e após o término do evento.
- Simulação de envio de e-mail de boas-vindas no console.
- Validações automáticas:
  - Máscaras de telefone  
  - Datas válidas (evita eventos no passado)  
  - Upload restrito a imagens  

### 🎨 Interface e Usabilidade

- Estilização com **CSS**.
- Ícones **FontAwesome**.
- Layout moderno e intuitivo.

---

## 👥 Perfis de Acesso

| Perfil | Permissões |
|--------|------------|
| **Aluno** | Inscrição em eventos, cancelamento e download de certificados. |
| **Professor** | Todas as permissões do Aluno + pode atuar como *Responsável Técnico* do evento. |
| **Organizador** | Acesso total ao sistema: criação de eventos, gerenciamento de presenças, visualização de logs e cadastro de usuários. **Não pode se inscrever.** |

---

## 🛠 Tecnologias Utilizadas

| Categoria | Tecnologia |
|----------|------------|
| **Backend** | Python 3, Django 5 |
| **API** | Django REST Framework |
| **Banco de Dados** | SQLite |
| **Frontend** | HTML5, Tailwind CSS, JavaScript |
| **PDF Engine** | ReportLab |
| **Ícones** | FontAwesome 6 |

---

## ⚙️ Instalação e Configuração

### 1. Clonar o Repositório

git clone https://github.com/paulosrng/gestao_eventos_projeto.git
cd gestao_eventos_projeto


2. Ativar a venv
venv\Scripts\activate

3. cd gestao_projeto

4. Rodar o servidor
python manage.py runserver

Acesse:

Site: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

🧪 Guia de Testes (Dados Iniciais)

Recomenda-se criar os seguintes usuários para conferir todas as regras de negócio:

| Perfil          | E-mail                                              | Senha         | Descrição                    |
| --------------- | --------------------------------------------------- | ------------- | ---------------------------- |
| **Organizador** | [organizador@sgea.com] | Admin@123     | Acesso total + Logs          |
| **Aluno**       | [aluno@sgea.com]       | Aluno@123     | Inscrição e certificados     |
| **Professor**   | [professor@sgea.com]   | Professor@123 | Pode ser responsável técnico |

📚 Documentação da API

A API segue o padrão REST e é autenticada por Token.

🔑 1. Obter Token

POST /api/token/

Body:

{
  "username": "usuario",
  "password": "senha"
}


🌐 2. Endpoints Disponíveis
| Método   | Endpoint          | Descrição                     | Limite     |
| -------- | ----------------- | ----------------------------- | ---------- |
| **GET**  | `/api/eventos/`   | Lista todos os eventos        | 20 req/dia |
| **POST** | `/api/inscrever/` | Inscreve usuário em um evento | 50 req/dia |










   
