from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.service import crime_service
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import base64

def register_user_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")
    @app.route("/home")
    def home_redirect():
        return redirect(url_for('home'))
    @app.route("/about")
    def about():
        return render_template("about.html")
    
    @app.route("/login")
    def login():
        return render_template("login.html")
    
    @app.route("/signup")
    def signup():
        return render_template("signup.html")
    
    @app.route('/userdashboard')
    def user_dashboard():
        email = session.get('email')
        return render_template("user_dashboard.html", email=email)
    
    @app.route('/registration')
    def registration():
        email = session.get('email')
        userdata = crime_service.getallinputbyEmail(email)
        return render_template("registration.html", fullname=userdata[1], emailid=userdata[2], phoneNo=userdata[4])
    
    @app.route('/staffdashboard')
    def staff_dashboard():
        email = session.get('email')
        return render_template("staff_dashboard.html", email=email)
    
    @app.route('/emergency')
    def emergency():
        return render_template("emergency.html")
    
    @app.route('/complaint_tracking')
    def complaint_tracking():
        email = session.get('email')
        if not email:
            return redirect(url_for('login'))

        complaint_tracking_data = crime_service.get_complaint_tracking_data(email)  # returns list of dicts
        # Format datetime objects to strings (optional but avoids Jinja datetime issues)
       
        for item in complaint_tracking_data:
            dt = item.get('crimeDate')
            if isinstance(dt, datetime):
                item['crimeDate'] = dt.strftime('%Y-%m-%d %H:%M')
       
        
        return render_template('complaint_tracking.html', complaints=complaint_tracking_data)
    
    @app.route('/complaintDetails/<int:complaint_id>')
    def complaint_details(complaint_id):
        email = session.get('email')
        # You can fetch complaint details using the complaint_id here
        complaint = crime_service.get_complaint_details(complaint_id,email)
        # `complaint` is expected to be a dict (or None). Handle accordingly.
        if not complaint:
            flash('Complaint not found or you do not have access.', 'error')
            return redirect(url_for('complaint_tracking'))

        print(complaint)
        # Use dict key for evidence path (repository returns a dict)
        evidence_path = complaint.get('evidence_path') or complaint.get('evidence') or complaint.get('evidencePath')
        print('evidence_path:', evidence_path)
        idProof_path = complaint.get('idProof_path') or complaint.get('idProof') or complaint.get('idProofPath')
        print('idProof_path:', idProof_path)

        # Format the crimeDate if present and a datetime
        dt = complaint.get('crimeDate')
        if isinstance(dt, datetime):
            complaint['crimeDate'] = dt.strftime('%Y-%m-%d %H:%M')

        evidence_img = None
        if evidence_path and os.path.exists(evidence_path):
            try:
                with open(evidence_path, 'rb') as f:
                    evidence_img = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"[WARNING] Could not read evidence file: {e}")
                evidence_img = None
        else:
            print("[INFO] No evidence file found or path does not exist")

        idProof_img = None
        if idProof_path and os.path.exists(idProof_path):
            try:
                with open(idProof_path, 'rb') as f:
                    idProof_img = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"[WARNING] Could not read ID Proof file: {e}")
                idProof_img = None

        return render_template("complaint_details.html", complaint=complaint, evidence_img=evidence_img, idProof_img=idProof_img)

    @app.route('/api/complaintDetails/<int:complaint_id>')
    def api_complaint_details(complaint_id):
        from flask import jsonify
        email = session.get('email')
        complaint = crime_service.get_complaint_details(complaint_id, email)
        
        if not complaint:
            return jsonify({"error": "Complaint not found or you do not have access."}), 404

        # Format crimeDate
        dt = complaint.get('crimeDate')
        if isinstance(dt, datetime):
            complaint['crimeDate'] = dt.strftime('%Y-%m-%d %H:%M')

        # Encode images
        evidence_path = complaint.get('evidence_path') or complaint.get('evidence') or complaint.get('evidencePath')
        evidence_img = None
        if evidence_path and os.path.exists(evidence_path):
            try:
                with open(evidence_path, 'rb') as f:
                    evidence_img = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"[WARNING] Could not read evidence file: {e}")

        idProof_path = complaint.get('idProof_path') or complaint.get('idProof') or complaint.get('idProofPath')
        idProof_img = None
        if idProof_path and os.path.exists(idProof_path):
            try:
                with open(idProof_path, 'rb') as f:
                    idProof_img = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"[WARNING] Could not read ID Proof file: {e}")

        return jsonify({
            "complaint": complaint,
            "evidence_img": evidence_img,
            "idProof_img": idProof_img
        })

    @app.route('/complainthistory')
    def complainthistory():
        email = session.get('email')
        complaints = crime_service.get_complaints_history_by_email(email) if email else []
        return render_template("complaint_history.html", email=email, complaints=complaints)

    @app.route('/test')
    def test():
        return render_template("test.html")
    
    @app.route('/submit', methods=['POST'])
    def submit_form():
        # Placeholder for actual form processing logic
        success = False
        if success:
            flash("Form submitted successfully!", "success")
            return redirect(url_for('test'))
        else:
            flash("There was an error submitting the form.", "danger")
            return redirect(url_for('test'))  
    
    @app.route("/registerUser", methods=["POST"])
    def register_user():
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        if None not in [fullname, email, phonenumber, dob, gender, password, confirm_password]:
            is_registered = crime_service.register_user(fullname, email, phonenumber, dob, gender, password, confirm_password)
        
            if is_registered:
                flash("Registration successful. Please log in.", "success")
                return redirect("/login")
            else:
                flash("Registration failed: account may already exist.", "error")
                return redirect(url_for('signup'))
        else:
            flash("Please fill in all required fields.", "error")
            return render_template("signup.html")

    @app.route("/loginUser", methods=["POST"])
    def login_user():
        userName = request.form.get('userName')
        password = request.form.get('password')

        if userName and password:
            is_login = crime_service.login(userName, password)

            if isinstance(is_login, tuple) and is_login[0] == "Success":
                user_role = is_login[1]
                session['email'] = is_login[2]

                if user_role == "user":
                    return redirect("userdashboard")
                
            elif is_login == "Invalid_Username":
                flash("The given username is invalid", "error")
                return redirect(url_for('login'))

            elif is_login == "Invalid_Password":
                flash("The given password is incorrect", "error")
                return redirect(url_for('login'))

            elif is_login == "UserNotFound":
                flash("User not found", "error")
                return redirect(url_for('login'))
        else:
            flash("Please provide both username and password", "error")
            return redirect(url_for('login')) 

        return redirect(url_for('login')) 
    
    @app.route("/crimeFormRegister", methods=["POST"])
    def crime_form_register():
        # Get form data
        fullname = request.form.get('fullname')
        emailid = request.form.get('emailid')
        phoneNo = request.form.get('phoneNo')
        aadhaarNo = request.form.get('aadhaarNo')
        Address = request.form.get('Address')
        crimeDate = request.form.get('crimeDate')
        LOC = request.form.get('LOC')
        crimeType = request.form.get('crimeType')
        detailedDescription = request.form.get('detailedDescription')
        idProof = request.files.get('idProof')
        evidence = request.files.get('evidence')
        bankName = request.form.get('bankName')
        transactionId = request.form.get('transactionId')
        fraudAmount = request.form.get('fraudAmount')
        suspectProfile = request.form.get('suspectProfile')
        suspectContact = request.form.get('suspectContact')
        victimAge = request.form.get('victimAge')
        relationship = request.form.get('relationship')
        incidentType = request.form.get('incidentType')
        theftType = request.form.get('theftType')
        suspectDescription = request.form.get('suspectDescription')

        issaved = crime_service.register_crime(fullname, emailid, phoneNo, aadhaarNo, Address, crimeDate, LOC, crimeType, detailedDescription, idProof, evidence,
                                                bankName, transactionId, fraudAmount, suspectProfile, suspectContact, victimAge, relationship, incidentType,
                                                theftType, suspectDescription)
        if issaved:
            flash("Crime report registered successfully!", "success")
        else:
            flash("Failed to register the crime. Please try again.", "error")

        return redirect(url_for('registration'))

    @app.route("/forgotPassword")
    def forgot_password():
        return render_template("forgot_password.html")
    
    @app.route("/sendotp", methods=["POST"])
    def send_otp():
        email = request.form.get("userName")
        if not email:
            flash("Please provide your email address.", "error")
            return redirect(url_for('forgot_password'))
        isvalid_user = crime_service.check_user_exists(email)
        if not isvalid_user:
            flash("No account found with the provided email.", "error")
            return redirect(url_for('forgot_password'))
        else:
            otp_sent = crime_service.send_otp_to_email(email)
            if otp_sent != False:
                session["otp_reset_email"] = otp_sent
                session["otp_timestamp"] = datetime.now().timestamp()
                flash("OTP has been sent to your email.", "success")
                return render_template('forgot_password.html', email=email, otp_sent=True)
            else:
                flash("Failed to send OTP. Please check your email and try again.", "error")
                return redirect(url_for('forgot_password'))

    @app.route("/validate_otp", methods=["POST"])
    def validate_otp():
        email = request.form.get("email")
        otp = request.form.get("otp")
        current_time = datetime.now().timestamp()
        otp_timestamp = session.get("otp_timestamp")
        if otp_timestamp and (current_time - otp_timestamp) > 120:  # 2 minutes = 120 seconds
            flash("OTP has expired. Please request a new one.", "error")
            return redirect(url_for('forgot_password'))
        print(f"Validating OTP: {otp} and session OTP: {session.get('otp_reset_email')}")
        if not email or not otp:
            flash("Please provide both email and OTP.", "error")
            return redirect(url_for('forgot_password'))
        if otp == session.get("otp_reset_email"):
            flash("OTP validated. Please enter your new password.", "success")
            return render_template("forgot_password.html", email=email, reset_password=True)
        else:
            session["otp_reset_email"] = ""
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('forgot_password'))
        
    @app.route("/reset_password", methods=["POST"])
    def reset_password():
        email = request.form.get("email")
        new_password = request.form.get("newpassword")
        if not email or not new_password:
            flash("Please provide both email and new password.", "error")
            return redirect(url_for('forgot_password'))
        is_reset = crime_service.reset_password(email, new_password)
        if is_reset:
            flash("Password has been reset successfully. Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Failed to reset password. Please try again.", "error")
            return redirect(url_for('forgot_password'))
        
    @app.route("/submitEmergency", methods=["POST"])
    def submit_emergency():
        # Get form data
        name = request.form.get('name')
        contact = request.form.get('contact')
        email = request.form.get('email')
        location = request.form.get('location')
        emergencyType = request.form.get('emergencyType')
        description = request.form.get('description')
        datetime_val = request.form.get('datetime')
        media = request.files.get('media')

        issaved = crime_service.register_emergency(name, email, contact, location, emergencyType, description, media, datetime_val)
        if issaved:
            flash("Emergency report submitted successfully!", "success")
        else:
            flash("Failed to submit the emergency report. Please try again.", "error")

        return redirect(url_for('emergency'))    
    
    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for('home'))
    