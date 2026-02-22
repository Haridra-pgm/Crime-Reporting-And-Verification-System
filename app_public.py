from app import user_app 
import os

# Initialize the app
app = user_app()

# Configuration
app.secret_key = 'SFSPhfl5QTkYb0Ygyb0oCUZ0NRnklJWE-yVNFJ7oGrY='
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# File upload folders
idProof_UPLOAD_FOLDER = os.path.join('app', 'crime_image', 'idProof')
evidence_UPLOAD_FOLDER = os.path.join('app', 'crime_image', 'evidence')
app.config['idProof_UPLOAD_FOLDER'] = idProof_UPLOAD_FOLDER
app.config['evidence_UPLOAD_FOLDER'] = evidence_UPLOAD_FOLDER

if __name__ == '__main__':
    # Run the app with SSL (HTTPS)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
    )


