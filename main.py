import string
from datetime import datetime
from flask import Flask, request, jsonify
import requests
import csv
import io

URL_EXCEL_CSV = "https://google.com"

app = Flask(__name__)

class EncriptadoVecinalNube:
    def __init__(self):
        self.filas = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        self.subcapa_simbolos = {
            'Q':'1', 'W':'2', 'E':'3', 'R':'4', 'T':'5', 'Y':'6', 'U':'7', 'I':'8', 'O':'9', 'P':'0',
            'A':'!', 'S':'@', 'D':'#', 'F':'$', 'G':'%', 'H':'^', 'J':'&', 'K':'*', 'L':'(',
            'Z':')', 'X':'-', 'C':'=', 'V':'[', 'B':']', 'N':'{', 'M':'}'
        }
        self.subcapa_letras = {v: k for k, v in self.subcapa_simbolos.items()}
        self.filas_simbolos = ["1234567890", "!@#$%^&*()", ")-=[]{}"]

    def _buscar_posicion(self, caracter, matriz):
        for num_fila, fila in enumerate(matriz):
            idx = fila.find(caracter.upper())
            if idx != -1:
                return num_fila, idx, caracter.isupper()
        return None, None, False

    def procesar_caracter(self, car, modo_direccion, modo_borde, cifrar=True):
        es_simbolo = car in self.subcapa_letras or (car in "".join(self.filas_simbolos) and car not in string.ascii_letters)
        matriz_actual = self.filas_simbolos if es_simbolo else self.filas
        
        num_fila, idx, es_mayuscula = self._buscar_posicion(car, matriz_actual)
        if num_fila is None:
            return car

        fila = matriz_actual[num_fila]
        largo_fila = len(fila)

        desplazamiento = 1 if modo_direccion == 'R' else -1
        if not cifrar:
            desplazamiento *= -1

        nuevo_idx = idx + desplazamiento

        if nuevo_idx < 0: 
            if modo_borde == 'C': 
                nuevo_idx = largo_fila - 1
            else: 
                nuevo_idx = 1
        elif nuevo_idx >= largo_fila: 
            if modo_borde == 'C': 
                nuevo_idx = 0
            else: 
                nuevo_idx = largo_fila - 2

        resultado = fila[nuevo_idx]
        return resultado if es_mayuscula or es_simbolo else resultado.lower()

    def procesar_texto(self, texto, modo_dir_fijo, clave, modo_borde, usar_simbolos, cifrar=True):
        texto_resultado = []
        for i, car in enumerate(texto):
            if modo_dir_fijo == "L":
                direccion = "L"
            elif modo_dir_fijo == "R":
                direccion = "R"
            else:
                direccion = clave[i % len(clave)].upper() if clave else "L"
            
            if cifrar and usar_simbolos and car.upper() in self.subcapa_simbolos:
                if modo_dir_fijo != "K" or i % 2 == 1:
                    car = self.subcapa_simbolos[car.upper()]

            car_procesado = self.procesar_caracter(car, direccion, modo_borde, cifrar=cifrar)
            
            if not cifrar and usar_simbolos and car_procesado in self.subcapa_letras:
                letra = self.subcapa_letras[car_procesado]
                car_procesado = letra if car.isupper() else letra.lower()

            texto_resultado.append(car_procesado)
        return "".join(texto_resultado)

motor = EncriptadoVecinalNube()

# RUTA DE LA API PARA ENCRIPTAR Y RASTREAR
@app.route('/', methods=['GET', 'POST'])
def home():
    return "Servidor C0MRADE en linea."




@app.route('/procesar', methods=['POST'])
def procesar():
    datos = request.json
    id_usuario = datos.get("usuario", "Anonimo")
    
    try:
        respuesta = requests.get(URL_EXCEL_CSV)
        texto_csv = respuesta.content.decode('utf-8')
        lector = csv.DictReader(io.StringIO(texto_csv))
        usuarios_dict = {fila['usuario']: fila for fila in lector if 'usuario' in fila}
        
        if id_usuario not in usuarios_dict:
            return jsonify({"resultado": "Error: Licencia no válida o usuario no registrado."}), 401
        if usuarios_dict[id_usuario].get("estado") != "activo":
            return jsonify({"resultado": "Error: Tu suscripción ha vencido. Renueva tu pago."}), 403
    except Exception as e:
        return jsonify({"resultado": f"Error de base de datos: {str(e)}"}), 500
    
    datos = request.json
    texto = datos.get('texto', '')
    direccion = datos.get('direccion', 'L')
    clave = datos.get('clave', 'LR')
    borde = datos.get('borde', 'C')
    simbolos = datos.get('simbolos', True)
    cifrar = datos.get('cifrar', True)
    usuario = datos.get('usuario', 'Desconocido')

    # --- RASTREADOR EN TIEMPO REAL ---
    accion = "CIFRAR" if cifrar else "DESCIFRAR"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ahora}] [ALERTA DE USO] El usuario '{usuario}' ejecuto la accion: {accion}")

    resultado = motor.procesar_texto(texto, direccion, clave, borde, simbolos, cifrar=cifrar)
    return jsonify({'resultado': resultado})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
