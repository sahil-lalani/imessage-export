from iphone_backup_decrypt import EncryptedBackup, RelativePath, MatchFiles
import getpass
import sqlite3
import json
from datetime import datetime, timedelta

def decrypt_backup():
    try:
        passphrase = getpass.getpass("Enter the passphrase: ")  # Ask for passphrase securely
        backup_path = r"C:\Users\[user]\Apple\MobileSync\Backup\[device-hash]"
        # Or MacOS: "/Users/[user]/Library/Application Support/MobileSync/Backup/[device-hash]"

        backup = EncryptedBackup(backup_directory=backup_path, passphrase=passphrase)

        # Extract imessages
        backup.extract_file(relative_path=RelativePath.TEXT_MESSAGES, 
                            output_filename="./imessage.sqlite")
        # Extract contacts
        backup.extract_file(relative_path=RelativePath.ADDRESS_BOOK, 
                            output_filename="./contacts.sqlite")
            
        print("Backup decrypted successfully!")
        return True  # Return True if successful
    except ValueError as e:
        if "incorrect passphrase" in str(e).lower():
            print("Incorrect passphrase. Please try again.")
        else:
            print(f"Another error occurred: {e}")
        return False  # Return False if there was an error

def apple_time_to_iso(apple_timestamp):
    # Convert Apple timestamp (nanoseconds) to seconds
    seconds_since_reference = apple_timestamp / 1_000_000_000

    # Apple's reference date is January 1, 2001
    reference_date = datetime(2001, 1, 1)

    # Calculate the actual date
    actual_date = reference_date + timedelta(seconds=seconds_since_reference)

    # Convert to ISO 8601 format
    iso_string = actual_date.isoformat()

    return iso_string

# Connect to the iMessage SQLite database
def get_imessage_data():
    imessage_conn = sqlite3.connect('imessage.sqlite')
    imessage_cursor = imessage_conn.cursor()

    # Connect to the contacts SQLite database
    contacts_conn = sqlite3.connect('contacts.sqlite')
    contacts_cursor = contacts_conn.cursor()

    # Query to fetch messages
    message_query = """
    SELECT 
        message.ROWID,
        message.text,
        message.date,
        handle.id as contact,
        message.is_from_me
    FROM 
        message 
    LEFT JOIN 
        handle ON message.handle_id = handle.ROWID
    ORDER BY 
        message.date DESC
    """

    # Query to fetch contacts
    contact_query = """
    SELECT 
        CASE
            WHEN c0First IS NOT NULL AND c1Last IS NOT NULL THEN c0First || ' ' || c1Last
            WHEN c0First IS NOT NULL THEN c0First
            ELSE "NO CONTACT"
        END as full_name,
        c16Phone
    FROM 
        ABPersonFullTextSearch_content
    WHERE 
        c16Phone IS NOT NULL AND c16Phone != ''
    """

    # Execute queries
    imessage_cursor.execute(message_query)
    contacts_cursor.execute(contact_query)

    # Fetch all results
    messages = imessage_cursor.fetchall()
    contacts = contacts_cursor.fetchall()

    # save contacts to a JSON!!
    with open('contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)

    # Create a dictionary to map phone numbers to names
    contact_dict = {}
    for full_name, phone in contacts: 
        # Remove any non-digit characters from the phone number
        clean_phone = ''.join(filter(str.isdigit, phone))
        # Store multiple versions of the phone number
        if len(clean_phone) >= 10:
            contact_dict[clean_phone[-10:]] = full_name.strip()  # Last 10 digits
            contact_dict[clean_phone[-7:]] = full_name.strip()   # Last 7 digits
            if len(clean_phone) > 10:
                contact_dict[clean_phone[-11:]] = full_name.strip()  # Last 11 digits (with country code)

    # Convert to list of dictionaries
    message_list = []
    for msg in messages:
        contact = msg[3]
        if contact:
            # Remove any non-digit characters from the contact
            clean_contact = ''.join(filter(str.isdigit, contact)) or contact
            # Try to match with different lengths
            if len(clean_contact) >= 10:
                name = contact_dict.get(clean_contact[-10:], contact)
            if len(clean_contact) >= 7:
                name = contact_dict.get(clean_contact[-7:], name)
            if len(clean_contact) > 10:
                name = contact_dict.get(clean_contact[-11:], name)
        
        if msg[1] is not None:
            message_list.append({
                'id': msg[0],
                'text': msg[1],
                'date': apple_time_to_iso(msg[2]) if msg[2] is not None else None,
                'contact': name,
                'is_from_me': True if msg[4] == 1 else False
            })

    # Close the database connections
    imessage_conn.close()
    contacts_conn.close()

    # Save to JSON file
    with open('imessage_data.json', 'w') as f:
        json.dump(message_list, f, indent=2)

    print("Data saved to imessage_data.json")

if __name__ == "__main__":
    if decrypt_backup():
        get_imessage_data()
    else:
        print("Backup decryption failed. iMessage data extraction skipped.")