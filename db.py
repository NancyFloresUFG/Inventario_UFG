import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",          
        password="toor",      
        database="inventario_ufg" 
    )