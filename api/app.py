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

def aplicar_mascara_em_nova_imagem(imagem_comp, mascara_path, resultado_output_path):
    mascara = cv2.imread(mascara_path, cv2.IMREAD_GRAYSCALE)
    if mascara is None:
        print(f"ERRO: Não foi possível carregar a máscara de '{mascara_path}'.")
        print("Você executou a Fase 1 para gerar a máscara primeiro?")
        return False

    # Aplica a máscara para isolar o objeto
    objeto_isolado = cv2.bitwise_and(imagem_comp, imagem_comp, mask=mascara)
    
    resultado_rgba = cv2.cvtColor(objeto_isolado, cv2.COLOR_RGB2RGBA)
    resultado_rgba[:, :, 3] = mascara
    cv2.imwrite(resultado_output_path, resultado_rgba)
    print(f"SUCESSO: Resultado salvo em '{resultado_output_path}'")
    return True

def analise_histograma(img_base, img_comp, threshold=0.9):
    if img_base is None or img_comp is None:
        print(f"ERRO: Não foi possível carregar as imagens.")
        return

    # Converte para HSV
    hsv_base = cv2.cvtColor(img_base, cv2.COLOR_BGR2HSV)
    hsv_comp = cv2.cvtColor(img_comp, cv2.COLOR_BGR2HSV)

    # Máscaras para vermelho em hsv
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([165, 70, 70])
    upper_red2 = np.array([179, 255, 255])

    mask_base = cv2.bitwise_or(cv2.inRange(hsv_base, lower_red1, upper_red1), cv2.inRange(hsv_base, lower_red2, upper_red2))
    mask_comp = cv2.bitwise_or(cv2.inRange(hsv_comp, lower_red1, upper_red1), cv2.inRange(hsv_comp, lower_red2, upper_red2))

    # Calculo e normalização dos histogramas
    hist_base = cv2.calcHist([hsv_base], [0], mask_base, [180], [0, 180])
    hist_comp = cv2.calcHist([hsv_comp], [0], mask_comp, [180], [0, 180])

    cv2.normalize(hist_base, hist_base, 0, 1, cv2.NORM_MINMAX)
    cv2.normalize(hist_comp, hist_comp, 0, 1, cv2.NORM_MINMAX)

    # Comparação de histogramas
    score = cv2.compareHist(hist_base, hist_comp, cv2.HISTCMP_CORREL)
    interacao = score < threshold
    return interacao, score
    

def processMqttResponse(image_infos):
    global coordenadas, contador
    sleep(5)
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
                alvo_base = cv2.imread(coordenada["target"])
                alvo_comp_sem_mascara = image[
                    coordenada["y"]:coordenada["y"]+coordenada["h"], 
                    coordenada["x"]:coordenada["x"]+coordenada["w"]
                ]
                caminho_alvo_comp_masc = f"mascaras_aplicadas/image{contador}-{coordenada["predicted"]}.png"

                aplicar_mascara_em_nova_imagem(
                    imagem_comp=alvo_comp_sem_mascara,
                    mascara_path=coordenada['mask'], 
                    resultado_output_path=caminho_alvo_comp_masc
                )

                alvo_comp = cv2.imread(caminho_alvo_comp_masc)
                threshold = 0.15
                interacao, score = analise_histograma(alvo_base, alvo_comp, threshold)
                if interacao: cont_inter+=1 

                print(f"Analisando '{coordenada["target"]}' vs '{caminho_alvo_comp_masc}'...")
                print(f"Score de Correlação Calculado: {score:.4f}")
                print(f"O score < {threshold}? {'Sim' if interacao else 'Não'}")
            
            print(f"Resultado Final: {'Interação com alvo detectada' if cont_inter == 1  else 'Não houve interação com o alvo'}")

        if mqtt_conf.mqtt_connected:
            mqtt_conf.on_publish(mqtt_conf.client, '0')
        # return        


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