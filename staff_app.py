from app import staff_app

# Initialize the app
app_staff = staff_app()
app_staff.secret_key = 'StaffSecretKey_7000_VerySecureKey123XYZ='

if __name__ == '__main__':
    
    app_staff.run(
        host='0.0.0.0',
        port=7000,
        debug=True,
    )
