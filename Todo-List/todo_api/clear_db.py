import os
import firebase_admin
from firebase_admin import credentials, firestore, auth

def clear_firestore(db):
    print("Clearing Firestore...")
    
    # Delete top-level todos (old structure)
    todos = db.collection("todos").stream()
    count = 0
    for doc in todos:
        doc.reference.delete()
        count += 1
    print(f"Deleted {count} top-level todos.")

    # Delete nested todos (using collection_group)
    nested_todos = db.collection_group("todos").stream()
    nested_count = 0
    for doc in nested_todos:
        doc.reference.delete()
        nested_count += 1
        
    print(f"Deleted {nested_count} nested todos.")

def clear_auth():
    print("Clearing Auth users...")
    page = auth.list_users()
    count = 0
    while page:
        for user in page.users:
            auth.delete_user(user.uid)
            count += 1
        page = page.get_next_page()
    print(f"Deleted {count} auth users.")

if __name__ == "__main__":
    cred_path = "serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print("Error: serviceAccountKey.json not found!")
        exit(1)
        
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    clear_firestore(db)
    clear_auth()
    print("✅ Database cleared successfully!")
