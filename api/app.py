from flask import Flask, jsonify, request
import os
import mqtt_conf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

contador = 0

# Rota de teste
# @app.route('/teste', methods=['GET'])
# def get_teste():
#     mqtt_conf.on_publish(mqtt_conf.client)
#     return jsonify({"message": "Conexão feita com sucesso"})

# Rota para fazer upload de imagem
@app.route('/imagens', methods=['POST'])
def upload_image():
    global contador
    try: 
        if request.data:
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