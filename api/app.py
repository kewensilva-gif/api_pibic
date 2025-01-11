from flask import Flask, jsonify, request
from banco import *
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import os
import paho.mqtt.client as mqtt
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
conexao = criar_conexao()

# Variáveis globais para status
latest_message = {"topic": None, "message": None}
mqtt_connected = False

def on_message(client, userdata, msg):
    global latest_message
    latest_message["topic"] = msg.topic
    latest_message["message"] = msg.payload.decode()
    print(f"Mensagem recebida: {msg.payload.decode()} no tópico {msg.topic}")

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    connection_codes = {
        0: "Conexão bem-sucedida",
        1: "Versão do protocolo incorreta",
        2: "Identificador do cliente inválido",
        3: "Servidor indisponível",
        4: "Credenciais inválidas",
        5: "Não autorizado"
    }
    
    if rc == 0:
        mqtt_connected = True
        print(f"✅ {connection_codes[rc]}")
        # Inscreva-se nos tópicos após confirmar a conexão
        client.subscribe("testtopic/1")
    else:
        mqtt_connected = False
        print(f"❌ Falha na conexão: {connection_codes.get(rc, 'Erro desconhecido')}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print("❌ Desconectado do broker MQTT")

# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set("mqtt_pibic", "Mqtt_pibic2024")
client.tls_set()

# Vincula as funções de callback
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Tenta conectar ao broker
try:
    client.connect("d7257de2da354fae9738d35f3212c93b.s1.eu.hivemq.cloud", 8883, 60)
    client.loop_start()
    
    # Aguarda até 5 segundos pela conexão
    timeout = time.time() + 5
    while not mqtt_connected and time.time() < timeout:
        time.sleep(0.1)
    
    if not mqtt_connected:
        print("❌ Timeout na conexão MQTT")
except Exception as e:
    print(f"❌ Erro ao conectar ao broker MQTT: {str(e)}")

# Nova rota para verificar o status da conexão MQTT
@app.route("/mqtt-status", methods=["GET"])
def get_mqtt_status():
    return jsonify({
        "connected": mqtt_connected,
        "latest_message": latest_message
    })

@app.route("/latest-message", methods=["GET"])
def get_latest_message():
    return jsonify(latest_message)

# Resto das suas rotas...
# [O resto do seu código permanece igual]

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)