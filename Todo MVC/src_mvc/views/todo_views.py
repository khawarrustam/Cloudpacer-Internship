"""
=============================================================================
VIEW LAYER — Pydantic Schemas for Request & Response (MVC Pattern)
=============================================================================
MVC architecture mein "View" ka matlab hota hai user/client ko kya nazar aayega.
Kyunki yeh ek REST API hai (HTML templates nahi hain), is liye Pydantic Models
hi hamari "Views" hain jo Request body aur Response JSON ka structure define karti hain.

MVC vs Clean Architecture / DDD:
- MVC mein yahi Schemas dono kaam karti hain (API validation + data transfer).
- DDD mein do alag cheezein hoti hain: Presentation Schemas (FastAPI ke liye) aur
  Application DTOs (Data Transfer Objects jo layers ke darmiyan data le jati hain).

Kahan Connected Hai:
- Yeh classes `src_mvc/controllers/todo_controller.py` mein har route ke input (`req: CreateTodoRequest`)
  aur output (`response_model=TodoResponse`) ke tor par use hoti hain.
=============================================================================
"""

# ---------------------------------------------------------------------------
# LIBRARIES / IMPORTS (Kyun aur kis liye import ki gayi hain):
# ---------------------------------------------------------------------------
# 'BaseModel': Pydantic ka base class jo request aur response data ko validate aur serialize karta hai.
# 'Field': Model fields par additional constraints (jaise min_length, max_length, examples) lagane ke liye.
from pydantic import BaseModel, Field

# 'Optional': Batane ke liye ke field ki value string bhi ho sakti hai ya phir None (null) bhi.
from typing import Optional


# ---------------------------------------------------------------------------
# REQUEST SCHEMAS (Client se aane wala data):
# ---------------------------------------------------------------------------
class CreateTodoRequest(BaseModel):
    """
    Kyun banaya gaya:
    - Jab client POST /todos par naya task create karne ki request kare,
      toh aane wale JSON body ko validate karne ke liye.

    Fields aur Rules:
    - title: String hona zaroori hai, kam az kam 3 aur zyada se zyada 120 characters ka ho.
    - priority: Optional string, default value 'MEDIUM' hogi.

    Kahan connected hai:
    - `src_mvc/controllers/todo_controller.py` ke `create_todo(req: CreateTodoRequest)` mein parameter ke tor par.
    """
    title: str = Field(
        ..., min_length=3, max_length=120, examples=["Setup MVC Architecture"]
    )
    priority: str = Field(default="MEDIUM", examples=["HIGH"])


# ---------------------------------------------------------------------------
# RESPONSE SCHEMAS (Client ko wapis bheja jane wala data):
# ---------------------------------------------------------------------------
class TodoResponse(BaseModel):
    """
    Kyun banaya gaya:
    - Client ko jo Todo ka data response mein bhejna hai, uska JSON contract fix karne ke liye.

    Fields:
    - id: Todo ka unique ID string.
    - title: Task ka title.
    - priority: Task ki priority (LOW, MEDIUM, HIGH).
    - is_completed: Boolean flag (True/False).
    - created_at: Timestamp jab todo bana.
    - completed_at: Timestamp jab todo complete hua (agar nahi hua toh null/None).

    Kahan connected hai:
    - `src_mvc/controllers/todo_controller.py` mein `response_model=TodoResponse` ya `List[TodoResponse]` ke tor par.
    """
    id: str
    title: str
    priority: str
    is_completed: bool
    created_at: str
    completed_at: Optional[str] = None
