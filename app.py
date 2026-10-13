"""
Portal SST - Lema de Seguridad (v04)
UNMSM - Facultad de Ingenieria Industrial - Escuela Profesional de SST

v02: al ejecutar, la interfaz se abre sola en una ventana propia (pywebview).
     Si pywebview no esta instalado, se abre sola en el navegador.

Ejecutar:
    pip install -r requirements.txt
    python app.py      (o doble clic en iniciar_portal.pyw / iniciar_portal.command)
"""
import threading
import webbrowser
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
VIDEO_DIR = BASE_DIR / "static" / "video"
VIDEO_NOMBRE = "video_portal.mp4"          # nombre fijo del video que se reproduce
LEMA_MAX = 120                             # longitud maxima del lema

# --- Menu del portal (editar aqui para agregar/quitar opciones) ---
MENU = [
    {"id": "inicio",         "titulo": "Inicio",          "icono": "🏠"},
    {"id": "capacitaciones", "titulo": "Capacitaciones",  "icono": "🎓"},
    {"id": "inspecciones",   "titulo": "Inspecciones",    "icono": "🔍"},
    {"id": "epp",            "titulo": "EPP",             "icono": "🦺"},
    {"id": "incidentes",     "titulo": "Incidentes",      "icono": "⚠️"},
    {"id": "normativa",      "titulo": "Normativa",       "icono": "📘"},
]

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024  # 300 MB maximo por video


def hay_video() -> bool:
    return (VIDEO_DIR / VIDEO_NOMBRE).exists()


@app.route("/", methods=["GET"])
def inicio():
    """Pantalla para escribir el lema y (opcional) subir el video."""
    return render_template("index.html", hay_video=hay_video(), lema_max=LEMA_MAX)


@app.route("/generar", methods=["POST"])
def generar():
    lema = (request.form.get("lema") or "").strip()[:LEMA_MAX]
    if not lema:
        return render_template(
            "index.html",
            hay_video=hay_video(),
            lema_max=LEMA_MAX,
            error="Escribe un lema de seguridad.",
            lema="",
        )

    archivo = request.files.get("video")
    if archivo and archivo.filename:
        nombre = archivo.filename.lower()
        if not nombre.endswith(".mp4"):
            return render_template(
                "index.html",
                hay_video=hay_video(),
                lema_max=LEMA_MAX,
                error="El video debe ser un archivo .mp4",
                lema=lema,
            )

        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        archivo.save(VIDEO_DIR / VIDEO_NOMBRE)  # reemplaza el video anterior

    return redirect(url_for("portal", lema=lema))


@app.route("/portal")
def portal():
    lema = (request.args.get("lema") or "Seguridad y Salud, lo importante eres tú")[:LEMA_MAX]
    return render_template("portal.html", lema=lema, menu=MENU,
                           hay_video=hay_video(), video_nombre=VIDEO_NOMBRE)


@app.errorhandler(413)
def demasiado_grande(_e):
    return render_template(
        "index.html",
        hay_video=hay_video(),
        lema_max=LEMA_MAX,
        error="El video supera los 300 MB.",
        lema="",
    ), 413


HOST, PUERTO = "127.0.0.1", 5000
URL = f"http://{HOST}:{PUERTO}"


def _servidor():
    app.run(debug=False, host=HOST, port=PUERTO, use_reloader=False)


def main():
    """Abre la interfaz del portal (no el codigo)."""
    try:
        import webview  # pywebview
    except ImportError:
        webview = None

    if webview:
        # Servidor en segundo plano + ventana de escritorio con la interfaz
        threading.Thread(target=_servidor, daemon=True).start()
        webview.create_window("Portal SST - Lema de Seguridad", URL,
                              width=1280, height=820, min_size=(900, 600))
        webview.start()          # al cerrar la ventana, termina el programa
    else:
        # Respaldo: abre la interfaz en el navegador predeterminado
        threading.Timer(1.2, lambda: webbrowser.open(URL)).start()
        _servidor()


if __name__ == "__main__":
    main()
