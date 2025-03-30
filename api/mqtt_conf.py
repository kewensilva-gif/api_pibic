import paho.mqtt.client as mqtt

# Variáveis de configuração mqtt
broker = 'd7257de2da354fae9738d35f3212c93b.s1.eu.hivemq.cloud'
port = 8883
user = 'mqtt_pibic'
password = 'Mqtt_pibic2024'
topic_send = 'api/send/esp'
topic_image = 'camera/image'

mqtt_connected = False

# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set(user, password)
client.tls_set()

# Funções MQTT
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print("Conexão bem-sucedida")
        client.subscribe(topic_image)
    else:
        print("Falha na conexão, código:", rc)

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print("Desconectado do broker MQTT")

def on_publish(client, message):
    client.publish(topic_send, message)

# Vincula as funções de callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Tenta conectar ao broker MQTT
try:
    client.connect(broker, port, 60)
    client.loop_start()
except Exception as e:
    print("Erro ao conectar ao broker MQTT:", str(e))