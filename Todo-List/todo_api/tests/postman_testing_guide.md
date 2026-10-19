# 📬 Postman Testing Guide — Step by Step

Server is running at: `http://127.0.0.1:8000`

---

## Step 1: Import the Collection

1. Open **Postman**
2. Click **Import** (top-left corner)
3. Drag and drop this file:
   ```
   Todo-List/todo_api/Todo_API.postman_collection.json
   ```
4. You'll see **"Todo Onion Architecture API"** appear in your sidebar with 3 folders:
   - Health
   - Todos
   - Error Cases

---

## Step 2: Health Check ✅

| Setting | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `http://127.0.0.1:8000/` |

**Click Send**

**Expected Response (200 OK):**
```json
{
    "status": "ok",
    "architecture": "Onion / DDD"
}
```

✅ If you see this, the server is running!

---

## Step 3: Create Todo — HIGH Priority 🟢

| Setting | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/todos` |
| **Headers** | `Content-Type: application/json` |
| **Body** | raw → JSON |

**Body:**
```json
{
    "title": "Setup Firebase Firestore",
    "priority": "HIGH"
}
```

**Click Send**

**Expected Response (201 Created):**
```json
{
    "id": "some-uuid-here",
    "title": "Setup Firebase Firestore",
    "priority": "HIGH",
    "is_completed": false,
    "created_at": "2026-09-29T...",
    "completed_at": null
}
```

> ⚠️ **IMPORTANT:** Copy the `id` value from the response — you'll need it in Step 6!
> The Postman collection auto-saves it, but if you're doing it manually, save this ID.

---

## Step 4: Create Todo — MEDIUM Priority (Default) 🟡

| Setting | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/todos` |
| **Body** | raw → JSON |

**Body (notice: no priority field):**
```json
{
    "title": "Implement Onion Architecture layers"
}
```

**Click Send**

**Expected Response (201 Created):**
```json
{
    "id": "another-uuid",
    "title": "Implement Onion Architecture layers",
    "priority": "MEDIUM",
    "is_completed": false,
    "created_at": "2026-09-29T...",
    "completed_at": null
}
```

✅ Notice `priority` defaults to `"MEDIUM"` even though we didn't send it!

---

## Step 5: Create Todo — LOW Priority 🔵

| Setting | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/todos` |
| **Body** | raw → JSON |

**Body:**
```json
{
    "title": "Write unit tests for domain layer",
    "priority": "LOW"
}
```

**Expected Response (201 Created):** priority = `"LOW"` ✅

---

## Step 6: List All Todos 📋

| Setting | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `http://127.0.0.1:8000/todos` |

**Click Send**

**Expected Response (200 OK):**
```json
[
    {
        "id": "...",
        "title": "Setup Firebase Firestore",
        "priority": "HIGH",
        "is_completed": false,
        ...
    },
    {
        "id": "...",
        "title": "Implement Onion Architecture layers",
        "priority": "MEDIUM",
        "is_completed": false,
        ...
    },
    {
        "id": "...",
        "title": "Write unit tests for domain layer",
        "priority": "LOW",
        "is_completed": false,
        ...
    }
]
```

✅ You should see all 3 todos! Also check your **Firebase Console → Firestore** — you'll see them there too.

---

## Step 7: Complete a Todo ✔️

| Setting | Value |
|---|---|
| **Method** | `PATCH` |
| **URL** | `http://127.0.0.1:8000/todos/{ID_FROM_STEP_3}/complete` |

> Replace `{ID_FROM_STEP_3}` with the actual UUID you got in Step 3.
> Example: `http://127.0.0.1:8000/todos/70cdc975-e905-4f06-ac0a-337c57aadad0/complete`

**Click Send**

**Expected Response (200 OK):**
```json
{
    "id": "70cdc975-...",
    "title": "Setup Firebase Firestore",
    "priority": "HIGH",
    "is_completed": true,
    "created_at": "2026-09-29T...",
    "completed_at": "2026-09-29T..."
}
```

✅ Notice: `is_completed` changed to `true` and `completed_at` now has a timestamp!

---

## Step 8: Error Case — Title Too Short ❌

| Setting | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `http://127.0.0.1:8000/todos` |
| **Body** | raw → JSON |

**Body:**
```json
{
    "title": "AB",
    "priority": "HIGH"
}
```

**Expected Response (422 Unprocessable Entity):**
```json
{
    "detail": [
        {
            "type": "string_too_short",
            "msg": "String should have at least 3 characters",
            ...
        }
    ]
}
```

✅ Pydantic validation catches titles shorter than 3 characters!

---

## Step 9: Error Case — Missing Title ❌

**Body:**
```json
{
    "priority": "HIGH"
}
```

**Expected Response (422):** Field required error ✅

---

## Step 10: Error Case — Todo Not Found ❌

| Setting | Value |
|---|---|
| **Method** | `PATCH` |
| **URL** | `http://127.0.0.1:8000/todos/non-existent-id-12345/complete` |

**Expected Response (404 Not Found):**
```json
{
    "detail": "Todo with ID 'non-existent-id-12345' was not found."
}
```

✅ Domain exception `TodoNotFoundError` is raised and caught by the router!

---

## Step 11: Error Case — Complete Already Completed Todo ❌

Use the **same URL from Step 7** (the todo you already completed) and send PATCH again.

**Expected Response (400 Bad Request):**
```json
{
    "detail": "Todo with ID '...' is already completed."
}
```

✅ Domain rule enforced! `TodoItem.mark_as_completed()` throws `TaskAlreadyCompletedError`.

---

## Step 12: List Todos Again — Verify Final State 📋

`GET http://127.0.0.1:8000/todos`

You should see:
- 1 todo with `is_completed: true` (the one you completed)
- 2 todos with `is_completed: false`

---

## 🎯 Summary: What Each Test Proves

| Test | What It Proves |
|---|---|
| Health Check | Server is running |
| Create HIGH/MEDIUM/LOW | Factory method + Value Objects work |
| List All | Repository `get_all()` works |
| Complete Todo | `mark_as_completed()` business logic works |
| Title Too Short | Pydantic schema validation works |
| Missing Title | Required field validation works |
| Not Found | `TodoNotFoundError` domain exception works |
| Already Completed | `TaskAlreadyCompletedError` business rule works |

---

## 🔥 Bonus: Check Firebase Console

Go to: **Firebase Console → Firestore Database → `todos` collection**

You should see all your created todos as documents — the data persists even if you restart the server!

