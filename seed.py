"""
Este módulo se encarga de rellenar la base de datos con unos datos iniciales.
Se insertan los roles (admin y usuario), permisos (añadir, borrar, verificar)
y se crea el usuario administrador.

Author: Miguel Gómez Vera
"""

from server import app, db, bcrypt
from models import Role, Permission, User

with app.app_context():
    db.create_all()

    # Create roles
    admin_role = Role(name='admin')
    user_role = Role(name='user')

    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.commit()

    # Create permissions
    add_feature_perm = Permission(name='add_feature')
    delete_feature_perm = Permission(name='delete_feature')
    verify_feature_perm = Permission(name='verify_feature')

    # Assign permissions to roles
    admin_role.permissions.extend([add_feature_perm, delete_feature_perm, verify_feature_perm])
    user_role.permissions.append(add_feature_perm)

# Create admin user
    admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin_user = User(username='admin', email='admin@test.com', password=admin_password, role_id=admin_role.id)

    # Add to session and commit
    
    db.session.add(add_feature_perm)
    db.session.add(delete_feature_perm)
    db.session.add(verify_feature_perm)
    db.session.add(admin_user)
    db.session.commit()
