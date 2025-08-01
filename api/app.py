from flask import Flask, jsonify, request
import os
import mqtt_conf
import numpy as np
from PIL import Image
import det_seg as ds
from threading import Thread
from time import sleep 
import cv2
import mlp_cods.target_identification as ti
import json
import interacao as interacao
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

path_coordenadas = "coordenadas.json"
contador = 0
coordenadas = None
if os.path.exists(path_coordenadas):
    with open(path_coordenadas, 'r') as f:
        coordenadas = json.load(f)
class_response = {"lampada": "2", "colcheias": "3", "floco": "4", "helice": "5", "tv": "6"}

def convertionAndShowImage(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    imagem_pil = Image.fromarray(image_rgb)
    imagem_pil.show()

def processMqttResponse(image_infos):
    global coordenadas, contador
    # sleep(5)
    caminho_saida = f"segments/{image_infos["image_name"]}"
    response_mqtt = "1"

    if(coordenadas == None):
        coordenadas = ds.segObjetos(
            image_infos["image_path"], 
            caminho_saida + "/", 
            image_infos["image_name"]
        )
        ti.test_images_from_coordenadas(coordenadas)
        with open(path_coordenadas, 'w') as f:
            json.dump(coordenadas, f, indent=4)
    else:
        image = cv2.imread(image_infos["image_path"])
        cont_inter = 0
        for coordenada in coordenadas:
            if(coordenada["predicted"] != None):
                alvo_base = cv2.imread(coordenada["target_rectangle"])
                alvo_comp = image[
                    coordenada["y"]:coordenada["y"]+coordenada["h"], 
                    coordenada["x"]:coordenada["x"]+coordenada["w"]
                ]
                
                if alvo_base is None or alvo_comp is None:
                    raise FileNotFoundError(f"Erro ao carregar imagens")
                
                hist_base = interacao.extrair_histograma(alvo_base)
                hist_comp = interacao.extrair_histograma(alvo_comp)

                interacao_cosseno, dissim_cosseno = interacao.deteccao_interacao_correl(hist_base, hist_comp)
                interacao_correl, correlacao = interacao.deteccao_interacao_coss(hist_base, hist_comp)

                print(f"Analisando '{coordenada["target_rectangle"]}' vs '{coordenada['predicted']}-image{contador}.png'...")
                print(f"Score de Correlação Calculado: {correlacao:.4f}")
                print(f"O score < {interacao.thresholds_correl}? {'Sim' if interacao_correl else 'Não'}")
                print(f"Score de Dissimilaridade Cosseno Calculado: {dissim_cosseno:.4f}")
                print(f"O score > {interacao.thresholds_coss}? {'Sim' if interacao_cosseno else 'Não'}")
                
                # Salva as possíveis interações detectadas
                if interacao_cosseno: 
                    path = "teste-interacao-coss"
                    if not os.path.exists(path):
                        os.makedirs(path)
               
                    cv2.imwrite(f"{path}/{coordenada['predicted']}-image{contador}.png", alvo_comp)

                if interacao_cosseno:
                    path = "teste-interacao-correl"
                    if not os.path.exists(path):
                        os.makedirs(path)
               
                    cv2.imwrite(f"{path}/{coordenada['predicted']}-image{contador}.png", alvo_comp)

                if interacao_cosseno or interacao_correl: 
                    cont_inter+=1 

            print(f"Resultado Final: {'Interação com alvo detectada' if cont_inter == 1  else 'Não houve interação com o alvo'}")

        if mqtt_conf.mqtt_connected:
            mqtt_conf.on_publish(mqtt_conf.client, '0')

    if mqtt_conf.mqtt_connected:
        mqtt_conf.on_publish(mqtt_conf.client, response_mqtt)
    
# Rota para fazer upload de imagem
@app.route('/imagens', methods=['POST'])
def upload_image():
    global contador
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