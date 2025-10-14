from datetime import datetime
from src.models import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships to users_has_roles
    users = db.relationship('UserHasRoles', back_populates='role', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()
    
    @classmethod
    def create_role(cls, name, description=None):
        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.commit()
        return role
    
    @classmethod
    def delete_role(cls, role_id):
        role = cls.query.get(role_id)
        if role:
            db.session.delete(role)
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def get_all_roles():
        return Role.query.all()
    
class UserHasRoles(db.Model):
    __tablename__ = 'user_has_roles'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='roles')
    role = db.relationship('Role', back_populates='users')
    
    def __repr__(self):
        return f'<UserHasRoles UserID: {self.user_id} RoleID: {self.role_id}>'
    
    @classmethod
    def assign_role(cls, user_id, role_id):
        assignment = cls(user_id=user_id, role_id=role_id)
        db.session.add(assignment)
        db.session.commit()
        return assignment
    
    @classmethod
    def remove_role(cls, user_id, role_id):
        assignment = cls.query.filter_by(user_id=user_id, role_id=role_id).first()
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_roles_for_user(user_id):
        return UserHasRoles.query.filter_by(user_id=user_id).all()
    
