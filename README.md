# Documentation for Flask and Keycloak Project

## 1. Setting up and Running the Project

Before running the project, you need to install the required libraries. Follow these steps:

### 1.1 Clone the project:

```bash
git clone <https://github.com/yasenOfficial/VOT2024-2025/tree/dr2> 
cd <VOT2024-2025>
```

### 1.2 Create a virtual environment (optional but recommended):

```bash

python3 -m venv venv
source venv/bin/activate  # For Linux / macOS
venv\Scripts\activate     # For Windows
```
### 1.3 Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Step 2: Configure the .env file
Create a .env file in the root of the project with the following values:

```ini
KEYCLOAK_SERVER_URL=http://<KEYCLOAK_SERVER_URL>
KEYCLOAK_REALM=<REALM_NAME>
KEYCLOAK_CLIENT_ID=<CLIENT_ID>
KEYCLOAK_CLIENT_SECRET=<CLIENT_SECRET>
MINIO_ENDPOINT=<MINIO_ENDPOINT>
MINIO_ACCESS_KEY=<MINIO_ACCESS_KEY>
MINIO_SECRET_KEY=<MINIO_SECRET_KEY>
MINIO_BUCKET=<BUCKET_NAME>
```

## Step 3: Run the server
Once you’ve configured everything, run the project with the following command:

```bash
docker-compose up --build
```

The project will be available at http://127.0.0.1:5000.

## 2. Keycloak Configuration
### Step 1: Create a Realm
Log in to the Keycloak admin panel.
Create a new Realm (if you don’t have one already) via the Realms menu and click Create Realm.
Set a name for the Realm, e.g., myrealm.
### Step 2: Create a Client
In the selected Realm, go to Clients and click Create.
Enter the Client ID, e.g., myclient.
Under the Settings tab:
Set Root URL to your project’s URL (e.g., http://127.0.0.1:5000).
Set Access Type to confidential.
Set Valid Redirect URIs (e.g., http://127.0.0.1:5000/*).
### Step 3: Generate Client Secret
Go back to the Clients section and select your client.
Go to the Credentials tab and generate a Client Secret.
Save the generated secret for use in the .env file.
### Step 4: Create a User
In the Users section, click Add user.
Fill in the necessary information (username, password, etc.).
Ensure the user is activated and assign the necessary roles.

## 3. Configure MinIO

### 3.1 Create Buckets:

After logging into the MinIO console (http://127.0.0.1:9001), click on the Create Bucket button to create a new bucket to store your files.
Enter a unique name for your bucket and click Create.
Setting Bucket Policies:

Select a bucket from the dashboard.
You can set access policies (e.g., public or private) depending on your use case by selecting the Policies option.

### 3.2 Create New Access Keys:

On the left sidebar of the MinIO Console, click on the Access Keys option (this will show you a list of existing keys).
Click on the Create New Key button.
Enter the Access Key and Secret Key that you want to generate. These should be secure and unique.

## 4. Sample API Requests

### 1. Login
```bash
curl -X POST http://127.0.0.1:5000/login \
    -H "Content-Type: application/json" \
    -d '{"username": "your_username", "password": "your_password"}'
```
Response:

```json
{
    "token": "<JWT_token>"
}
```

### 2. File Upload

```bash
curl -X POST http://127.0.0.1:5000/upload \
    -H "Authorization: Bearer <JWT_token>" \
    -F "file=@<path_to_file>"
```

Response:

```json
{
    "message": "File uploaded successfully"
}
```

### 3. File Download

```bash
curl -X GET http://127.0.0.1:5000/download/<filename> \
    -H "Authorization: Bearer <JWT_token>" \
    --output <filename>
```
The file will be downloaded to the local machine as <filename>.

### 4. List Files

```bash
curl -X GET http://127.0.0.1:5000/files \
    -H "Authorization: Bearer <JWT_token>"
```
Response:

```json
{
    "files": ["file1.txt", "file2.jpg", "document.pdf"]
}
```

### 5. Modify File
```bash
curl -X PUT http://127.0.0.1:5000/modify/<filename> \
    -H "Authorization: Bearer <JWT_token>" \
    -F "file=@<path_to_new_file>"
```
Response:

```json
{
    "message": "File modified successfully"
}
```

### 6. Delete File


```bash
curl -X DELETE http://127.0.0.1:5000/delete/<filename> \
    -H "Authorization: Bearer <JWT_token>"
```
Response:

```json
{
    "message": "File deleted successfully"
}
```

### 7. Rename File

```bash
curl -X POST http://127.0.0.1:5000/rename/<filename> \
    -H "Authorization: Bearer <JWT_token>" \
    -H "Content-Type: application/json" \
    -d '{"new_name": "new_filename"}'
```

Response:

```json
{
    "message": "File renamed successfully"
}
```
