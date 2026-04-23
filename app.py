from flask import Flask

app = Flask(__name__)
app.secret_key = "1234"

from routes.dashboard import dashboard_bp
from routes.gestion import gestion_bp
from routes.entradas import entradas_bp
from routes.movimientos import movimientos_bp
from routes.traslados import traslados_bp
from routes.busqueda import busqueda_bp
from routes.retiros import retiros_bp
from routes.resumenes import resumenes_bp
from routes.reportes import reportes_bp
from routes.login import login_bp


app.register_blueprint(dashboard_bp)
app.register_blueprint(gestion_bp)
app.register_blueprint(entradas_bp)
app.register_blueprint(movimientos_bp)
app.register_blueprint(traslados_bp)
app.register_blueprint(busqueda_bp)
app.register_blueprint(retiros_bp)
app.register_blueprint(resumenes_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(login_bp)

if __name__ == '__main__':
    app.run(debug=True)