# TodoFlow ko Redux Toolkit par migrate karne ki complete guide

> Audience: React/Redux beginner
>
> Language: Roman Urdu + simple English
>
> Scope: Is project ka **current frontend audit**, Redux concepts, required slices/reducers, complete data flow, aur safe migration roadmap.

## Copy/paste index: exact files aur line numbers

Yeh links GitHub ke committed **pre-Redux baseline `f373040`** ko point karti hain. Yeh permanent links hain, is liye future edits ke baad bhi old code exact lines par khulega.

- Pehli edit ke baad local line numbers shift ho sakte hain; phir function/variable name search karo.
- Link par highlighted block compare karo; line-number text ko code ke sath copy mat karna.
- `New file line 1` ka matlab blank file mein guide ka poora code line 1 se paste karna hai.
- Migration phase-by-phase karo aur har phase ke baad app test karo.

### Current code line map

| Feature | Exact current lines | Abhi kya ho raha hai? |
|---|---|---|
| React root | [`main.jsx` 1-13](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/main.jsx#L1-L13) | `StrictMode`, `ToastProvider`, `App`; Redux Provider nahi. |
| Auth imports/state | [`App.jsx` 1-28](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/App.jsx#L1-L28) | `useAuth()` aur duplicate `isLoggedIn` state. |
| Auth effect | [`App.jsx` 30-53](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/App.jsx#L30-L53) | Token check aur `auth-failure` listener. |
| Auth handlers | [`App.jsx` 55-74](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/App.jsx#L55-L74) | Signup/login/logout custom-hook calls. |
| Auth rendering | [`App.jsx` 76-103](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/App.jsx#L76-L103) | Loading, AuthForm ya dashboard decision. |
| Auth custom hook | [`useAuth.js` 17-87](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/hooks/useAuth.js#L17-L87) | User/loading/error, APIs aur storage. |
| Todos custom hook | [`useTodos.js` 17-104](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/hooks/useTodos.js#L17-L104) | Todo state, fetch effect aur CRUD. |
| JWT request interceptor | [`client.js` 11-18](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/api/client.js#L11-L18) | Token Authorization header mein lagata hai. |
| Old `401` bridge | [`client.js` 20-31](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/api/client.js#L20-L31) | Storage clear + `auth-failure` event. |
| Dashboard imports/state | [`TodoDashboard.jsx` 1-37](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L1-L37) | `useTodos`, forms, filters aur request flags. |
| Keyboard effect - keep local | [`TodoDashboard.jsx` 40-56](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L40-L56) | `/` aur `N` shortcuts. |
| Stats | [`TodoDashboard.jsx` 59-64](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L59-L64) | Local `useMemo`; future `selectTodoStats`. |
| Visible todos | [`TodoDashboard.jsx` 66-91](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L66-L91) | Filter/sort `useMemo`; future selector. |
| Todo CRUD handlers | [`TodoDashboard.jsx` 95-139](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L95-L139) | Add, complete aur delete calls. |
| Todo row flags | [`TodoDashboard.jsx` 177-186](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L177-L186) | Current completing/deleting ID comparison. |
| Search/sort/refresh | [`TodoDashboard.jsx` 238-254](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L238-L254) | Local setters aur refresh callback. |
| Filter buttons | [`TodoDashboard.jsx` 258-268](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L258-L268) | `setFilter` ko Redux action banana hai. |
| Auth form - keep local | [`AuthForm.jsx` 7-28](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/AuthForm.jsx#L7-L28) | Email/password/name/form mode. |
| Toast system | [`Toast.jsx` 4-40](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/ui/Toast.jsx#L4-L40) | Optional last migration. |
| Modal ref/effect - keep local | [`ConfirmModal.jsx` 5-26](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/ui/ConfirmModal.jsx#L5-L26) | DOM focus/keyboard behavior. |

### Exact copy/paste order

| Step | File and line | Kya karna hai? | Code kahan hai? |
|---:|---|---|---|
| 1 | `todo-frontend/package.json` dependencies | Install command run karo; JSON manually paste na karo. | [Phase 1](#phase-1--packages-install-karo) |
| 2 | `src/features/taskView/taskViewSlice.js`, **new file line 1** | Poora taskView slice paste karo. | [Phase 2](#phase-2--sab-se-simple-taskviewslice) |
| 3 | `src/app/store.js`, **new file line 1** | Initial store paste karo. | [Phase 3](#phase-3--store-banao) |
| 4 | [`src/main.jsx` 1-13](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/main.jsx#L1-L13) | Poora file Provider wale block se replace karo. | [Phase 4](#phase-4--root-par-provider-lagao) |
| 5a | [`TodoDashboard.jsx` 1-19](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L1-L19) | React-Redux/taskView imports add karo; `useTodos` todos phase tak rehne do. | [Phase 5](#phase-5--dashboard-ke-filtersearchsort-connect-karo) |
| 5b | [`TodoDashboard.jsx` 32-34](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L32-L34) | Filter/query/sort local states remove; selector block component ke start par paste karo. | [Phase 5](#phase-5--dashboard-ke-filtersearchsort-connect-karo) |
| 5c | [`TodoDashboard.jsx` 242](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L242) | `setQuery(...)` ko `dispatch(queryChanged(...))` se replace karo. | [Phase 5](#phase-5--dashboard-ke-filtersearchsort-connect-karo) |
| 5d | [`TodoDashboard.jsx` 248](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L248) | `setSort(...)` ko `dispatch(sortChanged(...))` se replace karo. | [Phase 5](#phase-5--dashboard-ke-filtersearchsort-connect-karo) |
| 5e | [`TodoDashboard.jsx` 264](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L264) | `setFilter(...)` ko `dispatch(filterChanged(...))` se replace karo. | [Phase 5](#phase-5--dashboard-ke-filtersearchsort-connect-karo) |
| 6 | `src/features/auth/authSlice.js`, **new file line 1** | Poora auth slice paste karo. | [`authSlice` code](#9-authslice-ka-recommended-code) |
| 7 | `src/app/store.js` | `authReducer` import aur `auth:` entry add karo. | [`authSlice` code](#9-authslice-ka-recommended-code) |
| 8 | [`src/App.jsx` 1-104](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/App.jsx#L1-L104) | Poora file Redux App block se replace karo. | [Auth component flow](#10-auth-component-flow-redux-ke-baad) |
| 9 | [`src/api/client.js` 1-33](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/api/client.js#L1-L33) | Poora file callback-registration version se replace karo. | [Axios 401 bridge](#11-axios-401-ko-redux-se-connect-karna--circular-import-ke-baghair) |
| 10 | `src/main.jsx`, imports ke baad, render se pehle | `setUnauthorizedHandler(...)` registration paste karo. | [Axios 401 bridge](#11-axios-401-ko-redux-se-connect-karna--circular-import-ke-baghair) |
| 11 | `src/features/todos/todosSlice.js`, **new file line 1** | Poora todos slice paste karo. | [`todosSlice` code](#12-todosslice-ka-recommended-code) |
| 12 | `src/features/todos/todosSelectors.js`, **new file line 1** | Poora selectors block paste karo. | [Derived selectors](#13-derived-data-ke-selectors) |
| 13 | `src/app/store.js` | `todosReducer` import aur `todos:` entry add karo. | [`todosSlice` code](#12-todosslice-ka-recommended-code) |
| 14a | [`TodoDashboard.jsx` 1-37](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L1-L37) | `useTodos` aur old request flags replace karo. `text`, `priority`, `submitError`, `deleteTarget` local rakho. | [Dashboard migration](#14-tododashboard-migration-pattern) |
| 14b | [`TodoDashboard.jsx` 59-91](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L59-L91) | Stats/visibleTodos `useMemo` remove; selector results use karo. | [Dashboard migration](#14-tododashboard-migration-pattern) |
| 14c | [`TodoDashboard.jsx` 95-139](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L95-L139) | CRUD handlers dispatch + `.unwrap()` versions se replace karo. | [Dashboard migration](#14-tododashboard-migration-pattern) |
| 14d | [`TodoDashboard.jsx` 177-186](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L177-L186) | Row flags ko `completingIds[todo.id]` / `deletingIds[todo.id]` se replace karo. | [Dashboard migration](#14-tododashboard-migration-pattern) |
| 15 | `src/features/notifications/notificationsSlice.js`, **optional new file line 1** | Auth/todos stable hone ke baad hi paste karo. | [Optional notifications](#17-optional-notificationsslice) |
| 16 | [`useAuth.js` 1-87](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/hooks/useAuth.js#L1-L87) and [`useTodos.js` 1-104](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/hooks/useTodos.js#L1-L104) | Sab imports remove aur Redux flow verify hone ke baad old files delete karo. | [One-to-one mapping](#16-current-to-redux-one-to-one-mapping) |

### Line-number safety rule

Har step ke baad:

```bash
npm run lint
npm run build
```

Agar lines shift ho chuki hon to VS Code mein `Ctrl+F` se relevant symbol search karo, jaise `const visibleTodos`, `handleComplete`, `setFilter`, ya `auth-failure`. Symbol name line number se zyada reliable hota hai.

## 1. Short answer: abhi Redux ki jagah kya use ho raha hai?

Is app mein abhi Redux, Redux Toolkit, Zustand ya koi doosri global state library installed nahi hai.

Current app state ko in cheezon se manage karta hai:

1. **React `useState`** — component ke andar state rakhne ke liye.
2. **Custom hooks (`useAuth`, `useTodos`)** — related state aur functions ko ek file mein organize karne ke liye.
3. **Props aur callback functions** — parent se child component tak data/actions bhejne ke liye.
4. **`localStorage`** — login token aur basic user data ko browser reload ke baad bachane ke liye.
5. **Axios interceptors** — har request mein JWT token lagane aur `401 Unauthorized` handle karne ke liye.
6. **Browser `CustomEvent` events** — door components/code ke darmiyan global notification bhejne ke liye:
   - `auth-failure`
   - `app-toast`
7. **`useMemo`** — todos se filtered list aur statistics derive karne ke liye.

Important distinction:

- Custom hook Redux ka replacement nahi hota.
- Custom hook logic reuse karta hai, lekin har mounted hook instance ki apni local state hoti hai.
- Redux store application ke top par ek shared, central state container hota hai.

Is waqt app chhota hai, is liye current approach valid hai. Redux Toolkit zaroori nahi, magar Redux seekhne aur app ko future scaling ke liye structure karne ke liye yeh project bohat acha exercise hai.

---

## 2. Maine current frontend mein kya trace kiya?

### Application entry: `src/main.jsx`

Current component tree roughly yeh hai:

```text
StrictMode
└── ToastProvider
    └── App
        ├── AuthForm            (logged out)
        └── TodoDashboard      (logged in)
            ├── Navbar
            ├── TodoItem(s)
            └── ConfirmModal
```

`main.jsx` mein abhi Redux ka `<Provider>` nahi hai. Isi wajah se kisi component ke paas central Redux store available nahi.

### Current state ownership map

| State/data | Abhi kahan hai? | Abhi ka mechanism | Recommended future place |
|---|---|---|---|
| Logged-in user | `useAuth` | `useState` + `localStorage` | `authSlice` |
| Auth loading/error | `useAuth` | `useState` | `authSlice` |
| Logged-in view decision | `App` | `isLoggedIn` `useState` | `auth` selector |
| Todos list | `useTodos` | `useState` | `todosSlice` |
| Fetch/add/complete/delete status | `useTodos` + `TodoDashboard` | multiple `useState` | `todosSlice` |
| Fetch/API errors | `useTodos` | `useState` | `todosSlice` |
| Filter/search/sort | `TodoDashboard` | `useState` | `taskViewSlice` (learning choice) |
| Derived stats/progress | `TodoDashboard` | `useMemo` | memoized selectors |
| Auth form inputs | `AuthForm` | `useState` | **local state hi rehni chahiye** |
| New todo title/priority | `TodoDashboard` | `useState` | **local state recommended** |
| Delete modal target | `TodoDashboard` | `useState` | **local state recommended** |
| Toast messages | `ToastProvider` | `useState` + browser event | optional `notificationsSlice` |
| JWT token | browser storage | `localStorage` | storage/cookie; Redux mein nahi |
| Modal DOM ref/focus | `ConfirmModal` | `useRef` | **kabhi Redux mein nahi** |

---

## 3. Current app ka exact flow

### 3.1 Page load aur authentication

```text
Browser opens app
  ↓
main.jsx renders <App />
  ↓
useAuth() localStorage se user_uid/user_email read karta hai
  ↓
App ka useEffect auth_token read karta hai
  ↓
token hai → TodoDashboard
token nahi → AuthForm
```

Yahan ek hi truth do jagah represent ho rahi hai:

- `App.isLoggedIn`
- `useAuth.user`

Yeh abhi kaam karta hai, lekin dono accidentally out of sync ho sakte hain. Redux migration ke baad `selectIsAuthenticated` ek hi source of truth hoga.

### 3.2 Login/signup

```text
AuthForm submit
  ↓ props callback
App.handleLogin / App.handleSignup
  ↓ custom hook
useAuth.login / useAuth.signup
  ↓
authApi → Axios → backend
  ↓ success
token, uid, email localStorage mein save
  ↓
useAuth.user update + App.isLoggedIn true
  ↓
React re-render → TodoDashboard
```

### 3.3 Todos load

```text
TodoDashboard mounts
  ↓
useTodos mounts
  ↓ useEffect
fetchTodos()
  ↓
todoApi.getAll() → Axios → GET /todos
  ↓
setTodos(data)
  ↓
TodoDashboard re-renders
```

### 3.4 Add, complete aur delete

- Add: API result ko `[...previous, newTodo]` se local array mein add kiya jata hai.
- Complete: `map` se matching todo replace hota hai.
- Delete: `filter` se matching todo remove hota hai.
- Yeh **request successful hone ke baad update** hai; strict meaning mein optimistic update nahi.

### 3.5 Expired session (`401`)

```text
Any Axios request returns 401
  ↓
response interceptor localStorage clear karta hai
  ↓
window par "auth-failure" event dispatch hota hai
  ↓
App ka event listener isLoggedIn=false karta hai
  ↓
AuthForm render hota hai
```

Redux ke baad browser event ki jagah `store.dispatch(sessionExpired())` use hoga.

### 3.6 Toast flow

```text
toast.success("Task added")
  ↓
window par "app-toast" event
  ↓
ToastProvider event listen karta hai
  ↓
local toasts state update
  ↓
timer ke baad toast remove
```

Redux migration mein notifications optional hain. Toast system Redux ke baghair bhi bilkul valid hai.

---

## 4. Redux ko zero se samjho

### Store

Store ek central JavaScript object hai jahan app ki shared state hoti hai.

```js
{
  auth: { user: null, status: 'idle', error: null },
  todos: { items: [], fetchStatus: 'idle' },
  taskView: { filter: 'all', query: '', sort: 'smart' }
}
```

Roman Urdu: Store ko app ki central memory samjho.

### Action

Action ek plain object hai jo batata hai **kya hua**.

```js
{ type: 'taskView/filterChanged', payload: 'completed' }
```

Roman Urdu: Action request/order hai, direct state change nahi.

### Dispatch

`dispatch(action)` action ko Redux store tak bhejta hai.

```js
dispatch(filterChanged('completed'));
```

### Reducer

Reducer decide karta hai ke action aane par state kaise change hogi.

```js
filterChanged(state, action) {
  state.filter = action.payload;
}
```

Reducer rules:

- reducer synchronous aur predictable hona chahiye;
- reducer ke andar API request, timer, `localStorage`, DOM access ya random side effect nahi hona chahiye;
- Redux Toolkit Immer use karta hai, is liye reducer ke andar `state.filter = ...` likhna safe hai. Actual state immutable tareeqe se update hoti hai.

### Slice

Slice feature ki state + reducers + generated actions ka bundle hai.

```js
const taskViewSlice = createSlice({
  name: 'taskView',
  initialState,
  reducers: { ... },
});
```

### Selector

Selector store se data read ya derive karta hai.

```js
const selectTodos = (state) => state.todos.items;
```

Component:

```js
const todos = useSelector(selectTodos);
```

### Thunk

Thunk async logic ka function hai. API call thunk mein hogi, reducer mein nahi.

```text
component dispatches thunk
  ↓
pending action
  ↓
API call
  ├── success → fulfilled action
  └── failure → rejected action
```

`createAsyncThunk` yeh teen lifecycle actions automatically banata hai.

### Provider

`<Provider store={store}>` component tree ko store deta hai. Iske andar ke components `useSelector` aur `useDispatch` use kar sakte hain.

### `useSelector` vs `useDispatch`

- `useSelector`: store se value **read** karo.
- `useDispatch`: action/thunk **send** karo.

```js
const todos = useSelector((state) => state.todos.items);
const dispatch = useDispatch();

dispatch(fetchTodos());
```

---

## 5. Is app ke liye kaun se slices chahiye?

### Required slice 1: `authSlice`

Owns:

```js
{
  user: null,
  status: 'idle', // idle | loading | succeeded | failed
  error: null
}
```

Async thunks:

- `loginUser({ email, password })`
- `signupUser({ email, password, displayName })`

Synchronous reducers/actions:

- `loggedOut()`
- `sessionExpired()`
- `clearAuthError()`

Selectors:

- `selectCurrentUser`
- `selectIsAuthenticated`
- `selectAuthStatus`
- `selectAuthError`

### Required slice 2: `todosSlice`

Owns:

```js
{
  items: [],
  fetchStatus: 'idle',
  createStatus: 'idle',
  completingIds: {},
  deletingIds: {},
  fetchError: null,
  mutationError: null
}
```

Async thunks:

- `fetchTodos()`
- `createTodo({ title, priority })`
- `completeTodo(id)`
- `deleteTodo(id)`

Synchronous reducers/actions:

- `clearTodosError()`
- `resetTodos()`

Selectors:

- `selectAllTodos`
- `selectTodosLoading`
- `selectTodoStats`
- `selectVisibleTodos`
- `selectIsCompletingById`
- `selectIsDeletingById`

### Recommended learning slice 3: `taskViewSlice`

Owns:

```js
{
  filter: 'all',
  query: '',
  sort: 'smart'
}
```

Reducers/actions:

- `filterChanged(value)`
- `queryChanged(value)`
- `sortChanged(value)`
- `taskViewReset()`

Why separate? `todos` server/business data hai; `taskView` sirf UI ke viewing rules hain. Separation se har slice ka purpose clear rehta hai.

### Optional slice 4: `notificationsSlice`

Owns toast list. Reducers:

- `notificationAdded({ id, type, message })`
- `notificationRemoved(id)`

Timer reducer mein nahi; thunk ya component effect mein chalega.

Beginner recommendation: pehle existing Toast system rehne do. Auth + todos + taskView samajhne ke baad notification migrate karo.

---

## 6. Har `useState` Redux mein kyun nahi jana chahiye?

Official Redux guidance ke mutabiq local component state bilkul valid hai. Redux mein woh state rakho jo:

- multiple components ko chahiye;
- app-wide shared hai;
- cache/restore/debug karni hai;
- multiple values derive karti hai;
- component unmount hone ke baad bhi relevant hai.

Local hi rakho:

- login email/password/name inputs;
- show/hide password;
- new task title aur priority (jab tak form sirf isi component mein hai);
- current modal target;
- DOM refs/focus;
- keyboard event listener;
- temporary form validation message.

Redux mein **mat** rakho:

- functions;
- Promises;
- `Error` class instances;
- DOM nodes/refs;
- `Map`/`Set` (plain objects/arrays use karo);
- Axios response object;
- timers.

JWT token Redux state mein duplicate mat karo. Current setup mein request interceptor token `localStorage` se read karta hai. Long-term production security ke liye backend-supported `HttpOnly`, `Secure`, `SameSite` cookie localStorage JWT se safer hoti hai, kyun ke JavaScript HttpOnly cookie read nahi kar sakta. Yeh backend/auth design change hoga, sirf Redux change nahi.

---

## 7. Target folder structure

```text
src/
├── api/
│   ├── client.js
│   ├── authApi.js
│   └── todoApi.js
├── app/
│   └── store.js
├── features/
│   ├── auth/
│   │   └── authSlice.js
│   ├── todos/
│   │   ├── todosSlice.js
│   │   └── todosSelectors.js
│   ├── taskView/
│   │   └── taskViewSlice.js
│   └── notifications/          # optional, last phase
│       └── notificationsSlice.js
├── components/
├── App.jsx
└── main.jsx
```

Feature folders ka matlab: feature ka related Redux code ek jagah. `components` ke naam par root state slices mat banao; data/feature ke naam par banao.

---

## 8. Copy/paste migration order

Har phase ke baad app run/test karo. Sab kuch ek hi baar replace karoge to bug ka source samajhna mushkil hoga.

### Section 8 line-number summary

Yeh line numbers committed pre-migration version `f373040` ke hain. Blue link par click karoge to GitHub exact lines highlight karega.

| Phase | Paste/edit location |
|---|---|
| Phase 1 | Terminal command hai; kisi source-code line par paste nahi karna. |
| Phase 2 | `src/features/taskView/taskViewSlice.js` **new file, line 1**. |
| Phase 3 | `src/app/store.js` **new file, line 1**. |
| Phase 4 | [`src/main.jsx` lines 1-13 replace karo](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/main.jsx#L1-L13). |
| Phase 5 imports | [`TodoDashboard.jsx` lines 1-19](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L1-L19). |
| Phase 5 local state | [`TodoDashboard.jsx` lines 32-34 remove/replace karo](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L32-L34). |
| Phase 5 search | [`TodoDashboard.jsx` line 242](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L242): `setQuery` replace karo. |
| Phase 5 sort | [`TodoDashboard.jsx` line 248](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L248): `setSort` replace karo. |
| Phase 5 filter | [`TodoDashboard.jsx` line 264](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L264): `setFilter` replace karo. |

Note: ek edit ke baad local lines shift ho sakti hain. Is surat mein `Ctrl+F` se `setQuery`, `setSort`, ya `setFilter` search karo.

### Phase 1 — packages install karo

Frontend directory mein:

```bash
cd todo-frontend
npm install @reduxjs/toolkit react-redux
```

Roles:

- `@reduxjs/toolkit`: store, slices, thunks, selectors.
- `react-redux`: React ko Redux se connect karne wala `<Provider>`, `useSelector`, `useDispatch`.

### Phase 2 — sab se simple `taskViewSlice`

Pehle API ke baghair filter/search/sort Redux par shift karo. Is se action → reducer → selector → UI flow samajh aayega.

Paste location: `src/features/taskView/taskViewSlice.js` **new file, line 1**.

```js
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  filter: 'all',
  query: '',
  sort: 'smart',
};

const taskViewSlice = createSlice({
  name: 'taskView',
  initialState,
  reducers: {
    filterChanged(state, action) {
      state.filter = action.payload;
    },
    queryChanged(state, action) {
      state.query = action.payload;
    },
    sortChanged(state, action) {
      state.sort = action.payload;
    },
    taskViewReset() {
      return initialState;
    },
  },
});

export const {
  filterChanged,
  queryChanged,
  sortChanged,
  taskViewReset,
} = taskViewSlice.actions;

export const selectTaskFilter = (state) => state.taskView.filter;
export const selectTaskQuery = (state) => state.taskView.query;
export const selectTaskSort = (state) => state.taskView.sort;

export default taskViewSlice.reducer;
```

### Phase 3 — store banao

Paste location: `src/app/store.js` **new file, line 1**.

```js
import { configureStore } from '@reduxjs/toolkit';
import taskViewReducer from '../features/taskView/taskViewSlice';

export const store = configureStore({
  reducer: {
    taskView: taskViewReducer,
  },
});
```

`configureStore` automatically:

- slice reducers combine karta hai;
- thunk middleware add karta hai;
- development checks add karta hai;
- Redux DevTools integration enable karta hai.

### Phase 4 — root par Provider lagao

Paste location: [`src/main.jsx` ki current lines 1-13](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/main.jsx#L1-L13) ko neeche wale poore block se replace karo.

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import App from './App';
import { store } from './app/store';
import { ToastProvider } from './components/ui/Toast';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <ToastProvider>
        <App />
      </ToastProvider>
    </Provider>
  </React.StrictMode>,
);
```

Provider ke baghair `useSelector`/`useDispatch` use karne par “could not find react-redux context value” type error aayega.

### Phase 5 — Dashboard ke filter/search/sort connect karo

Edit locations: imports [`lines 1-19`](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L1-L19), local filter state [`lines 32-34`](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L32-L34), aur JSX handlers [`lines 242, 248, 264`](https://github.com/khawarrustam/Cloudpacer-Internship/blob/f373040/todo-frontend/src/components/TodoDashboard.jsx#L242-L264).

Old local state remove:

```js
const [filter, setFilter] = useState('all');
const [query, setQuery] = useState('');
const [sort, setSort] = useState('smart');
```

New imports/state:

```js
import { useDispatch, useSelector } from 'react-redux';
import {
  filterChanged,
  queryChanged,
  sortChanged,
  selectTaskFilter,
  selectTaskQuery,
  selectTaskSort,
} from '../features/taskView/taskViewSlice';

const dispatch = useDispatch();
const filter = useSelector(selectTaskFilter);
const query = useSelector(selectTaskQuery);
const sort = useSelector(selectTaskSort);
```

Event handlers replace:

```jsx
onChange={(event) => dispatch(queryChanged(event.target.value))}
onChange={(event) => dispatch(sortChanged(event.target.value))}
onClick={() => dispatch(filterChanged(item.value))}
```

Redux DevTools mein ab actions nazar aayenge:

```text
taskView/queryChanged
taskView/sortChanged
taskView/filterChanged
```

---

## 9. `authSlice` ka recommended code

Create `src/features/auth/authSlice.js`:

```js
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { authApi } from '../../api/authApi';

function readStoredUser() {
  const token = localStorage.getItem('auth_token');
  const uid = localStorage.getItem('user_uid');
  const email = localStorage.getItem('user_email');

  return token && uid ? { uid, email: email || '' } : null;
}

function saveSession(data) {
  localStorage.setItem('auth_token', data.token);
  localStorage.setItem('user_uid', data.uid);
  localStorage.setItem('user_email', data.email || '');
}

function clearSession() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_uid');
  localStorage.removeItem('user_email');
}

function getErrorMessage(error, fallback) {
  return error.response?.data?.detail || fallback;
}

export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const data = await authApi.login({ email, password });
      saveSession(data);
      return { uid: data.uid, email: data.email || email };
    } catch (error) {
      return rejectWithValue(
        getErrorMessage(error, 'Login failed. Please check your credentials.'),
      );
    }
  },
);

export const signupUser = createAsyncThunk(
  'auth/signupUser',
  async ({ email, password, displayName }, { rejectWithValue }) => {
    try {
      const data = await authApi.signup({
        email,
        password,
        display_name: displayName,
      });
      saveSession(data);
      return { uid: data.uid, email: data.email || email };
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, 'Signup failed'));
    }
  },
);

const initialState = {
  user: readStoredUser(),
  status: 'idle',
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loggedOut(state) {
      state.user = null;
      state.status = 'idle';
      state.error = null;
    },
    sessionExpired(state) {
      state.user = null;
      state.status = 'idle';
      state.error = 'Your session expired. Please sign in again.';
    },
    clearAuthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || action.error.message;
      })
      .addCase(signupUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(signupUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(signupUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || action.error.message;
      });
  },
});

export const { loggedOut, sessionExpired, clearAuthError } = authSlice.actions;

export const logoutUser = () => (dispatch) => {
  clearSession();
  dispatch(loggedOut());
};

export const expireSession = () => (dispatch) => {
  clearSession();
  dispatch(sessionExpired());
};

export const selectCurrentUser = (state) => state.auth.user;
export const selectIsAuthenticated = (state) => Boolean(state.auth.user);
export const selectAuthStatus = (state) => state.auth.status;
export const selectAuthError = (state) => state.auth.error;

export default authSlice.reducer;
```

Why storage functions thunk ke aas paas hain, reducer mein nahi?

- `localStorage` write ek side effect hai.
- Reducer pure/predictable rehna chahiye.
- `loggedOut` sirf Redux state change karta hai.
- `logoutUser` thunk pehle storage clear karta hai, phir reducer action dispatch karta hai.

Store mein reducer add karo:

```js
import authReducer from '../features/auth/authSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    taskView: taskViewReducer,
  },
});
```

---

## 10. Auth component flow Redux ke baad

`App.jsx` mein `useAuth`, `isLoggedIn` aur auth event listener ki zaroorat nahi rahegi:

```jsx
import { useDispatch, useSelector } from 'react-redux';
import AuthForm from './components/AuthForm';
import TodoDashboard from './components/TodoDashboard';
import {
  loginUser,
  signupUser,
  logoutUser,
  selectAuthStatus,
  selectCurrentUser,
  selectIsAuthenticated,
} from './features/auth/authSlice';

export default function App() {
  const dispatch = useDispatch();
  const user = useSelector(selectCurrentUser);
  const isLoggedIn = useSelector(selectIsAuthenticated);
  const authStatus = useSelector(selectAuthStatus);

  const handleLogin = async (email, password) => {
    try {
      await dispatch(loginUser({ email, password })).unwrap();
      return { success: true };
    } catch (error) {
      return { success: false, error };
    }
  };

  const handleSignup = async (email, password, displayName) => {
    try {
      await dispatch(signupUser({ email, password, displayName })).unwrap();
      return { success: true };
    } catch (error) {
      return { success: false, error };
    }
  };

  if (!isLoggedIn) {
    return (
      <AuthForm
        onLogin={handleLogin}
        onSignup={handleSignup}
        loading={authStatus === 'loading'}
      />
    );
  }

  return (
    <TodoDashboard
      user={user}
      onLogout={() => dispatch(logoutUser())}
    />
  );
}
```

`unwrap()` kyun?

Normal thunk dispatch resolved Promise deta hai chahe request fulfilled ho ya rejected, kyun ke result ek Redux action hota hai. `.unwrap()`:

- fulfilled par original payload return karta hai;
- rejected par `rejectWithValue` wala error throw karta hai;
- component mein normal `try/catch` possible banata hai.

AuthForm ki email/password/name/showPassword state local hi reh sakti hai. Is component ko Redux janne ki zaroorat bhi nahi; woh callbacks receive karke presentational/reusable rehta hai.

---

## 11. Axios `401` ko Redux se connect karna — circular import ke baghair

`client.js` ke andar directly store/authSlice import karna circular dependency bana sakta hai:

```text
authSlice → authApi → client → store → authSlice
```

Clean callback registration pattern use karo.

`src/api/client.js`:

```js
import axios from 'axios';

let unauthorizedHandler = null;

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler;
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      unauthorizedHandler?.();
    }
    return Promise.reject(error);
  },
);

export default apiClient;
```

`main.jsx`, store create/import hone ke baad:

```js
import { setUnauthorizedHandler } from './api/client';
import { expireSession } from './features/auth/authSlice';
import { store } from './app/store';

setUnauthorizedHandler(() => {
  store.dispatch(expireSession());
});
```

Ab flow:

```text
Axios gets 401
  ↓
registered callback
  ↓
store.dispatch(expireSession())
  ↓
storage cleared + sessionExpired action
  ↓
auth reducer user=null
  ↓
selectIsAuthenticated returns false
  ↓
App automatically renders AuthForm
```

`window.dispatchEvent('auth-failure')` aur `App` ka listener phir delete kiya ja sakta hai.

---

## 12. `todosSlice` ka recommended code

Create `src/features/todos/todosSlice.js`:

```js
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { todoApi } from '../../api/todoApi';
import { loggedOut, sessionExpired } from '../auth/authSlice';

function errorMessage(error, fallback) {
  if (error.response?.status === 401) {
    return 'Session expired. Please log in again.';
  }
  if (error.response?.status === 403) {
    return 'You do not have permission to access these tasks.';
  }
  return error.response?.data?.detail || fallback;
}

export const fetchTodos = createAsyncThunk(
  'todos/fetchTodos',
  async (_, { rejectWithValue }) => {
    try {
      return await todoApi.getAll();
    } catch (error) {
      return rejectWithValue(
        errorMessage(error, 'Unable to connect to the server. Is the backend running?'),
      );
    }
  },
  {
    condition: (_, { getState }) => {
      return getState().todos.fetchStatus !== 'loading';
    },
  },
);

export const createTodo = createAsyncThunk(
  'todos/createTodo',
  async ({ title, priority }, { rejectWithValue }) => {
    try {
      return await todoApi.create({ title, priority });
    } catch (error) {
      return rejectWithValue(errorMessage(error, 'Failed to add todo'));
    }
  },
);

export const completeTodo = createAsyncThunk(
  'todos/completeTodo',
  async (id, { rejectWithValue }) => {
    try {
      return await todoApi.complete(id);
    } catch (error) {
      return rejectWithValue(errorMessage(error, 'Failed to complete todo'));
    }
  },
);

export const deleteTodo = createAsyncThunk(
  'todos/deleteTodo',
  async (id, { rejectWithValue }) => {
    try {
      await todoApi.delete(id);
      return id;
    } catch (error) {
      return rejectWithValue(errorMessage(error, 'Failed to delete todo'));
    }
  },
);

const initialState = {
  items: [],
  fetchStatus: 'idle',
  createStatus: 'idle',
  completingIds: {},
  deletingIds: {},
  fetchError: null,
  mutationError: null,
};

const todosSlice = createSlice({
  name: 'todos',
  initialState,
  reducers: {
    clearTodosError(state) {
      state.fetchError = null;
      state.mutationError = null;
    },
    resetTodos() {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch
      .addCase(fetchTodos.pending, (state) => {
        state.fetchStatus = 'loading';
        state.fetchError = null;
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        state.fetchStatus = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchTodos.rejected, (state, action) => {
        state.fetchStatus = 'failed';
        state.fetchError = action.payload || action.error.message;
      })

      // Create
      .addCase(createTodo.pending, (state) => {
        state.createStatus = 'loading';
        state.mutationError = null;
      })
      .addCase(createTodo.fulfilled, (state, action) => {
        state.createStatus = 'succeeded';
        state.items.push(action.payload);
      })
      .addCase(createTodo.rejected, (state, action) => {
        state.createStatus = 'failed';
        state.mutationError = action.payload || action.error.message;
      })

      // Complete
      .addCase(completeTodo.pending, (state, action) => {
        state.completingIds[action.meta.arg] = true;
        state.mutationError = null;
      })
      .addCase(completeTodo.fulfilled, (state, action) => {
        delete state.completingIds[action.meta.arg];
        const index = state.items.findIndex((todo) => todo.id === action.payload.id);
        if (index !== -1) state.items[index] = action.payload;
      })
      .addCase(completeTodo.rejected, (state, action) => {
        delete state.completingIds[action.meta.arg];
        state.mutationError = action.payload || action.error.message;
      })

      // Delete
      .addCase(deleteTodo.pending, (state, action) => {
        state.deletingIds[action.meta.arg] = true;
        state.mutationError = null;
      })
      .addCase(deleteTodo.fulfilled, (state, action) => {
        delete state.deletingIds[action.payload];
        state.items = state.items.filter((todo) => todo.id !== action.payload);
      })
      .addCase(deleteTodo.rejected, (state, action) => {
        delete state.deletingIds[action.meta.arg];
        state.mutationError = action.payload || action.error.message;
      })

      // Auth ends: private data must disappear immediately
      .addCase(loggedOut, () => initialState)
      .addCase(sessionExpired, () => initialState);
  },
});

export const { clearTodosError, resetTodos } = todosSlice.actions;
export default todosSlice.reducer;
```

Notes:

- `state.items.push(...)` Redux Toolkit/Immer ke andar safe hai.
- `action.meta.arg` woh original ID hai jo thunk ko diya tha.
- `completingIds`/`deletingIds` object use karne se multiple rows ka status separately track hota hai.
- Logout/session expiry par private todo data clear hota hai.
- `condition` React Strict Mode/dependent re-render ke waqt duplicate in-flight fetch ko rokta hai.

Store mein add:

```js
import todosReducer from '../features/todos/todosSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    todos: todosReducer,
    taskView: taskViewReducer,
  },
});
```

---

## 13. Derived data ke selectors

Create `src/features/todos/todosSelectors.js`:

```js
import { createSelector } from '@reduxjs/toolkit';
import {
  selectTaskFilter,
  selectTaskQuery,
  selectTaskSort,
} from '../taskView/taskViewSlice';

export const selectAllTodos = (state) => state.todos.items;
export const selectTodosFetchStatus = (state) => state.todos.fetchStatus;
export const selectTodosError = (state) => state.todos.fetchError;
export const selectCreateStatus = (state) => state.todos.createStatus;
export const selectCompletingIds = (state) => state.todos.completingIds;
export const selectDeletingIds = (state) => state.todos.deletingIds;

export const selectTodoStats = createSelector([selectAllTodos], (todos) => {
  const completed = todos.filter((todo) => todo.is_completed).length;
  return {
    total: todos.length,
    completed,
    pending: todos.length - completed,
  };
});

export const selectVisibleTodos = createSelector(
  [selectAllTodos, selectTaskFilter, selectTaskQuery, selectTaskSort],
  (todos, filter, query, sort) => {
    const priorityWeight = { HIGH: 3, MEDIUM: 2, LOW: 1 };
    const normalizedQuery = query.trim().toLowerCase();

    return todos
      .filter((todo) => {
        if (filter === 'active' && todo.is_completed) return false;
        if (filter === 'completed' && !todo.is_completed) return false;
        return !normalizedQuery || todo.title.toLowerCase().includes(normalizedQuery);
      })
      .sort((a, b) => {
        if (sort === 'newest') {
          return new Date(b.created_at) - new Date(a.created_at);
        }
        if (sort === 'oldest') {
          return new Date(a.created_at) - new Date(b.created_at);
        }
        if (a.is_completed !== b.is_completed) {
          return Number(a.is_completed) - Number(b.is_completed);
        }
        const priorityDifference =
          (priorityWeight[String(b.priority).toUpperCase()] || 0) -
          (priorityWeight[String(a.priority).toUpperCase()] || 0);
        return priorityDifference || new Date(b.created_at) - new Date(a.created_at);
      });
  },
);
```

Selector benefits:

- component lean hota hai;
- calculation reusable/testable hoti hai;
- `createSelector` input references same hon to cached result return karta hai;
- every render par unnecessary new derived array se bach sakte ho.

Warning: Redux state array ko direct `.sort()` mat karo outside reducer. Is code mein `.filter()` pehle new array banata hai, phir us new array ko sort karta hai. Agar filter step na hota to `[...todos].sort(...)` use karna zaroori hota.

---

## 14. `TodoDashboard` migration pattern

`useTodos()` remove karke:

```js
import { useDispatch, useSelector } from 'react-redux';
import {
  fetchTodos,
  createTodo,
  completeTodo,
  deleteTodo,
} from '../features/todos/todosSlice';
import {
  selectAllTodos,
  selectCreateStatus,
  selectCompletingIds,
  selectDeletingIds,
  selectTodoStats,
  selectTodosError,
  selectTodosFetchStatus,
  selectVisibleTodos,
} from '../features/todos/todosSelectors';

const dispatch = useDispatch();
const todos = useSelector(selectAllTodos);
const visibleTodos = useSelector(selectVisibleTodos);
const stats = useSelector(selectTodoStats);
const fetchStatus = useSelector(selectTodosFetchStatus);
const createStatus = useSelector(selectCreateStatus);
const completingIds = useSelector(selectCompletingIds);
const deletingIds = useSelector(selectDeletingIds);
const error = useSelector(selectTodosError);

const loading = fetchStatus === 'loading';
const creating = createStatus === 'loading';
```

Initial fetch:

```js
useEffect(() => {
  if (fetchStatus === 'idle') {
    dispatch(fetchTodos());
  }
}, [dispatch, fetchStatus]);
```

Refresh button:

```jsx
onClick={() => dispatch(fetchTodos())}
```

Create handler:

```js
const handleSubmit = async (event) => {
  event.preventDefault();
  const cleanTitle = text.trim();
  setSubmitError(null);

  if (cleanTitle.length < 3) {
    setSubmitError('Use at least 3 characters so the task is clear.');
    return;
  }
  if (cleanTitle.length > 120) {
    setSubmitError('Keep the task under 120 characters.');
    return;
  }

  try {
    await dispatch(createTodo({ title: cleanTitle, priority })).unwrap();
    setText('');
    toast.success('Task added to your plan.');
  } catch (error) {
    setSubmitError(error);
  }
};
```

Complete handler:

```js
const handleComplete = async (id) => {
  try {
    await dispatch(completeTodo(id)).unwrap();
    toast.success('Nice work — task completed.');
  } catch (error) {
    toast.error(error);
  }
};
```

Delete handler:

```js
const handleRemove = async () => {
  if (!deleteTarget) return;

  try {
    await dispatch(deleteTodo(deleteTarget.id)).unwrap();
    setDeleteTarget(null);
    toast.success('Task removed.');
  } catch (error) {
    toast.error(error);
  }
};
```

Row statuses:

```jsx
<TodoItem
  todo={todo}
  onComplete={handleComplete}
  onDelete={() => setDeleteTarget(todo)}
  isCompleting={Boolean(completingIds[todo.id])}
  isDeleting={Boolean(deletingIds[todo.id])}
/>
```

Local state jo Dashboard mein ab bhi rehni chahiye:

```js
const [text, setText] = useState('');
const [priority, setPriority] = useState('medium');
const [submitError, setSubmitError] = useState(null);
const [deleteTarget, setDeleteTarget] = useState(null);
```

Old local states jo remove ho jayengi:

```js
creating
completingId
deletingId
filter
query
sort
```

---

## 15. Ek async thunk ka full flow — line by line mental model

User “Complete” click karta hai:

```js
dispatch(completeTodo(todo.id));
```

Redux Toolkit automatically:

1. `todos/completeTodo/pending` dispatch karta hai.
2. Reducer `completingIds[id] = true` karta hai.
3. Selector new value read karta hai.
4. `TodoItem` spinner/disabled state show karta hai.
5. Thunk `todoApi.complete(id)` call karta hai.
6. Success par `todos/completeTodo/fulfilled` dispatch hota hai.
7. Reducer updated todo ko list mein replace karta hai aur loading ID remove karta hai.
8. React-Redux relevant subscribed components ko re-render karta hai.

Failure par:

1. `todos/completeTodo/rejected` dispatch hota hai.
2. Reducer loading ID remove aur error store karta hai.
3. `.unwrap()` error throw karta hai.
4. Component `catch` mein toast show karta hai.

Reducer API call nahi karta. Component todo array manually update nahi karta. Har layer ka ek clear role hai.

---

## 16. Current-to-Redux one-to-one mapping

| Current code | Redux Toolkit version |
|---|---|
| `useAuth().user` | `useSelector(selectCurrentUser)` |
| `useAuth().loading` | `selectAuthStatus === 'loading'` |
| `useAuth().login()` | `dispatch(loginUser(payload)).unwrap()` |
| `useAuth().signup()` | `dispatch(signupUser(payload)).unwrap()` |
| `useAuth().logout()` | `dispatch(logoutUser())` |
| `App.isLoggedIn` | `useSelector(selectIsAuthenticated)` |
| `auth-failure` browser event | `dispatch(expireSession())` |
| `useTodos().todos` | `useSelector(selectAllTodos)` |
| `useTodos().loading` | `selectTodosFetchStatus` |
| `useTodos().fetchTodos()` | `dispatch(fetchTodos())` |
| `useTodos().addTodo()` | `dispatch(createTodo(payload)).unwrap()` |
| `useTodos().completeTodo()` | `dispatch(completeTodo(id)).unwrap()` |
| `useTodos().removeTodo()` | `dispatch(deleteTodo(id)).unwrap()` |
| Dashboard `useMemo(stats)` | `selectTodoStats` |
| Dashboard `useMemo(visibleTodos)` | `selectVisibleTodos` |
| Dashboard filter/search/sort states | `taskViewSlice` |
| `setTodos(prev => ...)` | thunk fulfilled case reducers |

After successful migration:

- `src/hooks/useAuth.js` delete ho sakta hai;
- `src/hooks/useTodos.js` delete ho sakta hai;
- `App` ka auth `useEffect` delete ho sakta hai;
- old `auth-failure` browser event delete ho sakta hai;
- duplicate local loading flags delete ho sakte hain.

Un files ko tab tak delete mat karna jab tak their Redux replacement verified na ho.

---

## 17. Optional `notificationsSlice`

Sirf auth/todos samajhne ke baad:

```js
import { createSlice, nanoid } from '@reduxjs/toolkit';

const notificationsSlice = createSlice({
  name: 'notifications',
  initialState: { items: [] },
  reducers: {
    notificationAdded: {
      reducer(state, action) {
        state.items.push(action.payload);
      },
      prepare(type, message) {
        return { payload: { id: nanoid(), type, message } };
      },
    },
    notificationRemoved(state, action) {
      state.items = state.items.filter((item) => item.id !== action.payload);
    },
  },
});

export const { notificationAdded, notificationRemoved } =
  notificationsSlice.actions;

export const showNotification = (type, message) => (dispatch) => {
  const action = notificationAdded(type, message);
  dispatch(action);
  setTimeout(() => dispatch(notificationRemoved(action.payload.id)), 3500);
};

export default notificationsSlice.reducer;
```

Reducer mein timer nahi. Timer thunk mein hai, kyun ke timer side effect hai.

Phir:

```js
dispatch(showNotification('success', 'Task added to your plan.'));
```

Existing toast system already clean enough hai, is liye yeh learning/centralization choice hai, mandatory improvement nahi.

---

## 18. Redux DevTools se learning ka best tareeqa

Browser mein Redux DevTools extension install karo. Har interaction par yeh dekho:

1. Action ka exact naam kya hai?
2. `payload` kya gaya?
3. Action se pehle state kya thi?
4. Action ke baad state mein exactly kya change hua?
5. API request mein `pending → fulfilled` hua ya `pending → rejected`?

Login example:

```text
auth/loginUser/pending
auth/loginUser/fulfilled
```

Failed login:

```text
auth/loginUser/pending
auth/loginUser/rejected
```

Complete todo:

```text
todos/completeTodo/pending
todos/completeTodo/fulfilled
```

DevTools mein “Diff” tab reducer samajhne ka bohat acha tool hai.

---

## 19. Common beginner mistakes

### Mistake 1: reducer ke andar API call

Wrong:

```js
reducers: {
  async loadTodos(state) {
    state.items = await todoApi.getAll();
  }
}
```

API `createAsyncThunk` mein honi chahiye.

### Mistake 2: action ko call kiya, dispatch nahi

Wrong:

```js
filterChanged('completed');
```

Correct:

```js
dispatch(filterChanged('completed'));
```

Action creator object banata hai; dispatch us object ko store tak pohanchata hai.

### Mistake 3: state ke do sources

Wrong:

```js
const [todos, setTodos] = useState([]);
const reduxTodos = useSelector(selectAllTodos);
```

Ek feature migrate hone ke baad ek authoritative source rakho.

### Mistake 4: `useSelector` se har render new object

Risky:

```js
const data = useSelector((state) => ({
  todos: state.todos.items,
  status: state.todos.fetchStatus,
}));
```

Is se reference har baar new ho sakta hai. Separate selectors/calls ya memoized selector use karo.

### Mistake 5: selector mein original array sort

Wrong:

```js
state.todos.items.sort(...);
```

Correct:

```js
[...state.todos.items].sort(...);
```

### Mistake 6: non-serializable state

`Set`, `Map`, DOM refs, functions aur Axios errors store mein mat rakho. Isi liye IDs plain object mein track ki hain.

### Mistake 7: one boolean for every mutation

Sirf `loading: true` use karoge to ek todo complete karte waqt poora UI loading lag sakta hai. Separate `fetchStatus`, `createStatus`, `completingIds`, `deletingIds` better control dete hain.

### Mistake 8: rejected error ko na samajhna

`rejectWithValue('message')` ka result `action.payload` mein aata hai. Unexpected thrown error aam tor par `action.error.message` mein hota hai.

### Mistake 9: `Provider` bhool jana

Store banane se alone React connected nahi hota. Root ko `<Provider store={store}>` se wrap karna zaroori hai.

### Mistake 10: Redux aur React hooks ko opponents samajhna

Redux ke baad bhi `useState`, `useEffect`, `useMemo`, `useRef` use honge. Redux shared state solve karta hai; React hooks component behavior solve karte hain.

---

## 20. Verification checklist after each phase

### Store/task view

- App render hoti hai, Provider error nahi.
- Filter buttons work karte hain.
- Search aur sort work karte hain.
- DevTools mein taskView actions/state nazar aati hai.

### Auth

- Fresh browser mein AuthForm show hota hai.
- Login success par dashboard show hota hai.
- Wrong password par readable error show hota hai.
- Reload ke baad session restore hoti hai.
- Logout par user aur private todos clear hote hain.
- Expired token/401 par AuthForm show hota hai.

### Todos

- Dashboard mount par GET `/todos` sirf intended request karta hai.
- Refresh works.
- Add result list mein aata hai.
- Complete correct row ko update karta hai.
- Delete correct row remove karta hai.
- Request failure par row/button permanently loading mein stuck nahi hota.
- Filter/search/sort create/complete/delete ke baad correct rehte hain.

### Commands

```bash
npm run lint
npm run build
```

---

## 21. Recommended learning sequence

```text
1. Plain action + reducer concept
2. createSlice
3. configureStore + Provider
4. useSelector + useDispatch
5. taskViewSlice (no API)
6. createAsyncThunk lifecycle
7. authSlice
8. todosSlice
9. memoized selectors
10. interceptor → store bridge
11. optional notificationsSlice
12. RTK Query
```

`createAsyncThunk` pehle seekhna is project ke current manual Axios flow ko clearly expose karta hai. Jab pending/fulfilled/rejected aur cache problems samajh aa jayein, tab RTK Query seekho.

---

## 22. RTK Query alternative — baad mein

Todos asal mein server state hain. Redux Toolkit ke andar RTK Query data fetching/caching tool included hai. Woh:

- generated React hooks;
- loading/error state;
- caching;
- duplicate request avoidance;
- mutation ke baad cache invalidation/refetch

provide kar sakta hai.

Lekin learning ke liye do approaches ek sath mat lagao:

- Phase A: pehle `createAsyncThunk + todosSlice` implement karo aur lifecycle samjho.
- Phase B: separate exercise mein todos ko RTK Query par migrate karo.

Auth/session UI state normal slice mein reh sakti hai; todos API RTK Query mein ja sakti hai. Production app ke liye yeh often less hand-written code deta hai.

---

## 23. Final recommended architecture

```text
React components
  │
  ├── local UI state
  │   ├── form inputs
  │   ├── modal target
  │   └── DOM refs/focus
  │
  └── React-Redux
      ├── useSelector ← selectors ← Redux store
      └── useDispatch → actions/thunks
                           │
                           ├── reducers update state
                           └── API modules → Axios → backend
                                                │
                                                └── 401 callback → dispatch session expiry
```

### Minimal recommended store

```js
{
  auth: { ... },
  todos: { ... },
  taskView: { ... }
}
```

### Full learning store

```js
{
  auth: { ... },
  todos: { ... },
  taskView: { ... },
  notifications: { ... }
}
```

Bottom line:

- Current app “wrong” nahi; it uses React local state and custom hooks effectively.
- Current global communication (`window` events) Redux ke baad explicit actions ban sakti hai.
- Auth aur todos Redux migration ke strongest candidates hain.
- Filter/search/sort Redux practice ke liye acha simple first slice hai.
- Har local input ko Redux mein daalna over-engineering hoga.
- Migration incremental honi chahiye; har phase DevTools aur UI se verify karo.

---

## 24. Official learning resources

Yeh guide current project ke context mein likhi gayi hai. Concepts verify/deepen karne ke liye official docs:

- [Redux Toolkit Quick Start](https://redux.js.org/tutorials/quick-start)
- [`configureStore` API](https://redux.js.org/toolkit/api/configureStore)
- [`createSlice` API](https://redux.js.org/toolkit/api/createSlice)
- [`createAsyncThunk` API](https://redux.js.org/toolkit/api/createAsyncThunk)
- [React-Redux hooks: `useSelector` and `useDispatch`](https://redux.js.org/react-redux/api/hooks)
- [React-Redux `<Provider>`](https://redux.js.org/react-redux/api/provider)
- [Redux Style Guide](https://redux.js.org/style-guide/)
- [How to decide what belongs in Redux](https://redux.js.org/faq/organizing-state)
- [RTK Query overview](https://redux.js.org/toolkit/rtk-query/overview)

---

## 25. Aap ka practical next lesson

Sab se pehle sirf yeh four changes karo:

1. packages install;
2. `taskViewSlice.js` create;
3. `store.js` create aur `main.jsx` mein Provider;
4. Dashboard filter/search/sort ko `useSelector` + `useDispatch` par shift.

Uske baad browser Redux DevTools mein ek filter click trace karo:

```text
click
→ dispatch(filterChanged('completed'))
→ action { type, payload }
→ reducer state.filter update
→ selector new value read
→ component re-render
→ completed todos visible
```

Jab yeh chain bilkul clear ho jaye, tab `authSlice` start karo. Isi incremental order mein Redux “copy/paste magic” ke bajaye understandable data flow banega.
