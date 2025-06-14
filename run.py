import subprocess
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Carpeta temporal donde se extraen los archivos
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def run_streamlit():
    # Reconstruye la ruta al archivo principal dentro del bundle
    script_path = resource_path(os.path.join("src", "app.py"))
    subprocess.run(["streamlit", "run", script_path])

if __name__ == "__main__":
    run_streamlit()

    #pyinstaller --onefile --windowed --collect-all streamlit --add-data "appx.py;." run.py
