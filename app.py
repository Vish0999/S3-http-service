from flask import Flask, jsonify
import boto3
import os   
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Initialize S3 client using environment variables
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

@app.route('/list-bucket-content', defaults={'path': ''}, methods=['GET'])
@app.route('/list-bucket-content/<path:path>', methods=['GET'])
def list_bucket_content(path):
    try:
        # Add trailing slash if not empty path
        prefix = path if path == '' or path.endswith('/') else f"{path}/"
        
        # Fetch objects from S3 bucket
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter='/')

        # Parse folder and file contents
        contents = []

        if 'CommonPrefixes' in response:
            contents.extend([prefix['Prefix'].rstrip('/') for prefix in response['CommonPrefixes']])

        if 'Contents' in response:
            contents.extend([obj['Key'] for obj in response['Contents'] if obj['Key'] != prefix])

        # Remove the prefix path for relative paths
        contents = [item[len(prefix):] for item in contents]

        return jsonify({"content": contents})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)