from flask import Flask, render_template, request, redirect, url_for
from db import conectar

app = Flask(__name__)

# DASHBOARD
@app.route('/')
def dashboard():
    return render_template("dashboard.html")


# GESTIÓN 
@app.route('/gestion')
def gestion():
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

# EDITAR ACTIVO 
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM areas WHERE estado=1")
    areas = cursor.fetchall()
    cursor.execute("SELECT * FROM responsables WHERE estado=1")
    responsables = cursor.fetchall()
    cursor.execute("SELECT * FROM tipos_activo")
    tipos = cursor.fetchall()
    cursor.execute("SELECT * FROM usos_activo")
    usos = cursor.fetchall()

    if request.method == 'POST':
        cursor.execute("""
            UPDATE activos_fijos SET
                nombre=%s,
                descripcion=%s,
                marca=%s,
                modelo=%s,
                serie=%s,
                valor=%s,
                estado=%s,
                id_area=%s,
                id_responsable=%s,
                id_tipo=%s,
                id_uso=%s
            WHERE id_activo=%s
        """, (
            request.form['nombre'],
            request.form['descripcion'],
            request.form['marca'],
            request.form['modelo'],
            request.form['serie'],
            request.form['valor'],
            request.form['estado'],
            request.form['id_area'],
            request.form['id_responsable'],
            request.form['id_tipo'],
            request.form['id_uso'],
            id
        ))

        conn.commit()
        conn.close()
        return redirect(url_for('gestion'))
    cursor.execute("SELECT * FROM activos_fijos WHERE id_activo=%s", (id,))
    activo = cursor.fetchone()

    conn.close()

    return render_template("editar.html",
                           activo=activo,
                           areas=areas,
                           responsables=responsables,
                           tipos=tipos,
                           usos=usos)


# ENTRADAS 
@app.route('/entradas', methods=['GET', 'POST'])
def entradas():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM areas WHERE estado=1")
    areas = cursor.fetchall()
    cursor.execute("SELECT * FROM responsables WHERE estado=1")
    responsables = cursor.fetchall()
    cursor.execute("SELECT * FROM tipos_activo")
    tipos = cursor.fetchall()
    cursor.execute("SELECT * FROM usos_activo")
    usos = cursor.fetchall()

    if request.method == 'POST':
        cursor.execute(
            "SELECT depreciacion FROM tipos_activo WHERE id_tipo = %s",
            (request.form['id_tipo'],)
        )
        depreciacion = cursor.fetchone()['depreciacion']

        cursor.execute("""
            INSERT INTO activos_fijos 
            (codigo, nombre, descripcion, marca, modelo, serie, valor, depreciacion, fecha_ingreso, estado, id_area, id_responsable, id_tipo, id_uso)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form['codigo'],
            request.form['nombre'],
            request.form['descripcion'],
            request.form['marca'],
            request.form['modelo'],
            request.form['serie'],
            request.form['valor'],
            depreciacion,
            request.form['fecha_ingreso'],
            request.form['estado'],
            request.form['id_area'],
            request.form['id_responsable'],
            request.form['id_tipo'],
            request.form['id_uso']
        ))
        cursor.execute("""
            INSERT INTO movimientos (tipo, id_activo, detalle)
            VALUES ('Entrada', LAST_INSERT_ID(), 'Ingreso de activo')
        """)

        conn.commit()
        conn.close()

        return redirect(url_for('gestion'))

    conn.close()
    return render_template("entradas.html",
                           areas=areas,
                           responsables=responsables,
                           tipos=tipos,
                           usos=usos)


# MOVIMIENTOS 
@app.route('/movimientos', methods=['GET', 'POST'])
def movimientos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    tipo = request.form.get('tipo')
    fecha = request.form.get('fecha')

    query = """
        SELECT 
            m.id_movimiento,
            m.tipo,
            m.fecha,
            m.detalle,
            a.nombre AS activo
        FROM movimientos m
        JOIN activos_fijos a ON m.id_activo = a.id_activo
        WHERE 1=1
    """

    valores = []

    if tipo and tipo != "Todos":
        query += " AND m.tipo = %s"
        valores.append(tipo)

    if fecha:
        query += " AND DATE(m.fecha) = %s"
        valores.append(fecha)

    query += " ORDER BY m.fecha DESC"

    cursor.execute(query, tuple(valores))
    movimientos = cursor.fetchall()

    conn.close()
    return render_template("movimientos.html", movimientos=movimientos)


# TRASLADOS
@app.route('/traslados', methods=['GET', 'POST'])
def traslados():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM areas WHERE estado=1")
    areas = cursor.fetchall()

    cursor.execute("SELECT * FROM responsables WHERE estado=1")
    responsables = cursor.fetchall()

    if request.method == 'POST':

        codigo = request.form.get('codigo')

        if not codigo:
            conn.close()
            return "❌ Debes buscar un activo primero"

        cursor.execute("""
            SELECT * FROM activos_fijos WHERE codigo = %s
        """, (codigo,))
        activo = cursor.fetchone()

        if not activo:
            conn.close()
            return "❌ Activo no encontrado"

        id_activo = activo['id_activo']
        nueva_area = request.form.get('id_area')
        nuevo_responsable = request.form.get('id_responsable')

        detalle = ""

        if nueva_area:
            cursor.execute("SELECT nombre_area FROM areas WHERE id_area=%s", (nueva_area,))
            nombre_area = cursor.fetchone()['nombre_area']

            cursor.execute("""
                UPDATE activos_fijos SET id_area=%s WHERE id_activo=%s
            """, (nueva_area, id_activo))

            detalle += f"Área cambiada a {nombre_area}. "

        if nuevo_responsable:
            cursor.execute("SELECT nombre FROM responsables WHERE id_responsable=%s", (nuevo_responsable,))
            nombre_resp = cursor.fetchone()['nombre']

            cursor.execute("""
                UPDATE activos_fijos SET id_responsable=%s WHERE id_activo=%s
            """, (nuevo_responsable, id_activo))

            detalle += f"Responsable cambiado a {nombre_resp}. "

        if detalle == "":
            conn.close()
            return "⚠️ No hiciste ningún cambio"

        cursor.execute("""
            INSERT INTO movimientos (tipo, id_activo, detalle)
            VALUES ('Traslado', %s, %s)
        """, (id_activo, detalle))

        conn.commit()
        conn.close()

        return redirect(url_for('movimientos'))

    conn.close()
    return render_template("traslados.html",
                           areas=areas,
                           responsables=responsables)


# API BUSCAR ACTIVO 
@app.route('/buscar_activo')
def buscar_activo():
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


# BÚSQUEDA 
@app.route('/busqueda', methods=['GET', 'POST'])
def busqueda():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    resultados = []

    if request.method == 'POST':
        dato = request.form['busqueda']

        cursor.execute("""
            SELECT 
                a.codigo,
                a.nombre,
                a.estado,
                ar.nombre_area,
                r.nombre AS responsable
            FROM activos_fijos a
            LEFT JOIN areas ar ON a.id_area = ar.id_area
            LEFT JOIN responsables r ON a.id_responsable = r.id_responsable
            WHERE a.codigo LIKE %s OR a.nombre LIKE %s
        """, (f"%{dato}%", f"%{dato}%"))

        resultados = cursor.fetchall()

    conn.close()
    return render_template("busqueda.html", resultados=resultados)


# RUN 
if __name__ == '__main__':
    app.run(debug=True)