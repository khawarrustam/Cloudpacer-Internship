# TodoFlow Google Login — Easy Roman Urdu Guide

Yeh guide Google Login ka complete lekin short explanation hai. Isay parh kar
aap presentation mein code kholay baghair flow explain kar saktay hain.

## 1. Google Login ka short answer

User **Continue with Google** press karta hai. Google user ko verify karke aik
**Google ID token** deta hai. Frontend token backend ko bhejta hai. Backend token
verify karta hai, selected database mein user find/create karta hai aur apni
**TodoFlow JWT** return karta hai. Isi JWT se user apne tasks access karta hai.

```text
Google         -> identity verify karta hai
Selected DB    -> user aur tasks save karti hai
TodoFlow JWT   -> application access deti hai
```

Firebase Authentication use nahi ho rahi. Auth user usi database mein save hota
hai jahan uske tasks save hotay hain.

## 2. Important terms

| Term | Asaan matlab |
|---|---|
| Google ID token | Google ka proof ke user verify ho chuka hai |
| `credential` | Frontend mein Google ID token ka field name |
| `google_sub` | Google account ki stable aur unique ID |
| Local UID | Selected database mein TodoFlow user ki ID |
| TodoFlow JWT | Backend ka banaya hua session token |
| Repository | Database se data read/write karne wali class |

### Google token aur TodoFlow JWT different kyun hain?

```text
Google ID token = identity proof
TodoFlow JWT    = TodoFlow ka access card
```

Google token sirf login ke waqt verify hota hai. Tasks ki protected requests
TodoFlow JWT ke sath chalti hain.

## 3. Complete login flow

```text
1. User Google button press karta hai
2. Google account chooser open hota hai
3. Google frontend ko ID token deta hai
4. Frontend POST /auth/google request bhejta hai
5. Backend Google token verify karta hai
6. Selected database mein user find/create hota hai
7. Backend TodoFlow JWT banata hai
8. Frontend JWT ko memory mein rakhta hai
9. JWT ke sath user apne tasks access karta hai
```

Backend `google-auth` library se token ki signature, Client ID, issuer, expiry
aur verified email check karta hai. Verification fail ho to login reject hota
hai. Google password hamari application ko kabhi nahi milta.

## 4. Same Google email, different database users

Example email: `rajputkhawarali@gmail.com`

| Database | Local account |
|---|---|
| Firestore | `UID-A` + Firestore tasks |
| MongoDB | `UID-B` + MongoDB tasks |
| PostgreSQL | `UID-C` + PostgreSQL tasks |

Email aur `google_sub` same ho saktay hain, lekin local UIDs different hoti
hain. Har repository sirf apni database check karti hai; koi shared users table
nahi hai.

TodoFlow JWT mein database ka naam bhi hota hai. Isliye MongoDB ki JWT
PostgreSQL par accept nahi hoti. Database switch ke baad dobara login karna
security requirement hai.

## 5. Frontend files ka role

| File | Important function | Kya kaam hai? |
|---|---|---|
| `GoogleSignInButton.jsx` | `setupGoogleButton()` | Google script aur button load karke credential leta hai |
| `AuthForm.jsx` | `handleGoogleLogin()` | Credential ko login flow mein bhejta aur message show karta hai |
| `App.jsx` | `googleLogin()` | UI ko Redux action se connect karta hai |
| `authSlice.js` | `googleLoginUser` | Async login, loading, success aur failure handle karta hai |
| `authApi.js` | `loginWithGoogle()` | `POST /auth/google` request bhejta hai |
| `authSession.js` | `saveSession()` | TodoFlow JWT ko JavaScript memory mein rakhta hai |

Frontend Google token ko khud verify nahi karta. Security decision backend leta
hai. `localStorage` use nahi hoti, isliye refresh par dobara login hota hai.

## 6. Backend files ka role

Backend request is order mein move karti hai:

```text
Schema -> Router -> DTO -> Service -> Repository -> Security/Database
```

| File | Class/function | Kya kaam hai? |
|---|---|---|
| `presentation/schemas.py` | `GoogleLoginRequest` | Request mein credential validate karta hai |
| `presentation/routers/auth.py` | `login_with_google()` | `/auth/google` request receive aur response return karta hai |
| `application/dto.py` | `GoogleLoginInput` | Credential ko next layer tak carry karta hai |
| `application/auth_service.py` | `login_with_google()` | Use case ko coordinate karta hai |
| `domain/auth.py` | `GoogleIdentity`, `GoogleAccountPolicy` | Clean Google identity aur safe account-linking rules enforce karta hai |
| `infrastructure/repository_factory.py` | `create_repositories()` | Selected database ke matching auth + todo repositories banata hai |
| `infrastructure/security.py` | `verify_google_credential()` | Google token verify karta hai |
| `infrastructure/security.py` | `create_token()` | TodoFlow JWT banata hai |
| Database `auth_repository.py` | `login_with_google()` | User ko apni database mein find/create karta hai |

Service ko SQL, MongoDB ya Firestore syntax ka pata nahi. Repository apni
database ki technology handle karti hai, isliye main flow simple rehta hai.

## 7. Database mein kya save hota hai?

Teenon databases mein basic user data same hai:

```text
local UID
email
display_name
google_sub
password_hash (sirf password account/link ho to)
```

- Firestore: `auth_users` collection
- MongoDB: `users` collection
- PostgreSQL: `users` table

Plain password kabhi save nahi hota. Google-only account ka `password_hash`
empty ho sakta hai.

## 8. Google Cloud aur `.env` setup

Google Cloud mein:

1. Personal Gmail/testing ke liye **External** audience select karein.
2. Apna Gmail **Test users** mein add karein.
3. **Web application** OAuth client banayein.
4. Authorized JavaScript origins add karein:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Same public Client ID dono `.env` files mein honi chahiye:

```env
# backend/DDD/.env
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com

# frontend/.env
VITE_GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
```

Current flow client secret use nahi karta. Downloaded client-secret JSON ko
GitHub, frontend ya backend mein add nahi karna.

## 9. Database kaise switch karein?

Backend stop karke aik database select karein:

```powershell
$env:DATABASE = "firestore"
python -m uvicorn main:app --reload

$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload

$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

Aik waqt mein sirf aik command pair run karein. Factory selected database ke
matching auth aur todo repositories banati hai.

## 10. Request, response aur logs

Request:

```http
POST /auth/google
Content-Type: application/json

{ "credential": "Google-ID-token" }
```

Successful response:

```json
{
  "uid": "local-database-uid",
  "email": "student@gmail.com",
  "token": "TodoFlow-JWT",
  "message": "Google login successful"
}
```

Logs:

```text
Presentation   | Google login request received.
Infrastructure | Database Google authentication succeeded.
Application    | Google login completed.
```

Password aur token ki actual values logs mein print nahi hotin.

## 11. Presentation demo

1. `DATABASE=mongodb` select karke Google login karein.
2. MongoDB Compass mein user aur tasks dikhayein.
3. MongoDB local UID note karein.
4. Backend restart karke `DATABASE=postgresql` select karein.
5. Same Google account se login karein.
6. pgAdmin mein user aur tasks dikhayein.
7. Dono UIDs compare karein — woh different hongi.

Is se prove hota hai ke same Google identity ke bawajood har database ka account
aur data independent hai.

## 12. Common errors

| Error | Solution |
|---|---|
| `Google login setup pending` | Frontend `.env` mein `VITE_GOOGLE_CLIENT_ID` add karke restart karein |
| `The given origin is not allowed` | Exact frontend URL Google Cloud origins mein add karein |
| `Invalid Google login` | Frontend aur backend ki Client ID same check karein |
| Google app access nahi deta | Gmail ko Google Cloud Test users mein add karein |
| Database switch ke baad `401` | New database mein dobara login karein |
| Refresh par logout | Expected hai; token sirf memory mein hai |

## 13. Short viva answers

### Firebase Authentication use ho rahi hai?

Nahi. Google identity verify karta hai; user selected database mein save hota
hai.

### `google_sub` kyun save hota hai?

Yeh Google account ki stable unique ID hai. Email change ho sakti hai.

### Do tokens kyun hain?

Google token identity proof hai. TodoFlow JWT hamari APIs ka access token hai.

### Same Gmail har database mein different user kyun hai?

Har database ka apna users store aur apni local UID hai.

### Repository pattern ka faida?

Application flow same rehta hai aur sirf database implementation change hoti
hai.

### Client secret kyun use nahi ho raha?

Current Google ID-token flow ko Web Client ID chahiye; client secret required
nahi hai.

## 14. One-minute presentation answer

> “Frontend Google Identity Services se Google ID token leta hai aur usay
> `POST /auth/google` par bhejta hai. Backend official `google-auth` library se
> token verify karta hai. Selected repository `google_sub` ke through user ko
> apni database mein find ya create karti hai. Backend local UID aur database
> name wali TodoFlow JWT return karta hai. Isi JWT se tasks access hotay hain.
> Har database ka user store separate hai, isliye same Gmail ko Firestore,
> MongoDB aur PostgreSQL mein different local UIDs milti hain.”

## 15. Yaad rakhne wali line

```text
Google identity verify karta hai,
selected database user aur tasks own karti hai,
TodoFlow JWT access control karti hai.
```

## Important code links

- [Google button](../frontend/src/components/GoogleSignInButton.jsx)
- [Frontend auth flow](../frontend/src/features/auth/authSlice.js)
- [Google login route](../backend/DDD/app/presentation/routers/auth.py)
- [Auth service](../backend/DDD/app/application/auth_service.py)
- [Repository factory](../backend/DDD/app/infrastructure/repository_factory.py)
- [Google/JWT security](../backend/DDD/app/infrastructure/security.py)
- [Firestore auth repository](../backend/DDD/app/infrastructure/firestore/auth_repository.py)
- [MongoDB auth repository](../backend/DDD/app/infrastructure/mongodb/auth_repository.py)
- [PostgreSQL auth repository](../backend/DDD/app/infrastructure/postgresql/auth_repository.py)
