from flask import Flask, jsonify, request
import os
import mqtt_conf
import numpy as np
from PIL import Image
import struct

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

contador = 0

contador = 0

def rgb565_to_rgb888(data, width, height):
    # Verifica a quantidade de bytes em relação a resolução
    expected_length = width * height * 2
    if len(data) != expected_length:
        raise ValueError(f"Tamanho de dados incompatível. Esperado: {expected_length}, Recebido: {len(data)}")
    
    rgb888 = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Processa cada pixel
    for y in range(height):
        for x in range(width):
            idx = (y * width + x) * 2
            
            # Lê o valor RGB565 (Big Endian)
            pixel = struct.unpack(">H", data[idx:idx+2])[0]
            
            r = ((pixel >> 11) & 0x1F) << 3  # 5 bits para R, expande para 8 bits
            g = ((pixel >> 5) & 0x3F) << 2   # 6 bits para G, expande para 8 bits
            b = (pixel & 0x1F) << 3          # 5 bits para B, expande para 8 bits
            
            rgb888[y, x, 0] = r
            rgb888[y, x, 1] = g
            rgb888[y, x, 2] = b

    return rgb888

def visualizar_rgb565(data, width, height):
    rgb565_array = np.frombuffer(data, dtype=np.uint16).reshape((height, width))

    # Converte para uma imagem PIL de 16 bits
    img = Image.fromarray(rgb565_array, mode='I;16')  # 'I;16' -> Imagem de 16 bits

    # Mostra a imagem em tons de cinza
    img.show()

# Rota para fazer upload de imagem
@app.route('/imagens', methods=['POST'])
def upload_image():
    global contador
    width = int(request.headers['X-Image-Width'])
    height = int(request.headers['X-Image-Height'])
    try: 
        if request.data:
            if(request.headers['X-Image-Format'] == "RGB565"):
                rgb888 = rgb565_to_rgb888(request.data, width, height)
                img = Image.fromarray(rgb888)
                img.show()
                return "", 201
        

            if(request.headers['X-Image-Format'] == "JPEG"):
                image_infos = write_image(contador)
                if image_infos['result']:
                    contador += 1

                    if mqtt_conf.mqtt_connected:
                        mqtt_conf.on_publish(mqtt_conf.client, image_infos)

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