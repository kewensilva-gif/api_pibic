from flask import Flask, jsonify, request
# from banco import *
from datetime import datetime, timezone
# from werkzeug.utils import secure_filename
import os
import paho.mqtt.client as mqtt
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
# conexao = criar_conexao()

# Variáveis de configuração
endereco_broker = 'd7257de2da354fae9738d35f3212c93b.s1.eu.hivemq.cloud'
porta = 8883
porta_websocket = 8884
usuario = 'mqtt_pibic'
senha = 'Mqtt_pibic2024'
topico_envio = 'api/send/esp'
topico_image= "camera/image"

# Variáveis globais para status
mqtt_conectado = False

contador = 0

# Toda vez que a mensagem de um tópico é alterada essa função é chamada
def on_message(client, userdata, msg):
    global contador

    if msg.topic == "camera/image":
        extensao = '.jpg'
        filename = f"{int(datetime.now(timezone.utc).timestamp())}{extensao}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(image_path, "wb") as img_file:
            img_file.write(msg.payload)

        print(f"Imagem recebida via MQTT (binário) - nº {contador}")
        contador = contador+1
        # client.publish('topico_envio', "0")
    # contador+=1
    # if contador>3 :
    #     client.publish('topico_envio', "0")
    # if ultima_mensagem["message"] == "teste":
    #     client.publish("topico_envio", "O resultado é igual a teste")


# # Teste com base64
# def on_message(client, userdata, msg):
#     global contador

#     if msg.topic == "camera/image":
#         extensao = '.jpg'
#         filename = f"{int(datetime.now(timezone.utc).timestamp())}{extensao}"
#         image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#         # Decodifica a imagem base64 para binário
#         try:
#             image_data = base64.b64decode(msg.payload)
#             with open(image_path, "wb") as img_file:
#                 img_file.write(image_data)

#             print(f"Imagem recebida via MQTT (base64) - nº {contador}")
#             contador += 1
#         except Exception as e:
#             print(f"Erro ao decodificar imagem: {e}")

def on_connect(client, userdata, flags, rc):
    global mqtt_conectado
    codigos_conexao = {
        0: "Conexão bem-sucedida",
        1: "Versão do protocolo incorreta",
        2: "Identificador do cliente inválido",
        3: "Servidor indisponível",
        4: "Credenciais inválidas",
        5: "Não autorizado"
    }
    
    if rc == 0:
        mqtt_conectado = True
        print(f"{codigos_conexao[rc]}")
        
        client.subscribe("camera/image")
    else:
        mqtt_conectado = False
        print(f"Falha na conexão: {codigos_conexao.get(rc, 'Erro desconhecido')}")

def on_disconnect(client, userdata, rc):
    global mqtt_conectado
    mqtt_conectado = False
    print("Desconectado do broker MQTT")

# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set(usuario, senha)
client.tls_set()

# Vincula as funções de callback
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Tenta conectar ao broker
try:
    client.connect(endereco_broker, porta, 60)
    client.publish(topico_envio, "mensagem 1")
    client.loop_start()
    
    # Aguarda até 5 segundos pela conexão
    timeout = time.time() + 5
    while not mqtt_conectado and time.time() < timeout:
        time.sleep(0.1)
    
    if not mqtt_conectado:
        print("Timeout na conexão MQTT")
except Exception as e:
    print(f"Erro ao conectar ao broker MQTT: {str(e)}")


# @app.route("/mqtt-status", methods=["GET"])
# def get_mqtt_status():
#     return jsonify({
#         "connected": mqtt_conectado,
#         "ultima_mensagem": ultima_mensagem
#     })

# @app.route("/ultima-mensagem", methods=["GET"])
# def pega_ultima_mensagem():
#     return jsonify(ultima_mensagem)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)