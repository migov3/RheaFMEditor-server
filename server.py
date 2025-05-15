"""
Este módulo es el principal y se encarga de la gestión de peticiones recibidas por el cliente
y su comunicación mediante servicios con la base de datos (para el repositorio).
También contiene las configuraciones de flask, sqlalchemy y jwt.

Contributions:
  - functions: create_tables (Miguel Gómez Vera)
  - endpoints: allowed_languages, getCachedFM, register, login, refresh,
    get_features, get_feature, add_feature, update_feature, download_file,
    delete_feature, verify_feature   (Miguel Gómez Vera)
"""

import datetime
from io import BytesIO
import os
import inspect
import importlib
import json
import tempfile
import subprocess
from typing import Optional

from flask import Flask, jsonify, request, redirect, make_response, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask_caching import Cache
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from flamapy.metamodels.fm_metamodel.models import FeatureModel
from flamapy.metamodels.fm_metamodel.transformations import (
    UVLReader, 
    UVLWriter, 
    FeatureIDEReader, 
    GlencoeReader,
    GlencoeWriter,
    SPLOTWriter
)

from rhea.metamodels.fm_metamodel.transformations import JSONWriter, JSONReader
from rhea.refactorings import utils
from rhea import refactorings
from flask_sqlalchemy import SQLAlchemy
from models import db, bcrypt, Role, Permission, User, Feature_Model
from services import FeatureService

FEATURE_MODEL_SESSION = 'FeatureModel'
UPLOAD_FOLDER = ''
ALLOWED_LANGUAGES = {('UVL (.uvl)', 'uvl'), ('FeatureIDE (.xml)', 'xml'), ('Glencoe (.gfm, .json)', 'gfm.json'), ('SPLOT (.sxfm, .xml)', 'sxfm.xml'), ('Rhea (.json)', '.json')}
ALLOWED_EXTENSIONS = {'uvl', 'xml', 'json'}
EXAMPLE_MODELS_DIR = 'fm_models'

static_url = ''
static_dir = 'template'
static_folder = 'web'

config = {                        # some Flask specific configs
    "CACHE_TYPE": 'SimpleCache',  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///features.db',
    "SQLALCHEMY_TRACK_MODIFICATIONS": True,
    "JWT_SECRET_KEY" : 'MUY_SECRETA',
    "UPLOAD_FOLDER": UPLOAD_FOLDER,
    "JWT_ACCESS_TOKEN_EXPIRES": datetime.timedelta(hours=12),
    "JWT_REFRESH_TOKEN_EXPIRES": datetime.timedelta(days=30)
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

CORS(app, supports_credentials=True)

@app.before_first_request
def create_tables():
    db.create_all()

def get_example_models() -> list[str]:
    models = []
    for root, dirs, files in os.walk(os.path.join(EXAMPLE_MODELS_DIR)):
        for file in files:
            #filepath = os.path.join(root, file)
            models.append(file)
    # Put a specific model first:
    pizza_model = next((m for m in models if m == 'Pizzas with refactorings.json'), None)
    if pizza_model is not None:
        models.remove(pizza_model)
        models.insert(0, pizza_model)
    return models


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_fm_file(filename: str) -> Optional[FeatureModel]:
    """Read a feature model object from a file in the sopported formats."""
    if filename.endswith('.uvl'):
        return UVLReader(filename).transform()
    elif filename.endswith('.sxfm.xml'):
        return None
    elif filename.endswith('.xml') or filename.endswith('.fide'):
        return FeatureIDEReader(filename).transform()
    elif filename.endswith('.gfm.json'):
        return GlencoeReader(filename).transform()
    elif filename.endswith('.json'):
        return JSONReader(filename).transform()
    else:
        return None


def write_fm_file(fm: FeatureModel, format: str) -> str:
    """Write a feature model object to a temporal file and returns its content.
    
    This is required because the current Writter always writes to file, and the front-end needs
    the content directly.
    """
    result = None
    #temporal_filepath = f'FM_{fm.root.name}_temp.{format}'
    if format == 'uvl':
        uvl_writer = UVLWriter(source_model=fm, path=None)
        result = uvl_writer.read_features(fm.root, "features", 0) + "\n" + uvl_writer.read_constraints()
    elif format == 'gfm.json':
        temporal_filepath = tempfile.NamedTemporaryFile(mode='w', encoding='utf8').name
        result = GlencoeWriter(source_model=fm, path=temporal_filepath).transform()
        print(result)
    elif format == 'sxfm.xml':
        temporal_filepath = tempfile.NamedTemporaryFile(mode='w', encoding='utf8').name
        result = SPLOTWriter(source_model=fm, path=temporal_filepath).transform()
    elif format == 'json':
        result = JSONWriter(source_model=fm, path=None).transform()
    return result

@app.route('/allowed-languages', methods=['GET'])
def allowed_languages():
    if request.method != 'GET':
        return None
    else:
        response = make_response(list(ALLOWED_LANGUAGES))
        return response

@app.route('/getExampleFMs', methods=['GET'])
def get_example_feature_models():
    if request.method != 'GET':
        return None
    else:
        models = get_example_models()
        response = make_response(json.dumps(models))
        return response

@app.route('/uploadExampleFM', methods=['POST'])
def upload_example_feature_model():
    if request.method != 'POST':
        return None
    else:
        # Get parameters
        filename = request.form['filename']
        filepath = os.path.join(EXAMPLE_MODELS_DIR, filename)
        fm = read_fm_file(filepath)
        json_fm = JSONWriter(path=None, source_model=fm).transform()
        response = make_response(json_fm)
        hash_fm = hash(fm)
        cache.set(str(hash_fm), fm)
        return response

@app.route('/uploadFM', methods=['POST'])
def upload_feature_model():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
        filepath = secure_filename(filepath)
        file.save(filepath)
        fm = read_fm_file(filepath)
        os.remove(filepath)
        # record the feature model for the session
        json_fm = JSONWriter(path=None, source_model=fm).transform()
        response = make_response(json_fm)
        hash_fm = hash(fm)
        cache.set(str(hash_fm), fm)
        return response
    return None


@app.route('/updateFM', methods=['POST'])
def updateFeature():
    if request.method == 'POST':
        # Get parameters
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename.endswith('.json'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
            filepath = secure_filename(filepath)
            file.save(filepath)
            fm = read_fm_file(filepath)
            os.remove(filepath)
            json_fm = JSONWriter(path=None, source_model=fm).transform()
            response = make_response(json_fm)
            hash_fm = hash(fm)
            cache.set(str(hash_fm), fm)
            return response
    return None


@app.route('/refactor', methods=['POST'])
def refactor():
    if request.method == 'POST':
        # Get parameters
        fm_hash = request.form['fm_hash']
        class_name = request.form['refactoring_id']
        instance_name = None
        if 'instance_name' in request.form:
            instance_name = request.form['instance_name']
        fm = cache.get(fm_hash)
        if fm is None:
            print('FM expired.')
            return None

        modules = inspect.getmembers(refactorings)
        modules = filter(lambda x: inspect.ismodule(x[1]), modules)
        modules = [importlib.import_module(m[1].__name__) for m in modules]
        class_ = next((getattr(m, class_name) for m in modules if hasattr(m, class_name)), None)
        if class_ is None:
            print('Invalid identifier for refactoring.')
            return None
        if instance_name is not None:  # Refactor a specific instance (feature or constraint)
            instance = fm.get_feature_by_name(instance_name)
            if instance is None:
                instance = next((ctc for ctc in fm.get_constraints() if ctc.name == instance_name), None)
            if instance is None:
                print('Invalid feature/constraint identifier.')
                return None
            fm = class_.transform(fm, instance)
        else:  # Refactor all
            fm = utils.apply_refactoring(fm, class_)
        json_fm = JSONWriter(path=None, source_model=fm).transform()
        response = make_response(json_fm)
        fm_hash = hash(fm)
        cache.set(str(fm_hash), fm)
        return response
    return None

@app.route('/getCachedFM', methods=['POST'])
def get_cached_feature_model():
    fm_hash = request.form['fm_hash']
    fm = cache.get(fm_hash)
    if fm is None:
        print('FM expired.')
        return None
    json_fm = JSONWriter(path=None, source_model=fm).transform()
    response = make_response(json_fm)
    return response

@app.route('/downloadFM', methods=['POST'])
def download_feature_model():
    if request.method != 'POST':
        return None
    else:
        # Get parameters
        fm_hash = request.form['fm_hash']
        fm_format = request.form['fm_format']  # 'uvl', 'xml', 'json', 'gfm.json', 'sxfm.xml'
        fm = cache.get(fm_hash)
        if fm is None:
            print('FM expired.')
            return None
        fm_str = write_fm_file(fm, fm_format)
        if fm_str is None:
            return None
        response = make_response(fm_str)
        return response

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data['password'])
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    FeatureService.add_user(data, hashed_password)
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity={'username': user.username, 'role_id': user.role_id})
        refresh_token = create_refresh_token(identity={'username': user.username, 'role_id': user.role_id})
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200

@app.route('/features', methods=['GET'])
def get_features():
    features = FeatureService.get_all_features()
    return jsonify([{'id': f.id, 'name': f.name, 'description': f.description, 'filename': f.filename, 'verified': f.verified, 'doi': f.doi, 'owner': f.owner, 'metrics': f.metrics} for f in features])

@app.route('/features', methods=['POST'])
@jwt_required()
def add_feature():
    current_user = get_jwt_identity()
    user_role = Role.query.filter_by(id=current_user['role_id']).first()
    if 'add_feature' not in [perm.name for perm in user_role.permissions]:
        return jsonify({'message': 'Permission denied'}), 403
    
    name = request.form.get('name')
    description = request.form.get('description')
    doi = request.form.get('doi')
    file = request.files['file']

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "A valid file is required"}), 400
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_data = file.read()

        # Save the file temporarily as it cannot be read() and then saved()
        with open(file_path, 'wb') as f:
            f.write(file_data)

        fm = read_fm_file(file_path)
        os.remove(file_path)

        json_fm = JSONWriter(path=None, source_model=fm).transform()
        metrics = json.loads(json_fm)['semantics_metrics']
        
        new_feature = FeatureService.add_feature(name=name, description=description, doi=doi, file=file_data, filename=filename, owner=current_user['username'], metrics=metrics)
    
        return jsonify(new_feature.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/features/<int:feature_id>', methods=['GET'])
def get_feature(feature_id):
    feature = FeatureService.get_feature_by_id(feature_id)
    if feature:
        return jsonify(feature.to_dict())
    return jsonify({'message': 'Feature not found'}), 404

@app.route('/features/<int:feature_id>', methods=['PUT'])
def update_feature(feature_id):
    data = request.get_json()
    updated_feature = FeatureService.update_feature(feature_id, data['name'], data.get('description', ''))
    if updated_feature:
        return jsonify(updated_feature.to_dict())
    return jsonify({'message': 'Feature not found'}), 404


@app.route('/features/<int:id>/download', methods=['GET'])
def download_file(id):
    feature = FeatureService.get_feature_by_id(id)
    
    if feature is None:
        return jsonify({'message': 'File not found'}), 404

    file_data = feature.file
    file_name = feature.name # Maybe add extension?

    return send_file(
        BytesIO(file_data),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=file_name
    )

@app.route('/features/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_feature(id):
    current_user = get_jwt_identity()
    user_role = Role.query.filter_by(id=current_user['role_id']).first()
    if 'delete_feature' not in [perm.name for perm in user_role.permissions]:
        return jsonify({'message': 'Permission denied'}), 403
    feature = FeatureService.get_feature_by_id(id)
    if feature is None:
        return jsonify({'message': 'File not found'}), 404
    db.session.delete(feature)
    db.session.commit()
    return jsonify({'message': 'Feature deleted'}), 200

@app.route('/features/<int:id>/verify', methods=['PUT'])
@jwt_required()
def verify_feature(id):
    current_user = get_jwt_identity()
    user_role = FeatureService.get_user_role(current_user['role_id'])
    if 'verify_feature' not in [perm.name for perm in user_role.permissions]:
        return jsonify({'message': 'Permission denied'}), 403
    FeatureService.verify_feature(id)
    return jsonify({'message': 'Feature verified'}), 200

if __name__ == '__main__':
    app.run(debug=True)
