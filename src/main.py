import os
from functools import wraps
from flask import Flask, request, jsonify, send_file, send_from_directory
import boto3
from dotenv import load_dotenv
from keycloak import KeycloakOpenID
from flask_cors import CORS
import requests

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

CORS(app)

KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET
)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = os.getenv("MINIO_BUCKET")

s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith("Bearer "):
            return jsonify({'message': 'Token is missing or invalid!'}), 401
        try:
            token_data = keycloak_openid.userinfo(token.split(" ")[1]) 
            request.user = token_data['preferred_username']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return send_from_directory("static", "index.html")

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory("static", path)

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    username = auth.get('username')
    password = auth.get('password')

    try:
        token = keycloak_openid.token(username, password)
        return jsonify({'access_token': token['access_token']})
    except Exception as e:
        return jsonify({'message': 'Invalid credentials', 'error': str(e)}), 401
    
@app.route('/register', methods=['POST'])
def register():
    user_data = request.json
    username = user_data.get('username')
    password = user_data.get('password')
    email = user_data.get('email')
    first_name = user_data.get('first_name')  
    last_name = user_data.get('last_name')

    if not username or not password or not email or not first_name or not last_name:
        return jsonify({"message": "Username, password, email, first name, and last name are required"}), 400

    try:
        token_url = f"{KEYCLOAK_SERVER_URL}/realms/master/protocol/openid-connect/token"
        token_data = {
            "client_id": "admin-cli",
            "username": os.getenv("KEYCLOAK_ADMIN_USERNAME"),
            "password": os.getenv("KEYCLOAK_ADMIN_PASSWORD"),
            "grant_type": "password"
        }

        response = requests.post(token_url, data=token_data)
        if response.status_code != 200:
            return jsonify({"message": "Failed to obtain access token", "error": response.text}), 500

        access_token = response.json().get("access_token")

        create_user_url = f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        user_payload = {
            "username": username,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,   
            "enabled": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}],
            "requiredActions": []  
        }

        user_response = requests.post(create_user_url, json=user_payload, headers=headers)

        if user_response.status_code == 201:
            return jsonify({"message": "User registered successfully"}), 201
        else:
            return jsonify({"message": "Failed to create user", "error": user_response.text}), 500

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"message": "Failed to register user", "error": str(e)}), 500



@app.route('/upload', methods=['POST'])
@token_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']
    file_name = file.filename

    try:
        s3_client.upload_fileobj(file, BUCKET_NAME, file_name)
        return jsonify({'message': f'File {file_name} uploaded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files', methods=['GET'])
@token_required
def list_files():
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
@token_required
def get_file(filename):
    try:
        local_file = f"/tmp/{filename}"
        s3_client.download_file(BUCKET_NAME, filename, local_file)
        return send_file(local_file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/modify/<filename>', methods=['PUT'])
@token_required
def modify_file(filename):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']
    try:
        s3_client.upload_fileobj(file, BUCKET_NAME, filename)
        return jsonify({'message': f'File {filename} modified successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rename/<filename>', methods=['POST'])
@token_required
def rename_file(filename):
    data = request.json
    new_name = data.get('new_name')

    if not new_name:
        return jsonify({"message": "New file name not provided"}), 400

    try:
        copy_source = {'Bucket': BUCKET_NAME, 'Key': filename}
        s3_client.copy_object(Bucket=BUCKET_NAME, CopySource=copy_source, Key=new_name)
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        return jsonify({"message": f"File {filename} renamed to {new_name} successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
@token_required
def delete_file(filename):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        return jsonify({"message": f"File {filename} deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_bucket():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' already exists.")
    except Exception:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created.")

if __name__ == '__main__':
    create_bucket()
    app.run(host="0.0.0.0", port=5000, debug=True)
