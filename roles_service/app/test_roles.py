from app.database import SessionLocal
from app.models import Role, Permission, RolePermission

def test_roles_and_permissions():
    db = SessionLocal()
    
    try:
        # Verificar roles
        roles = db.query(Role).all()
        print(f"📋 Roles encontrados: {len(roles)}")
        for role in roles:
            print(f"  - {role.name}: {role.description}")
        
        # Verificar permisos
        permissions = db.query(Permission).all()
        print(f"\n🔐 Permisos encontrados: {len(permissions)}")
        for perm in permissions:
            print(f"  - {perm.name}: {perm.description}")
        
        # Verificar asignaciones
        print(f"\n🔗 Asignaciones de permisos por rol:")
        for role in roles:
            role_perms = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
            print(f"\n  {role.name.upper()}:")
            for rp in role_perms:
                perm = db.query(Permission).filter(Permission.id == rp.permission_id).first()
                print(f"    ✓ {perm.name}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_roles_and_permissions()