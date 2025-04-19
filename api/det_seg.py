import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

variacao = 12
def mostrarImagem(image, titulo):
  if len(image.shape) == 3 and image.shape[2] == 3:  # Imagem colorida
      # Testa um pixel para verificar se está em HSV
      test_pixel = image[0, 0]
      test_hsv = cv2.cvtColor(np.uint8([[test_pixel]]), cv2.COLOR_RGB2HSV)[0][0]

      if np.array_equal(test_pixel, test_hsv):
          # Se os valores forem iguais, significa que já está em HSV
          img_plot = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)  # Converter HSV → RGB
          formato = "hsv"
      else:
          img_plot = image
          formato = "rgb"
  else:
      img_plot = image
      formato = "cinza"

  # Exibir a imagem corretamente
  plt.figure(figsize=(3,3))
  plt.imshow(img_plot, cmap="gray" if formato == "cinza" else None)
  plt.title(f"{titulo} ({formato})")
  plt.axis("off")
  plt.show()

def salvarImagem(caminho, image):
  if len(image.shape) == 3 and image.shape[2] == 3:  # Imagem colorida
      # Testa um pixel para verificar se está em HSV
      test_pixel = image[0, 0]
      test_hsv = cv2.cvtColor(np.uint8([[test_pixel]]), cv2.COLOR_RGB2HSV)[0][0]

      if np.array_equal(test_pixel, test_hsv):
          # Se os valores forem iguais, significa que já está em HSV
          img_plot = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)  # Converter HSV → BGR
          formato = "hsv"
      else:
          img_plot = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Converter BGR → RGB
          formato = "rgb"
  else:
      img_plot = image
      formato = "cinza"

  # Exibir a imagem corretamente
  cv2.imwrite(caminho, img_plot)

def definirMascaraOBJ(pasta_saida, imagem, imagem_hsv, c, n):
    global variacao
    # Máscara
    selected_color = rgb_to_hsv(c[0], c[1], c[2])
    
    # Converte os valores para inteiros para evitar problemas de tipo
    h_value = int(selected_color[0])
    
    # Calcula os limites com tratamento apropriado de overflow/underflow
    h_min = max(0, h_value - variacao)
    h_max = min(179, h_value + variacao)
    
    lower_red = np.array([h_min, 70, 20], dtype=np.uint8)
    upper_red = np.array([h_max, 255, 150], dtype=np.uint8) 

    # Cria máscaras para a cor
    mask = cv2.inRange(imagem_hsv, lower_red, upper_red)

    # Mostra máscaras aplicadas individualmente à imagem de entrada
    img = cv2.bitwise_and(imagem, imagem, mask=mask)

    return mask
def rgb_to_hsv(r, g, b):
    # Converte a cor de RGB para HSV
    rgb_color = np.uint8([[[r, g, b]]])  # Cria um array NumPy com a cor RGB
    hsv_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)  # Converte para HSV
    return hsv_color[0][0]  # Retorna o valor HSV

def carregaImagem(imagem_caminho):
    imagem = cv2.imread(imagem_caminho) # Carrega a imagem (BGR por padrão no OpenCV)
    imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB) # Converte para RGB
    return imagem

def removeRuido(mask,deltaRuido):
  # Filtro Mediano - Remover ruídos da máscara
  return cv2.medianBlur(mask, deltaRuido)

def segObjetos(imagem_caminho, pasta_saida, nomeImagem, deltaRuido=3, tamSeg=200):
    multCoordenadas = []
    global variacao
    # Carrega a imagem local
    imagem = carregaImagem(imagem_caminho)
    if imagem is None:
        print("Erro ao carregar a imagem. Verifique o caminho.")
        return

    # Cria a pasta de saída, se não existir
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # Converte a imagem para HSV
    imagem_hsv = cv2.cvtColor(imagem, cv2.COLOR_RGB2HSV)

    # Definição das Máscaras ref. aos Objetos
    # Máscara 1
    rgb = [196, 125, 137]
    mask1 = definirMascaraOBJ(pasta_saida,imagem,imagem_hsv,rgb,1)
    # Máscara 2
    rgb = [198, 131, 127]
    mask2 = definirMascaraOBJ(pasta_saida,imagem,imagem_hsv,rgb,2)
    # Máscara 3
    rgb = [173, 105, 129]
    mask3 = definirMascaraOBJ(pasta_saida,imagem,imagem_hsv,rgb,3)
    # Máscara 4
    rgb = [154, 87, 105]
    mask4 = definirMascaraOBJ(pasta_saida,imagem,imagem_hsv,rgb,4)

    # Combina as máscaras e apresenta
    mask_red = cv2.add(mask1, mask2)
    mask_red = cv2.add(mask_red, mask3)
    mask_red = cv2.add(mask_red, mask4)

    # Aplica a máscara na imagem original
    imagem_vermelho = cv2.bitwise_and(imagem, imagem, mask=mask_red)

    # Filtro Mediano - Remover ruídos da máscara
    mask_red = removeRuido(mask_red, deltaRuido)

    # Aplicar operação morfológica CLOSE para conectar componentes próximos
    kernel = np.ones((5,5), np.uint8)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)

    # Encontra os contornos dos objetos vermelhos
    contornos, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Segmenta cada objeto vermelho encontrado
    for i, contorno in enumerate(contornos):

        # Cria uma máscara vazia do mesmo tamanho da imagem original
        mask_objeto = np.zeros_like(mask_red)

        # Desenha o contorno na máscara
        cv2.drawContours(mask_objeto, [contorno], -1, (255), thickness=cv2.FILLED)

        # Normaliza para 0 e 1
        mask_objeto_binario = (mask_objeto > 0).astype(np.uint8)

        #-----------------------------------------------------------------------------------
        # Obtém o retângulo delimitador para cada contorno
        x, y, w, h = cv2.boundingRect(contorno)

        
        # Extrai a região do objeto da imagem original
        objeto = imagem[y:y+h, x:x+w]

        # Obtém as dimensões da imagem (altura, largura, canais)
        altura, largura, _ = objeto.shape
        total_pixels = altura * largura  # Número total de pixels
        
        # Condição para considerar somente segmentos com total_pixels > n
        if total_pixels > 1000 and altura > 10 and largura > 10:
            # Salva o objeto como um arquivo separado
            salvarImagem(f"{pasta_saida}{nomeImagem}_{i+1}_seg.png",objeto) # Salva como imagem binária (0 e 255)
            # multCoordenadas = multCoordenadas + f"{x},{y},{w},{h};

            multCoordenadas.append({'x': x, 'y': y, 'w': w, 'h': h, 'recorte': f"{pasta_saida}{nomeImagem}_{i+1}_seg.png"})
            #-----------------------------------------------------------------------------------
            # Recorta o segmento binário com base no retângulo delimitador
            segmento_recortado = mask_objeto[y:y+h, x:x+w]
            segmento_binario = (segmento_recortado > 0).astype(np.uint8)
        else :
            print(f"Objeto {i+1}: não considerado por tratar-se de um possível ruído (total pixels {total_pixels}px)")

    return multCoordenadas

