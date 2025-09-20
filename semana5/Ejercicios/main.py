# Importar las nuevas funciones y schemas
from . import auth

# Endpoint para crear primer admin (solo si no existe ningún admin)
@app.post("/create-admin", response_model=UserResponse)
def create_first_admin(user_data: UserRegister, db: Session = Depends(get_db)):
    """Crear primer usuario administrador"""

    # Verificar si ya existe un admin
    existing_admin = db.query(User).filter(User.role == "admin").first()

    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un administrador en el sistema"
        )

    # Verificar si username ya existe
    if auth.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=400,
            detail="Username ya está registrado"
        )

    # Crear admin
    admin_user = auth.create_admin_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    return UserResponse(
        id=admin_user.id,
        username=admin_user.username,
        email=admin_user.email,
        is_active=admin_user.is_active,
        role=admin_user.role
    )

# Endpoint solo para admins: ver todos los usuarios
@app.get("/admin/users", response_model=List[UserResponse])
def list_all_users(
    admin_user: User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Listar todos los usuarios (solo admin)"""

    users = auth.get_all_users(db)

    return [UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role
    ) for user in users]

# Endpoint solo para admins: cambiar role de usuario
@app.put("/admin/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    admin_user: User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Actualizar role de un usuario (solo admin)"""

    # No permitir que el admin se cambie su propio rol
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=400,
            detail="No puedes cambiar tu propio rol"
        )

    # Actualizar role
    updated_user = auth.update_user_role(db, user_id, role_data.role)

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        is_active=updated_user.is_active,
        role=updated_user.role
    )

# Actualizar endpoint de registro para incluir role en respuesta
@app.post("/register", response_model=UserResponse)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""

    if auth.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=400,
            detail="Username ya está registrado"
        )

    user = auth.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role  # NUEVO: incluir role
    )

@app.post("/posts")
def create_post(
    post: Post,
    current_user = Depends(get_current_user)  # Requiere login
):
    new_post = {
        "id": len(posts) + 1,
        "title": post.title,
        "content": post.content,
        "author": current_user.username
    }
    posts.append(new_post)
    return new_post