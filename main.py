import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Ambas cadenas tienen exactamente 27 caracteres.
# Las posiciones coinciden 1 a 1 según la distribución original del teclado:
# Q->1, W->2, E->3 ... A->@, S-># ... Z->*, X->_ , C->' ... M->?
LETRAS   = "QWERTYUIOPASDFGHJKLÑZXCVBNM"
SIMBOLOS = "1234567890@#$_&-+()/*_':;!?"

def procesar_caracter(car, direccion, cifrar):
    origen = LETRAS if cifrar else SIMBOLOS
    destino = SIMBOLOS if cifrar else LETRAS
    
    # Si el carácter no está en la matriz (ej. espacios o signos desconocidos), no se altera
    if car not in origen:
        return car
        
    idx = origen.index(car)
    largo = len(origen)
    
    # Dirección del movimiento
    if cifrar:
        paso = 1 if direccion == "R" else -1
    else:
        paso = -1 if direccion == "R" else 1
        
    # El módulo (%) maneja los límites dando la vuelta automáticamente
    nuevo_idx = (idx + paso) % largo
    
    return destino[nuevo_idx]

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
