from flask import Blueprint, render_template, session, redirect, url_for
from db import conectar

resumenes_bp = Blueprint('resumenes', __name__)

@resumenes_bp.route('/resumenes')
def resumenes():

    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM activos_fijos")
    total = cursor.fetchone()['total']

    cursor.execute("""
        SELECT estado, COUNT(*) AS cantidad
        FROM activos_fijos
        GROUP BY estado
    """)
    estados = cursor.fetchall()

    cursor.execute("""
        SELECT t.nombre_tipo, COUNT(*) AS cantidad
        FROM activos_fijos a
        JOIN tipos_activo t ON a.id_tipo = t.id_tipo
        GROUP BY t.nombre_tipo
    """)
    tipos = cursor.fetchall()

    cursor.execute("SELECT SUM(valor) AS total_valor FROM activos_fijos")
    total_valor = cursor.fetchone()['total_valor'] or 0

    cursor.execute("SELECT SUM(depreciacion) AS total_dep FROM activos_fijos")
    total_dep = cursor.fetchone()['total_dep'] or 0

    conn.close()

    return render_template("resumenes.html",
                           total=total,
                           estados=estados,
                           tipos=tipos,
                           total_valor=total_valor,
                           total_dep=total_dep)