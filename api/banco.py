import mysql.connector
from mysql.connector import Error
import os
import time

def criar_conexao():
    while True:
        try:
            conexao = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '3307'),
                database=os.getenv('DB_NAME', 'db_pesquisa'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'root_password')
            )
            if conexao.is_connected():
                print("Conectado ao MySQL")
                return conexao
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            time.sleep(5)


def fechar_conexao(conexao):
    if conexao.is_connected():
        conexao.close()
        print("Conexão ao MySQL encerrada")

def obter_imagens(conexao):
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM imagens")
        resultados = cursor.fetchall()
        return resultados
    except Error as e:
        print(f"Erro ao executar consulta: {e}")
        return []


def salvar_imagem_no_banco(caminho_imagem, conexao):
    cursor = conexao.cursor()
    
    query = "INSERT INTO imagens (caminho_imagem) VALUES (%s)"
    cursor.execute(query, (caminho_imagem,))
    conexao.commit()
    cursor.close()
