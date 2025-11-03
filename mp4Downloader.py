import sys
import os 
from pathlib import Path
import requests
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QRadioButton, QLabel,
                             QTextEdit, QProgressBar, QFileDialog)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, pyqtSignal, QStandardPaths, Qt 
import yt_dlp

# --- (Función resource_path) ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- (Función format_bytes) ---
def format_bytes(b):
    if b is None or b < 0:
        return "? MB"
    if b < 1024:
        return f"{b} B"
    if b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    if b < 1024 * 1024 * 1024:
        return f"{b / (1024 * 1024):.1f} MB"
    else:
        return f"{b / (1024 * 1024 * 1024):.1f} GB"

# --- (Clase UpdateWorker) ---
class UpdateWorker(QThread):
    finished = pyqtSignal(str) 
    URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    FILENAME = "yt-dlp.exe" 

    def run(self):
        try:
            self.finished.emit("Buscando actualizaciones del motor (yt-dlp)...")
            r = requests.get(self.URL, stream=True, allow_redirects=True, timeout=30)
            r.raise_for_status() 
            # Usa resource_path para guardar el exe
            # Así, si la app se ejecuta desde un .exe, guarda el yt-dlp.exe al lado
            ruta_guardado = resource_path(self.FILENAME)
            with open(ruta_guardado, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
            self.finished.emit(f"¡Motor ({self.FILENAME}) actualizado!")
        except Exception as e:
            self.finished.emit(f"Error al actualizar el motor: {e}")

# --- (Clase Worker de descarga) ---
class Worker(QThread):
    progreso = pyqtSignal(dict)
    finalizado = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, url, ydl_opts):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
    def hook_progreso(self, d):
        self.progreso.emit(d)
    def run(self):
        try:
            self.ydl_opts['progress_hooks'] = [self.hook_progreso]
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url]) 
            self.finalizado.emit("¡Descarga completada!")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


# --- (Modificamos la VentanaPrincipal) ---
class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi Descargador (Vídeo/Audio)") # Título simplificado
        self.setWindowIcon(QIcon(resource_path("mp4down.ico")))
        self.resize(600, 450) # El tamaño está bien
        
        try:
            self.ruta_descarga = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
            if not self.ruta_descarga:
                self.ruta_descarga = str(Path.home()) 
        except Exception as e:
            self.ruta_descarga = os.path.abspath(os.getcwd())
        
        self.worker = None 
        self.update_worker = None
        self.etiqueta_url = QLabel("Pegar URL:")
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("https...://")
        self.btn_elegir_ruta = QPushButton("Elegir Carpeta...")
        self.lbl_ruta = QLabel(f"Guardar en: {self.ruta_descarga}")
        self.lbl_ruta.setWordWrap(True) 
        
        self.rb_video = QRadioButton("Vídeo (MP4)")
        self.rb_audio = QRadioButton("Audio (MP3)")
       
        self.rb_video.setChecked(True) 
        
        self.btn_descargar = QPushButton("Descargar")
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setVisible(False) 
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Aquí aparecerá el estado...\nADVERTENCIA: Para X/Twitter, necesitas 'cookies_x.txt'.")
        
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)
       
        layout_opciones = QHBoxLayout()
        layout_opciones.addWidget(self.rb_video)
        layout_opciones.addWidget(self.rb_audio)
        
        layout_principal.addWidget(self.etiqueta_url)
        layout_principal.addWidget(self.txt_url)
        layout_principal.addWidget(self.btn_elegir_ruta)
        layout_principal.addWidget(self.lbl_ruta)
        layout_principal.addLayout(layout_opciones)
        layout_principal.addWidget(self.btn_descargar)
        layout_principal.addWidget(self.progress_bar) 
        layout_principal.addWidget(self.log_area)
        self.btn_descargar.clicked.connect(self.iniciar_descarga)
        self.btn_elegir_ruta.clicked.connect(self.elegir_ruta)
        
        self.iniciar_actualizacion()

    # --- (Funciones de elegir_ruta, iniciar_actualizacion, etc.) ---
    def elegir_ruta(self):
        nueva_ruta = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", self.ruta_descarga)
        if nueva_ruta:
            self.ruta_descarga = nueva_ruta
            self.lbl_ruta.setText(f"Guardar en: {self.ruta_descarga}")
            
    def iniciar_actualizacion(self):
        self.update_worker = UpdateWorker()
        self.update_worker.finished.connect(self.al_terminar_actualizacion)
        self.update_worker.start()

    def al_terminar_actualizacion(self, mensaje):
        self.log_area.append(mensaje)

    # --- LÓGICA DE DESCARGA ---
    def iniciar_descarga(self):
        url = self.txt_url.text() 
        if not url:
            self.log_area.append("ERROR: Pega una URL.")
            return

        self.btn_descargar.setEnabled(False)
        self.btn_elegir_ruta.setEnabled(False) 
        self.log_area.setText(f"Iniciando descarga de: {url}\n")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat("Iniciando...")

        # --- (Lógica de Motor y Cookies) ---
        ruta_limpia = self.ruta_descarga.replace('\\', '/')
        ydl_opts_base = {'noplaylist': True}
        motor_externo = resource_path('yt-dlp.exe')
        if os.path.exists(motor_externo):
            self.log_area.append("Usando motor externo (actualizado)")
            ydl_opts_base['yt_dlp_path'] = motor_externo
        else:
            self.log_area.append("Usando motor interno (el del .exe)")
        if "x.com" in url.lower() or "twitter.com" in url.lower():
            self.log_area.append("URL de X/Twitter detectada. Buscando 'cookies_x.txt'...")
            cookie_path = resource_path('cookies_x.txt')
            if os.path.exists(cookie_path):
                self.log_area.append("¡Cookies encontradas! Añadiendo al proceso.")
                ydl_opts_base['cookiefile'] = cookie_path
            else:
                self.log_area.append("ADVERTENCIA: No se encontró 'cookies_x.txt'.")
                
        # --- (Lógica de Nombres) ---
        if "x.com" in url.lower() or "twitter.com" in url.lower() or "instagram.com" in url.lower():
             plantilla_salida = f"{ruta_limpia}/%(display_id)s.%(ext)s"
        else:
             plantilla_salida = f"{ruta_limpia}/%(title)s.%(ext)s"
             
        # --- LÓGICA DE FORMATO ---
        if self.rb_audio.isChecked():
            self.log_area.append("Modo: Audio (MP3)")
            ydl_opts_base.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}], 'outtmpl': plantilla_salida})
        else: 
            # Si no es audio, por defecto es Vídeo
            self.log_area.append("Modo: Vídeo (MP4)")
            ydl_opts_base.update({'format': 'bestvideo+bestaudio[ext=m4a]/best', 'merge_output_format': 'mp4', 'outtmpl': plantilla_salida})
        
        self.worker = Worker(url, ydl_opts_base) 
        self.worker.progreso.connect(self.actualizar_progreso)
        self.worker.finalizado.connect(self.descarga_finalizada)
        self.worker.error.connect(self.descarga_error)
        self.worker.start()

  
    def actualizar_progreso(self, d):
        if d['status'] == 'downloading':
            porcentaje_str = d.get('_percent_str', '0.0%').strip().replace('%', '')
            try:
                porcentaje = float(porcentaje_str)
                self.progress_bar.setValue(int(porcentaje))
            except ValueError: pass
            downloaded = d.get('downloaded_bytes')
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_str = format_bytes(downloaded)
            total_str = format_bytes(total)
            self.progress_bar.setFormat(f"{downloaded_str} / {total_str}")
        elif d['status'] == 'finished':
            self.log_area.append("Descarga base completada. Procesando (FFmpeg)...")
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Procesando...")
    def descarga_finalizada(self, mensaje):
        self.log_area.append(f"\n{mensaje}")
        self.log_area.append(f"Guardado en: {self.ruta_descarga}")
        self.btn_descargar.setEnabled(True) 
        self.btn_elegir_ruta.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("%p%") 
    def descarga_error(self, error_msg):
        self.log_area.append(f"ERROR: {error_msg}")
        self.btn_descargar.setEnabled(True)
        self.btn_elegir_ruta.setEnabled(True) 
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("%p%")

# --- Punto de entrada ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()

    sys.exit(app.exec())
