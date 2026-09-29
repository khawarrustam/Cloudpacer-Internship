"""
=============================================================================
DATABASE LAYER — Firebase Firestore Connection & Operations (MVC Pattern)
=============================================================================
Yeh file database (Firebase Firestore) ke sath connection bananey aur manage
karne ke liye use hoti hai. MVC architecture mein controller direct is DB layer
se database ka instance leta hai.

Kahan Connected Hai:
- Is file ka `connect_db()` aur `disconnect_db()`: `main_mvc.py` ke lifespan mein call hota hai.
- Is file ka `get_db()`: `src_mvc/controllers/todo_controller.py` mein Firestore collection access karne ke liye use hota hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'os' library: Operating system se interact karne ke liye (jaise environment variables
# parhna aur check karna ke serviceAccountKey.json file exist karti hai ya nahi).
import os

# 'firebase_admin': Google Firebase ka official Python SDK hai, jo app initialize karne ke liye use hota hai.
import firebase_admin

# 'credentials': Service account key JSON file ko authenticate aur verify karne ke liye.
# 'firestore': Firestore database ka client create karne aur queries chalane ke liye.
from firebase_admin import credentials, firestore


# Global variable jo database client ka reference save rakhega
_db = None


def get_db():
    """
    Kyun use ho raha hai:
    - Jab bhi kisi controller ko Firestore database ke sath read/write karna ho,
      toh yeh function database ka active client instance provide karta hai.

    Kaise kaam karta hai:
    - Global `_db` variable check karta hai. Agar database connected nahi hai (None hai),
      toh RuntimeError raise karta hai ke pehle connect_db() call karo.
    - Agar connected hai toh `_db` return karta hai.

    Kahan connected hai:
    - `src_mvc/controllers/todo_controller.py` ke `_collection()` function mein call hota hai.
    """
    global _db
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db


async def connect_db() -> None:
    """
    Kyun use ho raha hai:
    - Application startup par Firebase Firestore ke sath safe aur authenticated connection banata hai.

    Kaise kaam karta hai:
    1. Environment variable 'FIREBASE_CREDENTIALS_PATH' ya default 'serviceAccountKey.json' path check karta hai.
    2. Agar Firebase app pehle se initialize nahi hai, toh check karta hai file mojood hai ya nahi.
    3. Agar file mojood ho toh certificate se initialize karta hai, warna default environment credentials use karta hai.
    4. `firestore.client()` call karke global `_db` variable mein client store kar leta hai.

    Kahan connected hai:
    - `main_mvc.py` ke `lifespan(app)` startup event mein call hota hai.
    """
    global _db
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    if not firebase_admin._apps:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    _db = firestore.client()
    print("✅ Firebase Firestore connected")


async def disconnect_db() -> None:
    """
    Kyun use ho raha hai:
    - Application shutdown ke waqt graceful cleanup notice dene ke liye.

    Kaise kaam karta hai:
    - Firebase Admin SDK ko explicit disconnect ki zaroorat nahi hoti, is liye yeh ek log print karta hai.

    Kahan connected hai:
    - `main_mvc.py` ke `lifespan(app)` shutdown event mein call hota hai.
    """
    print("🔌 Firebase connection closed.")
