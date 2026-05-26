from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import conectar

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_usuario, usuario, password, rol 
            FROM usuarios 
            WHERE usuario = %s
        """, (usuario,))

        usuario_db = cursor.fetchone()
        conn.close()

        if usuario_db and usuario_db['password'] == password:
            session['usuario'] = usuario_db['usuario']
            session['rol'] = usuario_db['rol']
            return redirect(url_for('dashboard.dashboard'))

        flash("Usuario o contraseña incorrectos")
        return redirect(url_for('login.login'))

    return render_template("login.html")


@login_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente")
    return redirect(url_for('login.login'))