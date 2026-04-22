from flask import Flask

app = Flask(__name__)


from routes import dashboard, gestion, entradas, movimientos, traslados, busqueda, api

if __name__ == '__main__':
    app.run(debug=True)