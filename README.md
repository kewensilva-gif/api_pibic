
# API PIBIC
Essa API é responsável por permitir o envio de imagens para o servidor onde estas serão processadas.



## Configuração do ambiente com DOCKER

Faça o clone do projeto e na pasta raíz rode os seguintes comandos.

Para subir os containers que estão configurados no arquivo docker-compose.yml:
```bash
  docker compose up  
  <!-- ou para forçar a reconstrução do container -->
  docker compose up --build
```

Rode o camando para verificar se os containers subiram corretamente:
```bash
  docker ps
```

Para subir o banco de dados para o container do mysql:
```bash
  cat db.sql | docker exec -i api_pibic-db-1 mysql -u root -proot_password db_pesquisa
```