# auth.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Configuración de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT (en producción usar variables de entorno)
SECRET_KEY = "mi-clave-super-secreta-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Convertir password a hash seguro"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar si password coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(username: str) -> str:
    """Crear JWT token para un usuario"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": username,  # subject = usuario
        "exp": expire     # expiration = cuándo expira
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str:
    """Verificar token y obtener username"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
    
    # Agregar al archivo auth.py existente
from sqlalchemy.orm import Session
from .models import User

def create_user(db: Session, username: str, email: str, password: str, role: str = "user"):
    """Crear usuario con password hasheado y role"""
    hashed_password = get_password_hash(password)

    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role  # NUEVO: asignar role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    """Obtener usuario por username"""
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Verificar usuario y password"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Agregar al archivo auth.py existente
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

security = HTTPBearer()

def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    """Obtener usuario actual desde JWT token"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodificar token
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Obtener usuario de la base de datos
    user = get_user_by_username(db, username=username)

    if user is None:
        raise credentials_exception

    return user

def require_admin(current_user: User = Depends(get_current_user)):
    """Dependencia que requiere rol de admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol de administrador"
        )
    return current_user

def get_all_users(db: Session):
    """Obtener todos los usuarios (solo admin)"""
    return db.query(User).all()

def update_user_role(db: Session, user_id: int, new_role: str):
    """Actualizar role de un usuario (solo admin)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

def create_admin_user(db: Session, username: str, email: str, password: str):
    """Crear usuario administrador"""
    return create_user(db, username, email, password, role="admin")


# Verificar en auth.py
SECRET_KEY = "tu-clave-secreta-muy-larga-aqui"  # Debe ser la misma siempre
ALGORITHM = "HS256"

# Verificar que el token se decodifica correctamente
def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG: Token decodificado: {payload}")  # Para debugging
        username: str = payload.get("sub")
        # resto del código...
    except JWTError as e:
        print(f"DEBUG: Error JWT: {e}")  # Para debugging
        raise credentials_exception