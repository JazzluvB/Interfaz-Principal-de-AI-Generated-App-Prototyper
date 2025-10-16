# app_pyqt5_ai_prototyper.py
import sys
import os
import time
import base64
import tempfile
from io import BytesIO

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QProgressBar, QMessageBox, QInputDialog, QFileDialog, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QByteArray
from PyQt5.QtGui import QFont, QPixmap, QImage, QPalette, QColor, QCursor

# Optional AI + export libs
try:
    import openai
except Exception:
    openai = None

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None

try:
    import pdfkit
except Exception:
    pdfkit = None

# ---------- Config ----------
    import os
try:
    import openai
except Exception:
    openai = None

# ------------ Configuración de OpenAI ------------
import os
try:
    import openai
except Exception:
    openai = None

# Aquí define tu API Key directamente para prueba:
OPENAI_API_KEY = "OPENAI_API_KEY"  # <- pon tu clave real aquí

print("OpenAI API Key:", OPENAI_API_KEY)

if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    print("OpenAI no está disponible o API Key no definida.")

# ---------- Helper: create fallback image if OpenAI not available ----------
def create_fallback_image(text, size=(800, 600), bgcolor="#1C1C1E", fg="#FFFFFF"):
    """Crea una imagen simple (Pillow) con texto para fallback."""
    if Image is None:
        return None
    img = Image.new("RGB", size, bgcolor)
    draw = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        fnt = ImageFont.load_default()
    # Wrap text
    lines = []
    words = text.split()
    line = ""
    for w in words:
        if len(line + " " + w) > 40:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    lines.append(line)
    y = 40
    for l in lines:
        draw.text((40, y), l, font=fnt, fill=fg)
        y += 30
    # return bytes
    with BytesIO() as b:
        img.save(b, format="PNG")
        return b.getvalue()

# ---------- Main App ----------
class AppPrototyper(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Generated App Prototyper")
        self.setGeometry(180, 120, 1100, 720)
        self.setStyleSheet("background-color: #1C1C1E; color: #FFFFFF;")
        self.initUI()

        # internal state
        self.generated_images = [None, None]  # bytes
        self.selected_index = None
        self.generated_code_html = None  # html string with code for pdf

    def initUI(self):
        # Main vertical layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # TITLE
        title = QLabel("AI-Generated App Prototyper")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; padding-bottom: 10px;")
        main_layout.addWidget(title, alignment=Qt.AlignLeft)

        # INPUT area
        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("Ingrese la descripción o su idea de su proyecto aquí")
        self.input_area.setFont(QFont("Arial", 12))
        self.input_area.setStyleSheet(
            "background-color: #2C2C2E; border-radius: 12px; color: #FFFFFF; padding: 12px;"
        )
        self.input_area.setFixedHeight(140)
        main_layout.addWidget(self.input_area)

        # GENERATE BUTTON
        self.btn_generate = QPushButton("Presiona aquí para generar prototipo")
        self.btn_generate.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_generate.setFont(QFont("Arial", 13, QFont.Bold))
        self.btn_generate.setStyleSheet(self.green_button_style())
        self.btn_generate.clicked.connect(self.on_generate_clicked)
        main_layout.addWidget(self.btn_generate, alignment=Qt.AlignLeft)

        # PROGRESS area
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFixedHeight(28)
        self.progress.setStyleSheet(self.progress_style())
        self.progress.hide()
        main_layout.addWidget(self.progress)

        # Processing message
        self.process_label = QLabel("")
        self.process_label.setFont(QFont("Arial", 11))
        self.process_label.setStyleSheet("color: #CCCCCC; padding-top: 6px;")
        main_layout.addWidget(self.process_label, alignment=Qt.AlignLeft)

        # Results area (scrollable)
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_widget.setLayout(self.results_layout)
        self.results_area.setWidget(self.results_widget)
        main_layout.addWidget(self.results_area)
        self.results_area.hide()

        # Image panel: two images side by side
        self.images_row = QHBoxLayout()
        self.img_label_1 = QLabel("Opción 1\n(esperando...)", alignment=Qt.AlignCenter)
        self.img_label_2 = QLabel("Opción 2\n(esperando...)", alignment=Qt.AlignCenter)
        for lbl in (self.img_label_1, self.img_label_2):
            lbl.setFixedSize(420, 320)
            lbl.setStyleSheet(self.image_box_style(selected=False))
            lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignCenter)
        self.img_label_1.mousePressEvent = lambda ev: self.select_image(0)
        self.img_label_2.mousePressEvent = lambda ev: self.select_image(1)
        self.images_row.addWidget(self.img_label_1)
        self.images_row.addWidget(self.img_label_2)
        self.results_layout.addLayout(self.images_row)

        # Buttons row (horizontal): Cambiar colores | Modificar textos | Exportar PDF/PNG | Descargar imagen
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)

        self.btn_colors = QPushButton("Cambiar colores")
        self.btn_colors.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_colors.setStyleSheet(self.purple_button_style())
        self.btn_colors.clicked.connect(self.change_colors)
        self.btn_colors.setEnabled(False)

        self.btn_modify = QPushButton("Modificar textos")
        self.btn_modify.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_modify.setStyleSheet(self.blue_button_style())
        self.btn_modify.clicked.connect(self.modify_text)
        self.btn_modify.setEnabled(False)

        self.btn_export = QPushButton("Exportar PDF")
        self.btn_export.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_export.setStyleSheet(self.orange_button_style())
        self.btn_export.clicked.connect(self.export_pdf)
        self.btn_export.setEnabled(False)

        self.btn_download = QPushButton("Descargar imagen")
        self.btn_download.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_download.setStyleSheet(self.orange_button_style(dark=True))
        self.btn_download.clicked.connect(self.download_image)
        self.btn_download.setEnabled(False)

        # add to row left-to-right
        for b in (self.btn_colors, self.btn_modify, self.btn_export, self.btn_download):
            b.setFixedHeight(40)
            buttons_row.addWidget(b)

        self.results_layout.addLayout(buttons_row)

        # Add a little footer note
        footer = QLabel("Selecciona la opción (clic) y usa 'Descargar imagen' para bajar la imagen seleccionada.")
        footer.setStyleSheet("color:#999999; padding-top:8px;")
        footer.setFont(QFont("Arial", 10))
        self.results_layout.addWidget(footer)

    # ---------- Styles ----------
    def green_button_style(self):
        return """
            QPushButton {
                background-color: #30D158;
                color: #000000;
                border-radius: 12px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #28A745; }
            QPushButton:pressed { background-color: #1E7A2E; }
        """

    def purple_button_style(self):
        return """
            QPushButton {
                background-color: #5856D6;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 8px 14px;
            }
            QPushButton:hover { background-color: #3A32A0; }
        """

    def blue_button_style(self):
        return """
            QPushButton {
                background-color: #007AFF;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 8px 14px;
            }
            QPushButton:hover { background-color: #005BB5; }
        """

    def orange_button_style(self, dark=False):
        if not dark:
            return """
                QPushButton {
                    background-color: #FF9500;
                    color: #000000;
                    border-radius: 12px;
                    padding: 8px 14px;
                }
                QPushButton:hover { background-color: #CC7A00; }
            """
        else:
            return """
                QPushButton {
                    background-color: #FF9F43;
                    color: #000000;
                    border-radius: 12px;
                    padding: 8px 14px;
                }
                QPushButton:hover { background-color: #CC7A00; }
            """

    def progress_style(self):
        return """
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 10px;
                text-align: center;
                color: #FFFFFF;
                background: #222222;
            }
            QProgressBar::chunk {
                background-color: #30D158;
                width: 10px;
            }
        """

    def image_box_style(self, selected: bool):
        if selected:
            return ("background-color: #212123; border-radius: 10px; "
                    "border: 3px solid #30D158; color: #FFFFFF;")
        else:
            return ("background-color: #212123; border-radius: 10px; "
                    "border: 2px solid #333333; color: #AAAAAA;")

    # ---------- Handlers ----------
    def on_generate_clicked(self):
        desc = self.input_area.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Atención", "Ingresa una descripción antes de generar.")
            return

        # reset UI
        self.progress.setValue(0)
        self.process_label.setText("Analizando tu descripción, estamos generando tu idea")
        self.progress.show()
        self.results_area.hide()
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("Generando...")

        # start progress timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._advance_progress_and_maybe_finish)
        self.timer.start(30)  # adjust speed

        # store description for later use
        self._current_description = desc

    def _advance_progress_and_maybe_finish(self):
        val = self.progress.value() + 1
        # slow but not demasiado
        if val > 100:
            val = 100
        self.progress.setValue(val)
        # message during progress
        self.process_label.setText(f"Analizando tu descripción, estamos generando tu idea... {val}%")
        if val >= 100:
            self.timer.stop()
            # after progress complete -> call AI to generate images & code
            QApplication.processEvents()
            self._generate_images_and_code()
            self.finish_generation_ui()

    def _generate_images_and_code(self):
        """Genera 2 imágenes de interfaz y el html de código usando OpenAI si está disponible.
        Fallback a imágenes de texto solo si OpenAI falla.
        """
        desc = self._current_description

        # Prompt para generar dos mockups visuales distintos de UI
        prompt_for_images = (
            f"Design two different macOS dark mode UI mockups for an app that does the following: {desc}. "
            "Include panels, buttons, text areas, progress bars, etc. Make them visually distinct, realistic, clean, minimal, and modern. "
            "Do NOT include text inside the UI. Return two separate images."
        )

        images_bytes = []
        code_html = None

        if openai and OPENAI_API_KEY:
            try:
                # Generar imágenes con OpenAI Image API
                img_resp = openai.Image.create(
                    prompt=prompt_for_images,
                    n=2,  # Dos opciones
                    size="1024x1024"
                )
                for d in img_resp['data']:
                    b64 = d['b64_json']
                    images_bytes.append(base64.b64decode(b64))
            except Exception as e:
                print("OpenAI Image generation failed:", e)
                images_bytes = []

            # Generar snippet de código PyQt5
            try:
                chat_resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Eres un experto en PyQt5 y diseño UI. Devuelve un bloque de código limpio y breve, y una lista de los widgets que se pueden crear con Qt Designer para este prototipo."},
                        {"role": "user", "content": f"Genera un ejemplo de código PyQt5 que contenga: título, QComboBox, QTableWidget, QTextEdit, QPushButton, y explica qué partes conviene crear con Qt Designer para el prototipo: {desc}"}
                    ],
                    temperature=0.2,
                    max_tokens=600
                )
                code_html = chat_resp['choices'][0]['message']['content']
            except Exception as e:
                print("OpenAI chat code generation failed:", e)
                code_html = None

        # Fallback solo si OpenAI falla
        if len(images_bytes) < 2:
            images_bytes = []
            for i in (1, 2):
                txt = f"Opción {i}: Visual fallback para:\n{desc[:200]}"
                fb = create_fallback_image(txt, size=(1024, 768))
                if fb:
                    images_bytes.append(fb)

        if not code_html:
            code_html = self._fallback_code_text(desc)

        # Guardar resultados
        self.generated_images = images_bytes[:2]
        self.generated_code_html = code_html
        
    def finish_generation_ui(self):
        # mostrar área de resultados
        self.results_area.show()
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("Presiona aquí para generar prototipo")
        self.process_label.setText("¡Creación completada!")

        # Asegurar al menos dos imágenes para mostrar
        if not self.generated_images or len(self.generated_images) < 2:
            self.generated_images = [
                create_fallback_image("Opción 1: Prototipo visual de tu idea"),
                create_fallback_image("Opción 2: Variante visual alternativa")
            ]

        # mostrar imágenes en labels
        if self.generated_images[0]:
            self._display_image_on_label(self.generated_images[0], self.img_label_1)
            self.img_label_1.setText("")
        else:
            self.img_label_1.setText("No image")

        if self.generated_images[1]:
            self._display_image_on_label(self.generated_images[1], self.img_label_2)
            self.img_label_2.setText("")
        else:
            self.img_label_2.setText("No image")

        # habilitar botones de acción
        self.btn_colors.setEnabled(True)
        self.btn_modify.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.btn_download.setEnabled(True)

        # reset selección
        self.selected_index = None
        self._update_image_borders()

    def _display_image_on_label(self, img_bytes: bytes, label: QLabel):
        """Carga bytes en QPixmap escalada y la pone en el label."""
        qimg = QImage.fromData(QByteArray(img_bytes))
        if qimg.isNull():
            # fallback: attempt via PIL -> raw bytes -> convert
            try:
                from PIL import Image
                im = Image.open(BytesIO(img_bytes)).convert("RGBA")
                data = im.tobytes("raw", "RGBA")
                qimg = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
            except Exception as e:
                print("Failed to convert image:", e)
                return
        pix = QPixmap.fromImage(qimg)
        # scale to label size keeping aspect ratio
        scaled = pix.scaled(label.width()-8, label.height()-8, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled)
        label.setAlignment(Qt.AlignCenter)

    def select_image(self, index: int):
        # toggle selection on click
        if index not in (0,1):
            return
        self.selected_index = index
        self._update_image_borders()

    def _update_image_borders(self):
        # update style to show green border if selected
        self.img_label_1.setStyleSheet(self.image_box_style(selected=(self.selected_index==0)))
        self.img_label_2.setStyleSheet(self.image_box_style(selected=(self.selected_index==1)))

    # ---------- Actions ----------
    def change_colors(self):
        # For demo: show a message. You can extend to show color pickers per widget.
        QMessageBox.information(self, "Cambiar colores", "Aquí se mostrarán paletas para cambiar colores de la UI (implementación futura).")

    def modify_text(self):
        if self.selected_index is None:
            QMessageBox.warning(self, "Selecciona una imagen", "Selecciona primero una opción (clic en la imagen).")
            return
        current_note = f"Texto actual para Opción {self.selected_index+1}"
        text, ok = QInputDialog.getText(self, "Modificar textos", "Escribe el nuevo texto/nota para el prototipo:", text=current_note)
        if ok:
            QMessageBox.information(self, "Texto modificado", "Tu modificación ha sido guardada para el prototipo (visual).")

    def download_image(self):
        if self.selected_index is None:
            QMessageBox.warning(self, "Selecciona", "Selecciona primero la opción que quieres descargar.")
            return
        img_bytes = self.generated_images[self.selected_index]
        if not img_bytes:
            QMessageBox.warning(self, "Error", "No hay imagen para descargar.")
            return
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar imagen", f"prototipo_opcion{self.selected_index+1}.png", "PNG Files (*.png);;All Files (*)", options=options)
        if filename:
            with open(filename, "wb") as f:
                f.write(img_bytes)
            QMessageBox.information(self, "Descargado", f"Imagen guardada en:\n{filename}")

    def export_pdf(self):
        # Export selected image + generated code to PDF
        if self.selected_index is None:
            QMessageBox.warning(self, "Selecciona", "Selecciona primero la opción que quieres exportar.")
            return
        if pdfkit is None:
            QMessageBox.warning(self, "Dependencia faltante", "pdfkit no está instalado. Instala pdfkit y wkhtmltopdf para exportar a PDF.")
            return
        img_bytes = self.generated_images[self.selected_index]
        # Create temporary image file
        tmp_dir = tempfile.mkdtemp()
        img_path = os.path.join(tmp_dir, f"prototipo_opcion{self.selected_index+1}.png")
        with open(img_path, "wb") as f:
            f.write(img_bytes)

        # Build HTML with embedded image and code block
        safe_code_html = self.generated_code_html or self._fallback_code_text(self._current_description)
        # wrap code in <pre>
        html = f"""
        <html>
        <head>
        <meta charset="utf-8"/>
        <style>
          body {{ background-color:#0F0F10; color:#FFFFFF; font-family: Arial, Helvetica, sans-serif; }}
          .card {{ background:#1C1C1E; padding:16px; border-radius:12px; margin:16px; }}
          img {{ max-width:800px; border-radius:8px; display:block; margin-bottom:16px; }}
          pre {{ background:#0B0B0C; color:#E6E6E6; padding:12px; border-radius:8px; overflow:auto; }}
          h1 {{ color:#FFFFFF; }}
        </style>
        </head>
        <body>
        <div class="card">
          <h1>Prototipo - Opción {self.selected_index+1}</h1>
          <img src="file://{img_path}" alt="prototipo" />
          <h2>Código sugerido (PyQt5 + Qt Designer recomendaciones)</h2>
          <pre>{safe_code_html}</pre>
        </div>
        </body>
        </html>
        """
        pdf_path = os.path.join(tmp_dir, f"prototipo_opcion{self.selected_index+1}.pdf")
        try:
            pdfkit.from_string(html, pdf_path)
            # ask where save
            options = QFileDialog.Options()
            save_file, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", f"prototipo_opcion{self.selected_index+1}.pdf", "PDF Files (*.pdf);;All Files (*)", options=options)
            if save_file:
                # copy tmp pdf -> destination
                with open(pdf_path, "rb") as src, open(save_file, "wb") as dst:
                    dst.write(src.read())
                QMessageBox.information(self, "Exportado", f"PDF creado en:\n{save_file}")
        except Exception as e:
            QMessageBox.warning(self, "Error al exportar", f"No se pudo crear el PDF: {str(e)}")

    # ---------- Fallback code ----------
    def _fallback_code_text(self, description):
        return (
            "Ejemplo de código PyQt5 (skeleton) y widgets recomendados para Qt Designer:\n\n"
            "Widgets recomendados en Qt Designer:\n"
            "- QMainWindow / QWidget (ventana principal)\n"
            "- QLabel (título)\n"
            "- QComboBox (listas desplegables)\n"
            "- QTableWidget (tablas de datos)\n"
            "- QTextEdit (áreas de texto para descripciones)\n"
            "- QPushButton (botones: generar, exportar, descargar)\n\n"
            "Ejemplo de código breve (PyQt5):\n\n"
            "from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QComboBox, QTableWidget\n\n"
            "class ExampleWindow(QMainWindow):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.setWindowTitle('Mi Prototipo')\n"
            "        # Crear widgets (puedes moverlos con Qt Designer)\n"
            "        self.title = QLabel('Título', self)\n"
            "        self.combo = QComboBox(self)\n"
            "        self.table = QTableWidget(self)\n"
            "        self.text = QTextEdit(self)\n"
            "        self.button = QPushButton('Acción', self)\n\n"
            "Sugerencia: Usa Qt Designer para colocar 'title QLabel', 'combo QComboBox', 'table QTableWidget', 'text QTextEdit' y 'button QPushButton'.\n"
        )

# ---------- Run ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppPrototyper()
    window.show()
    sys.exit(app.exec_())