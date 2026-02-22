from app.repository import crime_repository_admin
from app.util.mail_handler import send_email
from app.util.otp_generate import generate_otp
import datetime
from datetime import timedelta
from app.util.encryption import decrypt_message
from app.util.encryption import encrypt_message
from app.ml_model.imageVerificationSystem import verify_image_report
from app.ml_model.reportVerificationSystem import run_report_verification
from app.ml_model.riskAssessmentSystem import run_risk_assessment
from app.ml_model.summarisation import summary_generator


def generate_fallback_summary(report, crime_type):
    """Generate a basic summary when AI analysis fails or image is unavailable"""
    summary = f"""
🔍 Image Verification Summary
• No image available for verification
• Evidence image upload status: Missing or unavailable
• Claim support result: Cannot verify without image
• Final image verdict: Incomplete - Evidence required

📝 Report Verification Summary
• Incident category: {crime_type}
• Report validity status: Awaiting evidence verification
• Urgency level: Review required
• Key confirmed details: {report.get('Location of Crime', 'N/A')} - {report.get('Crime Type', 'N/A')}

⚠️ Risk Assessment Summary
• Severity score: Pending image analysis
• Threat probability: Pending evidence review
• Final risk score: Cannot assess without evidence
• Top contributing factors: Missing evidence image prevents complete assessment

📌 Overall Recommendation
• Combined conclusion: Report submitted but requires evidence verification for complete analysis
• Recommended action: human_review
• Any warnings: Evidence image is required to complete AI analysis. Please ensure image is properly uploaded.
"""
    return summary.strip()


def send_otp_to_email(email):
    try:
        otp = generate_otp()
        subject = "Your OTP for Admin Login"
        body = f"Your OTP for admin login is: {otp}. It is valid for 2 minutes."
        send =send_email(email, subject, body)
        otp_data = {
            "send_email": send,
            "otp": otp,
        }
        return otp_data
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False
    
def validate_admin_login(email, password):
    isvalid = crime_repository_admin.validate_admin_login(email)
    # Check if admin exists (isvalid will be False if not found)
    if not isvalid:
        return False
    
    # isvalid is a tuple: (id, fullname, email, phone, gender, password, status, created_at, updated_at)
    # Password is at index 5
    encrypted_password = isvalid[5]
    decrypted_password = decrypt_message(encrypted_password)

    # If decryption succeeded and matches
    if decrypted_password and decrypted_password == password:
        send_email_otp = send_otp_to_email(email)
        if send_email_otp and send_email_otp.get("send_email"):
            return send_email_otp["otp"]

    # Fallback: stored value may be plaintext (migration case)
    try:
        stored_plain = None
        if isinstance(encrypted_password, bytes):
            try:
                stored_plain = encrypted_password.decode()
            except Exception:
                stored_plain = None
        elif isinstance(encrypted_password, str):
            stored_plain = encrypted_password

        if stored_plain and stored_plain == password:
            # Re-encrypt with current key and update DB for future logins
            try:
                new_encrypted = encrypt_message(password)
                # update DB
                admin_id = isvalid[0]
                crime_repository_admin.update_admin_password(admin_id, new_encrypted)
            except Exception as e:
                print(f"Warning: could not migrate plaintext password to encrypted for admin id {isvalid[0]}: {e}")

            send_email_otp = send_otp_to_email(email)
            if send_email_otp and send_email_otp.get("send_email"):
                return send_email_otp["otp"]
    except Exception:
        pass

    return False

def get_complaints():
    complaints = crime_repository_admin.get_complaints()
    return complaints

def get_complaint_by_id(complaint_id):
    complaint = crime_repository_admin.get_complaint_by_id(complaint_id)
    print ("Complaint fetched by ID:", complaint)
    return complaint


def update_complaint_status(complaint_id, status, remarks=None):
    """Service wrapper to update complaint status and remarks."""
    try:
        return crime_repository_admin.update_complaint_status(complaint_id, status, remarks)
    except Exception as e:
        print(f"Error in service updating complaint status: {e}")
        return False

def ai_assistance_report(complaint_id):
    complaint = crime_repository_admin.get_complaint_by_id(complaint_id)

    # Prepare diagnostics collector
    diagnostics = []
    import os, traceback, base64

    # Support both dict (recommended) and tuple/list complaint shapes
    if isinstance(complaint, dict):
        date_value = complaint.get('crimeDate')
        image_path = complaint.get('evidence_path') or complaint.get('evidence') or complaint.get('evidencePath')
        report = {
            "report_id": complaint.get('id'),
            "Address": complaint.get('Address'),
            "crime Date": (date_value.strftime("%Y-%m-%d") if hasattr(date_value, 'strftime') else str(date_value)),
            "Date and Time": (date_value.strftime("%Y-%m-%d %H:%M:%S") if hasattr(date_value, 'strftime') else str(date_value)),
            "Location of Crime": complaint.get('LOC'),
            "Detailed Description": complaint.get('detailedDescription'),
            "Crime Type": complaint.get('crimeType')
        }
    else:
        # legacy tuple/list handling
        date_value = complaint[6]
        image_path = complaint[11]
        report = {
            "report_id": complaint[0],
            "Address": complaint[5],
            "crime Date": complaint[6].strftime("%Y-%m-%d") if hasattr(complaint[6], 'strftime') else str(complaint[6]),
            "Date and Time": date_value.strftime("%Y-%m-%d %H:%M:%S") if hasattr(date_value, 'strftime') else str(date_value),
            "Location of Crime": complaint[7],
            "Detailed Description": complaint[9],
            "Crime Type": complaint[8]
        }

    # CONDITIONAL FIELDS BASED ON TYPE
    crime_type = complaint.get('crimeType') if isinstance(complaint, dict) else complaint[8]
    try:
        if crime_type == "financial":
            if isinstance(complaint, dict):
                report.update({
                    "Bank Name": complaint.get('bankName'),
                    "Transaction Id": complaint.get('transactionId'),
                    "Fraud Amount": complaint.get('fraudAmount'),
                })
            else:
                report.update({
                    "Bank Name": complaint[12],
                    "Transaction Id": complaint[13],
                    "Fraud Amount": complaint[14],
                })

        elif crime_type == "cyber":
            if isinstance(complaint, dict):
                report.update({
                    "suspectProfile": complaint.get('suspectProfile'),
                    "suspectContact": complaint.get('suspectContact'),
                })
            else:
                report.update({
                    "suspectProfile": complaint[15],
                    "suspectContact": complaint[16],
                })

        elif crime_type == "women":
            if isinstance(complaint, dict):
                report.update({
                    "victim Age": complaint.get('victimAge') or complaint.get('victim_age') or complaint.get('victimAge'),
                    "Relationship": complaint.get('relationship'),
                    "incidentType": complaint.get('incidentType'),
                })
            else:
                report.update({
                    "victim Age": complaint[17],
                    "Relationship": complaint[18],
                    "incidentType": complaint[19],
                })

        elif crime_type == "theft":
            if isinstance(complaint, dict):
                report.update({
                    "IncidentType": complaint.get('theftType') or complaint.get('incidentType'),
                    "Suspect Description": complaint.get('suspectDescription'),
                })
            else:
                report.update({
                    "IncidentType": complaint[20],
                    "Suspect Description": complaint[21],
                })
        else:
            report["note"] = "No additional fields for this crime type."
    except Exception:
        diagnostics.append("Warning: failed to map conditional fields")

    # Diagnostics: check image availability and readability
    diagnostics.append(f"image_path={image_path}")
    if not image_path or not os.path.exists(image_path):
        diagnostics.append("image_missing_or_unavailable")
        fallback_summary = generate_fallback_summary(report, crime_type)
        combined = fallback_summary + "\n\n[DIAGNOSTICS]\n" + "\n".join(diagnostics)
        crime_repository_admin.save_aissistance_summary(complaint_id, combined)
        return {"summary_report": fallback_summary}

    # Try reading the image and report basic stats
    try:
        size = os.path.getsize(image_path)
        diagnostics.append(f"image_size_bytes={size}")
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
        diagnostics.append(f"image_read_bytes={len(img_bytes)}")
        try:
            b64len = len(base64.b64encode(img_bytes))
            diagnostics.append(f"image_b64_len={b64len}")
        except Exception as e:
            diagnostics.append(f"image_b64_error={str(e)}")
    except Exception as e:
        diagnostics.append(f"image_read_error={str(e)}")
        fallback_summary = generate_fallback_summary(report, crime_type)
        combined = fallback_summary + "\n\n[DIAGNOSTICS]\n" + "\n".join(diagnostics)
        crime_repository_admin.save_aissistance_summary(complaint_id, combined)
        return {"summary_report": fallback_summary}

    # Step 1: Image Verification
    try:
        image_verification = verify_image_report(report, image_path)
        diagnostics.append(f"image_verification_type={type(image_verification).__name__}")
        try:
            img_v_str = str(image_verification)
            diagnostics.append(f"image_verification_len={len(img_v_str)}")
            # keep short preview
            diagnostics.append(f"image_verification_preview={img_v_str[:500]}")
        except Exception:
            diagnostics.append("image_verification_preview_failed")
    except Exception as e:
        diagnostics.append("image_verification_exception:" + traceback.format_exc())
        fallback_summary = generate_fallback_summary(report, crime_type)
        combined = fallback_summary + "\n\n[DIAGNOSTICS]\n" + "\n".join(diagnostics)
        crime_repository_admin.save_aissistance_summary(complaint_id, combined)
        return {"summary_report": fallback_summary}

    # Step 2: Report Verification
    try:
        report_verification_result = run_report_verification(report, image_verification)
        diagnostics.append(f"report_verification_type={type(report_verification_result).__name__}")
        try:
            rv_str = str(report_verification_result)
            diagnostics.append(f"report_verification_len={len(rv_str)}")
            diagnostics.append(f"report_verification_preview={rv_str[:500]}")
        except Exception:
            diagnostics.append("report_verification_preview_failed")
    except Exception as e:
        diagnostics.append("report_verification_exception:" + traceback.format_exc())
        fallback_summary = generate_fallback_summary(report, crime_type)
        combined = fallback_summary + "\n\n[DIAGNOSTICS]\n" + "\n".join(diagnostics)
        crime_repository_admin.save_aissistance_summary(complaint_id, combined)
        return {"summary_report": fallback_summary}

    # Step 3: Risk Assessment
    try:
        risk_assessment = run_risk_assessment(report, image_verification, report_verification_result)
        diagnostics.append(f"risk_assessment_type={type(risk_assessment).__name__}")
        try:
            ra_str = str(risk_assessment)
            diagnostics.append(f"risk_assessment_len={len(ra_str)}")
            diagnostics.append(f"risk_assessment_preview={ra_str[:500]}")
        except Exception:
            diagnostics.append("risk_assessment_preview_failed")
    except Exception as e:
        diagnostics.append("risk_assessment_exception:" + traceback.format_exc())
        fallback_summary = generate_fallback_summary(report, crime_type)
        combined = fallback_summary + "\n\n[DIAGNOSTICS]\n" + "\n".join(diagnostics)
        crime_repository_admin.save_aissistance_summary(complaint_id, combined)
        return {"summary_report": fallback_summary}

    # Step 4: Summary Generation
    try:
        summary_report = summary_generator(image_verification, report_verification_result, risk_assessment)
        diagnostics.append(f"summary_report_type={type(summary_report).__name__}")
        try:
            sr_str = str(summary_report)
            diagnostics.append(f"summary_report_len={len(sr_str)}")
            diagnostics.append(f"summary_report_preview={sr_str[:500]}")
        except Exception:
            diagnostics.append("summary_report_preview_failed")
    except Exception as e:
        diagnostics.append("summary_generation_exception:" + traceback.format_exc())
        error_msg = f"⚠️ Summary generation failed: {str(e)}"
        combined = error_msg + "\n\n[DIAGNOSTICS]\n" + "\n".join(diagnostics)
        crime_repository_admin.save_aissistance_summary(complaint_id, combined)
        return {"summary_report": error_msg}

    # Handle None or empty summary_report
    if not summary_report:
        fallback_msg = "⚠️ AI summary generation returned no data. This may indicate API connectivity issues or insufficient data."
        combined = fallback_msg + "\n\n[DIAGNOSTICS]\n" + "\n".join(diagnostics)
        crime_repository_admin.save_aissistance_summary(complaint_id, combined)
        return {"summary_report": fallback_msg}

    # Normalize different possible response shapes from the summarization API
    assistant_content = None
    if isinstance(summary_report, dict):
        # Case 1: wrapper key 'summary_report' (legacy)
        if "summary_report" in summary_report and isinstance(summary_report["summary_report"], dict):
            choices = summary_report["summary_report"].get("choices")
        else:
            choices = summary_report.get("choices")

        if choices and isinstance(choices, list) and len(choices) > 0:
            first = choices[0]
            # OpenRouter-like shape: {'message': {'content': '...'}}
            if isinstance(first, dict) and "message" in first and isinstance(first["message"], dict) and "content" in first["message"]:
                assistant_content = first["message"]["content"]
            # Fallback: older shape with 'text'
            elif isinstance(first, dict) and "text" in first:
                assistant_content = first["text"]
    # If still None, stringify the whole response
    if assistant_content is None:
        try:
            assistant_content = str(summary_report)
        except Exception:
            assistant_content = ""

    # Final check - if assistant_content is empty, provide default message
    if not assistant_content or assistant_content.strip() == "":
        assistant_content = "AI analysis completed but no detailed output was generated. Please review the complaint details manually."

    # Save assistant content + diagnostics for troubleshooting (truncate diagnostics to avoid huge DB writes)
    diag_text = "\n".join(diagnostics)
    if len(diag_text) > 8000:
        diag_text = diag_text[:8000] + "\n...[truncated]"
    combined = str(assistant_content) + "\n\n[DIAGNOSTICS]\n" + diag_text
    crime_repository_admin.save_aissistance_summary(complaint_id, combined)
    return {"summary_report": assistant_content}

def get_complaints_history_by_email():
    complaints = crime_repository_admin.get_complaints_history_by_email()
    return complaints


def register_staff(fullname, email, staff_id, phone, gender, dob, rank, police_station, posting, location, state, password):
    """
    Register a new police staff member.
    
    Args:
        fullname: Staff member's full name
        email: Staff member's email
        staff_id: Unique staff ID
        phone: 10-digit phone number
        gender: Male/Female/Other
        dob: Date of birth (optional)
        rank: Police rank (Constable, Inspector, etc.)
        police_station: Assigned police station
        posting: Department/posting (e.g., Crime Branch)
        location: Location city
        state: State name
        password: Plain text password to be encrypted
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Encrypt the password
        encrypted_password = encrypt_message(password)
        
        # Call repository to save staff
        result = crime_repository_admin.save_staff(
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
            password=encrypted_password
        )
        
        if result:
            # Send welcome email to staff
            subject = "Staff Registration Successful"
            body = f"""
Welcome to the Crime Reporting System!

Dear {fullname},

Your staff account has been successfully registered with the following details:
- Staff ID: {staff_id}
- Rank: {rank}
- Police Station: {police_station}
- Location: {location}, {state}

You can now login using your email and password.

Best regards,
Admin Team
Crime Report System
            """
            send_email(email, subject, body)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error in register_staff service: {e}")
        return False


def get_all_staff():
    """
    Retrieve all registered staff members.
    
    Returns:
        List of staff tuples or empty list if error
    """
    try:
        staff_list = crime_repository_admin.get_all_staff()
        return staff_list if staff_list else []
    except Exception as e:
        print(f"Error fetching staff list: {e}")
        return []


def add_admin(fullname, email, phone, gender, password):
    """
    Add a new admin user to the system.
    
    Args:
        fullname: Admin's full name
        email: Admin's email (unique)
        phone: 10-digit phone number
        gender: Male/Female/Other
        password: Plain text password to be encrypted
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Step 1: Encrypt the password
        encrypted_password = encrypt_message(password)
        
        # Step 2: Call repository to save admin
        result = crime_repository_admin.save_admin(
            fullname=fullname,
            email=email,
            phone=phone,
            gender=gender,
            password=encrypted_password
        )
        
        if result:
            # Step 3: Send welcome email to admin
            subject = "Admin Account Created Successfully"
            body = f"""
Welcome to the Crime Reporting System Admin Panel!

Dear {fullname},

Your admin account has been successfully created. You now have full access to:
- View and manage crime complaints
- Review and assign complaints to police staff
- Register and manage police staff members
- Generate reports and analytics

Your login credentials:
- Email: {email}
- Password: [Use the password you set during registration]

You can login at: Admin Portal (Port 8000)

For security reasons:
- Do not share your password with anyone
- Change your password regularly
- Report any suspicious activity immediately

Best regards,
Crime Reporting System Administration
            """
            send_email(email, subject, body)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error in add_admin service: {e}")
        return False
