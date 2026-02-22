from app import admin_app


# Initialize the app
app_admin = admin_app()
app_admin.secret_key = 'SFSPhfl5QTkYb0Ygyb0oCUZ0NRnklJWE-yVNFJ7oGrY='

if __name__ == '__main__':
    
    app_admin.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
