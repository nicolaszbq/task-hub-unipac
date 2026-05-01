# Task Hub UNIPAC

Projeto com backend em Flask e camada de persistencia em MySQL, com frontend em React + Vite.

## Objetivo atual

O repositorio ainda esta em fase inicial. Hoje a parte mais estruturada do projeto esta no backend, em especial no arquivo `backend/core/database.py`, que:

- carrega configuracoes sensiveis do arquivo `.env`;
- abre conexao com o MySQL;
- cria o banco e a tabela `usuarios` se ainda nao existirem;
- consulta se um usuario ja existe;
- registra usuarios salvando a senha em hash.

## Estrutura principal

```text
task-hub-unipac/
|- backend/
|  |- app.py
|  \- core/
|     \- database.py
|- frontend/
|  |- package.json
|  \- src/
|- .env.example
|- .gitignore
\- README.md
```

## Requisitos

- Python 3.10+
- MySQL 8+
- Node.js 18+ (para o frontend)

## Configuracao do ambiente

1. Crie uma copia do arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

2. Preencha o `.env` com as credenciais corretas do seu MySQL.

Exemplo:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha_mysql
DB_NAME=task-hub-unipac
PASSWORD_HASH_ITERATIONS=100000
```

## Dependencias do backend

Instale as bibliotecas Python usadas hoje pelo backend:

```powershell
python -m pip install flask mysql-connector-python python-dotenv
```

## Inicializacao do banco

Para criar o banco e a tabela `usuarios`, execute:

```powershell
python backend\core\database.py
```

Isso cria:

- o banco configurado em `DB_NAME`;
- a tabela `usuarios`, se ela ainda nao existir.

## Backend Flask

Para subir a API atual:

```powershell
python backend\app.py
```

Endpoint disponivel hoje:

- `GET /api/ping`

Resposta esperada:

```json
{
  "status": "pong",
  "message": "API is running!"
}
```

## Frontend

Instale as dependencias:

```powershell
cd frontend
npm install
```

Ambiente de desenvolvimento:

```powershell
npm run dev
```

Build de producao:

```powershell
npm run build
```

## Sobre seguranca de senha

O registro de usuario nao salva a senha em texto puro.

O arquivo `backend/core/database.py` usa:

- `salt` aleatorio por usuario;
- `hashlib.pbkdf2_hmac`;
- numero configuravel de iteracoes por `PASSWORD_HASH_ITERATIONS`.

O valor salvo no banco segue este formato:

```text
iteracoes$salt$hash
```

## Proximos passos recomendados

- criar funcao de verificacao de senha para login;
- mover regras de negocio para modulos separados;
- adicionar migracoes de banco em vez de bootstrap manual;
- criar testes automatizados para o backend;
- documentar melhor os endpoints quando a API crescer.
