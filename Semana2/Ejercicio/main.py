# Importar el módulo FastAPI
from fastapi import FastAPI

# Crear la aplicación
# Solo necesitas hacer esto una vez al inicio de tu archivo.
app = FastAPI(title="Mi Primera API")

# Endpoint 1: Hello World (OBLIGATORIO)
@app.get("/")
def hello_world():
    return {"message": "¡Mi primera API FastAPI!"}

# Endpoint 2: Info básica (OBLIGATORIO)
@app.get("/info")
def info():
    return {"api": "FastAPI", "week": 1, "status": "running"}

# Endpoint personalizado
@app.get("/greeting/{name}")
def greet_user(name: str):
    # La imagen muestra que este endpoint funciona
    return {"greeting": f"¡Hola {name}!"}

# Endpoint my-profile
# Asegúrate de que este endpoint tenga el decorador @app.get()
@app.get("/my-profile")
def my_profile():
    # Asegúrate de rellenar tus datos aquí
    return {
        "name": "Tu Nombre Aquí",
        "bootcamp": "FastAPI",
        "week": 1,
        "date": "2025",
        "likes_fastapi": True
    }