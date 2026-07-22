from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class MotorCifradoCelularVecinal:
    def __init__(self):
        # Filas de letras (Mayúsculas)
        self.filas_letras = [
            "QWERTYUIOP",  # 10
            "ASDFGHJKLÑ",  # 10 letras
            "ZXCVBNM"      # 7
        ]
        
        # Filas de símbolos del celular emparejadas en tamaño (10, 10 y 7)
        # Añadimos un espacio al final de la fila 2 para balancear la Ñ
        self.filas_simbolos = [
            "1234567890",
            "@#$_&-+()/",
            "*_':;!?"
        ]

    def procesar_caracter(self, car, direccion, cifrar):
        # 1. Determinar en qué matriz buscar (Letras o Símbolos)
        matriz_origen = self.filas_letras if cifrar else self.filas_simbolos
        matriz_destino = self.filas_simbolos if cifrar else self.filas_letras
        
        num_fila = None
        idx = -1
        
        for i, fila in enumerate(matriz_origen):
            if car in fila:
                num_fila = i
                idx = fila.index(car)
                break
                
        # Si el carácter no está en la matriz (ej. espacios, saltos de línea), se deja intacto
        if num_fila is None:
            return car
            
        fila_origen_str = matriz_origen[num_fila]
        fila_destino_str = matriz_destino[num_fila]
        largo_fila = len(fila_origen_str)
        
        # 2. Configurar el sentido del desplazamiento
        if cifrar:
            paso = 1 if direccion == "R" else -1
        else:
            # Al descifrar el paso se invierte automáticamente para deshacer el camino
            paso = -1 if direccion == "R" else 1
            
        nuevo_idx = idx + paso
        
        # 3. Lógica de Rebote en las Orillas Físicas del Teclado Celular
        if nuevo_idx >= largo_fila:
            # Rebota hacia la izquierda si toca la pared derecha (ej: P, Ñ, M, 0, /, ?)
            nuevo_idx = idx - 1
        elif nuevo_idx < 0:
            # Rebota hacia la derecha si toca la pared izquierda (ej: Q, A, Z, 1, @, *)
            nuevo_idx = idx + 1
            
        # 4. Devolver el carácter transformado de la matriz opuesta
        return fila_destino_str[nuevo_idx]

    def procesar_mensaje(self, texto, direccion, cifrar=True):
        resultado = []
        # Procesamos en mayúsculas para evitar choques con el teclado
        for car in texto.upper():
            resultado.append(self.procesar_caracter(car, direccion, cifrar))
        return "".join(resultado)

motor = MotorCifradoCelularVecinal()

@app.route('/procesar', methods=['POST'])
def procesar():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400
        
    texto = datos.get("texto", "")
    direccion = datos.get("direccion", "R")  # "L" o "R"
    cifrar = datos.get("cifrar", True)       # True o False
    
    resultado_texto = motor.procesar_mensaje(texto, direccion, cifrar=cifrar)
    
    return jsonify({"resultado": resultado_texto})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
