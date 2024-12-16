import os
import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
import boto3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

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

USER_DATA = {
    os.getenv('USER1_USERNAME'): os.getenv('USER1_PASSWORD'),
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token.split(" ")[1], app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user = data['username']
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

    if USER_DATA.get(username) == password:
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

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
    app.run(debug=True, port=5000)
