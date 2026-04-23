from flask import Blueprint, render_template, request, redirect, url_for, session
from db import conectar

traslados_bp = Blueprint('traslados', __name__)

@traslados_bp.route('/traslados', methods=['GET', 'POST'])
def traslados():

    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM areas WHERE estado=1")
    areas = cursor.fetchall()

    cursor.execute("SELECT * FROM responsables WHERE estado=1")
    responsables = cursor.fetchall()

    if request.method == 'POST':
        codigo = request.form['codigo']

        cursor.execute("SELECT * FROM activos_fijos WHERE codigo=%s", (codigo,))
        activo = cursor.fetchone()

        if not activo:
            conn.close()
            return "❌ Activo no encontrado"

        id_activo = activo['id_activo']

        nueva_area = request.form.get('id_area')
        nuevo_responsable = request.form.get('id_responsable')

        detalle = ""

        if nueva_area:
            cursor.execute(
                "UPDATE activos_fijos SET id_area=%s WHERE id_activo=%s",
                (nueva_area, id_activo)
            )
            detalle += "Cambio de área. "

        if nuevo_responsable:
            cursor.execute(
                "UPDATE activos_fijos SET id_responsable=%s WHERE id_activo=%s",
                (nuevo_responsable, id_activo)
            )
            detalle += "Cambio de responsable."

        if detalle == "":
            conn.close()
            return "⚠️ No hiciste cambios"

        cursor.execute("""
            INSERT INTO movimientos (tipo, id_activo, detalle)
            VALUES ('Traslado', %s, %s)
        """, (id_activo, detalle))

        conn.commit()
        conn.close()

        return redirect(url_for('movimientos.movimientos'))

    conn.close()
    return render_template("traslados.html",
                           areas=areas,
                           responsables=responsables)