from flask import url_for
from app.util.db_connection import get_connection
from mysql.connector import Error

def debug_print_all_emails():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        query = "SELECT email FROM user_table"
        cursor.execute(query)
        emails = cursor.fetchall()
        print("[DEBUG] Emails in user_table:")
        for row in emails:
            print(row[0])
    except Exception as e:
        print(f"[DEBUG] Error fetching all emails: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def save_user(fullname, email, phonenumber, dob, gender, encrypted_password,role):
    connection = get_connection()
    if connection is None:
        return False
    try: 
        cursor = connection.cursor()
        query = """INSERT INTO user_table(fullname, email, dob, phonenumber, gender, password, role) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (fullname, email, dob, phonenumber, gender, encrypted_password,role)
        cursor.execute(query, values)
        connection.commit()
        return True
    except Error as e:
        print(f"Error while saving user to MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def getDataByPhone(phoneNo):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """SELECT * FROM user_table WHERE phonenumber = %s"""
        values = (phoneNo,)  # tuple with one element
        cursor.execute(query, values)
        
        result = cursor.fetchone()  # Fetching a single record
        
        if result:
            return result  # If the user is found, return the result
        else:
            return False  # If not found, return False
    
    except Error as e:
        print(f"Error while fetching user by phone number from MySQL: {e}")
        return False
    
    finally:
        # Ensure both cursor and connection are properly closed if they were opened
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def getDataByEmail(email):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """SELECT * FROM user_table WHERE email = %s"""
        values = (email,)  # tuple with one element
        cursor.execute(query, values)
        
        result = cursor.fetchone()  # Fetching a single record
        
        if result:
            return result  # If the user is found, return the result
        else:
            return False  # If not found, return False
    
    except Error as e:
        print(f"Error while fetching user by email from MySQL: {e}")
        return False
    
    finally:
        # Ensure both cursor and connection are properly closed if they were opened
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def save_crime(fullname, emailid, phoneNo, aadhaarNo, Address, crimeDate, LOC, crimeType, 
               detailedDescription, idProof_path, evidence_path, bankName, transactionId, 
               fraudAmount, suspectProfile, suspectContact, victimAge, relationship, 
               incidentType, theftType, suspectDescription, status):
    connection = get_connection()
    if connection is None:
        return False
    try: 
        cursor = connection.cursor()
        query = """INSERT INTO crime_report(fullname, emailid, phoneNo, aadhaarNo, Address, crimeDate, LOC, crimeType, 
                   detailedDescription, idProof_path, evidence_path, bankName, transactionId, 
                   fraudAmount, suspectProfile, suspectContact, victimAge, relationship, 
                   incidentType, theftType, suspectDescription, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (fullname, emailid, phoneNo, aadhaarNo, Address, crimeDate, LOC, crimeType,
                    detailedDescription, idProof_path, evidence_path, bankName, transactionId, 
                    fraudAmount, suspectProfile, suspectContact, victimAge, relationship, 
                    incidentType, theftType, suspectDescription, status)
        cursor.execute(query, values)
        connection.commit()
        return True
    except Error as e:
        print(f"Error while saving crime report to MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_complaint_tracking_data(email):
    connection = None
    cursor = None
    complaint_list = [] 
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """SELECT id, fullname, emailid, crimeDate, LOC, crimeType, status FROM crime.crime_report WHERE emailid = %s AND status IN ('Pending', 'Progress');"""
        values = (email,)
        cursor.execute(query, values)
        results = cursor.fetchall()
        for row in results:
            complaint_list.append(row)
        return complaint_list
    except Error as e:
        print(f"Error while fetching complaint tracking data from MySQL: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_crime_details_by_id(complaint_id,email):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """SELECT * FROM crime.crime_report WHERE id = %s AND emailid = %s;"""
        values = (complaint_id,email)
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Error while fetching crime details by ID from MySQL: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def complaints_history_by_email(email):
    connection = None
    cursor = None
    complaint_list = [] 
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """SELECT id, fullname, emailid, crimeDate, LOC, crimeType, status FROM crime.crime_report WHERE emailid = %s;"""
        values = (email,)
        cursor.execute(query, values)
        results = cursor.fetchall()
        for row in results:
            complaint_list.append(row)
        return complaint_list
    except Error as e:
        print(f"Error while fetching complaints history by email from MySQL: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def update_user_password(email, encrypted_password):
    connection = get_connection()   
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """UPDATE user_table SET password = %s WHERE email = %s"""
        values = (encrypted_password, email)
        cursor.execute(query, values)
        connection.commit()
        return True     
    except Error as e:
        print(f"Error while updating user password in MySQL: {e}")
        return False    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_emergency(fullname, email, phoneNo, locations, emergencyType, description, media_path, datetime, status):
    connection = get_connection()
    if connection is None:
        return False
    try: 
        cursor = connection.cursor()
        # Truncate fields that may exceed column limits (safety guard)
        locations = locations[:255] if locations else ""
        media_path = media_path[:255] if media_path else ""

        query = """INSERT INTO emergency_report(fullname, email, phoneNo, location, emergencyType, description, media_path, datetime, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (fullname, email, phoneNo, locations, emergencyType, description, media_path, datetime, status)
        cursor.execute(query, values)
        connection.commit()
        return True
    except Error as e:
        print(f"Error while saving emergency report to MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
