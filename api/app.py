from flask import Flask, jsonify, request
# from banco import *
# from datetime import datetime, timezone
# from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
# conexao = criar_conexao()

contador = 0

# Rota de teste
# @app.route('/teste', methods=['GET'])
# def get_teste():
#     mqtt_conf.on_publish(mqtt_conf.client)
#     return jsonify({"message": "Conexão feita com sucesso"})

# rota store, resposável por inserir as imagens nos arquivos da api e inserir o caminho no banco
@app.route('/imagens', methods=['POST'])
def upload_image():
    global contador
    try: 
        if request.data:
            image_infos = write_image()

            if image_infos['result']:
                contador += 1

                return "", 201
            else:
                return "", 400
   
        return "", 400
    except Exception as e:
        print(str(e))
   
        return "", 400
    
def write_image():
    caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], f"image{contador}.jpg")
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with open(caminho_imagem, 'wb') as f:
        f.write(request.data)
    
    # verifica se a imagem foi realmente adicionada
    result = os.path.exists(caminho_imagem) and os.path.getsize(caminho_imagem) > 0

    return {"image_path": caminho_imagem, "result": result}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
