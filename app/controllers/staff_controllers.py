from flask import render_template, request, redirect, url_for, session, flash
from app.repository.crime_repository_admin import validate_staff_login, get_complaints, get_complaint_by_id, get_complaints_history_by_email
from app.util.encryption import encrypt_message, decrypt_message
import os
import base64
from datetime import datetime

def register_staff_routes(app):
    """Register all staff routes."""
    
    @app.route('/')
    @app.route('/staff-login', methods=['GET', 'POST'])
    def staff_login():
        """Staff login page."""
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            # Validation
            if not email or not password:
                flash('Email and password are required', 'error')
                return redirect(url_for('staff_login'))
            
            if '@' not in email:
                flash('Invalid email format', 'error')
                return redirect(url_for('staff_login'))
            
            if len(password) < 8:
                flash('Invalid password', 'error')
                return redirect(url_for('staff_login'))
            
            # Validate staff login from database
            staff = validate_staff_login(email)
            
            if staff and isinstance(staff, tuple) and len(staff) > 12:
                # staff = (id, fullname, email, staff_id, phone, gender, dob, rank, police_station, posting, location, state, password, status)
                # Password is at index 12
                db_password = staff[12]  # encrypted password from DB
                
                # Decrypt and compare
                try:
                    decrypted_password = decrypt_message(db_password)
                    if decrypted_password == password:
                        # Set session
                        session['staff_id'] = staff[0]
                        session['staff_email'] = email
                        session['staff_name'] = staff[1]  # fullname
                        session['logged_in'] = True
                        
                        flash(f'Welcome, {staff[1]}!', 'success')
                        return redirect(url_for('staff_dashboard'))
                    else:
                        flash('Invalid email or password', 'error')
                        return redirect(url_for('staff_login'))
                except Exception as e:
                    print(f"Error decrypting password: {e}")
                    flash('Login error. Please try again.', 'error')
                    return redirect(url_for('staff_login'))
            else:
                flash('Invalid email or password', 'error')
                return redirect(url_for('staff_login'))
        
        return render_template('staff_login.html')
    
    @app.route('/staff-dashboard')
    def staff_dashboard():
        """Staff dashboard."""
        if 'logged_in' not in session or not session.get('logged_in'):
            flash('Please login first', 'error')
            return redirect(url_for('staff_login'))
        
        staff_name = session.get('staff_name', 'Staff Member')
        return render_template('staff_dashboard_new.html', staff_name=staff_name)
    
    @app.route('/total-complaints')
    def total_complaints():
        """Display total number of complaints."""
        if 'logged_in' not in session or not session.get('logged_in'):
            flash('Please login first', 'error')
            return redirect(url_for('staff_login'))
        
        complaints = get_complaints_history_by_email()
        total = len(complaints) if complaints else 0
        
        return render_template('total_complaints.html', 
                             total=total, 
                             complaints=complaints,
                             staff_name=session.get('staff_name', 'Staff Member'))
    
    @app.route('/update-status')
    def update_status():
        """Update complaint status page."""
        if 'logged_in' not in session or not session.get('logged_in'):
            flash('Please login first', 'error')
            return redirect(url_for('staff_login'))
        
        complaints = get_complaints()
       
           # If no complaints from DB, create sample data with 3 for each status
        if not complaints:
               sample_complaints = [
                   # Pending complaints (3)
                   (1, 'Rajesh Kumar', '2025-12-01', 'Mumbai', 'Theft', 'Pending', 'Pending'),
                   (2, 'Priya Singh', '2025-12-02', 'Delhi', 'Fraud', 'Pending', 'Pending'),
                   (3, 'Amit Patel', '2025-11-30', 'Bangalore', 'Cybercrime', 'Pending', 'Pending'),
                   # Progress complaints (3)
                   (4, 'Neha Sharma', '2025-11-28', 'Pune', 'Assault', 'Progress', 'Progress'),
                   (5, 'Vikram Reddy', '2025-11-25', 'Hyderabad', 'Robbery', 'Progress', 'Progress'),
                   (6, 'Anjali Verma', '2025-11-20', 'Chennai', 'Harassment', 'Progress', 'Progress'),
                # Verified complaints (3)
                (7, 'Suresh Gupta', '2025-11-15', 'Kolkata', 'Burglary', 'Verified', 'Verified'),
                (8, 'Meera Nair', '2025-11-10', 'Jaipur', 'Vandalism', 'Verified', 'Verified'),
                (9, 'Deepak Singh', '2025-11-05', 'Ahmedabad', 'Hit & Run', 'Verified', 'Verified'),
                # Resolved complaints (3)
                (10, 'Ramesh Bhat', '2025-10-25', 'Ernakulam', 'Theft', 'Resolved', 'Resolved'),
                (11, 'Kavita Rao', '2025-10-18', 'Lucknow', 'Scam', 'Resolved', 'Resolved'),
                (12, 'Mohit Das', '2025-10-12', 'Bhubaneswar', 'Assault', 'Resolved', 'Resolved'),
               ]
               complaints = sample_complaints
       
        return render_template('update_complaint_status.html',
                                 complaints=complaints,
                                 staff_name=session.get('staff_name', 'Staff Member'))
    
    @app.route('/update-status/<int:complaint_id>', methods=['GET', 'POST'])
    def update_complaint(complaint_id):
        """Update specific complaint status."""
        if 'logged_in' not in session or not session.get('logged_in'):
            flash('Please login first', 'error')
            return redirect(url_for('staff_login'))
        
        if request.method == 'POST':
            status = request.form.get('status', '').strip()
            remarks = request.form.get('remarks', '').strip()
            
            if not status:
                flash('Status is required', 'error')
                return redirect(url_for('update_complaint', complaint_id=complaint_id))
            
            # TODO: Update complaint status in database
            
            # This would call a service function to update the complaint
            

            flash('Complaint status updated successfully', 'success')
            return redirect(url_for('update_status'))
        
        complaint = get_complaint_by_id(complaint_id)
        
        if not complaint:
            flash('Complaint not found', 'error')
            return redirect(url_for('update_status'))
        
        return render_template('update_single_complaint.html',
                             complaint=complaint,
                             staff_name=session.get('staff_name', 'Staff Member'))
    
    @app.route('/emergency-complaint', methods=['GET', 'POST'])
    def emergency_complaint():
        """Emergency complaint reporting."""
        if 'logged_in' not in session or not session.get('logged_in'):
            flash('Please login first', 'error')
            return redirect(url_for('staff_login'))
        
        if request.method == 'POST':
            crime_type = request.form.get('crime_type', '').strip()
            location = request.form.get('location', '').strip()
            description = request.form.get('description', '').strip()
            urgency = request.form.get('urgency', '').strip()
            
            # Validation
            if not crime_type or not location or not description or not urgency:
                flash('All fields are required', 'error')
                return redirect(url_for('emergency_complaint'))
            
            # TODO: Save emergency complaint to database
            # This would call a service function to create emergency complaint
            
            flash('Emergency complaint registered successfully', 'success')
            return redirect(url_for('staff_dashboard'))
        
        return render_template('emergency_complaint.html',
                             staff_name=session.get('staff_name', 'Staff Member'))
    
    @app.route('/detial-complaint/<int:complaint_id>', methods=['GET', 'POST'])
    def detail_complaint(complaint_id):
        """Display details of a specific complaint."""
        if 'logged_in' not in session or not session.get('logged_in'):
            flash('Please login first', 'error')
            return redirect(url_for('staff_login'))
        
        complaint = get_complaint_by_id(complaint_id)
        
        if not complaint:
            flash('Complaint not found', 'error')
            return redirect(url_for('update_status'))
        if isinstance(complaint, dict):
            comp = complaint
            dt = comp.get('crimeDate')
            if isinstance(dt, datetime):
                comp['crimeDate'] = dt.strftime('%Y-%m-%d %H:%M')

            evidence_path = comp.get('evidence_path') or comp.get('evidence') or comp.get('evidencePath')
            idProof_path = comp.get('idProof_path') or comp.get('idProof') or comp.get('idProofPath')
        else:
            comp = list(complaint)
            dt = comp[2] if len(comp) > 2 else None
            if isinstance(dt, datetime):
                comp[2] = dt.strftime('%Y-%m-%d %H:%M')

            # try to locate evidence and id proof paths in the tuple/list by heuristics
            evidence_path = None
            idProof_path = None
            for val in comp:
                if isinstance(val, str):
                    low = val.lower()
                    if any(low.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov')):
                        # prefer evidence path if not set, otherwise idProof
                        if evidence_path is None:
                            evidence_path = val
                        elif idProof_path is None:
                            idProof_path = val
                    elif 'evidence' in low and evidence_path is None:
                        evidence_path = val
                    elif ('id' in low or 'idproof' in low or 'id_proof' in low) and idProof_path is None:
                        idProof_path = val

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
        # Safely extract AI assistance report from the complaint record (supports dict or tuple/list)
        ai_report = ""
        if isinstance(complaint, dict):
            # Try several possible keys where AI output might be stored
            ai_report = complaint.get('ai_report') or complaint.get('ai_assist') or complaint.get('ai_assistance') or complaint.get('ai_reports') or ''
        else:
            # complaint is a tuple/list - try index 23 if present
            try:
                comp_list = list(complaint)
                if len(comp_list) > 23 and comp_list[23]:
                    ai_report = comp_list[23]
            except Exception:
                ai_report = ""

        # Normalize AI report: convert literal "\\n" sequences to real newlines, then prepare HTML with <br>
        ai_report_text = ''
        ai_report_html = ''
        if ai_report:
            try:
                ai_report_text = str(ai_report)
                # Convert literal backslash-n sequences to actual newlines
                ai_report_text = ai_report_text.replace('\\n', '\n')
                # Prepare HTML-safe version with <br>
                ai_report_html = ai_report_text.replace('\n', '<br>')
            except Exception:
                ai_report_text = str(ai_report)
                ai_report_html = ai_report_text.replace('\n', '<br>')

        return render_template('staff_complaint_detail.html',
                     complaint=complaint,
                     staff_name=session.get('staff_name', 'Staff Member'), 
                     evidence_img=evidence_img,
                     idProof_img=idProof_img,
                     ai_report_text=ai_report_text,
                     ai_report_html=ai_report_html,
                     ai_report=ai_report)

    @app.route('/staff-logout')
    def staff_logout():
        """Logout staff member."""
        session.clear()
        flash('You have been logged out', 'success')
        return redirect(url_for('staff_login'))
