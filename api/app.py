from flask import Flask, jsonify, request
from banco import *
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
conexao = criar_conexao()


@app.route("/teste", methods=['GET'])
def get_teste():
    return jsonify({"message:": "Conexão feita com sucesso"})
# rota index, obtem todas as imagens
@app.route('/imagens', methods=['GET'])
def get_imagens():
    imagens = obter_imagens(conexao)
    return jsonify(imagens)


# rota store, resposável por inserir as imagens nos arquivos da api e inserir o caminho no banco
@app.route('/imagens', methods=['POST'])
def upload_imagem():
    if request.data:
        extensao = '.jpg'
        filename = f"{int(datetime.now(timezone.utc).timestamp())}{extensao}"
        caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        with open(caminho_imagem, 'wb') as f:
            f.write(request.data)
            
        if os.path.exists(caminho_imagem) and os.path.getsize(caminho_imagem) > 0:
            salvar_imagem_no_banco(caminho_imagem, conexao)
            return jsonify({"message": "Imagem criada com sucesso!"})
        else:
            return jsonify({"error": "Não foi possível criar a imagem!"})

    
    return jsonify({"error": "Sem dados de imagem"}), 400
""" @app.route('/imagens', methods=['POST'])
def upload_imagem():
    imagem = request.files.get('image')
    if imagem and imagem.filename.endswith(('jpeg', 'png', 'jpg')):
        extensao = os.path.splitext(imagem.filename)[1]
        filename = secure_filename(f"{int(datetime.now(timezone.utc).timestamp())}{extensao}")
        caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # caso a pasta não exista ele força a criação
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        imagem.save(caminho_imagem)

        salvar_imagem_no_banco(caminho_imagem, conexao)
        return jsonify({"message": "Imagem criada com sucesso!", "image_path": caminho_imagem})
    
    return jsonify({"error": "Imagem inválida ou formato não suportado!"}), 400
 """

# rota destroy, deleta um elemento
@app.route('/imagens/<int:id>', methods=['DELETE'])
def delete_equipamento(id):
    global imagens
    imagens = [e for e in imagens if e['id'] != id]
    return jsonify({'message': 'Equipamento removido'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
