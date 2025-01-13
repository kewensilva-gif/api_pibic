from flask import Flask
import os
import paho.mqtt.client as mqtt
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

# Variáveis de configuração
address_broker = 'd7257de2da354fae9738d35f3212c93b.s1.eu.hivemq.cloud'
port = 8883
port_websocket = 8884
user = 'mqtt_pibic'
password = 'Mqtt_pibic2024'
topic_send = 'api/send/esp'
topic_image= "camera/image"

# Variáveis globais para status
mqtt_connected = False

contador = 0

# Toda vez que a mensagem de um tópico é alterada essa função é chamada
def on_message(client, userdata, msg):
    global contador

    if msg.topic == "camera/image":
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"image{contador}.jpg")
        with open(image_path, "wb") as img_file:
            img_file.write(msg.payload)

        client.publish(topic_send, "1")
        # print(f"Imagem recebida via MQTT (binário) - nº {contador}")
        contador = contador+1
    client.publish(topic_send, "0")

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    cods_connection = {
        0: "Conexão bem-sucedida",
        1: "Versão do protocolo incorreta",
        2: "Identificador do cliente inválido",
        3: "Servidor indisponível",
        4: "Credenciais inválidas",
        5: "Não autorizado"
    }
    
    if rc == 0:
        mqtt_connected = True
        print(f"{cods_connection[rc]}")
        
        client.subscribe("camera/image")
    else:
        mqtt_connected = False
        print(f"Falha na conexão: {cods_connection.get(rc, 'Erro desconhecido')}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print("Desconectado do broker MQTT")

# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set(user, password)
client.tls_set()

# Vincula as funções de callback
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Tenta conectar ao broker
try:
    client.connect(address_broker, port, 60)
    client.publish(topic_send, "mensagem 1")
    client.loop_start()
    
    # Aguarda até 5 segundos pela conexão
    timeout = time.time() + 5
    while not mqtt_connected and time.time() < timeout:
        time.sleep(0.1)
    
    if not mqtt_connected:
        print("Timeout na conexão MQTT")
except Exception as e:
    print(f"Erro ao conectar ao broker MQTT: {str(e)}")


# @app.route("/mqtt-status", methods=["GET"])
# def get_mqtt_status():
#     return jsonify({
#         "connected": mqtt_connected,
#         "ultima_mensagem": ultima_mensagem
#     })

# @app.route("/ultima-mensagem", methods=["GET"])
# def pega_ultima_mensagem():
#     return jsonify(ultima_mensagem)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)