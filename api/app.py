from flask import Flask, jsonify, request
import os
import mqtt_conf
import numpy as np
from PIL import Image
import det_seg as ds
from threading import Thread
from time import sleep 
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

contador = 0
coordenadas = None

def convertionAndShowImage(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    imagem_pil = Image.fromarray(image_rgb)
    imagem_pil.show()

def processMqttResponse(image_infos):
    global coordenadas, contador
    sleep(5)
    caminho_saida = f"segments/{image_infos["image_name"]}"

    if(coordenadas == None):
        coordenadas = ds.segObjetos(
            image_infos["image_path"], 
            caminho_saida + "/", 
            image_infos["image_name"]
        )
    else:
        image = cv2.imread(image_infos["image_path"])
        for coordenada in coordenadas:
            recorte = image[coordenada["y"]:coordenada["y"]+coordenada["h"], coordenada["x"]:coordenada["x"]+coordenada["w"]]
            
            # Converter para HSV
            recorte_hsv = cv2.cvtColor(recorte, cv2.COLOR_BGR2HSV)
            recorte_coordenada_hsv = cv2.cvtColor(coordenada["recorte"], cv2.COLOR_BGR2HSV)

            # Calcular histogramas do canal H (matiz)
            recorte_hist = cv2.calcHist([recorte_hsv], [0], None, [256], [0, 256])
            recorte_coordenada_hist = cv2.calcHist([recorte_coordenada_hsv], [0], None, [256], [0, 256])

            # Normalizar os histogramas para evitar influências de iluminação
            cv2.normalize(recorte_hist, recorte_hist, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(recorte_coordenada_hist, recorte_coordenada_hist, 0, 1, cv2.NORM_MINMAX)

            similaridade = cv2.compareHist(recorte_hist, recorte_coordenada_hist, cv2.HISTCMP_CORREL)

            print(f"Similaridade entre os histogramas: {similaridade}")

            if similaridade < 0.5:
                print("Possível obstrução detectada!")
                convertionAndShowImage(recorte)
                sleep(10)
        
            else:
                print("Alvo visível normalmente.")

    if mqtt_conf.mqtt_connected:
        mqtt_conf.on_publish(mqtt_conf.client, "1")

# Rota para fazer upload de imagem
@app.route('/imagens', methods=['POST'])
def upload_image():
    global contador
    width = int(request.headers['X-Image-Width'])
    height = int(request.headers['X-Image-Height'])
    try: 
        if request.data:
            if(request.headers['X-Image-Format'] == "JPEG"):
                image_infos = write_image(contador)
                if image_infos['result']:
                    thread = Thread(target=processMqttResponse(image_infos=image_infos))
                    thread.start()

                    contador += 1
                    return "", 201
                else:
                    return "", 400
        return "", 400
    except Exception as e:
        print(str(e))
        return "", 400

def write_image(contador):
    name_image = f"image{contador}"
    extension_image = ".jpg"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{name_image}{extension_image}")
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with open(image_path, 'wb') as f:
        f.write(request.data)
    
    # verifica se a imagem foi realmente adicionada
    result = os.path.exists(image_path) and os.path.getsize(image_path) > 0

    return {"image_path": image_path, "image_name": name_image, "extension_image": extension_image, "result": result}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)