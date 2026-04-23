from flask import request, session, redirect, url_for
from app import app
from db import conectar

@app.route('/buscar_activo')
def buscar_activo():

    if 'usuario' not in session:
        return {"error": "No autorizado"}

    codigo = request.args.get('codigo')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.codigo, a.nombre,
               ar.nombre_area AS area,
               r.nombre AS responsable
        FROM activos_fijos a
        LEFT JOIN areas ar ON a.id_area = ar.id_area
        LEFT JOIN responsables r ON a.id_responsable = r.id_responsable
        WHERE a.codigo = %s
    """, (codigo,))

    activo = cursor.fetchone()
    conn.close()

    if not activo:
        return {"error": "No encontrado"}

    return activo