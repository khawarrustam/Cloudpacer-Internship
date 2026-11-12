# TodoFlow Google Login — Complete Roman Urdu Guide

Yeh guide Google login ki poori integration ko easy Roman Urdu mein explain
karti hai. Isay parh kar presentation ke waqt har code file kholne ki zaroorat
nahi paray gi.

## 1. Hum ne kya integrate kiya hai?

TodoFlow mein ab login ke do tareeqay hain:

1. Email aur password.
2. Continue with Google.

Google sirf user ki identity verify karta hai. Actual TodoFlow user aur uske
todos hamesha terminal se select ki gayi database mein save hotay hain:

```text
DATABASE=firestore   -> user + todos Firestore mein
DATABASE=mongodb     -> user + todos MongoDB mein
DATABASE=postgresql  -> user + todos PostgreSQL mein
```

Is integration mein Firebase Authentication use nahi ho rahi.

## 2. Sab se important concept: do alag tokens

Google login mein do tokens alag alag kaam kartay hain:

| Token | Kon banata hai? | Kya kaam hai? |
|---|---|---|
| Google ID token | Google | Prove karta hai ke Google ne user verify kiya |
| TodoFlow JWT | Hamara backend | Baad ki protected todo requests authenticate karti hai |

Easy explanation:

```text
Google ID token: “Google ne is person ko verify kiya hai.”
TodoFlow JWT:    “Yeh local database user apne todos access kar sakta hai.”
```

Google ID token sirf aik dafa `/auth/google` endpoint ko bheja jata hai. Backend
verification ke baad apni TodoFlow JWT return karta hai. Frontend Google token
ko application session samajh kar use nahi karta.

## 3. Google Cloud par kya setup chahiye?

Google Auth Platform mein:

1. **Branding** mein app name aur support email set karein.
2. Personal Gmail/testing ke liye **External** audience select karein.
3. **Web application** type ka OAuth client banayein.
4. Yeh Authorized JavaScript origins add karein:

```text
http://localhost:5173
http://127.0.0.1:5173
```

5. Generated public Client ID copy karein.

Is flow ke liye yeh cheezen required nahi hain:

- Firebase Authentication;
- frontend ya backend mein Google client secret;
- authorized redirect URI;
- downloaded client-secret JSON ko repository mein rakhna.

## 4. `.env` configuration kaise hoti hai?

Same public Client ID dono local `.env` files mein honi chahiye:

```env
# backend/DDD/.env
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com

# frontend/.env
VITE_GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
```

Dono jagah same Client ID kyun?

- Frontend ko official Google button render karne ke liye chahiye.
- Backend ko Google token ka `aud` yani audience verify karne ke liye chahiye.

Agar token kisi doosri application ki Client ID ke liye bana ho, hamara backend
usay reject kar deta hai.

## 5. Complete Google login flow

```text
User “Continue with Google” click karta hai
        |
        v
Google Identity Services account chooser kholti hai
        |
        v
Google `credential` mein ID token return karta hai
        |
        v
Frontend `googleLoginUser` Redux thunk dispatch karta hai
        |
        v
POST /auth/google  { credential }
        |
        v
GoogleLoginRequest HTTP body validate karti hai
        |
        v
GoogleLoginInput credential ko AuthService tak le jati hai
        |
        v
AuthService.login_with_google
        |
        v
Selected AuthRepository.login_with_google
        |
        v
AuthSecurity.verify_google_credential
  - Google signature check
  - Client ID / audience check
  - issuer check
  - expiry check
  - verified email check
        |
        v
Selected database mein user find, link ya create hota hai
        |
        v
Backend database-bound TodoFlow JWT banata hai
        |
        v
Frontend JWT ko sirf JavaScript memory mein rakhta hai
        |
        v
Todo requests ke sath JWT Bearer token jati hai
```

## 6. Frontend files kya kaam karti hain?

### `frontend/src/components/GoogleSignInButton.jsx`

Is file ka purpose:

- Google ki official `gsi/client` browser library sirf aik dafa load karna.
- `VITE_GOOGLE_CLIENT_ID` read karna.
- Official Continue with Google button render karna.
- Account select honay ke baad `response.credential` lena.
- Credential ko normal Redux authentication flow mein bhejna.

Yeh component Google credential ko khud decode ya trust nahi karta. Trust ka
decision sirf backend verification ke baad hota hai.

### `frontend/src/components/AuthForm.jsx`

Is file ka purpose:

- Google button aur email/password form aik screen par show karna.
- Success ya error message display karna.
- Temporary input values React local state mein rakhna.

### `frontend/src/features/auth/authSlice.js`

`googleLoginUser` async thunk ka flow:

```text
Google credential
 -> authApi.loginWithGoogle
 -> backend response
 -> saveSession(response)
 -> Redux user state update
```

### `frontend/src/api/authApi.js`

Yeh file Google login request bhejti hai:

```http
POST /auth/google
Content-Type: application/json

{
  "credential": "Google ID token"
}
```

Component directly Axios call nahi karta. API ka kaam `authApi.js` mein rehta
hai taa-ke UI simple rahe.

### `frontend/src/features/auth/authSession.js`

Sirf TodoFlow JWT ko JavaScript memory mein rakhti hai. `localStorage` use nahi
hoti. Page refresh ke baad session clear hoti hai aur user dobara login karta
hai.

## 7. Backend files kya kaam karti hain?

### `presentation/schemas.py`

`GoogleLoginRequest` check karti hai ke HTTP request mein Google credential
maujood ho.

### `presentation/routers/auth.py`

`POST /auth/google` ka kaam:

1. HTTP request receive karna.
2. `GoogleLoginInput` banana.
3. `AuthService.login_with_google` call karna.
4. Success par `AuthResponse` return karna.
5. Invalid Google login ko HTTP 401 mein map karna.

### `application/dto.py`

`GoogleLoginInput` presentation se application layer tak credential carry
karti hai. Application layer FastAPI ya Pydantic import nahi karti.

### `application/auth_service.py`

`login_with_google` complete use case coordinate karta hai. Is file mein Google
SDK, Mongo query, Firestore URL ya SQL nahi hoti.

### `domain/auth.py`

`AuthRepository.login_with_google` aik common contract hai. Firestore, MongoDB
aur PostgreSQL ke adapters isi method ko apni technology ke mutabiq implement
kartay hain.

### `infrastructure/security.py`

`verify_google_credential` official `google-auth` library use karta hai.
Successful verification ke baad `GoogleProfile` milti hai:

```text
subject       = stable Google `sub`
email         = normalized verified email
display_name  = Google name ya email prefix
can_link_existing_email = safe auto-link decision
```

Google `sub` kyun use hota hai?

Email future mein change ho sakti hai, lekin Google `sub` stable account ID hai.
Isliye databases `google_sub` save karti hain.

### Database auth repositories

Teenon repositories same contract ko apni storage language mein implement
karti hain:

| Database | Google user kaise find/save hota hai? |
|---|---|
| Firestore | `runQuery` se `google_sub`, phir document PATCH |
| MongoDB | `find_one` se `google_sub`, phir insert/update |
| PostgreSQL | `SELECT` se `google_sub`, phir INSERT/UPDATE |

## 8. Har database mein kya save hota hai?

### Firestore `auth_users` document

```text
uid
email
display_name
google_sub
password_hash  (sirf jab password account/link ho)
```

### MongoDB `users` document

```text
_id             = local TodoFlow UUID
email
display_name
google_sub
password_hash   = optional
```

MongoDB `email` aur sparse `google_sub` ke unique indexes banati hai.

### PostgreSQL `users` row

```text
id              = local TodoFlow UUID
email
display_name
password_hash   = nullable
google_sub      = nullable; value ho to unique
```

Repository existing password-only `users` table ko data delete kiye baghair
safely extend karti hai.

## 9. Same email teen databases mein alag user kaise banti hai?

Example Google account:

```text
student@gmail.com
```

Har database mein first Google login:

| Selected database | Local UID | Account |
|---|---|---|
| Firestore | UUID-A | Sirf Firestore ka local user |
| MongoDB | UUID-B | Sirf MongoDB ka local user |
| PostgreSQL | UUID-C | Sirf PostgreSQL ka local user |

`UUID-A`, `UUID-B` aur `UUID-C` different hain, chahe Google `sub` aur email
same hon.

Reason:

Har selected repository sirf apni database read/write karti hai. Koi shared
global users table nahi hai.

TodoFlow JWT ke payload mein yeh claim bhi hoti hai:

```text
database = firestore | mongodb | postgresql
```

Isi liye MongoDB ki JWT PostgreSQL select karne ke baad reject ho jati hai.

## 10. Existing password account ke sath kya hota hai?

Aik selected database ke andar:

- Existing Google `sub` mil jaye -> same local UID se login.
- New Google `sub` aur unused email ho -> new local UID create.
- Same Gmail/Google Workspace email ka password account ho -> Google usi local
  account se safely link.
- Same non-Gmail third-party email ka password account ho -> automatic link ke
  bajaye password login required.

Gmail/Workspace restriction ka reason security hai. In cases mein Google email
ka authoritative provider hota hai.

## 11. Request aur response ka shape

Request:

```http
POST /auth/google
Content-Type: application/json

{
  "credential": "eyJ...Google-ID-token..."
}
```

Successful response:

```json
{
  "uid": "local-database-uuid",
  "email": "student@gmail.com",
  "token": "TodoFlow.database-bound.JWT",
  "message": "Google login successful"
}
```

Google ID token response mein wapas nahi jata aur application session ke taur
par store nahi hota.

## 12. Terminal logs mein kya nazar aaye ga?

```text
Presentation   | Google login request received.
Infrastructure | PostgreSQL/MongoDB/Firestore Google authentication succeeded.
Application    | Google login completed.
```

Password ya token ki actual value logs mein print nahi hoti.

## 13. Database switch karke kaise test karein?

Backend stop karein, phir aik database select karein:

```powershell
$env:DATABASE = "firestore"
python -m uvicorn main:app --reload

$env:DATABASE = "mongodb"
python -m uvicorn main:app --reload

$env:DATABASE = "postgresql"
python -m uvicorn main:app --reload
```

Har restart ke baad same Google account se login karein. Phir user yahan check
karein:

- Firestore Console -> `auth_users` collection;
- MongoDB Compass -> `users` collection;
- pgAdmin -> `users` table.

Har database mein different local UID honi chahiye.

## 14. Security checklist

- Google ID token backend par verify hota hai.
- Expected Client ID/audience verify hoti hai.
- Stable Google `sub` database mein save hota hai.
- Verified email required hai.
- Todo ownership local database UUID se hoti hai.
- TodoFlow JWT selected database se bound hoti hai.
- Client secret frontend/backend mein store nahi hota.
- Downloaded client-secret JSON Git mein commit nahi hoti.
- TodoFlow JWT `localStorage` ke bajaye memory mein rehti hai.

## 15. Common problems aur solutions

### Google button `setup pending` show kare

Client ID dono `.env` files mein set karein aur backend/frontend restart karein.

### `The given origin is not allowed`

Google Cloud mein exact frontend URL Authorized JavaScript origins mein add
karein. `localhost` aur `127.0.0.1` alag origins hain, isliye dono add karein.

### `Invalid Google login`

Confirm karein ke frontend aur backend mein exact same Web Client ID hai.

### Aik database mein account hai, doosri mein nahi

Yeh expected behavior hai. Har selected database ke sath aik dafa Google login
karein.

### Database switch ke baad purani JWT par 401 aaye

Yeh expected security behavior hai. New selected database mein dobara login
karein.

## 16. Implementation ke waqt kya verify kiya gaya?

Yeh checks successfully run huay:

- Google claims mapping aur invalid-token rejection;
- Google-only account par password rejection;
- real Firestore, MongoDB aur PostgreSQL mein password + Google linking;
- same database mein repeat Google login par same UID;
- teen databases mein same identity ke different local UIDs;
- cross-database JWT rejection;
- `/auth/google` HTTP aur OpenAPI contract;
- backend compile aur dependency health;
- frontend lint aur production build.

Temporary verification users tests ke baad delete kar diye gaye.

## 17. Presentation mein ready answer

> “Frontend Google Identity Services se Google ID token leta hai aur usay
> `POST /auth/google` par bhejta hai. Backend official `google-auth` library se
> token verify karta hai aur Google ka stable `sub` identifier use karta hai.
> Current selected repository sirf apni database mein local user find ya create
> karti hai. Isi liye same Google account ko Firestore, MongoDB aur PostgreSQL
> mein different local UIDs milti hain. Aakhir mein TodoFlow apni database-bound
> JWT issue karta hai jo protected todo requests mein use hoti hai. Google
> identity prove karta hai, lekin actual application account aur tasks selected
> database own karti hai.”

## 18. Important code links

- [Google button](../frontend/src/components/GoogleSignInButton.jsx)
- [Frontend authentication thunk](../frontend/src/features/auth/authSlice.js)
- [Auth HTTP route](../backend/DDD/app/presentation/routers/auth.py)
- [Auth application service](../backend/DDD/app/application/auth_service.py)
- [Auth contract](../backend/DDD/app/domain/auth.py)
- [Google/JWT security](../backend/DDD/app/infrastructure/security.py)
- [Firestore auth adapter](../backend/DDD/app/infrastructure/firestore/auth_repository.py)
- [MongoDB auth adapter](../backend/DDD/app/infrastructure/mongodb/auth_repository.py)
- [PostgreSQL auth adapter](../backend/DDD/app/infrastructure/postgresql/auth_repository.py)
