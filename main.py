import os
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
        
    # Corrección para límites
    nuevo_idx = (idx + paso) % largo_fila
        
    return fila_destino_str[nuevo_idx]

def procesar_mensaje(texto, direccion, cifrar=True):
    resultado = []
    for car in str(texto).upper():
        resultado.append(procesar_caracter(car, direccion, cifrar))
    return "".join(resultado)

@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        datos = request.get_json(silent=True, force=True)
        if not datos:
            return jsonify({"error": "No se recibieron datos JSON válidos"}), 400
            
        texto = datos.get("texto", "")
        direccion = str(datos.get("direccion", "R")).upper()
        cifrar = bool(datos.get("cifrar", True))
        
        resultado_texto = procesar_mensaje(texto, direccion, cifrar=cifrar)
        
        return jsonify({"resultado": resultado_texto})

    except Exception as e:
        return jsonify({"error": "Ocurrió un error en el servidor", "detalle": str(e)}), 500

# IMPORTANTE PARA RENDER: Lee el puerto que asigna el servidor automáticamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
