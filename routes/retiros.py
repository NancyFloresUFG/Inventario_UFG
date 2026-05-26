from flask import Blueprint, render_template, request, redirect, url_for, session
from db import conectar
from utils.seguridad import requiere_admin

retiros_bp = Blueprint('retiros', __name__)

@retiros_bp.route('/retiros', methods=['GET', 'POST'])
@requiere_admin
def retiros():

    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        codigo = request.form['codigo']
        motivo = request.form['motivo']

        cursor.execute("SELECT * FROM activos_fijos WHERE codigo=%s", (codigo,))
        activo = cursor.fetchone()

        if not activo:
            conn.close()
            return "Activo no encontrado"

        id_activo = activo['id_activo']

        cursor.execute("SELECT nombre FROM responsables WHERE id_responsable=%s", (activo['id_responsable'],))
        responsable_row = cursor.fetchone()
        responsable_nombre = responsable_row['nombre'] if responsable_row else ''

        cursor.execute("""
            UPDATE activos_fijos SET estado='Retirado'
            WHERE id_activo=%s
        """, (id_activo,))

        motivo = motivo.strip()
        detalle = f'Activo retirado del inventario. Responsable al retiro: {responsable_nombre}'
        usuario_sesion = session.get('usuario')
        print(f"DEBUG retiros.py - Usuario en sesión al guardar retiro: '{usuario_sesion}' | id_usuario: {session.get('id_usuario')} | rol: {session.get('rol')}")

        cursor.execute("""
            INSERT INTO movimientos (tipo, id_activo, detalle, motivo, usuario)
            VALUES (%s, %s, %s, %s, %s)
        """, ('Retiro', id_activo, detalle, motivo, usuario_sesion))

        conn.commit()
        conn.close()

        return redirect(url_for('movimientos.movimientos'))

    conn.close()
    return render_template("retiros.html")