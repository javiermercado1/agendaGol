from app.database import SessionLocal, init_db
from app.models import Role, Permission, RolePermission

def setup_default_roles_and_permissions():
    init_db()
    db = SessionLocal()
    
    try:
        # Crear roles por defecto
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(
                name="admin",
                description="Administrador con acceso total al sistema",
                is_active=True
            )
            db.add(admin_role)
        
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(
                name="user",
                description="Usuario normal del sistema",
                is_active=True
            )
            db.add(user_role)
        
        db.commit()
        
        # Crear permisos simplificados
        permissions_data = [
            # Permisos de usuario normal
            {"name": "create_reservations", "resource": "reservations", "action": "create", "description": "Crear reservas"},
            {"name": "view_own_reservations", "resource": "reservations", "action": "view", "description": "Ver sus propias reservas"},
            {"name": "edit_own_profile", "resource": "profile", "action": "edit", "description": "Editar su propio perfil"},
            
            # Permisos de administrador
            {"name": "manage_fields", "resource": "fields", "action": "manage", "description": "Gestionar canchas"},
            {"name": "manage_users", "resource": "users", "action": "manage", "description": "Gestionar usuarios"},
            {"name": "create_admin", "resource": "users", "action": "create_admin", "description": "Crear administradores"},
            {"name": "view_all_reservations", "resource": "reservations", "action": "view_all", "description": "Ver todas las reservas"},
        ]
        
        for perm_data in permissions_data:
            permission = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not permission:
                permission = Permission(**perm_data)
                db.add(permission)
        
        db.commit()
        
        # Asignar permisos al rol de usuario
        user_permissions = [
            "create_reservations",
            "view_own_reservations", 
            "edit_own_profile"
        ]
        
        for perm_name in user_permissions:
            permission = db.query(Permission).filter(Permission.name == perm_name).first()
            if permission:
                existing_assignment = db.query(RolePermission).filter(
                    RolePermission.role_id == user_role.id,
                    RolePermission.permission_id == permission.id
                ).first()
                
                if not existing_assignment:
                    role_permission = RolePermission(
                        role_id=user_role.id,
                        permission_id=permission.id
                    )
                    db.add(role_permission)
        
        admin_permissions = [
            "create_reservations",
            "view_own_reservations",
            "edit_own_profile",
            "manage_fields",
            "manage_users",
            "create_admin",
            "view_all_reservations"
        ]
        
        for perm_name in admin_permissions:
            permission = db.query(Permission).filter(Permission.name == perm_name).first()
            if permission:
                existing_assignment = db.query(RolePermission).filter(
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == permission.id
                ).first()
                
                if not existing_assignment:
                    role_permission = RolePermission(
                        role_id=admin_role.id,
                        permission_id=permission.id
                    )
                    db.add(role_permission)
        
        db.commit()
        print("✅ Roles y permisos configurados correctamente")
        
    except Exception as e:
        print(f"❌ Error configurando roles y permisos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_default_roles_and_permissions()
