"""Camada simples de acesso ao banco MySQL usada pelo backend.

Este arquivo concentra:
- carregamento das variaveis de ambiente do projeto;
- abertura de conexao com o MySQL;
- criacao inicial do banco e da tabela `usuarios`;
- consulta de existencia de usuario;
- registro de usuario com senha em hash.

Como regra geral, as funcoes daqui nao conhecem HTTP, Flask ou frontend.
Elas apenas executam operacoes de banco e devolvem valores simples para
serem usados pelas camadas superiores da aplicacao.
"""
import hmac
import hashlib
import os
import secrets
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


# Resolve o caminho do arquivo .env a partir da raiz do projeto para que
# o carregamento funcione mesmo quando o script for executado de outro diretorio.
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

# Configuracoes do banco carregadas do ambiente. Os valores padrao ajudam
# no desenvolvimento local, mas o ideal e definir tudo no arquivo .env.
DATABASE_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DB_PORT", "3306"))
DATABASE_USER = os.getenv("DB_USER", "root")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "")
DATABASE_NAME = os.getenv("DB_NAME", "task-hub-unipac")
PASSWORD_HASH_ITERATIONS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "100000"))



def verificar_hash_senha(senha, senha_hash_armazenada):
    """Compara a senha informada com o hash salvo no banco."""

    try:
        iteracoes_str, salt, senha_hash_salva = senha_hash_armazenada.split("$", 2)
        iteracoes = int(iteracoes_str)
    except (ValueError, AttributeError):
        return False

    senha_hash_calculada = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        iteracoes,
    ).hex()
    return hmac.compare_digest(senha_hash_calculada, senha_hash_salva)


def gerar_hash_senha(senha):
    """Gera um hash seguro da senha usando PBKDF2-HMAC com salt aleatorio.

    O valor salvo no banco segue o formato:
    `iteracoes$salt$hash`

    Isso permite, no futuro, validar a senha informada sem armazenar
    o texto puro da senha.
    """

    salt = secrets.token_hex(16)
    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return f"{PASSWORD_HASH_ITERATIONS}${salt}${senha_hash}"


def obter_conexao(database=None):
    """Abre uma conexao com o MySQL.

    Se `database` for informado, a conexao ja sera aberta apontando para
    esse banco. Caso contrario, a conexao abre apenas no servidor MySQL,
    o que e util para criar o banco na etapa inicial.
    """

    parametros = {
        "host": DATABASE_HOST,
        "port": DATABASE_PORT,
        "user": DATABASE_USER,
        "password": DATABASE_PASSWORD,
    }

    if database is not None:
        parametros["database"] = database

    return mysql.connector.connect(**parametros)


def iniciar_database():
    """Cria o banco e a tabela principal caso ainda nao existam.

    Esta funcao serve como bootstrap inicial do projeto. Em projetos
    maiores, o ideal e substituir essa abordagem por migracoes versionadas.
    """

    conexao = None
    cursor = None

    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()

        # O nome do banco tem hifen, por isso precisa estar entre crases.
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}`")
        cursor.execute(f"USE `{DATABASE_NAME}`")

        # Estrutura inicial da tabela de usuarios. A coluna `password`
        # armazena o hash gerado pela funcao `gerar_hash_senha`.
        sql_users = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            usuario VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            ativo BOOLEAN DEFAULT FALSE,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """
        cursor.execute(sql_users)
        conexao.commit()

    except Error as erro:
        print(f"Erro ao conectar ao MySQL: {erro}")

    finally:
        # O fechamento explicito evita conexoes abertas e vazamento de recurso.
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()
            print("Conexao com MySQL encerrada.")


def consultar_usuario(usuario):
    """Retorna os dados do usuario encontrado ou None.

    A consulta usa SQL parametrizado para evitar problemas de injecao.
    """

    conexao = None
    cursor = None

    try:
        conexao = obter_conexao(DATABASE_NAME)
        cursor = conexao.cursor()

        sql = """
        SELECT id, nome, usuario, password, email, ativo, data_cadastro
        FROM usuarios
        WHERE usuario = %s
        LIMIT 1
        """
        cursor.execute(sql, (usuario,))

        return cursor.fetchone()
    except Error as erro:
        print(f"Erro ao verificar usuario: {erro}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()

def registrar_usuario(nome, usuario, senha, email):
    """Insere um novo usuario no banco.

    Antes de salvar, a senha recebida e transformada em hash.
    Em caso de erro, a transacao e revertida com rollback.
    """

    conexao = None
    cursor = None

    try:
        conexao = obter_conexao(DATABASE_NAME)
        cursor = conexao.cursor()

        verificar_user = consultar_usuario(usuario)
        if verificar_user == True:
            print("Erro! Usuário já existe no Banco de Dados!")
            return False
        senha_hash = gerar_hash_senha(senha)

        sql = """
        INSERT INTO usuarios (nome, usuario, password, email)
        VALUES (%s, %s, %s, %s)
        """
        valores = (nome, usuario, senha_hash, email)

        cursor.execute(sql, valores)
        conexao.commit()
        print("Usuario registrado com sucesso!")
        return True
    except Error as erro:
        print(f"Erro ao registrar usuario: {erro}")
        if conexao is not None and conexao.is_connected():
            conexao.rollback()
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()

##asdasdasdasdasdadasd
def login_user(usuario, password):
    conexao = None
    cursor = None
    try:
        conexao = obter_conexao(DATABASE_NAME)
        cursor = conexao.cursor()
        usuario_encontrado = consultar_usuario(usuario)

        if usuario_encontrado is None:
            print("Usuario nao encontrado")
            return False
        senha_hash_armazenada = usuario_encontrado[3]
        if not verificar_hash_senha(password, senha_hash_armazenada):
            print("Usuario ou senha invalidos!")
            return False
        print("Usuario logado com sucesso!")
        return True
    except Exception as error:
        print(error)


if __name__ == "__main__":
    # Permite inicializar o banco executando este arquivo diretamente.
    iniciar_database()
