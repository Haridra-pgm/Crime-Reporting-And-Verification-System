#crime_service.py
import os
import shutil
from app.util.encryption import encrypt_message
from app.util.encryption  import decrypt_message
from app.repository import crime_repository
import re
from werkzeug.utils import secure_filename
from datetime import datetime
from app.util.otp_generate import generate_otp
from app.util.mail_handler import send_email


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4', 'mov'}
idProof_UPLOAD_FOLDER = 'app\\crime_image\\idProof'
evidence_UPLOAD_FOLDER = 'app\\crime_image\\evidence'
emergency_UPLOAD_FOLDER = 'app\\crime_image\\emergency'

def register_user(fullname, email, phonenumber, dob, gender, password, confirm_password):
    if password != confirm_password:
        return False

    role = "user"
    encrypted_password = encrypt_message(password)
    isSaved = crime_repository.save_user(fullname, email, phonenumber, dob, gender, encrypted_password, role)

    return bool(isSaved)

def login(userName, password):
    # Define regex patterns for phone and email
    phoneRegex = r'^[0-9]{10}$'
    emailRegex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

    # Validate phone number (10 digits)
    if re.match(phoneRegex, userName):
        userData = crime_repository.getDataByPhone(userName)
    elif re.match(emailRegex, userName):
        userData = crime_repository.getDataByEmail(userName)
    else:
        return "Invalid_Username"
    print(userData)
    if(userData):
        password_decrypt = decrypt_message(userData[6])

        if password_decrypt == password:
            return ("Success", userData[7], userData[2])
        else:
            # Return consistent error string matching controller checks
            return "Invalid_Password"
    else:
        # Standardize return value to match controller expectations
        return "UserNotFound"

# Helper function to check allowed file types
def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'mp4', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Function to save ID Proof with timestamp in the filename
def save_idProof(emailid, idProof):
    # Ensure the file is of allowed type and under the size limit
    if not allowed_file(idProof.filename):
        raise ValueError('Invalid ID Proof file type. Allowed types: jpg, jpeg, png')
    if idProof.content_length > 5 * 1024 * 1024:  # Max size 5MB
        raise ValueError('ID Proof file is too large')

    # Generate a new file name using emailid, the current date & time, and the original file extension
    extension = idProof.filename.rsplit('.', 1)[1].lower()
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")  # Current date and time as string
    new_filename = f"{emailid}_idProof_{current_datetime}.{extension}"
    new_filename = secure_filename(new_filename)

    # Save the file in the UPLOAD_FOLDER
    file_path = os.path.join(idProof_UPLOAD_FOLDER, new_filename)
    idProof.save(file_path)
    return file_path  # Return file path for reference if needed

# Function to save Evidence with timestamp in the filename
def save_evidence(emailid, evidence):
    # Ensure the file is of allowed type and under the size limit
    if not allowed_file(evidence.filename):
        raise ValueError('Invalid Evidence file type. Allowed types: jpg, jpeg, png, mp4, mov')
    if evidence.content_length > 10 * 1024 * 1024:  # Max size 10MB
        raise ValueError('Evidence file is too large')

    # Generate a new file name using emailid, the current date & time, and the original file extension
    extension = evidence.filename.rsplit('.', 1)[1].lower()
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")  # Current date and time as string
    new_filename = f"{emailid}_evidence_{current_datetime}.{extension}"
    new_filename = secure_filename(new_filename)

    # Save the file in the UPLOAD_FOLDER
    file_path = os.path.join(evidence_UPLOAD_FOLDER, new_filename)
    evidence.save(file_path)
    return file_path  # Return file path for reference if needed


def save_media(emailid, media):
    # Check if media file exists and has a filename
    if not media or not media.filename:
        raise ValueError('Media file is required')
    
    # Ensure the file is of allowed type and under the size limit
    if not allowed_file(media.filename):
        raise ValueError('Invalid media file type. Allowed types: jpg, jpeg, png, mp4, mov')
    if media.content_length > 10 * 1024 * 1024:  # Max size 10MB
        raise ValueError('Media file is too large')

    # Generate a new file name using emailid, the current date & time, and the original file extension
    extension = media.filename.rsplit('.', 1)[1].lower()
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")  # Current date and time as string
    new_filename = f"{emailid}_emergency_{current_datetime}.{extension}"
    new_filename = secure_filename(new_filename)

    # Save the file in the UPLOAD_FOLDER
    file_path = os.path.join(emergency_UPLOAD_FOLDER, new_filename)
    media.save(file_path)
    return file_path  # Return file path for reference if needed

def create_google_maps_link(location):
    # Regular expression to extract lat and lon from the string
    match = re.search(r"Lat:\s*(-?\d+\.\d+),\s*Lon:\s*(-?\d+\.\d+)", location)
    
    if match:
        lat = match.group(1)
        lon = match.group(2)
        return f"https://www.google.com/maps?q={lat},{lon}"
    else:
        return location
def getallinputbyEmail(email):
    userData = crime_repository.getDataByEmail(email)
    return userData

def register_crime(fullname, emailid, phoneNo, aadhaarNo, Address, crimeDate, LOC, crimeType, 
                    detailedDescription, idProof, evidence,bankName, transactionId, fraudAmount, 
                    suspectProfile, suspectContact, victimAge, relationship, incidentType,
                    theftType, suspectDescription):
    if not idProof or not evidence:
        return 'Both ID Proof and Evidence files are required', 400

    try:
        # Save both ID Proof and Evidence files using the helper functions
        idProof_path = save_idProof(emailid, idProof)
        evidence_path = save_evidence(emailid, evidence)
    except ValueError as e:
        # Handle any validation errors (e.g., file type or size)
        return str(e), 400
    status = "Pending"
    isSaved = crime_repository.save_crime(fullname, emailid, phoneNo, aadhaarNo, Address, crimeDate, LOC, crimeType, 
                                        detailedDescription, idProof_path, evidence_path, bankName, transactionId, 
                                        fraudAmount, suspectProfile, suspectContact, victimAge, relationship, 
                                        incidentType, theftType, suspectDescription, status)
    return isSaved

def get_complaint_tracking_data(email):
    complaint_data = crime_repository.get_complaint_tracking_data(email)
    print(complaint_data)
    return complaint_data

def get_complaint_details(complaint_id,email):
    complaint_data = crime_repository.get_crime_details_by_id(complaint_id,email)
    return complaint_data

def get_complaints_history_by_email(email):
    complaint_data = crime_repository.complaints_history_by_email(email)
    return complaint_data

def check_user_exists(email):
    email_exists = crime_repository.getDataByEmail(email)
    if email_exists:
        return True
    return False

def send_otp_to_email(email):
    otp= generate_otp()
    subject = "Your OTP for Password Reset"
    message = f"Your OTP for password reset is: {otp}. It is valid for 10 minutes."
    sendemail=send_email(email, subject, message)
    if sendemail:
        return otp
    else:
        return False

def reset_password(email, new_password):
    userData = crime_repository.getDataByEmail(email)
    if userData:
        encrypted_password = encrypt_message(new_password)
        isUpdated = crime_repository.update_user_password(email, encrypted_password)
        return isUpdated
    else:
        return False

def register_emergency(fullname, email, phoneNo, location, emergencyType, description, media, datetime):
    if not media:
        return 'Media file is required', 400
    try:
        # Save media file using the helper function
        media_path = save_media(email, media)
        locations = create_google_maps_link(location)

        # Reduce location size to avoid DB column overflow.
        # If locations is a Google Maps URL containing coordinates, extract lat,lon to store a short value.
        short_location = locations
        try:
            m = re.search(r"q=([-0-9.]+),([-0-9.]+)", locations)
            if m:
                short_location = f"{m.group(1)},{m.group(2)}"
            # Fallback: if the location is long, truncate to 255 chars
            if len(short_location) > 255:
                short_location = short_location[:255]
        except Exception:
            # On any parsing error, ensure we still truncate
            short_location = (locations[:255] if locations else "")

        status = "Pending"
        isSaved = crime_repository.save_emergency(fullname, email, phoneNo, short_location, emergencyType, description, media_path, datetime, status)
        if isSaved:
            send_email_notification = send_email(email, "Emergency Report Successfully Registered", f"""
            Dear {fullname},

            Thank you for submitting your emergency report. We have successfully registered your report submitted on **{datetime}**.

            **Emergency Report Summary:**
            - **Type of Emergency:** {emergencyType}
            - **Location:** {locations}
            - **Description:** {description}
            - **Date and Time of Report:** {datetime}

            Our team is actively reviewing the details you provided. If additional information is needed, we will contact you directly. In the meantime, you can track the status of your emergency report by clicking the link below:

            [Track Your Emergency Report Status](https://www.emergencyresponse.com/status/{status})

            **Important:** If this is a critical or life-threatening situation, we strongly advise you to contact local emergency services immediately.

            We understand the urgency of your situation and are here to assist you in any way we can. Should you have any further questions, feel free to reply to this email, and one of our team members will get back to you as soon as possible.

            Stay safe, and thank you for trusting us with your emergency report.

            Best regards,  
            The Emergency Response Team  
            [Emergency Response Website](https://www.emergencyresponse.com)
            """)
            if send_email_notification:
                return True
            else:
                return False
        else:
            return False
    except ValueError as e:
        # Handle any validation errors (e.g., file type or size)
        return str(e), 400

