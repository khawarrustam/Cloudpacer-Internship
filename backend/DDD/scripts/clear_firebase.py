"""Delete all Firebase todos and users.

Run this file only when you really want to clear the development database.
"""

import os

import firebase_admin
from firebase_admin import auth, credentials, firestore


def clear_firestore(database):
    print("Clearing Firestore. Roman Urdu: Firestore saaf ho raha hai.")

    top_level_count = 0
    for document in database.collection("todos").stream():
        document.reference.delete()
        top_level_count += 1
    print(
        f"Deleted {top_level_count} old todos. "
        f"Roman Urdu: {top_level_count} puranay todos delete huay."
    )

    nested_count = 0
    for document in database.collection_group("todos").stream():
        document.reference.delete()
        nested_count += 1
    print(
        f"Deleted {nested_count} user todos. "
        f"Roman Urdu: {nested_count} user todos delete huay."
    )


def clear_auth_users():
    print("Clearing users. Roman Urdu: Users delete ho rahe hain.")

    count = 0
    page = auth.list_users()
    while page:
        for user in page.users:
            auth.delete_user(user.uid)
            count += 1
        page = page.get_next_page()

    print(
        f"Deleted {count} users. "
        f"Roman Urdu: {count} users delete huay."
    )


if __name__ == "__main__":
    credentials_path = "serviceAccountKey.json"

    if not os.path.exists(credentials_path):
        print(
            "Error: serviceAccountKey.json was not found. "
            "Roman Urdu: serviceAccountKey.json file nahi mili."
        )
        raise SystemExit(1)

    firebase_admin.initialize_app(
        credentials.Certificate(credentials_path)
    )
    db = firestore.client()

    clear_firestore(db)
    clear_auth_users()
    print(
        "Database cleared successfully. "
        "Roman Urdu: Database kamyabi se saaf ho gaya."
    )
