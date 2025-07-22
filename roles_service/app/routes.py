from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas, database
from app.auth_client import validate_admin_token, validate_user_token, get_user_id_from_token

roles_router = APIRouter()

@roles_router.post("/validate-permission", response_model=schemas.PermissionValidationResponse)
def validate_user_permission(
    validation_request: schemas.PermissionValidationRequest,
    authorization: str = Header(...),
    db: Session = Depends(database.get_db)
):

    # Validar token (puede ser cualquier usuario autenticado)
    validate_user_token(authorization.replace("Bearer ", ""))
    
    user_id = validation_request.user_id
    resource = validation_request.resource
    action = validation_request.action
    
    # Obtener el rol del usuario
    user_role = db.query(models.UserRole).filter(
        models.UserRole.user_id == user_id,
        models.UserRole.is_active == True
    ).first()
    
    if not user_role:
        return schemas.PermissionValidationResponse(
            has_permission=False,
            user_id=user_id,
            resource=resource,
            action=action,
            role_name=None
        )
    
    # Si es administrador, tiene todos los permisos
    if user_role.role.name == "admin":
        has_permission = True
    else:
        # Buscar el permiso específico para usuarios normales
        permission = db.query(models.Permission).join(
            models.RolePermission, models.Permission.id == models.RolePermission.permission_id
        ).filter(
            models.RolePermission.role_id == user_role.role_id,
            models.Permission.resource == resource,
            models.Permission.action == action,
            models.Permission.is_active == True
        ).first()
        
        has_permission = permission is not None
    
    return schemas.PermissionValidationResponse(
        has_permission=has_permission,
        user_id=user_id,
        resource=resource,
        action=action,
        role_name=user_role.role.name
    )

# ============================================================================
# ROLES ENDPOINTS
# ============================================================================

@roles_router.get("/roles", response_model=List[schemas.RoleResponse])
def get_all_roles(
    authorization: str = Header(...),
    db: Session = Depends(database.get_db)
):
    """Obtener todos los roles (solo administradores)"""
    # Validar que sea administrador
    validate_admin_token(authorization.replace("Bearer ", ""))
    
    roles = db.query(models.Role).filter(models.Role.is_active == True).all()
    return roles

@roles_router.post("/roles", response_model=schemas.RoleResponse)
def create_role(
    role: schemas.RoleCreate,
    authorization: str = Header(...),
    db: Session = Depends(database.get_db)
):
    """Crear un nuevo rol (solo administradores)"""
    # Validar que sea administrador
    validate_admin_token(authorization.replace("Bearer ", ""))
    
    # Verificar que el rol no existe
    existing_role = db.query(models.Role).filter(models.Role.name == role.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    # Crear el rol
    db_role = models.Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# ============================================================================
# PERMISSIONS ENDPOINTS
# ============================================================================

@roles_router.get("/permissions", response_model=List[schemas.PermissionResponse])
def get_all_permissions(
    resource: Optional[str] = None,
    authorization: str = Header(...),
    db: Session = Depends(database.get_db)
):
    """Obtener todos los permisos, opcionalmente filtrados por recurso"""
    # Validar token
    validate_user_token(authorization.replace("Bearer ", ""))
    
    query = db.query(models.Permission).filter(models.Permission.is_active == True)
    
    if resource:
        query = query.filter(models.Permission.resource == resource)
    
    permissions = query.all()
    return permissions

@roles_router.post("/permissions", response_model=schemas.PermissionResponse)
def create_permission(
    permission: schemas.PermissionCreate,
    authorization: str = Header(...),
    db: Session = Depends(database.get_db)
):
    """Crear un nuevo permiso (solo administradores)"""
    # Validar que sea administrador
    validate_admin_token(authorization.replace("Bearer ", ""))
    
    # Verificar que el permiso no existe
    existing_permission = db.query(models.Permission).filter(
        models.Permission.name == permission.name
    ).first()
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    # Crear el permiso
    db_permission = models.Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

# ============================================================================
# USER ROLES ENDPOINTS
# ============================================================================

@roles_router.post("/users/{user_id}/assign-role", response_model=schemas.UserRoleResponse)
def assign_role_to_user(
    user_id: int,
    role_assignment: schemas.UserRoleCreate,
    authorization: str = Header(...),
    db: Session = Depends(database.get_db)
):
    """Asignar un rol a un usuario (solo administradores)"""
    # Validar que sea administrador
    admin_data = validate_admin_token(authorization.replace("Bearer ", ""))
    
    # Verificar que el rol existe
    role = db.query(models.Role).filter(models.Role.id == role_assignment.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Verificar si el usuario ya tiene un rol asignado
    existing_assignment = db.query(models.UserRole).filter(
        models.UserRole.user_id == user_id,
        models.UserRole.is_active == True
    ).first()
    
    if existing_assignment:
        # Desactivar el rol anterior
        existing_assignment.is_active = False
    
    # Crear nueva asignación
    new_assignment = models.UserRole(
        user_id=user_id,
        role_id=role_assignment.role_id,
        assigned_by=admin_data.get("id")
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

@roles_router.get("/users/{user_id}/permissions", response_model=schemas.UserPermissionsResponse)
def get_user_permissions(
    user_id: int,
    authorization: str = Header(...),
    db: Session = Depends(database.get_db)
):
    """Obtener todos los permisos de un usuario"""
    # Validar token
    validate_user_token(authorization.replace("Bearer ", ""))
    
    # Obtener el rol del usuario
    user_role = db.query(models.UserRole).filter(
        models.UserRole.user_id == user_id,
        models.UserRole.is_active == True
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=404, detail="User has no role assigned")
    
    # Obtener permisos del rol
    permissions = db.query(models.Permission).join(
        models.RolePermission, models.Permission.id == models.RolePermission.permission_id
    ).filter(
        models.RolePermission.role_id == user_role.role_id,
        models.Permission.is_active == True
    ).all()
    
    return {
        "user_id": user_id,
        "role": user_role.role,
        "permissions": permissions
    }

# ============================================================================
# ROLE PERMISSIONS ENDPOINTS
# ============================================================================

@roles_router.post("/roles/{role_id}/permissions", response_model=schemas.RolePermissionResponse)
def assign_permission_to_role(
    role_id: int,
    permission_assignment: schemas.RolePermissionCreate,
    authorization: str = Header(...),
    db: Session = Depends(database.get_db)
):

    admin_data = validate_admin_token(authorization.replace("Bearer ", ""))
    
    # Verificar que el rol y permiso existen
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permission = db.query(models.Permission).filter(
        models.Permission.id == permission_assignment.permission_id
    ).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Verificar que no esté ya asignado
    existing_assignment = db.query(models.RolePermission).filter(
        models.RolePermission.role_id == role_id,
        models.RolePermission.permission_id == permission_assignment.permission_id
    ).first()
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Permission already assigned to role")
    
    # Crear asignación
    role_permission = models.RolePermission(
        role_id=role_id,
        permission_id=permission_assignment.permission_id,
        granted_by=admin_data.get("id")
    )
    db.add(role_permission)
    db.commit()
    db.refresh(role_permission)
    return role_permission