from app.util.db_connection import get_connection
from mysql.connector import Error

def validate_admin_login(email):
    print("Validating admin login for email:", email)
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """SELECT * FROM crime.admin_user WHERE email = %s"""
        values = (email,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        if result:
            print("Admin login validated for email:", result)
            return result
        else:
            return False
    except Error as e:
        print(f"Error while validating admin login from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
def validate_staff_login(email):
    """Validate staff login credentials by email. Returns staff tuple or False."""
    print("Validating staff login for email:", email)
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """SELECT * FROM crime.staff_table WHERE email = %s"""
        values = (email,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        if result:
            print("Staff login validated for email:", result)
            return result
        else:
            return False
    except Error as e:
        print(f"Error while validating staff login from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_complaints():
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """SELECT id, fullname,crimeDate,LOC, crimeType, detailedDescription, status FROM crime.crime_report WHERE status='Pending' OR status='Progress';"""
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
            return result
        else:
            return False
    except Error as e:
        print(f"Error while fetching complaints from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def get_complaint_by_id(complaint_id):
    connection = get_connection()
    if connection is None:
        return False
    try:
        # return a dictionary so callers can reliably access columns by name
        cursor = connection.cursor(dictionary=True)
        query = """SELECT * FROM crime.crime_report WHERE id = %s"""
        values = (complaint_id,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        if result:
            print ("Fetched complaint:", result)
            return result
        else:
            return False
    except Error as e:
        print(f"Error while fetching complaints history by email from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_staff(fullname, email, staff_id, phone, gender, dob, rank, police_station, posting, location, state, password):
    """
    Save a new staff member to the database.
    
    Args:
        fullname, email, staff_id, phone, gender, dob, rank, police_station, posting, location, state, password
        password is already encrypted
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO `crime`.`staff_table`
            (`fullname`, `email`, `staff_id`, `phone`, `gender`, `dob`, `rank`, `police_station`, `posting`, `location`, `state`, `password`, `status`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Active')
        """
        values = (fullname, email, staff_id, phone, gender, dob, rank, police_station, posting, location, state, password)
        cursor.execute(query, values)
        connection.commit()
        print(f"Staff member {fullname} saved successfully")
        return True
    except Error as e:
        print(f"Error while saving staff to MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_all_staff():
    """
    Retrieve all staff members from the database.
    
    Returns:
        List of staff tuples or False if error
    """
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            SELECT `id`, `fullname`, `email`, `staff_id`, `phone`, `gender`, `dob`, `rank`, `police_station`, `posting`, `location`, `state`, `password`, `status`
            FROM `crime`.`staff_table`
            ORDER BY `id` DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
            return result
        else:
            return False
    except Error as e:
        print(f"Error while fetching staff from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_staff_by_id(staff_id):
    """
    Retrieve a specific staff member by ID.
    
    Args:
        staff_id: Database ID of the staff member
    
    Returns:
        Staff tuple or False if not found
    """
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            SELECT * FROM crime.staff_table WHERE id = %s
        """
        values = (staff_id,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result if result else False
    except Error as e:
        print(f"Error while fetching staff by ID from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_admin(fullname, email, phone, gender, password):
    """
    Save a new admin user to the database.
    
    Args:
        fullname: Admin's full name
        email: Admin's email (unique)
        phone: 10-digit phone number
        gender: Male/Female/Other
        password: Already encrypted password
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO crime.admin_user 
            (fullname, email, phone, gender, password, status)
            VALUES (%s, %s, %s, %s, %s, 'Active')
        """
        values = (fullname, email, phone, gender, password)
        cursor.execute(query, values)
        connection.commit()
        print(f"Admin {fullname} saved successfully")
        return True
    except Error as e:
        print(f"Error while saving admin to MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_admin_password(admin_id, new_encrypted_password):
    """
    Update the admin's password in the database (used for migrating plaintext to encrypted passwords).
    """
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            UPDATE crime.admin_user
            SET password = %s, updated_at = NOW()
            WHERE id = %s
        """
        values = (new_encrypted_password, admin_id)
        cursor.execute(query, values)
        connection.commit()
        print(f"Admin password for id={admin_id} updated successfully")
        return True
    except Error as e:
        print(f"Error while updating admin password in MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_all_admins():
    """
    Retrieve all admin users from the database.
    
    Returns:
        List of admin tuples or False if error
    """
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            SELECT id, fullname, email, phone, gender, password, status, created_at
            FROM crime.admin_user
            ORDER BY created_at DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        return result if result else False
    except Error as e:
        print(f"Error while fetching admins from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_admin_by_id(admin_id):
    """
    Retrieve a specific admin by ID.
    
    Args:
        admin_id: Database ID of the admin
    
    Returns:
        Admin tuple or False if not found
    """
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            SELECT * FROM crime.admin_user WHERE id = %s
        """
        values = (admin_id,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result if result else False
    except Error as e:
        print(f"Error while fetching admin by ID from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_complaints_history_by_email():
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """SELECT id, fullname, crimeDate, LOC, crimeType, status FROM crime.crime_report """
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
            return result
        else:
            return False
    except Error as e:
        print(f"Error while fetching complaints history by email from MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def save_aissistance_summary(complaint_id, summary_report):
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            UPDATE crime.crime_report
            SET ai_summaries = %s
            WHERE id = %s
        """
        values = (summary_report, complaint_id)
        cursor.execute(query, values)
        connection.commit()
        print(f"AI assistance summary for complaint id={complaint_id} saved successfully")
        return True
    except Error as e:
        print(f"Error while saving AI assistance summary to MySQL: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_complaint_status(complaint_id, status, remarks=None):
    """
    Update the status and optional remarks for a complaint.
    """
    connection = get_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """
            UPDATE crime.crime_report
            SET status = %s,
                remarks = %s,
                updated_at = NOW()
            WHERE id = %s
        """
        values = (status, remarks, complaint_id)
        cursor.execute(query, values)
        connection.commit()
        print(f"Complaint id={complaint_id} updated to status={status}")
        return True
    except Error as e:
        print(f"Error while updating complaint status in MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()