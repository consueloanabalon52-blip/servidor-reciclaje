from flask import Flask, request
import requests

app = Flask(__name__)

# Palabras clave de empaque -> reciclable o no
# Si el texto del empaque contiene alguna de estas palabras, se clasifica
materiales_reciclables = ["plastic", "pet", "glass", "metal", "aluminium", "steel", "carton", "paper", "cardboard"]
materiales_no_reciclables = ["polystyrene", "film", "multilayer", "composite"]

@app.route('/reciclable', methods=['POST'])
def reciclable():
    codigo = request.form.get('codigo')

    print(f"\n[ESCANEO] Codigo recibido: {codigo}")

    if not codigo:
        return "FALTA_CODIGO", 400

    try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{codigo}.json?product_type=all"
        headers = {"User-Agent": "AppReciclajeConsuelo/1.0"}
        resp = requests.get(url, headers=headers, timeout=8)
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] No se pudo consultar la API: {e}")
        return "ERROR_CONSULTA", 500

    if data.get("status") != 1:
        print("[INFO] Producto no encontrado en la base de datos.")
        return "PRODUCTO_NO_ENCONTRADO|Producto desconocido|", 404

    producto = data.get("product", {})
    nombre = producto.get("product_name", "Producto sin nombre")
    empaque = producto.get("packaging_text", "") or producto.get("packaging", "")

    print(f"[INFO] Producto: {nombre} | Empaque: {empaque}")

    if not empaque:
        return f"SIN_DATO_EMPAQUE|{nombre}", 200

    # Detectamos si hay alguna señal de "no reciclable" en el texto
    empaque_lower = empaque.lower()
    if any(palabra in empaque_lower for palabra in materiales_no_reciclables):
        etiqueta = "NO_RECICLABLE"
    elif any(palabra in empaque_lower for palabra in materiales_reciclables):
        etiqueta = "RECICLABLE"
    else:
        etiqueta = "SIN_DATO_EMPAQUE"

    return f"{etiqueta}|{nombre}|{empaque}", 200

if __name__ == '__main__':
    print("Servidor de reciclaje (Open Food Facts) encendido y escuchando...")
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)