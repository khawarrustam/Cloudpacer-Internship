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
from typing import List
from fastapi import APIRouter, HTTPException, status

from src_mvc.models.todo_model import (
    create_todo_dict,
    mark_completed,
    validate_title,
    TodoNotFoundError,
    TodoAlreadyCompletedError,
    InvalidTitleError,
)
from src_mvc.views.todo_views import CreateTodoRequest, TodoResponse
from src_mvc.db.firebase import get_db


router = APIRouter(prefix="/todos", tags=["Todos"])
COLLECTION = "todos"


def _collection():
    return get_db().collection(COLLECTION)


# ---------------------------------------------------------------------------
# ROUTES / CONTROLLER HANDLERS:
# ---------------------------------------------------------------------------

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(req: CreateTodoRequest):
    print("\n" + "="*60)
    print("📥 [MVC] REQUEST RECEIVED")
    print("="*60)
    print(f"   📂 File    : src_mvc/controllers/todo_controller.py")
    print(f"   🔧 Function: create_todo()")
    print(f"   🌐 Route   : POST /todos")
    print(f"   📝 Title   : {req.title}")
    print(f"   🎯 Priority: {req.priority}")
    print("-"*60)
    print("   ➡️  STEP 1: Controller → calling Model (todo_model.py)")
    print("              Function: create_todo_dict(title, priority)")

    try:
        todo = create_todo_dict(title=req.title, priority=req.priority)

        print(f"   ✅ STEP 2: Model returned new todo dict")
        print(f"              ID         : {todo['id']}")
        print(f"              Title      : {todo['title']}")
        print(f"              Priority   : {todo['priority']}")
        print(f"              created_at : {todo['created_at']}")
        print("-"*60)
        print(f"   ➡️  STEP 3: Controller → saving to Firestore DB")
        print(f"              Collection : '{COLLECTION}'")
        print(f"              Document ID: {todo['id']}")

        _collection().document(todo["id"]).set(todo)

        print(f"   ✅ STEP 4: Firestore saved successfully!")
        print("-"*60)
        print("   ➡️  STEP 5: Building TodoResponse (View)")
        print("              File: src_mvc/views/todo_views.py → TodoResponse")
        print("   📤 STEP 6: Sending Response to Client | Status: 201 Created")
        print("="*60 + "\n")

        return TodoResponse(**todo)

    except InvalidTitleError as err:
        print(f"   ❌ InvalidTitleError caught in Controller!")
        print(f"      Detail: {str(err)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("", response_model=List[TodoResponse])
async def list_todos():
    print("\n" + "="*60)
    print("📥 [MVC] REQUEST RECEIVED")
    print("="*60)
    print(f"   📂 File    : src_mvc/controllers/todo_controller.py")
    print(f"   🔧 Function: list_todos()")
    print(f"   🌐 Route   : GET /todos")
    print("-"*60)
    print(f"   ➡️  STEP 1: Controller → querying Firestore (collection='{COLLECTION}')")
    print(f"              Method: _collection().stream()")

    docs = _collection().stream()
    todos = [doc.to_dict() for doc in docs]

    print(f"   ✅ STEP 2: Firestore returned {len(todos)} document(s)")
    for i, t in enumerate(todos, 1):
        print(f"              [{i}] id={t['id'][:8]}... | title={t['title']} | completed={t['is_completed']}")
    print(f"   ➡️  STEP 3: Converting to TodoResponse list (View)")
    print(f"   📤 STEP 4: Sending Response to Client | Status: 200 OK")
    print("="*60 + "\n")

    return [TodoResponse(**t) for t in todos]


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: str):
    print("\n" + "="*60)
    print("📥 [MVC] REQUEST RECEIVED")
    print("="*60)
    print(f"   📂 File    : src_mvc/controllers/todo_controller.py")
    print(f"   🔧 Function: get_todo()")
    print(f"   🌐 Route   : GET /todos/{{todo_id}}")
    print(f"   🆔 todo_id : {todo_id}")
    print("-"*60)
    print(f"   ➡️  STEP 1: Controller → fetching from Firestore by ID")
    print(f"              Collection.document('{todo_id}').get()")

    doc = _collection().document(todo_id).get()

    if not doc.exists:
        print(f"   ❌ STEP 2: Document NOT FOUND in Firestore!")
        print(f"      Raising: 404 Not Found")
        print("="*60 + "\n")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID '{todo_id}' was not found.",
        )

    print(f"   ✅ STEP 2: Document FOUND!")
    data = doc.to_dict()
    print(f"              title      : {data['title']}")
    print(f"              completed  : {data['is_completed']}")
    print(f"   ➡️  STEP 3: Building TodoResponse (View)")
    print(f"   📤 STEP 4: Sending Response | Status: 200 OK")
    print("="*60 + "\n")

    return TodoResponse(**data)


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(todo_id: str):
    print("\n" + "="*60)
    print("📥 [MVC] REQUEST RECEIVED")
    print("="*60)
    print(f"   📂 File    : src_mvc/controllers/todo_controller.py")
    print(f"   🔧 Function: complete_todo()")
    print(f"   🌐 Route   : PATCH /todos/{{todo_id}}/complete")
    print(f"   🆔 todo_id : {todo_id}")
    print("-"*60)
    print(f"   ➡️  STEP 1: Controller → fetching from Firestore by ID")

    doc_ref = _collection().document(todo_id)
    doc = doc_ref.get()

    if not doc.exists:
        print(f"   ❌ STEP 2: Document NOT FOUND! Raising 404.")
        print("="*60 + "\n")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID '{todo_id}' was not found.",
        )

    todo = doc.to_dict()
    print(f"   ✅ STEP 2: Document FOUND!")
    print(f"              title        : {todo['title']}")
    print(f"              is_completed : {todo['is_completed']}")
    print("-"*60)
    print(f"   ➡️  STEP 3: Controller → calling Model (todo_model.py)")
    print(f"              Function: mark_completed(todo)")

    try:
        updated = mark_completed(todo)

        print(f"   ✅ STEP 4: Model applied business rule successfully!")
        print(f"              is_completed : {updated['is_completed']}")
        print(f"              completed_at : {updated['completed_at']}")
        print("-"*60)
        print(f"   ➡️  STEP 5: Controller → updating Firestore document")
        print(f"              doc_ref.update(is_completed=True, completed_at=...)")

        doc_ref.update({
            "is_completed": True,
            "completed_at": updated["completed_at"]
        })

        print(f"   ✅ STEP 6: Firestore updated successfully!")
        print(f"   ➡️  STEP 7: Building TodoResponse (View)")
        print(f"   📤 STEP 8: Sending Response | Status: 200 OK")
        print("="*60 + "\n")

        return TodoResponse(**updated)

    except TodoAlreadyCompletedError as err:
        print(f"   ❌ TodoAlreadyCompletedError caught!")
        print(f"      Detail: {str(err)}")
        print("="*60 + "\n")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str):
    print("\n" + "="*60)
    print("📥 [MVC] REQUEST RECEIVED")
    print("="*60)
    print(f"   📂 File    : src_mvc/controllers/todo_controller.py")
    print(f"   🔧 Function: delete_todo()")
    print(f"   🌐 Route   : DELETE /todos/{{todo_id}}")
    print(f"   🆔 todo_id : {todo_id}")
    print("-"*60)
    print(f"   ➡️  STEP 1: Controller → checking if document exists in Firestore")

    doc_ref = _collection().document(todo_id)

    if not doc_ref.get().exists:
        print(f"   ❌ STEP 2: Document NOT FOUND! Raising 404.")
        print("="*60 + "\n")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID '{todo_id}' was not found.",
        )

    print(f"   ✅ STEP 2: Document exists. Proceeding with delete.")
    print(f"   ➡️  STEP 3: Controller → calling doc_ref.delete()")

    doc_ref.delete()

    print(f"   ✅ STEP 4: Firestore document deleted successfully!")
    print(f"   📤 STEP 5: Sending Response | Status: 204 No Content")
    print("="*60 + "\n")
