# TodoFlow Email Reminder Service — Beginner Step-by-Step Guide

> **Purpose:** Is document mein email reminder feature ka complete flow simple
> Roman Urdu mein explain kiya gaya hai: UI se reminder select honay se lekar
> database save, automatic scan, Resend email aur sent-state update tak.

---

## 1. Feature kya karta hai?

User todo create karte waqt:

- due date/time select karta hai;
- reminder option select karta hai;
- backend reminder ka exact UTC time calculate karta hai;
- selected database reminder ko permanently save karta hai;
- FastAPI ke sath background scheduler due reminders check karta rehta hai;
- reminder due ho to Resend professional email bhejta hai;
- successful delivery ke baad database mein `reminder_sent_at` save hota hai.

Available options:

```text
No reminder
1 minute before
1 hour before
1 day before
3 days before
Custom time
```

One-line flow:

```text
UI -> API -> Controller -> TodoService -> Domain rules -> Selected database
                                                     |
FastAPI BackgroundScheduler -> ReminderService -> Resend -> sent state save
```

---

## 2. Is feature ke liye kya changes kiye gaye?

| Area | Change | Reason |
|---|---|---|
| Frontend form | Due date aur reminder options add | User schedule select kar sake |
| Frontend task item | Due/reminder status show | User saved schedule dekh sake |
| Presentation | Reminder fields request/response schemas mein add | HTTP contract clear rahe |
| Controller | Route se mapping/error logic controller mein move | Routes thin aur readable rahen |
| Application | `ReminderService` add | Sending workflow aik use case mein rahe |
| Domain | `ReminderSettings` rules add | Date/reminder rules DB/UI se independent rahen |
| Domain port | `EmailSender` contract add | Domain Resend SDK par depend na kare |
| Infrastructure | `ResendEmailSender` add | Resend-specific API call isolate rahe |
| Infrastructure | `ReminderScheduler` add | API ke sath automatic recurring scan chale |
| Databases | Reminder fields/queries add | Firestore, MongoDB aur PostgreSQL same behavior dein |
| Configuration | Resend/scheduler `.env` values add | Secrets aur runtime values code se bahar rahen |
| Email design | Branded HTML + text fallback add | Received email professional aur compatible ho |

---

## 3. DDD layers mein cheezen kahan aur kyun rakhi hain?

### Domain — business rules

Files:

- [`domain/reminder.py`](../backend/DDD/app/domain/reminder.py)
- [`domain/notification.py`](../backend/DDD/app/domain/notification.py)
- [`domain/todo.py`](../backend/DDD/app/domain/todo.py)

Domain decide karta hai:

- due date future mein honi chahiye;
- reminder ke liye due date required hai;
- reminder due date se pehle hona chahiye;
- custom reminder future mein hona chahiye;
- completed todo ka reminder send nahi hoga;
- sent reminder dobara sent mark nahi ho sakta.

Domain ko FastAPI, Resend, MongoDB, Firestore ya SQL ka knowledge nahi hai.

### Application — workflow coordination

Files:

- [`application/todo_service.py`](../backend/DDD/app/application/todo_service.py)
- [`application/reminder_service.py`](../backend/DDD/app/application/reminder_service.py)
- [`application/dto.py`](../backend/DDD/app/application/dto.py)

Application ka kaam:

- domain entity create karwana;
- repository se due reminders lena;
- provider-independent email message banana;
- `EmailSender` ke through email bhejna;
- success ke baad sent state save karwana.

Application SQL/Firestore/PyMongo query nahi likhti.

### Presentation — HTTP input/output

Files:

- [`presentation/schemas.py`](../backend/DDD/app/presentation/schemas.py)
- [`presentation/routers/todos.py`](../backend/DDD/app/presentation/routers/todos.py)
- [`presentation/controllers/todo_controller.py`](../backend/DDD/app/presentation/controllers/todo_controller.py)

Presentation request validate, trusted user identity attach aur known business
errors ko HTTP response mein translate karti hai.

### Infrastructure — technical implementation

Files:

- [`infrastructure/resend_email_sender.py`](../backend/DDD/app/infrastructure/resend_email_sender.py)
- [`infrastructure/reminder_scheduler.py`](../backend/DDD/app/infrastructure/reminder_scheduler.py)
- three database todo repositories

Infrastructure Resend SDK, APScheduler aur actual database queries handle karti
hai. Yeh details domain se bahar rakhi gayi hain.

---

## 4. Step-by-step: user todo reminder kaise create karta hai?

### Step 1 — UI data collect karti hai

File: [`AddTodoForm.jsx`](../frontend/src/components/todos/AddTodoForm.jsx)

User title, priority, due date aur reminder select karta hai. Custom reminder
select ho to extra date/time input show hota hai.

Frontend validation:

- title 3–120 characters;
- due date future mein;
- reminder ke liye due date required;
- custom reminder future mein aur due date se pehle;
- preset reminder past mein calculate ho to later due date required.

Browser ka local `datetime-local` value API bhejne se pehle UTC ISO string banta
hai:

```javascript
new Date(dueAt).toISOString()
```

Is se Pakistan ya kisi aur timezone ka local time backend par consistent UTC
time mein receive hota hai.

### Step 2 — Redux/API request bhejte hain

`createTodo` thunk complete form payload `POST /todos` ko bhejta hai:

```json
{
  "title": "Prepare presentation",
  "priority": "high",
  "due_at": "2026-11-13T13:00:00.000Z",
  "reminder_option": "1_HOUR",
  "custom_reminder_at": null
}
```

### Step 3 — HTTP schema basic shape validate karti hai

`CreateTodoRequest` allowed reminder options aur datetime types validate karti
hai. Yeh HTTP validation hai; actual business date rules domain mein hain.

### Step 4 — thin route controller ko call karti hai

```text
POST /todos
 -> todos.create_todo route
 -> todo_controller.add_todo
```

Controller verified token se `owner_uid` aur `owner_email` leta hai. Email JSON
body se trust nahi hoti, isliye reminder kisi doosre address par force nahi ki
ja sakti.

### Step 5 — controller application DTO banata hai

`CreateTodoInput` mein yeh values jati hain:

```text
title, priority, owner_uid, owner_email,
due_at, reminder_option, custom_reminder_at
```

### Step 6 — TodoService domain entity create karwati hai

```text
TodoService.create
 -> TodoItem.create
 -> ReminderSettings.create
```

`ReminderSettings.create()` exact reminder time calculate aur validate karta
hai.

Example:

```text
Due time       = 06:00 PM
Selected       = 1_HOUR
Reminder time  = 05:00 PM
```

Custom example:

```text
Current time   = 05:30 PM
Reminder time  = 05:40 PM
Due time       = 06:00 PM
Result         = valid
```

Invalid example:

```text
Current time   = 05:37 PM
Due time       = 05:36 PM
Reminder time  = 05:40 PM
Result         = invalid: due past hai aur reminder due ke baad hai
```

### Step 7 — selected database entity save karta hai

Todo aur reminder aik hi entity/document/row ka part hain. Separate scheduler
memory par depend nahi kiya gaya, isliye API restart se schedule lose nahi hota.

---

## 5. Database mein kya save hota hai?

Har todo ke sath:

| Field | Meaning |
|---|---|
| `due_at` | Task kab due hai |
| `reminder_at` | Email kab send honi hai |
| `reminder_email` | Authenticated account email |
| `reminder_sent_at` | Successful delivery ka time; pehle `null` |
| `reminder_option` | `NONE`, `1_HOUR`, `CUSTOM`, etc. |

### MongoDB

[`mongodb/todo_repository.py`](../backend/DDD/app/infrastructure/mongodb/todo_repository.py)
document fields save karta hai aur due/incomplete/unsent reminders ke liye
compound index/query use karta hai.

### PostgreSQL

[`postgresql/todo_schema.py`](../backend/DDD/app/infrastructure/postgresql/todo_schema.py)
existing table ko safe `ADD COLUMN IF NOT EXISTS` migration se extend karta hai.
Partial reminder index due scan ko optimize karta hai.

[`postgresql/todo_repository.py`](../backend/DDD/app/infrastructure/postgresql/todo_repository.py)
parameterized SQL se due reminders read karta hai.

### Firestore

[`firestore/todo_mapper.py`](../backend/DDD/app/infrastructure/firestore/todo_mapper.py)
domain entity aur Firestore REST document convert karta hai.

[`firestore/todo_repository.py`](../backend/DDD/app/infrastructure/firestore/todo_repository.py)
collection-group query use karta hai. Agar project mein required collection-
group index missing ho, beginner/demo data ke liye safe scan fallback use hota
hai.

---

## 6. Automatic scheduler same terminal mein kaise chalta hai?

File: [`infrastructure/reminder_scheduler.py`](../backend/DDD/app/infrastructure/reminder_scheduler.py)

Project ko sirf aik command chahiye:

```powershell
python -m uvicorn main:app --reload
```

[`app/main.py`](../backend/DDD/app/main.py) FastAPI lifespan ke through:

```text
API startup  -> ReminderScheduler.start()
API running  -> interval scans background thread mein
API shutdown -> ReminderScheduler.shutdown()
```

`BackgroundScheduler` use hua hai kyun ke uska `start()` main FastAPI process ko
block nahi karta. API requests aur reminder scans same terminal/process mein
chal sakte hain.

### Kya yeh cron job hai?

Behavior cron job jaisa recurring hai, lekin technically Windows/Linux operating
system ka cron nahi. Yeh application-level **APScheduler interval job** hai.
Faida yeh hai ke project ke sath Python code mein configure hota hai aur local
development mein separate OS cron setup nahi chahiye.

Scheduler settings:

- `max_instances=1`: previous scan chal raha ho to overlapping scan nahi;
- `coalesce=True`: missed repeated runs ko aik run mein combine;
- `misfire_grace_time`: short delay ke baad bhi scan recover;
- startup scan: server downtime mein due honay wali reminders foran recover.

Important beginner limitation:

> Local project mein one Uvicorn process use karein. Production mein multiple
> Uvicorn workers start kiye to har process apna scheduler bana sakta hai. Us
> case mein dedicated scheduler ya distributed lock chahiye hota hai.

---

## 7. Due reminder milnay ke baad complete send flow

```text
ReminderScheduler._process_reminders
 -> ReminderService.process_due(now)
 -> TodoRepository.get_due_reminders(now, batch_size)
 -> TodoItem.reminder_is_due(now)
 -> ReminderService._build_message(todo)
 -> ResendEmailSender.send(message)
 -> Resend API success + provider email ID
 -> TodoItem.mark_reminder_sent(now)
 -> TodoRepository.save(todo)
 -> reminder_sent_at database mein save
```

Repository query sirf yeh reminders dhoondti hai:

```text
is_completed = false
reminder_at <= current time
reminder_sent_at = null
```

Domain dobara `reminder_is_due()` check karta hai. Query technical filter hai;
final business decision entity ke paas rehta hai.

---

## 8. Received email professional kaise bani?

Function: `ReminderService._build_message()`

Email mein:

- branded blue TodoFlow header;
- “Your task is due soon” heading;
- safely escaped task title;
- readable UTC due date;
- High/Medium/Low color-coded priority badge;
- short action message;
- automated-reminder footer.

Inline CSS use hoti hai kyun ke Gmail/Outlook jaisay email clients external CSS
ko consistently support nahi karte.

Plain-text fallback bhi banta hai:

```text
TODOFLOW TASK REMINDER

Task: Prepare presentation
Due: Friday, 13 November 2026 at 06:00 PM UTC
Priority: High

Open TodoFlow to review the task and mark it complete.
```

---

## 9. Resend adapter kya karta hai?

File: [`infrastructure/resend_email_sender.py`](../backend/DDD/app/infrastructure/resend_email_sender.py)

Domain ka `EmailSender` sirf contract hai:

```text
send(EmailMessage) -> provider message ID
```

`ResendEmailSender` is contract ko Resend SDK se implement karta hai. Isliye
future mein provider change ho to domain reminder rules change nahi hongi.

Resend request mein:

```text
from, to, subject, html, text, idempotency key
```

Idempotency key format:

```text
todo-reminder/{todo_id}/{reminder_timestamp}
```

Same reminder short retry mein dobara request ho to Resend same event ko
duplicate email banne se protect karta hai.

---

## 10. Success aur failure behavior

### Success

```text
Resend accepts email
 -> provider ID return
 -> mark_reminder_sent
 -> reminder_sent_at save
 -> next scan is reminder ko ignore karta hai
```

### Failure

```text
Resend/network error
 -> error bilingual log mein
 -> reminder_sent_at null rehta hai
 -> next scheduler scan retry karta hai
```

Sent state provider success se **pehle** save nahi hoti. Agar pehle save kar dein
aur email fail ho jaye to reminder permanently miss ho sakti hai.

### Todo complete/delete ho jaye

- completed todo `reminder_is_due()` mein false;
- deleted todo query mein milta hi nahi;
- isliye email send nahi hoti.

---

## 11. `.env` configuration

Real secrets sirf ignored `.env` mein:

```env
RESEND_API_KEY=your-real-secret-key
REMINDER_EMAIL_FROM=TodoFlow <reminders@your-verified-domain.com>
REMINDER_SCAN_INTERVAL_SECONDS=30
REMINDER_BATCH_SIZE=50
```

| Variable | Purpose |
|---|---|
| `RESEND_API_KEY` | Resend API authenticate karta hai |
| `REMINDER_EMAIL_FROM` | Received email ka sender |
| `REMINDER_SCAN_INTERVAL_SECONDS` | Kitne seconds baad DB scan ho |
| `REMINDER_BATCH_SIZE` | Aik scan mein maximum reminders |

`onboarding@resend.dev` development testing ke liye hai. Real users ko send
karne ke liye Resend dashboard mein apna domain verify karna chahiye.

Never commit:

- real API key;
- `.env`;
- Firebase service-account key.

---

## 12. Run aur manually test kaise karein?

### Backend run

```powershell
cd "C:\Users\Rana Khawar Ali\Desktop\Cloudpacer-Internship\backend\DDD"
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

Expected startup log:

```text
Email reminder scheduler started with the API.
Email reminder scheduler API ke sath start ho gaya.
```

### Manual test

1. Login/signup karein.
2. Due time current time se 5–10 minutes baad select karein.
3. Custom reminder due se pehle aur current time se 2–3 minutes baad select karein.
4. Todo save karein.
5. Task card par due/reminder schedule verify karein.
6. Backend terminal open rakhein.
7. Reminder time par terminal log aur inbox/Resend dashboard check karein.
8. Database mein `reminder_sent_at` populated verify karein.

Example:

```text
Current   05:30 PM
Reminder  05:33 PM
Due       05:38 PM
```

---

## 13. Common errors

### “Due date must be in the future”

Due time current clock se aagay set karein. Reminder future honay se past due
date valid nahi ban jati.

### “Reminder must be before the due date”

Correct order:

```text
current time < reminder time < due time
```

### “This reminder falls in the past”

Example: due sirf 30 minutes baad hai lekin `1_HOUR` select hai. Later due date
ya custom reminder choose karein.

### Email dashboard mein hai lekin inbox mein nahi

- spam/junk check karein;
- recipient address verify karein;
- Resend logs mein delivery status dekhein;
- real recipients ke liye verified sender domain use karein.

### Server reload par scheduler dobara start hota hai

Expected hai. Lifespan old scheduler cleanly stop aur new application scheduler
start karta hai. Reminder state database mein hai, memory mein nahi.

---

## 14. Quick presentation answer

> “User UI se due date aur reminder option select karta hai. Presentation layer
> request ko application DTO mein map karti hai. Domain ka `ReminderSettings`
> exact UTC time calculate aur business rules validate karta hai. Selected
> database todo ke sath reminder state save karta hai. FastAPI lifespan ke andar
> `BackgroundScheduler` recurring scans chalata hai. `ReminderService` due
> reminders read karke provider-independent `EmailMessage` banata hai aur domain
> `EmailSender` port ke Resend adapter se professional email bhejta hai. Sirf
> provider success ke baad `reminder_sent_at` save hota hai; failure next scan
> par retry hoti hai. Firestore, MongoDB aur PostgreSQL same domain/application
> workflow use karte hain, sirf repository implementation different hai.”

---

## 15. Official technical references

- [APScheduler BackgroundScheduler](https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/background.html)
- [APScheduler user guide](https://apscheduler.readthedocs.io/en/3.x/userguide.html)
- [Resend Python SDK](https://resend.com/python)
- [Resend idempotency keys](https://resend.com/changelog/idempotency-keys)
