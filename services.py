"""
Este módulo sirve como capa intermedia entre el servidor y la base de datos, 
y recoge la lógica a seguir para obtener la información o modificarla, 
de manera que queda localizada en este módulo.

Author: Miguel Gómez Vera
"""

from models import Role, Permission, User, Feature_Model, db

class FeatureService:

    @staticmethod
    def get_all_features():
        return Feature_Model.query.all()

    @staticmethod
    def get_feature_by_id(feature_id):
        return Feature_Model.query.get(feature_id)

    @staticmethod
    def add_feature(name, description, doi, file, filename, owner, metrics):
        new_feature = Feature_Model(name=name, description=description, doi=doi, file=file, filename=filename, owner=owner, metrics=metrics)
        db.session.add(new_feature)
        db.session.commit()
        return new_feature
    
    @staticmethod
    def add_user(data, hashed_password):
        new_user = User(username=data['username'], email=data['email'], password=hashed_password, role_id=2)
        db.session.add(new_user)
        db.session.commit()

    @staticmethod
    def update_feature(feature_id, name, description):
        feature = Feature_Model.query.get(feature_id)
        if feature:
            feature.name = name
            feature.description = description
            db.session.commit()
        return feature
    
    @staticmethod
    def get_user_role(id):
        return Role.query.filter_by(id=id).first()

    @staticmethod
    def verify_feature(feature_id):
        feature = Feature_Model.query.get(feature_id)
        if feature:
            feature.verified = True
            db.session.commit()
        return feature
    
    @staticmethod
    def update_feature_metrics(feature_id, metrics):
        feature = Feature_Model.query.get(feature_id)
        if feature:
            feature.metrics = metrics
            db.session.commit()
        return feature

    @staticmethod
    def delete_feature(feature_id):
        feature = Feature_Model.query.get(feature_id)
        if feature:
            db.session.delete(feature)
            db.session.commit()
        return feature