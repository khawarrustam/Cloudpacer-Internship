# TodoFlow frontend

A beginner-friendly React frontend for the Todo DDD API.

Roman Urdu: Yeh React frontend simple modules mein divide hai. Har module ka aik clear kaam hai, is liye code ko parhna aur change karna asaan hai.

## Start here

The app uses:

- React for the screen
- Redux Toolkit for shared state
- Axios for backend requests
- Tailwind CSS for styling
- Vite for local development and builds

The frontend runs on `http://localhost:5173` and calls the backend on `http://127.0.0.1:8000` by default.

## Run the frontend

First start the backend. Then open a second PowerShell window:

```powershell
cd todo-frontend
npm install
npm run dev
```

Open the URL shown by Vite, normally:

```text
http://localhost:5173
```

To make a production build:

```powershell
npm run build
```

## Optional environment setting

Create `.env` inside `todo-frontend` only when the backend uses another URL:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Roman Urdu: Agar backend isi default URL par hai to `.env` ki zaroorat nahi.

## Easy architecture

```text
main.jsx
  |
  +-- Redux Provider and Toast Provider
        |
        +-- App.jsx
              |
              +-- useAuth
              |     +-- authSlice
              |     +-- authApi
              |     +-- authStorage
              |
              +-- TodoDashboard
                    +-- useTodos
                    |     +-- todosSlice
                    |     +-- taskViewSlice
                    |     +-- todoApi
                    |
                    +-- DashboardHero
                    +-- TodoListPanel
                    +-- AddTodoForm
                    +-- FocusCard
```

Roman Urdu: `App.jsx` sirf decide karta hai login screen dikhani hai ya dashboard. Detail hooks aur small components mein hai.

## Folder guide

```text
src/
|-- api/
|   |-- client.js          # Axios setup and login token
|   |-- authApi.js         # Signup and login requests
|   |-- todoApi.js         # Todo CRUD requests
|   +-- errors.js          # API error messages
|
|-- app/
|   +-- store.js           # All Redux slices connect here
|
|-- components/
|   |-- AuthForm.jsx
|   |-- TodoDashboard.jsx  # Small dashboard coordinator
|   |-- TodoItem.jsx
|   |-- todos/             # Dashboard sections
|   +-- ui/                # Reusable buttons, cards, inputs
|
|-- features/
|   |-- auth/
|   |   |-- authSlice.js
|   |   +-- authStorage.js
|   |-- todos/
|   |   |-- todosSlice.js
|   |   +-- todosSelectors.js
|   +-- taskView/
|       +-- taskViewSlice.js
|
|-- hooks/
|   |-- useAuth.js
|   |-- useTodos.js
|   +-- useKeyboardShortcuts.js
|
|-- App.jsx
|-- main.jsx
+-- index.css
```

## Data flow in simple steps

### Login

1. `AuthForm` calls `login` from `useAuth`.
2. `useAuth` dispatches `loginUser`.
3. `authSlice` calls `authApi.login`.
4. The token is saved by `authStorage`.
5. Redux stores the user, so `App` shows the dashboard.

Roman Urdu: Form se action Redux ko jata hai, API call hoti hai, phir user state update hoti hai.

### Load todos

1. `TodoDashboard` calls `useTodos`.
2. `useTodos` dispatches `fetchTodos` once.
3. `todosSlice` calls `todoApi.getAll`.
4. Redux stores the returned list.
5. Selectors filter and sort the list.
6. `TodoListPanel` shows the result.

### Add, complete, or delete

The screen calls one simple function from `useTodos`:

- `addTodo`
- `finishTodo`
- `removeTodo`

The hook dispatches the correct Redux action. The slice updates state after the backend succeeds.

Roman Urdu: UI ko Axios ya Redux thunk ki detail nahi pata. UI sirf simple hook function call karti hai.

## Why Redux is used once

The old code had two possible state systems: Redux and separate `useState` todo/auth hooks. That could make two copies of the same data.

Now:

- Redux is the only shared data source.
- `useAuth` is a small Redux interface for authentication.
- `useTodos` is a small Redux interface for todos.
- Local `useState` is only used for temporary form or modal values.
- Frontend data flow is explained with English and Roman Urdu comments.
- Backend flow is not printed in the browser console; backend terminal owns those logs.

Roman Urdu: Shared data aik jagah Redux mein hai. Form ka temporary text local state mein hai.

### Redux flow to remember

```text
Component -> custom hook -> dispatch(thunk) -> API
API response -> fulfilled reducer -> Redux state -> selector -> component
```

Roman Urdu: Component action dispatch karta hai. API result reducer Redux mein save karta hai, phir selector updated data component ko deta hai.

### Redux files and their simple jobs

- `store.js`: joins all Redux slices in one store.
- `authSlice.js`: keeps the login user and login status.
- `todosSlice.js`: loads, adds, completes, and deletes todos.
- `taskViewSlice.js`: keeps search, filter, and sort choices.
- `todosSelectors.js`: reads Redux data and prepares the visible list.
- `useAuth.js` and `useTodos.js`: give components short, easy functions.

Roman Urdu: Slice data save karta hai, selector data read karta hai, aur hook component ko easy functions deta hai.

## Important files to learn first

Read these in order:

1. `src/App.jsx`
2. `src/hooks/useAuth.js`
3. `src/hooks/useTodos.js`
4. `src/features/todos/todosSlice.js`
5. `src/api/todoApi.js`
6. `src/components/TodoDashboard.jsx`
7. `src/components/todos/`

## Adding a new backend action

Example: add an edit feature.

1. Add `update(id, data)` in `todoApi.js`.
2. Add an async thunk in `todosSlice.js`.
3. Update the todo in the fulfilled reducer.
4. Expose a simple `editTodo` function from `useTodos.js`.
5. Call it from a small UI component.

Roman Urdu: Har feature API se slice, phir hook, phir component tak seedha flow follow karta hai.

## Common problems

### The page says it cannot connect

Make sure the backend is running:

```powershell
cd ..\Todo-List\todo_api
uvicorn main:app --reload
```

### Login fails

Authentication uses Firebase. Check the backend Firebase service account and `FIREBASE_WEB_API_KEY`.

### The session expires

A `401` response clears the saved session automatically. Log in again.

### The wrong backend is called

Check `VITE_API_URL` in `.env`, then restart `npm run dev`.

## Useful commands

```powershell
npm run dev
npm run build
npm run preview
```

The project currently has no ESLint configuration file, so use `npm run build` as the main frontend verification command.
