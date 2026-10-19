"""
=============================================================================
ENTRY POINT — FastAPI App Configuration & Lifespan (MVC Pattern)
=============================================================================
Yeh file pooray Todo MVC project ka Entry Point (Main Starting File) hai.
FastAPI application initialize karna, database connect karna, routes mount karna,
aur server start karna isi file ka kaam hai.

Chalanay Ka Tareeqa:
  uvicorn main_mvc:app --host 127.0.0.1 --port 8001 --reload

MVC vs Clean Architecture / DDD ka Farq:
- MVC mein wiring bohot direct hai: Controller ka router include hota hai,
  aur controller direct database se judaa hota hai.
- DDD mein `main.py` Dependency Injection karta hai (Repository choose karta hai,
  Use Cases banata hai, aur unhe FastAPI routes mein inject karta hai).

Kahan Connected Hai:
- Yeh file `src_mvc/controllers/todo_controller.py` ko import karke routes register karti hai.
- `src_mvc/db/firebase.py` se `connect_db` aur `disconnect_db` mangwa kar application ke startup/shutdown par chalati hai.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'sys' aur 'pathlib.Path': Current project directory ka absolute path nikal kar
# Python ke search path (`sys.path`) mein daalne ke liye, taake 'src_mvc' ke imports
# bina kisi error ke successfully load ho sakein.
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# 'asynccontextmanager': FastAPI ke modern lifespan event system ke liye (startup aur shutdown logic ko ek jagah manage karna).
from contextlib import asynccontextmanager

# 'FastAPI': Python ka fast aur asynchronous web framework jo REST APIs banane ke liye use hota hai.
from fastapi import FastAPI

# CONTROLLER IMPORT: Tamam Todo endpoints (POST, GET, PATCH, DELETE) ka router.
from src_mvc.controllers.todo_controller import router as todo_router
from src_mvc.controllers.auth_controller import router as auth_router

# DATABASE LIFECYCLE IMPORTS: Firebase Firestore ko initialize aur close karne wale functions.
from src_mvc.db.firebase import connect_db, disconnect_db


# ---------------------------------------------------------------------------
# LIFESPAN CONTEXT MANAGER (Startup & Shutdown Lifecycle):
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Kyun use ho raha hai:
    - FastAPI app ke start hotay waqt aur band hotay waqt zaroori tasks chalane ke liye.

    Kaise kaam karta hai:
    1. 'yield' se pehle: `connect_db()` chalta hai jo Firebase Firestore ko connect karta hai.
    2. 'yield': Jab tak application chal rahi hoti hai, yahan rehti hai.
    3. 'yield' ke baad: Jab server stop kiya jata hai, toh `disconnect_db()` chalta hai.

    Kahan connected hai:
    - FastAPI instance (`app = FastAPI(..., lifespan=lifespan)`) ke sath jurra hua hai.
    """
    await connect_db()
    yield
    await disconnect_db()


# ---------------------------------------------------------------------------
# FASTAPI APPLICATION INSTANCE:
# ---------------------------------------------------------------------------
# FastAPI app banayi gayi jisme metadata (title, description) aur lifespan attach kiya gaya hai.
app = FastAPI(
    title="Todo MVC API",
    description="Traditional MVC Architecture with FastAPI & Firebase Firestore — "
    "Compare with the DDD/Onion Clean Architecture version!",
    lifespan=lifespan,
)

# Controller ke router ko main app mein shaamil (include) karna
app.include_router(todo_router)
app.include_router(auth_router)


# ---------------------------------------------------------------------------
# HEALTH CHECK ENDPOINT:
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    """
    Kyun use ho raha hai:
    - Yeh check karne ke liye ke API zinda hai aur theek se chal rahi hai.
    - JSON return karta hai: {"status": "ok", "architecture": "MVC"}
    """
    return {"status": "ok", "architecture": "MVC"}


# ---------------------------------------------------------------------------
# DIRECT SCRIPT RUNNER:
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 'uvicorn': ASGI web server jo Python async apps ko host karta hai.
    # Jab yeh file direct run ki jaye: python main_mvc.py
    import uvicorn

    uvicorn.run("main_mvc:app", host="127.0.0.1", port=8001, reload=True)
