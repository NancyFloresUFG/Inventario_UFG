from functools import wraps
from flask import session, flash, redirect, url_for

def requiere_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'admin':
            flash("Acceso denegado: Solo usuarios con permisos de admin pueden realizar esta acción.", "error")
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
