"""
=============================================================================
CONTROLLER LAYER — Route Handlers & Orchestration (MVC Pattern)
=============================================================================
MVC architecture mein "Controller" central coordinator ya brain hota hai:
1. Client se aane wali HTTP requests ko pakarta hai.
2. View (Pydantic schemas) ke zariye input data validate karta hai.
3. Model ke functions ko call karke business rules chalata hai.
4. Database (Firestore) ke sath direct read/write operations karta hai.
5. Response View (TodoResponse) ke zariye client ko JSON wapis bhejta hai.

MVC vs Clean Architecture / DDD ka Farq:
- MVC mein Controller DB se direct baat karta hai aur use-case ka saara workflow
  isi controller ke andar likha hota hai (Tightly coupled).
- Clean Architecture (DDD) mein Controller sirf presentation layer hai;
  saara workflow Use Cases (Application Layer) mein hota hai aur DB
  Repositories (Infrastructure Layer) ke through abstract hoti hai.

Kahan Connected Hai:
- Is file ka `router`: `main_mvc.py` mein `app.include_router(todo_router)` ke zariye mount hota hai.
- Is file ke routes: Model (`src_mvc.models.todo_model`), View (`src_mvc.views.todo_views`),
  aur DB (`src_mvc.db.firebase`) ko aapas mein connect kartay hain.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'typing.List': Ek se zyada Todo items ka list response model define karne ke liye (List[TodoResponse]).
from typing import List

# 'APIRouter': FastAPI mein related routes ko ek group/module mein organize karne ke liye.
# 'HTTPException': Error aane par standard HTTP error status (400, 404 wagera) throw karne ke liye.
# 'status': HTTP status codes ke constants (jaise HTTP_201_CREATED, HTTP_404_NOT_FOUND) ke liye.
from fastapi import APIRouter, HTTPException, status

# MODEL IMPORTS: Business rules, data creation, aur custom exceptions jo model layer mein hain.
from src_mvc.models.todo_model import (
    create_todo_dict,
    mark_completed,
    validate_title,
    TodoNotFoundError,
    TodoAlreadyCompletedError,
    InvalidTitleError,
)

# VIEW IMPORTS: Request validation aur response formatting schemas.
from src_mvc.views.todo_views import CreateTodoRequest, TodoResponse

# DATABASE IMPORT: Firestore connection instance hasil karne ke liye.
from src_mvc.db.firebase import get_db


# APIRouter banaya gaya jo tamam Todo endpoints ko '/todos' prefix aur 'Todos' tag deta hai.
router = APIRouter(prefix="/todos", tags=["Todos"])

# Firestore collection ka naam jahan todos ke documents save honge.
COLLECTION = "todos"


# ---------------------------------------------------------------------------
# HELPER FUNCTION (Database Access):
# ---------------------------------------------------------------------------
def _collection():
    """
    Kyun use ho raha hai:
    - Har route mein baar baar `get_db().collection("todos")` likhne ke bajaye ek central helper.

    Kaise kaam karta hai:
    - `get_db()` se active Firestore client leta hai aur "todos" collection ka reference return karta hai.

    Kahan connected hai:
    - Is file ke tamam routes (create, list, get, complete, delete) is helper ko call karte hain.
    """
    return get_db().collection(COLLECTION)


# ---------------------------------------------------------------------------
# ROUTES / CONTROLLER HANDLERS:
# ---------------------------------------------------------------------------

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(req: CreateTodoRequest):
    """
    Kyun use ho raha hai:
    - Naya Todo task create karne ke liye (POST /todos).

    Kaise kaam karta hai (Flow):
    1. Input Data View Schema (`CreateTodoRequest`) ke zariye validate hota hai.
    2. Model ka `create_todo_dict()` function call hota hai jo title check karta hai aur naya dict banata hai.
    3. Agar title invalid ho toh `InvalidTitleError` catch karke 400 Bad Request phenk deta hai.
    4. Firestore collection mein document ID ke sath data save (.set()) karta hai.
    5. Save hone ke baad data ko `TodoResponse` View mein pack karke 201 Created status ke sath return karta hai.

    Data Flow:
    Client Request -> Controller -> Model (Validation & Factory) -> Firestore DB -> View Response -> Client
    """
    try:
        todo = create_todo_dict(title=req.title, priority=req.priority)
        _collection().document(todo["id"]).set(todo)
        return TodoResponse(**todo)
    except InvalidTitleError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        )


@router.get("", response_model=List[TodoResponse])
async def list_todos():
    """
    Kyun use ho raha hai:
    - Database mein mojood tamam Todos ki list lane ke liye (GET /todos).

    Kaise kaam karta hai (Flow):
    1. `_collection().stream()` ke zariye Firestore se saare documents fetch karta hai.
    2. Har document ko `.to_dict()` se Python dictionary mein convert karta hai.
    3. Saari dictionaries ko `TodoResponse` Pydantic models ki list bana kar return karta hai.

    Data Flow:
    Client Request -> Controller -> Firestore DB (fetch all) -> View Response List -> Client
    """
    docs = _collection().stream()
    todos = [doc.to_dict() for doc in docs]
    return [TodoResponse(**t) for t in todos]


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: str):
    """
    Kyun use ho raha hai:
    - Makhsoos ID ke zariye single Todo task fetch karne ke liye (GET /todos/{todo_id}).

    Kaise kaam karta hai (Flow):
    1. URL se `todo_id` hasil karta hai.
    2. Firestore se us ID ka document fetch karta hai (`.document(todo_id).get()`).
    3. Agar document mojood na ho (`not doc.exists`), toh 404 NOT FOUND HTTPException raise karta hai.
    4. Agar mojood ho toh data ko `TodoResponse` View mein convert karke return karta hai.

    Data Flow:
    Client Request -> Controller -> Firestore DB (find by ID) -> View Response -> Client
    """
    doc = _collection().document(todo_id).get()
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID '{todo_id}' was not found.",
        )
    return TodoResponse(**doc.to_dict())


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(todo_id: str):
    """
    Kyun use ho raha hai:
    - Kisi incomplete task ko mukammal (complete) mark karne ke liye (PATCH /todos/{todo_id}/complete).

    Kaise kaam karta hai (Flow):
    1. Firestore se document nikalta hai; agar na mile toh 404 NOT FOUND raise karta hai.
    2. Model layer ke `mark_completed(todo)` function ko call karta hai.
    3. Model check karta hai agar task already completed hai toh `TodoAlreadyCompletedError` raise karta hai,
       jisko controller pakar kar 400 BAD REQUEST return karta hai.
    4. Agar pehle se complete nahi tha, toh Firestore mein `is_completed=True` aur `completed_at` update karta hai.
    5. Updated todo ko `TodoResponse` View ke zariye client ko return karta hai.

    Data Flow:
    Client Request -> Controller -> Firestore (get) -> Model (business rule) -> Firestore (update) -> View Response -> Client
    """
    doc_ref = _collection().document(todo_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID '{todo_id}' was not found.",
        )
    todo = doc.to_dict()

    try:
        updated = mark_completed(todo)
    except TodoAlreadyCompletedError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        )

    doc_ref.update({
        "is_completed": True,
        "completed_at": updated["completed_at"]
    })
    return TodoResponse(**updated)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str):
    """
    Kyun use ho raha hai:
    - Database se kisi Todo ko mukammal taur par delete karne ke liye (DELETE /todos/{todo_id}).

    Kaise kaam karta hai (Flow):
    1. URL se `todo_id` hasil karta hai.
    2. Check karta hai document exist karta hai ya nahi; agar nahi toh 404 NOT FOUND deta hai.
    3. Agar mojood ho toh Firestore se `.delete()` call karke delete kar deta hai.
    4. 204 NO CONTENT status return karta hai (yani koi body nahi bhejni, task delete ho gaya).

    Data Flow:
    Client Request -> Controller -> Firestore DB (delete) -> 204 Status -> Client
    """
    doc_ref = _collection().document(todo_id)
    if not doc_ref.get().exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID '{todo_id}' was not found.",
        )
    doc_ref.delete()
