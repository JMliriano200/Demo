# Demo

Este repositorio será usado para pruebas con Codex.

## Aplicación web

Un pequeño ejemplo con Flask permite generar un informe simple para un estudiante.

### Uso

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta la aplicación:
   ```bash
   python app.py
   ```
3. Abre `http://127.0.0.1:5000` en el navegador, completa el formulario y genera el informe.

El informe se basa en `templates/student_report_template.md` y se renderiza como HTML.
