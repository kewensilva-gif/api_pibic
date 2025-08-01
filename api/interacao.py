import cv2
import numpy as np
from typing import Tuple

thresholds_correl:float = 0.4
thresholds_coss:float = 0.65

def extrair_histograma(imagem: np.ndarray, usar_mascara: bool = False) -> np.ndarray:
    hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
    
    if usar_mascara:
        # Criar máscaras para as duas faixas de vermelho em HSV
        lower_red1 = np.array([0, 70, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([165, 70, 70])
        upper_red2 = np.array([179, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        cv2.bitwise_or(mask1, mask2)
        
        # Calcular histogramas para as duas faixas de vermelho
        hist1 = cv2.calcHist([hsv], [0], mask1, [20], [0, 20])
        hist2 = cv2.calcHist([hsv], [0], mask2, [20], [160, 180])
        
        # Combinar os histogramas
        hist_completo = np.concatenate([hist1, hist2])
    else:
        # Calcular histograma completo sem máscara
        hist_completo = cv2.calcHist([hsv], [0], None, [180], [0, 180])
    
    # Normalizar
    cv2.normalize(hist_completo, hist_completo, 0, 1, cv2.NORM_MINMAX)
    return hist_completo

def dissimilaridade_cos(hist1: np.ndarray, hist2: np.ndarray) -> float:
    hist1 = hist1.flatten()
    hist2 = hist2.flatten()
    
    # Evitar divisão por zero
    if np.linalg.norm(hist1) == 0 or np.linalg.norm(hist2) == 0:
        return 1.0
    
    # Calcular similaridade de cosseno
    cos_sim = np.dot(hist1, hist2) / (np.linalg.norm(hist1) * np.linalg.norm(hist2))
    
    # Converter para dissimilaridade (1 - similaridade)
    return 1 - cos_sim


def deteccao_interacao_coss(hist_base: np.ndarray, hist_comp: np.ndarray) -> Tuple[bool, float]:
    global thresholds_coss

    dissim_cosseno: float = dissimilaridade_cos(hist_base, hist_comp)
    interacao_cosseno: bool = dissim_cosseno > thresholds_coss

    return interacao_cosseno, dissim_cosseno

def deteccao_interacao_correl(hist_base: np.ndarray, hist_comp: np.ndarray) -> Tuple[bool, float]:
    global thresholds_coss
    
    correlacao: float = cv2.compareHist(hist_base, hist_comp, cv2.HISTCMP_CORREL)
    interacao_correl: float = correlacao < thresholds_correl

    return interacao_correl, correlacao