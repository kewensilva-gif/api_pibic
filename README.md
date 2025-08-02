---

# API PIBIC

Essa API é responsável por permitir o envio de imagens para o servidor onde estas serão processadas.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

## 📦 Configuração do Ambiente com Docker

Faça o clone do projeto e, na pasta raiz, execute os seguintes comandos:

### Subir os containers (Docker Compose)

```bash
docker compose up
# ou para forçar a reconstrução do container
docker compose up --build
```

### Verificar se os containers estão em execução

```bash
docker ps
```

### Subir o banco de dados no container do MySQL

```bash
cat db.sql | docker exec -i api_pibic-db-1 mysql -u root -proot_password db_pesquisa
```

---

## 🐍 Configuração do Ambiente com Python Virtualenv (sem Docker)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/api-pibic.git
cd api-pibic
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

* No **Linux/macOS**:

  ```bash
  source venv/bin/activate
  ```

* No **Windows**:

  ```bash
  venv\Scripts\activate
  ```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto e adicione as variáveis conforme necessário, por exemplo:

```env
MQTT_BROKER=localhost
MQTT_PORT=1883
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=senha
MYSQL_DATABASE=db_pesquisa
```

### 6. Execute a aplicação

```bash
 python .\api\app.py
```

> Certifique-se de que o arquivo `app.py` é o ponto de entrada principal da aplicação.

---
