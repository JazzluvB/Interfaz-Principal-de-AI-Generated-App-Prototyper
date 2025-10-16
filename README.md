# AI-Generated App Prototyper

**Proyecto personal de Carlos Palacios Betancourt**  
“AI UX/UI prototyping app: Python, PyQt5, and Generative AI for interface design.
Aplicación de escritorio para prototipado de interfaces utilizando Python, PyQt5 y Generative AI, orientada a demostrar UX/UI con inteligencia artificial generativa.

---

## Descripción del Proyecto

Esta aplicación permite generar **prototipos de interfaces de usuario** a partir de descripciones de proyectos, mostrando **dos opciones visuales de UI** y ofreciendo la posibilidad de:

- Seleccionar la interfaz que más se ajuste a la idea.
- Modificar textos de prototipo.
- Cambiar colores (implementación futura con paleta de colores interactiva).
- Exportar prototipos en **PDF y PNG**.

El proyecto demuestra la integración de **UX Thinking** y diseño de interfaces (**UI**) con **inteligencia artificial generativa**, como parte de la especialización **Generative AI for UI/UX Design Specialization**.

> ⚠️ Nota: Para generar imágenes reales con IA, es necesario configurar la variable de entorno `OPENAI_API_KEY` con una clave válida de **GPT-4** o **GPT-3.5**. Actualmente, la aplicación muestra imágenes de fallback si no se dispone de la clave.

---

## Tecnologías Utilizadas

- **Python 3.10+**
- **PyQt5**: Desarrollo de aplicaciones de escritorio con interfaces gráficas interactivas.
- **Pillow (PIL)**: Generación de imágenes de fallback.
- **pdfkit + wkhtmltopdf**: Exportación de prototipos a PDF.
- **OpenAI API**: Integración opcional para generación de interfaces y código mediante IA generativa.
- **UX/UI Thinking**: Diseño centrado en el usuario, múltiples opciones visuales, facilidad de interacción.
- **Git/GitHub**: Control de versiones y portafolio de código abierto.

---

## Funcionalidades Clave

1.  Generación de prototipos visuales:  
   La aplicación produce dos opciones de UI basadas en la descripción del proyecto.

2.  Modificación de textos:  
   Permite personalizar notas o elementos de la interfaz.

3.  Selección de interfaz preferida:  
   Hacer clic sobre la opción deseada para exportación.

4.  Exportación a PDF o PNG:  
   Incluye imagen del prototipo y fragmento de código recomendado en PyQt5.

5.  Diseño futuro con paleta de colores:  
   Botón “Cambiar colores” preparado para integrar una API de paleta de colores.

---

## Especialización y Habilidades Demostradas

- Generative AI for UI/UX Design Specialization**: Aplicación práctica de generación de interfaces con IA.
- UX Thinking: Consideración de la experiencia del usuario en la interacción con prototipos.
- UI Design: Conceptualización y visualización de múltiples alternativas de interfaz.
- Python y PyQt5: Desarrollo completo de aplicaciones de escritorio interactivas.
- Integración de APIs y exportación de contenido**: Preparado para conectarse con OpenAI, pdfkit y futuras APIs de paletas de colores.

---

## Instalación y Configuración

1. Clonar el repositorio:  
   ```bash
   git clone <tu-repo-url>
