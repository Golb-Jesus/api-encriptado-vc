import string
from flask import Flask, request, jsonify
import requests
import csv
import io

app = Flask(__name__)

# ENLACE UNIVERSAL CSV DE TU GOOGLE SHEETS
URL_EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQlXTOefoSH6jgC8QW3XMKFMfespM0EGgjdYQUq7cebpJVMt1p4JvKvZtuSI9honNZN0JJux7UWU8Dq/pub?output=csv"

class EncriptadorVecinalNube:
    def __init__(self):
        self.filas = ["QWERTYUIOP", "ASDFGHJKLÑ", "ZXCVBNM"]
        self.subcaps_simbolos = {
            'Q': '1', 'W': '2', 'E': '3', 'R': '4', 'T': '5', 'Y': '6', 'U': '7', 'I': '8', 'O': '9', 'P': '0',
            'A': '!', 'S': '@', 'D': '#', 'F': '$', 'G': '%', 'H': '^', 'J': '&', 'K': '*', 'L': '(', 'Ñ': '>',
            'Z': ')', 'X': '_', 'C': '+', 'V': '=', 'B': '[', 'N': ']', 'M': '{', ',': '<', '.': ':'
        }
        self.selfsubcapa_letras = {v: k for k, v in self.subcaps_simbolos.items()}
        self.filas_simbolos = ["1234567890", "!@#$%^&*()", "}_+-=[]"]

    def _buscar_posicion(self, caracter, matriz):
        for num_fila, fila in enumerate(matriz):
            idx = fila.find(caracter.upper())
            if idx != -1:
                return num_fila, idx, caracter.isupper()
        return None, None, False

    def procesar_caracter(self, car, modo_direction, modo_borde, cifrar=True):
        es_simbolo = car in self.subcaps_simbolos or (car in "".join(self.filas_simbolos) and car not in string.ascii_letters)
        matriz_actual = self.filas_simbolos if es_simbolo else self.filas

        num_fila, idx, es_mayuscula = self._buscar_posicion(car, matriz_actual)
        if num_fila is None:
            return car

        fila_str = matriz_actual[num_fila]
        largo_fila = len(fila_str)

        paso = 1 if modo_direction == "R" else -1
        nuevo_idx = idx + paso

        if modo_borde == "C":
            nuevo_idx = nuevo_idx % largo_fila
        else:
            if nuevo_idx < 0 or nuevo_idx >= largo_fila:
                nuevo_idx = idx

        car_procesado = fila_str[nuevo_idx]

        if not es_simbolo and cifrar:
            car_procesado = self.subcaps_simbolos.get(car_procesado, car_procesado)
        elif es_simbolo and not cifrar:
            car_procesado = self.selfsubcapa_letras.get(car_procesado, car_procesado)

        return car_procesado if es_mayuscula or es_simbolo else car_procesado.lower()

    def procesar_mensaje(self, texto, modo_direction, modo_borde, cifrar=True):
        texto_resultado = []
        for car in texto:
            car_procesado = self.procesar_caracter(car, modo_direction, modo_borde, cifrar)
            texto_resultado.append(car_procesado)
        return "".join(texto_resultado)

motor = EncriptadorVecinalNube()

@app.route('/', methods=['GET', 'POST'])
def home():
    return "Servidor C0MRADE en línea."

@app.route('/procesar', methods=['POST'])
def procesar():
    datos = request.json
    id_usuario = str(datos.get("usuario", "")).strip()
    
    try:
        respuesta = requests.get(URL_EXCEL_CSV)
        texto_csv = respuesta.content.decode('utf-8')
        lector = csv.DictReader(io.StringIO(texto_csv))
        
        usuarios_dict = {}
        for fila in lector:
            fila_limpia = {str(k).strip().lower(): str(v).strip() for k, v in fila.items() if k is not None}
            
            key_usuario = None
            for k in fila_limpia.keys():
                if "usuario" in k or "user" in k:
                    key_usuario = k
                    break
            
            if key_usuario and fila_limpia[key_usuario]:
                nombre_usuario = fila_limpia[key_usuario]
                usuarios_dict[nombre_usuario] = fila_limpia

        # 1. VALIDAR SI EL USUARIO EXISTE
        if id_usuario not in usuarios_dict:
            return jsonify({"resultado": f"Error: Usuario '{id_usuario}' no registrado en el Excel."}), 401
            
        # 2. VALIDAR SI ESTÁ ACTIVO
        datos_usuario = usuarios_dict[id_usuario]
        estado_usuario = datos_usuario.get("estado", "").lower() or datos_usuario.get("status", "").lower()
        
        if estado_usuario != "activo":
            return jsonify({"resultado": f"Error: Suscripción vencida o {estado_usuario}."}), 403

    except Exception as e:
        return jsonify({"resultado": f"Error de lectura en Excel: {str(e)}"}), 500

    texto_original = datos.get("texto", "")
    direccion = datos.get("direccion", "L")
    borde = datos.get("borde", "C")
    cifrar = datos.get("cifrar", True)
    
    resultado_final = motor.procesar_mensaje(
        texto=texto_original,
        modo_direction=direccion,
        modo_borde=borde,
        cifrar=cifrar
    )
    
    return jsonify({"resultado": resultado_final})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
