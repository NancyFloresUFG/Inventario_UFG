from flask import Blueprint, render_template, session, redirect, url_for
from db import conectar

gestion_bp = Blueprint('gestion', __name__)

@gestion_bp.route('/gestion')
def gestion():

    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            a.*, 
            ar.nombre_area,
            r.nombre AS responsable,
            t.nombre_tipo,
            u.nombre_uso
        FROM activos_fijos a
        LEFT JOIN areas ar ON a.id_area = ar.id_area
        LEFT JOIN responsables r ON a.id_responsable = r.id_responsable
        LEFT JOIN tipos_activo t ON a.id_tipo = t.id_tipo
        LEFT JOIN usos_activo u ON a.id_uso = u.id_uso
    """)

    activos = cursor.fetchall()
    conn.close()

    return render_template("gestion.html", activos=activos)