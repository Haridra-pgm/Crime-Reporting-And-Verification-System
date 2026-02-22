from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.service import crime_service_admin
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import base64

def admin_dashboard(app_admin):
    @app_admin.route('/')
    def adminLogin():
        return render_template('admin_login.html')
    
    @app_admin.route('/dashboard')
    def admin_dashboard():
        return render_template('admin_dashboard.html')
    
    @app_admin.route('/login', methods=['POST'])
    def admin_login():
        email = request.form['email']
        password = request.form['password']

        isValidAdmin = crime_service_admin.validate_admin_login(email, password)
        session['otp']=isValidAdmin
        session['otp_send_time']=datetime.now().timestamp()
        session['email']=email
        
        if isValidAdmin != False:
            flash('OTP sent to your email. Please verify to continue.', 'success')
            return render_template('admin_login.html', email=email,)           
        else:
            flash('Invalid admin credentials', 'error')
            return redirect(url_for('adminLogin'))
    
    @app_admin.route('/valid_otp', methods=['POST'])
    def validate_otp():
        email = request.form['email']
        entered_otp = request.form['otp']
        sent_otp = session.get('otp')
        otp_send_time = session.get('otp_send_time')
        if email != session.get('email'):
            flash('Invalid email session. Please login again.', 'error')
            return redirect(url_for('adminLogin'))
        if not sent_otp or not otp_send_time:
            flash('OTP session expired. Please login again.', 'error')
            return redirect(url_for('adminLogin'))

        current_time = datetime.now().timestamp()
        elapsed_time = current_time - otp_send_time

        if elapsed_time > 120:
            flash('OTP has expired. Please login again.', 'error')
            return redirect(url_for('adminLogin'))

        if entered_otp == str(sent_otp):
            session.pop('otp', None)
            session.pop('otp_send_time', None)
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
            return redirect(url_for('adminLogin'))
    
    @app_admin.route('/logout')
    def admin_logout():
        session.clear()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('adminLogin'))
    
    @app_admin.route('/complaints')
    def view_complaints():
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin dashboard.', 'error')
            return redirect(url_for('adminLogin'))
        else:
            complaints = crime_service_admin.get_complaints()
            # complaints may be False, a list of tuples, or a list of dicts
            if not complaints:
                return render_template('admin_complaints.html', complaint=[])

            formatted = []
            for row in complaints:
                # if row is a dict (cursor with dictionary=True)
                if isinstance(row, dict):
                    dt = row.get('crimeDate')
                    if isinstance(dt, datetime):
                        row['crimeDate'] = dt.strftime('%Y-%m-%d %H:%M')
                    formatted.append(row)
                else:
                    # assume tuple/list -> convert to list for mutability
                    row_list = list(row)
                    dt = row_list[2] if len(row_list) > 2 else None
                    if isinstance(dt, datetime):
                        row_list[2] = dt.strftime('%Y-%m-%d %H:%M')
                    formatted.append(row_list)

            return render_template('admin_complaints.html', complaint=formatted)
    @app_admin.route('/complaint-history')
    def complaint_history():
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin dashboard.', 'error')
            return redirect(url_for('adminLogin'))
        else:
            complaints = crime_service_admin.get_complaints_history_by_email()
            # complaints may be False, a list of tuples, or a list of dicts
            if not complaints:
                return render_template('admin_complaints_history.html', complaint=[])
            formatted = []
            for row in complaints:
                # if row is a dict (cursor with dictionary=True)
                if isinstance(row, dict):
                    dt = row.get('crimeDate')
                    if isinstance(dt, datetime):
                        row['crimeDate'] = dt.strftime('%Y-%m-%d %H:%M')
                    formatted.append(row)
                else:
                    # assume tuple/list -> convert to list for mutability
                    row_list = list(row)
                    dt = row_list[2] if len(row_list) > 2 else None
                    if isinstance(dt, datetime):
                        row_list[2] = dt.strftime('%Y-%m-%d %H:%M')
                    formatted.append(row_list)
            
            print(formatted)        
            return render_template('admin_complaints_history.html', complaints=formatted)
    
    @app_admin.route('/complaint-details/<int:complaint_id>')
    def view_complaint_detail(complaint_id):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin dashboard.', 'error')
            return redirect(url_for('adminLogin'))
        else:
            complaint = crime_service_admin.get_complaint_by_id(complaint_id)
            if not complaint:
                return jsonify({"error": "Complaint not found or you do not have access."}), 404
        # Convert dict to tuple for template compatibility but also extract stored AI summary
        ai_raw = None
        if isinstance(complaint, dict):
            # Extract image paths first
            evidence_path = complaint.get('evidence_path')
            idProof_path = complaint.get('idProof_path')
            # Extract any stored AI summary/diagnostics
            ai_raw = complaint.get('ai_summaries') or complaint.get('ai_report') or complaint.get('ai_assistance') or complaint.get('ai_reports') or ''
            # Convert dict to tuple in the order expected by template
            dt = complaint.get('crimeDate')
            if isinstance(dt, datetime):
                complaint_tuple = (
                    complaint.get('id'),                    # [0]
                    complaint.get('fullname'),              # [1]
                    complaint.get('emailid'),               # [2]
                    complaint.get('phoneNo'),               # [3]
                    complaint.get('aadhaarNo'),             # [4]
                    complaint.get('Address'),               # [5]
                    dt.strftime('%Y-%m-%d %H:%M'),          # [6]
                    complaint.get('LOC'),                   # [7]
                    complaint.get('crimeType'),             # [8]
                    complaint.get('detailedDescription'),   # [9]
                    complaint.get('idProof_path'),          # [10]
                    complaint.get('evidence_path'),         # [11]
                    complaint.get('bankName'),              # [12]
                    complaint.get('transactionId'),         # [13]
                    complaint.get('fraudAmount'),           # [14]
                    complaint.get('suspectProfile'),        # [15]
                    complaint.get('suspectContact'),        # [16]
                    complaint.get('victimAge'),             # [17]
                    complaint.get('relationship'),          # [18]
                    complaint.get('incidentType'),          # [19]
                    complaint.get('theftType'),             # [20]
                    complaint.get('suspectDescription'),    # [21]
                    complaint.get('status'),                # [22]
                )
            else:
                complaint_tuple = (
                    complaint.get('id'),                    # [0]
                    complaint.get('fullname'),              # [1]
                    complaint.get('emailid'),               # [2]
                    complaint.get('phoneNo'),               # [3]
                    complaint.get('aadhaarNo'),             # [4]
                    complaint.get('Address'),               # [5]
                    complaint.get('crimeDate'),             # [6]
                    complaint.get('LOC'),                   # [7]
                    complaint.get('crimeType'),             # [8]
                    complaint.get('detailedDescription'),   # [9]
                    complaint.get('idProof_path'),          # [10]
                    complaint.get('evidence_path'),         # [11]
                    complaint.get('bankName'),              # [12]
                    complaint.get('transactionId'),         # [13]
                    complaint.get('fraudAmount'),           # [14]
                    complaint.get('suspectProfile'),        # [15]
                    complaint.get('suspectContact'),        # [16]
                    complaint.get('victimAge'),             # [17]
                    complaint.get('relationship'),          # [18]
                    complaint.get('incidentType'),          # [19]
                    complaint.get('theftType'),             # [20]
                    complaint.get('suspectDescription'),    # [21]
                    complaint.get('status'),                # [22]
                )
            complaint = complaint_tuple
        else:
            # complaint is already tuple/list
            evidence_path = complaint[11] if len(complaint) > 11 else None
            idProof_path = complaint[10] if len(complaint) > 10 else None
            # no ai_raw for tuple case
            ai_raw = ''

        evidence_img = None
        if evidence_path and isinstance(evidence_path, str) and os.path.exists(evidence_path):
            try:
                with open(evidence_path, 'rb') as f:
                    evidence_img = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"[WARNING] Could not read evidence file: {e}")

        idProof_img = None
        if idProof_path and isinstance(idProof_path, str) and os.path.exists(idProof_path):
            try:
                with open(idProof_path, 'rb') as f:
                    idProof_img = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"[WARNING] Could not read ID Proof file: {e}")
        # Get AI assistance report from the complaint tuple (no index 23, needs to be fetched separately or generated on demand)
        # If an AI summary was already saved in the DB (extracted into `ai_raw` above), use it so the page shows stored results
        if ai_raw:
            # Normalize saved AI output: strip diagnostics payload and code fences, keep the human-readable assistant summary
            ai_text = str(ai_raw)
            # Remove the diagnostics section if present
            if "\n\n[DIAGNOSTICS]" in ai_text:
                ai_text = ai_text.split("\n\n[DIAGNOSTICS]")[0].strip()
            # Remove common markdown/json fences
            ai_text = ai_text.replace('```json', '').replace('```', '').strip()
            # Prefer to start from the visual summary marker if present
            for marker in ['🔍 Image Verification Summary', 'Image Verification Summary', '🔍']:
                idx = ai_text.find(marker)
                if idx != -1:
                    ai_text = ai_text[idx:].strip()
                    break
            ai_report_text = ai_text
            ai_report_html = ai_text.replace('\n', '<br>')
        else:
            # default empty values; template button can trigger live generation
            ai_report = ""
            ai_report_text = ''
            ai_report_html = ''

        # Always pass both text and HTML versions so template can choose how to render
        return render_template(
            'admin_complaint_detail.html',
            complaint=complaint,
            evidence_img=evidence_img,
            idProof_img=idProof_img,
            ai_report=ai_report_text,
            ai_report_html=ai_report_html
        )
        
    @app_admin.route('/ai-assist/<int:complaint_id>')
    def ai_assist(complaint_id):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin dashboard.', 'error')
            return redirect(url_for('adminLogin'))
        else:
            complaint = crime_service_admin.get_complaint_by_id(complaint_id)
            if not complaint:
                return jsonify({"error": "Complaint not found or you do not have access."}), 404
        # Convert dict to tuple for template compatibility
        if isinstance(complaint, dict):
            evidence_path = complaint.get('evidence_path')
            idProof_path = complaint.get('idProof_path')
            
            dt = complaint.get('crimeDate')
            if isinstance(dt, datetime):
                complaint_tuple = (
                    complaint.get('id'),                    # [0]
                    complaint.get('fullname'),              # [1]
                    complaint.get('emailid'),               # [2]
                    complaint.get('phoneNo'),               # [3]
                    complaint.get('aadhaarNo'),             # [4]
                    complaint.get('Address'),               # [5]
                    dt.strftime('%Y-%m-%d %H:%M'),          # [6]
                    complaint.get('LOC'),                   # [7]
                    complaint.get('crimeType'),             # [8]
                    complaint.get('detailedDescription'),   # [9]
                    complaint.get('idProof_path'),          # [10]
                    complaint.get('evidence_path'),         # [11]
                    complaint.get('bankName'),              # [12]
                    complaint.get('transactionId'),         # [13]
                    complaint.get('fraudAmount'),           # [14]
                    complaint.get('suspectProfile'),        # [15]
                    complaint.get('suspectContact'),        # [16]
                    complaint.get('victimAge'),             # [17]
                    complaint.get('relationship'),          # [18]
                    complaint.get('incidentType'),          # [19]
                    complaint.get('theftType'),             # [20]
                    complaint.get('suspectDescription'),    # [21]
                    complaint.get('status'),                # [22]
                )
            else:
                complaint_tuple = (
                    complaint.get('id'),                    # [0]
                    complaint.get('fullname'),              # [1]
                    complaint.get('emailid'),               # [2]
                    complaint.get('phoneNo'),               # [3]
                    complaint.get('aadhaarNo'),             # [4]
                    complaint.get('Address'),               # [5]
                    complaint.get('crimeDate'),             # [6]
                    complaint.get('LOC'),                   # [7]
                    complaint.get('crimeType'),             # [8]
                    complaint.get('detailedDescription'),   # [9]
                    complaint.get('idProof_path'),          # [10]
                    complaint.get('evidence_path'),         # [11]
                    complaint.get('bankName'),              # [12]
                    complaint.get('transactionId'),         # [13]
                    complaint.get('fraudAmount'),           # [14]
                    complaint.get('suspectProfile'),        # [15]
                    complaint.get('suspectContact'),        # [16]
                    complaint.get('victimAge'),             # [17]
                    complaint.get('relationship'),          # [18]
                    complaint.get('incidentType'),          # [19]
                    complaint.get('theftType'),             # [20]
                    complaint.get('suspectDescription'),    # [21]
                    complaint.get('status'),                # [22]
                )
            complaint = complaint_tuple
        else:
            evidence_path = complaint[11] if len(complaint) > 11 else None
            idProof_path = complaint[10] if len(complaint) > 10 else None

        evidence_img = None
        if evidence_path and isinstance(evidence_path, str) and os.path.exists(evidence_path):
            try:
                with open(evidence_path, 'rb') as f:
                    evidence_img = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"[WARNING] Could not read evidence file: {e}")

        idProof_img = None
        if idProof_path and isinstance(idProof_path, str) and os.path.exists(idProof_path):
            try:
                with open(idProof_path, 'rb') as f:
                    idProof_img = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"[WARNING] Could not read ID Proof file: {e}")
        
        ai_reports = None
        ai_report = "AI assistance not available."
        ai_report_html = ""
        try:
            ai_reports = crime_service_admin.ai_assistance_report(complaint_id)
            print(f"[DEBUG] AI reports result: {ai_reports}")
            if ai_reports and isinstance(ai_reports, dict):
                ai_report = ai_reports.get('summary_report') or ai_reports.get('error') or "No AI report generated."
                # Convert newlines to HTML line breaks
                ai_report_html = str(ai_report).replace('\\n', '\n').replace('\n', '<br>')
        except Exception as e:
            print(f"[ERROR] AI assistance failed: {e}")
            import traceback
            traceback.print_exc()
            ai_report = f"AI analysis failed: {str(e)}"
            ai_report_html = ai_report
        
        return render_template('admin_complaint_detail.html', complaint=complaint, evidence_img=evidence_img, idProof_img=idProof_img, ai_reports=ai_reports, ai_report=ai_report, ai_report_html=ai_report_html)
    
    @app_admin.route('/update-complaint/<int:complaint_id>', methods=['GET', 'POST'])
    def update_complaint_admin(complaint_id):
        """Allow admin to update complaint status and add remarks."""
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin dashboard.', 'error')
            return redirect(url_for('adminLogin'))

        if request.method == 'POST':
            status = request.form.get('status', '').strip()
            remarks = request.form.get('remarks', '').strip()

            if not status:
                flash('Status is required', 'error')
                return redirect(url_for('update_complaint_admin', complaint_id=complaint_id))

            ok = crime_service_admin.update_complaint_status(complaint_id, status, remarks)
            if ok:
                flash('Complaint status updated successfully', 'success')
                return redirect(url_for('view_complaints'))
            else:
                flash('Failed to update complaint. See server logs for details.', 'error')
                return redirect(url_for('view_complaints'))

        # GET -> show update form (reuse staff template but a dedicated admin copy exists)
        complaint = crime_service_admin.get_complaint_by_id(complaint_id)
        if not complaint:
            flash('Complaint not found', 'error')
            return redirect(url_for('view_complaints'))

        # convert dict->tuple if needed (template expects positional indices)
        if isinstance(complaint, dict):
            dt = complaint.get('crimeDate')
            if isinstance(dt, datetime):
                complaint_tuple = (
                    complaint.get('id'),
                    complaint.get('fullname'),
                    complaint.get('emailid'),
                    complaint.get('phoneNo'),
                    complaint.get('aadhaarNo'),
                    complaint.get('Address'),
                    dt.strftime('%Y-%m-%d %H:%M'),
                    complaint.get('LOC'),
                    complaint.get('crimeType'),
                    complaint.get('detailedDescription'),
                    complaint.get('idProof_path'),
                    complaint.get('evidence_path'),
                    complaint.get('bankName'),
                    complaint.get('transactionId'),
                    complaint.get('fraudAmount'),
                    complaint.get('suspectProfile'),
                    complaint.get('suspectContact'),
                    complaint.get('victimAge'),
                    complaint.get('relationship'),
                    complaint.get('incidentType'),
                    complaint.get('theftType'),
                    complaint.get('suspectDescription'),
                    complaint.get('status'),
                )
            else:
                complaint_tuple = (
                    complaint.get('id'),
                    complaint.get('fullname'),
                    complaint.get('emailid'),
                    complaint.get('phoneNo'),
                    complaint.get('aadhaarNo'),
                    complaint.get('Address'),
                    complaint.get('crimeDate'),
                    complaint.get('LOC'),
                    complaint.get('crimeType'),
                    complaint.get('detailedDescription'),
                    complaint.get('idProof_path'),
                    complaint.get('evidence_path'),
                    complaint.get('bankName'),
                    complaint.get('transactionId'),
                    complaint.get('fraudAmount'),
                    complaint.get('suspectProfile'),
                    complaint.get('suspectContact'),
                    complaint.get('victimAge'),
                    complaint.get('relationship'),
                    complaint.get('incidentType'),
                    complaint.get('theftType'),
                    complaint.get('suspectDescription'),
                    complaint.get('status'),
                )
            complaint = complaint_tuple

        return render_template('update_single_complaint_admin.html', complaint=complaint)
    
    @app_admin.route('/register-staff', methods=['GET', 'POST'])
    def register_staff():
        if 'admin_logged_in' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('adminLogin'))
        
        if request.method == 'GET':
            return render_template('register_staff.html')
        
        elif request.method == 'POST':
            try:
                # Get form data
                fullname = request.form.get('fullname', '').strip()
                email = request.form.get('email', '').strip()
                staff_id = request.form.get('staff_id', '').strip()
                phone = request.form.get('phone', '').strip()
                gender = request.form.get('gender', '').strip()
                dob = request.form.get('dob', '').strip() or None
                rank = request.form.get('rank', '').strip()
                police_station = request.form.get('police_station', '').strip()
                posting = request.form.get('posting', '').strip()
                location = request.form.get('location', '').strip()
                state = request.form.get('state', '').strip()
                password = request.form.get('password', '')
                confirm_password = request.form.get('confirm_password', '')
                
                # Validate inputs
                if not all([fullname, email, staff_id, phone, gender, rank, police_station, posting, location, state, password]):
                    flash('All required fields must be filled', 'error')
                    return render_template('register_staff.html')
                
                if len(phone) != 10 or not phone.isdigit():
                    flash('Phone number must be 10 digits', 'error')
                    return render_template('register_staff.html')
                
                if password != confirm_password:
                    flash('Passwords do not match', 'error')
                    return render_template('register_staff.html')
                
                if len(password) < 8:
                    flash('Password must be at least 8 characters long', 'error')
                    return render_template('register_staff.html')
                
                # Call service to register staff
                result = crime_service_admin.register_staff(
                    fullname=fullname,
                    email=email,
                    staff_id=staff_id,
                    phone=phone,
                    gender=gender,
                    dob=dob,
                    rank=rank,
                    police_station=police_station,
                    posting=posting,
                    location=location,
                    state=state,
                    password=password
                )
                
                if result:
                    flash(f'Staff member {fullname} registered successfully!', 'success')
                    return redirect(url_for('view_staff'))
                else:
                    flash('Failed to register staff member. Please try again.', 'error')
                    return render_template('register_staff.html')
                    
            except Exception as e:
                print(f"Error registering staff: {e}")
                flash(f'An error occurred: {str(e)}', 'error')
                return render_template('register_staff.html')
    
    @app_admin.route('/view-staff')
    def view_staff():
        if 'admin_logged_in' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('adminLogin'))
        
        staff_list = crime_service_admin.get_all_staff()
        return render_template('view_staff.html', staff_list=staff_list)
    
    @app_admin.route('/add-admin', methods=['GET', 'POST'])
    def add_admin():
        if 'admin_logged_in' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('adminLogin'))
        
        if request.method == 'GET':
            return render_template('add_admin.html')
        
        elif request.method == 'POST':
            try:
                # Get form data
                fullname = request.form.get('fullname', '').strip()
                email = request.form.get('email', '').strip()
                phone = request.form.get('phone', '').strip()
                gender = request.form.get('gender', '').strip()
                password = request.form.get('password', '')
                confirm_password = request.form.get('confirm_password', '')
                
                # Validate inputs
                if not all([fullname, email, phone, gender, password]):
                    flash('All required fields must be filled', 'error')
                    return render_template('add_admin.html')
                
                if len(phone) != 10 or not phone.isdigit():
                    flash('Phone number must be 10 digits', 'error')
                    return render_template('add_admin.html')
                
                if password != confirm_password:
                    flash('Passwords do not match', 'error')
                    return render_template('add_admin.html')
                
                if len(password) < 8:
                    flash('Password must be at least 8 characters long', 'error')
                    return render_template('add_admin.html')
                
                # Call service to add admin
                result = crime_service_admin.add_admin(
                    fullname=fullname,
                    email=email,
                    phone=phone,
                    gender=gender,
                    password=password
                )
                
                if result:
                    flash(f'Admin {fullname} created successfully!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Failed to create admin. Email might already exist.', 'error')
                    return render_template('add_admin.html')
                    
            except Exception as e:
                print(f"Error creating admin: {e}")
                flash(f'An error occurred: {str(e)}', 'error')
                return render_template('add_admin.html')
        