from flask import Blueprint, render_template, request, send_file, session, redirect, url_for
from db import conectar
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes', methods=['GET', 'POST'])
def reportes():

    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    if request.method == 'POST':

        fecha = request.form['fecha']

        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT m.tipo, m.fecha, m.detalle, a.nombre
            FROM movimientos m
            JOIN activos_fijos a ON m.id_activo = a.id_activo
            WHERE DATE(m.fecha) = %s
        """, (fecha,))

        data = cursor.fetchall()
        conn.close()

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        y = 750

        pdf.drawString(200, 800, "REPORTE DE MOVIMIENTOS")
        pdf.drawString(50, 780, f"Fecha: {fecha}")

        for row in data:
            texto = f"{row['fecha']} - {row['tipo']} - {row['nombre']} - {row['detalle']}"
            pdf.drawString(50, y, texto)
            y -= 20

            if y < 50:
                pdf.showPage()
                y = 750

        pdf.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="reporte.pdf",
            mimetype='application/pdf'
        )

    return render_template("reportes.html")