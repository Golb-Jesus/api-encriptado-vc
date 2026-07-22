from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FILAS_LETRAS = [
    "QWERTYUIOP",
    "ASDFGHJKLÑ",
    "ZXCVBNM"
]

FILAS_SIMBOLOS = [
    "1234567890",
    "@#$_&-+()/",
    "*_':;!?"
]

def procesar_caracter(car, direccion, cifrar):
    matriz_origen = FILAS_LETRAS if cifrar else FILAS_SIMBOLOS
    matriz_destino = FILAS_SIMBOLOS if cifrar else FILAS_LETRAS
    
    num_fila = None
    idx = -1
    
    for i, fila in enumerate(matriz_origen):
        if car in fila:
            num_fila = i
            idx = fila.index(car)
            break
            
    if num_fila is None:
        return car
        
    fila_destino_str = matriz_destino[num_fila]
    largo_fila = len(fila_destino_str)
    
    if cifrar:
        paso = 1 if direccion == "R" else -1
    else:
        paso = -1 if direccion == "R" else 1
        
    # Corrección: El operador módulo (%) evita errores de reasignación
    # y maneja los límites de la fila automáticamente.
    nuevo_idx = (idx + paso) % largo_fila
        
    return fila_destino_str[nuevo_idx]

def procesar_mensaje(texto, direccion, cifrar=True):
    resultado = []
    for car in texto.upper():
        resultado.append(procesar_caracter(car, direccion, cifrar))
    return "".join(resultado)

@app.route('/procesar', methods=['POST'])
def procesar():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400
        
    texto = datos.get("texto", "")
    direccion = datos.get("direccion", "R")
    cifrar = datos.get("cifrar", True)
    
    resultado_texto = procesar_mensaje(texto, direccion, cifrar=cifrar)
    
    return jsonify({"resultado": resultado_texto})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
