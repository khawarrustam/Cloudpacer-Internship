# TodoFlow React Learning Guide

> A beginner-friendly guide in **English and Roman Urdu**, based on the actual React code in this project.

This README is for you if you are starting React from zero. Instead of learning hooks through unrelated examples, we will learn them through this TodoFlow application.

---

## Table of contents

1. [What is React?](#1-what-is-react)
2. [The most important React mental model](#2-the-most-important-react-mental-model)
3. [Project component map](#3-project-component-map)
4. [All hooks used in this project](#4-all-hooks-used-in-this-project)
5. [`useState`](#5-usestate)
6. [`useEffect`](#6-useeffect)
7. [`useMemo`](#7-usememo)
8. [`useRef`](#8-useref)
9. [Custom hook: `useAuth`](#9-custom-hook-useauth)
10. [Custom hook: `useTodos`](#10-custom-hook-usetodos)
11. [`forwardRef`—related to hooks, but not a hook](#11-forwardrefrelated-to-hooks-but-not-a-hook)
12. [How data moves through TodoFlow](#12-how-data-moves-through-todoflow)
13. [React patterns used in the project](#13-react-patterns-used-in-the-project)
14. [Rules of Hooks](#14-rules-of-hooks)
15. [Common beginner questions](#15-common-beginner-questions)
16. [Practice exercises](#16-practice-exercises)
17. [How to run the frontend](#17-how-to-run-the-frontend)

---

## 1. What is React?

React is a JavaScript library for building user interfaces from small reusable pieces called **components**.

**Roman Urdu:** React JavaScript ki library hai jo user interface banane ke liye use hoti hai. React mein hum screen ko chhotay reusable parts mein divide karte hain jinhein **components** kehte hain.

For example, TodoFlow contains these components:

- `App` decides whether to show authentication or the dashboard.
- `AuthForm` displays login and signup forms.
- `TodoDashboard` displays task controls and the task list.
- `TodoItem` displays one task.
- `Button`, `Input`, `Card`, and `Badge` are reusable UI components.

A component is normally a JavaScript function that returns JSX:

```jsx
function Welcome() {
  return <h1>Welcome to TodoFlow</h1>;
}
```

JSX looks like HTML, but it is written inside JavaScript. React converts it into browser elements.

**Roman Urdu:** JSX dekhne mein HTML jaisa hota hai, lekin JavaScript file ke andar likha jata hai. React is JSX ko browser ke elements mein convert karta hai.

---

## 2. The most important React mental model

Think of a React component as:

```text
UI = function(props, state)
```

- **Props** are information received from a parent component.
- **State** is information remembered by the component.
- When props or state change, React runs the component again and updates the screen.

**Roman Urdu:**

- **Props** woh data hai jo parent component child component ko deta hai.
- **State** component ki apni memory hai.
- Jab props ya state change hoti hai, React component ko dobara run karta hai aur screen update kar deta hai.

Example from TodoFlow:

```jsx
const [filter, setFilter] = useState('all');
```

Here:

- `filter` is the current state value.
- `setFilter` changes that value.
- `'all'` is the initial value.
- Calling `setFilter('completed')` causes a re-render.

Do not imagine a re-render as a full browser refresh. React compares the old and new UI and changes only what is needed.

**Roman Urdu:** Re-render ka matlab poora browser refresh nahi hota. React purani aur nayi UI compare karke sirf zaroori hissa update karta hai.

---

## 3. Project component map

```text
main.jsx
└── React.StrictMode
    └── ToastProvider
        └── App
            ├── AuthForm                 when logged out
            └── TodoDashboard            when logged in
                ├── Navbar
                ├── Card
                │   └── new-task form
                ├── TodoItem             one for every task
                └── ConfirmModal
```

Important supporting files:

```text
src/hooks/useAuth.js       authentication state and actions
src/hooks/useTodos.js      todo state and API actions
src/api/client.js          shared Axios client and auth token
src/api/authApi.js         login and signup requests
src/api/todoApi.js         todo HTTP requests
```

### Where the application starts

[`src/main.jsx`](./src/main.jsx) finds the HTML element with `id="root"` and renders the React application inside it.

```jsx
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ToastProvider>
      <App />
    </ToastProvider>
  </React.StrictMode>,
);
```

`React.StrictMode` is a development helper. It warns about unsafe React patterns. In development, it may run some logic twice to reveal missing cleanup.

**Roman Urdu:** `StrictMode` development mein ghaltiyan dhoondhne mein madad karta hai. Kabhi development mode mein effect do dafa chalta nazar aa sakta hai. Production mein yeh double behavior nahi hota.

---

## 4. All hooks used in this project

| Hook | Type | Main purpose | Used in |
|---|---|---|---|
| `useState` | Built-in | Remember data and update the UI | `App`, `AuthForm`, `TodoDashboard`, `ToastProvider`, custom hooks |
| `useEffect` | Built-in | Synchronize with systems outside React | auth events, API loading, keyboard events, modal focus, toast events |
| `useMemo` | Built-in | Reuse a calculated value until dependencies change | dashboard statistics, filtered and sorted todos |
| `useRef` | Built-in | Remember a mutable reference without re-rendering | modal cancel button reference |
| `useAuth` | Custom | Authentication state and actions | `App` |
| `useTodos` | Custom | Todo state and CRUD actions | `TodoDashboard` |

The project does **not** currently use `useContext`, `useReducer`, `useCallback`, or third-party state management such as Redux.

**Roman Urdu:** Is project mein abhi `useContext`, `useReducer`, `useCallback`, ya Redux use nahi ho raha. Pehle existing hooks achhi tarah samajhna zyada zaroori hai.

---

## 5. `useState`

### What does it do?

`useState` gives a component memory. Normal local variables disappear between renders, but state values are remembered by React.

**Roman Urdu:** `useState` component ko memory deta hai. Normal variable har render par dobara ban jata hai, lekin state ki value React yaad rakhta hai.

### Basic syntax

```jsx
const [value, setValue] = useState(initialValue);
```

Example:

```jsx
const [showPassword, setShowPassword] = useState(false);
```

- `showPassword` contains `true` or `false`.
- `setShowPassword` changes it.
- It starts as `false`.

```jsx
setShowPassword(true);
```

After the setter is called, React schedules a re-render.

### Every `useState` in TodoFlow

#### `App.jsx`

```jsx
const [isLoggedIn, setIsLoggedIn] = useState(null);
```

This is a tri-state value:

- `null`: the browser session is still being checked.
- `true`: show the dashboard.
- `false`: show the authentication form.

**Why?** Without the `null` state, the login screen could flash briefly before React checks `localStorage`.

**Roman Urdu:** `null` is liye use hua hai taake session check hone tak galat screen flash na ho. Token mil jaye to `true`, warna `false` set hota hai.

#### `AuthForm.jsx`

```jsx
const [isLogin, setIsLogin] = useState(true);
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [name, setName] = useState('');
const [showPassword, setShowPassword] = useState(false);
const [error, setError] = useState(null);
```

These state values control:

- login versus signup mode;
- input field values;
- password visibility;
- authentication error messages.

**Roman Urdu:** Yeh states form ka mode, user ki typed values, password show/hide, aur error message control karti hain.

#### `TodoDashboard.jsx`

```jsx
const [text, setText] = useState('');
const [priority, setPriority] = useState('medium');
const [submitError, setSubmitError] = useState(null);
const [filter, setFilter] = useState('all');
const [query, setQuery] = useState('');
const [sort, setSort] = useState('smart');
const [creating, setCreating] = useState(false);
const [completingId, setCompletingId] = useState(null);
const [deleteTarget, setDeleteTarget] = useState(null);
const [deletingId, setDeletingId] = useState(null);
```

These values are separate because they represent separate UI concerns.

| State | What it remembers | Why it exists |
|---|---|---|
| `text` | New task title | Makes the title input controlled |
| `priority` | Selected priority | Sends the chosen value to the API |
| `submitError` | Form error | Shows validation next to the form |
| `filter` | All/open/done | Chooses which tasks are visible |
| `query` | Search text | Filters tasks by title |
| `sort` | Sort mode | Controls task order |
| `creating` | Creation request status | Prevents duplicate submissions and shows a spinner |
| `completingId` | Task currently completing | Shows loading on only that task |
| `deleteTarget` | Task selected for deletion | Opens the confirmation modal with the correct task |
| `deletingId` | Task currently deleting | Disables repeated deletion clicks |

**Roman Urdu:** Har state ka aik specific kaam hai. Misal ke taur par `creating` poori list ko loading nahi banata; sirf create button ki loading handle karta hai. `completingId` se sirf clicked task par spinner aata hai.

#### `Toast.jsx`

```jsx
const [toasts, setToasts] = useState([]);
```

This array contains all notifications currently visible on the screen.

**Roman Urdu:** `toasts` array mein tamam current notifications hoti hain. Naya toast array mein add hota hai aur timeout ke baad remove ho jata hai.

### Functional state updates

The project often uses this form:

```jsx
setTodos((previousTodos) => [...previousTodos, newTodo]);
```

Use a function when the next state depends on the previous state.

**Roman Urdu:** Jab nayi state purani state par depend karti ho, setter ke andar function use karein. Is se aapko hamesha latest state milti hai.

Other examples:

```jsx
setTodos((previousTodos) =>
  previousTodos.map((todo) => todo.id === id ? updatedTodo : todo)
);

setTodos((previousTodos) =>
  previousTodos.filter((todo) => todo.id !== id)
);
```

Notice that we create new arrays with `...`, `map`, and `filter`. We do not directly mutate React state.

Bad:

```jsx
todos.push(newTodo);
```

Good:

```jsx
setTodos((previous) => [...previous, newTodo]);
```

**Roman Urdu:** State ko direct change nahi karna. Naya array ya object bana kar setter ko dena hai. Isi ko immutable update kehte hain.

### Lazy initial state

[`useAuth.js`](./src/hooks/useAuth.js) uses a function as the initial value:

```jsx
const [user, setUser] = useState(() => {
  const uid = localStorage.getItem('user_uid');
  const email = localStorage.getItem('user_email');
  return uid ? { uid, email: email || '' } : null;
});
```

React calls this initializer only during the first render.

**Why?** Reading `localStorage` on every render would be unnecessary.

**Roman Urdu:** Function initializer sirf pehli render par run hota hai. Is wajah se har render par `localStorage` read nahi hota.

---

## 6. `useEffect`

### What does it do?

`useEffect` synchronizes React with something outside React.

Examples of outside systems:

- an HTTP API;
- browser events;
- timers;
- `localStorage`;
- manual focus;
- subscriptions.

**Roman Urdu:** `useEffect` React ko bahar ki duniya ke saath synchronize karta hai, jaise API, browser event, timer, localStorage, ya kisi element par focus.

### Basic syntax

```jsx
useEffect(() => {
  // Start or synchronize something.

  return () => {
    // Optional cleanup.
  };
}, [dependencies]);
```

### Dependency array meanings

```jsx
useEffect(() => {
  // Runs after every render.
});
```

```jsx
useEffect(() => {
  // Runs after the component first appears.
}, []);
```

```jsx
useEffect(() => {
  // Runs when userId changes.
}, [userId]);
```

**Roman Urdu:** Dependency array React ko batati hai ke effect dobara kab chalana hai. Khali array `[]` ka matlab mount ke baad effect run karna hai.

### Every `useEffect` in TodoFlow

#### Session and authentication event — `App.jsx`

```jsx
useEffect(() => {
  const token = localStorage.getItem('auth_token');
  setIsLoggedIn(Boolean(token));

  const handleAuthFailure = () => setIsLoggedIn(false);
  window.addEventListener('auth-failure', handleAuthFailure);

  return () => {
    window.removeEventListener('auth-failure', handleAuthFailure);
  };
}, []);
```

What happens:

1. The saved token is checked.
2. A global `auth-failure` listener is registered.
3. The listener is removed when `App` unmounts.

**Why cleanup?** Without cleanup, old listeners could remain in memory and execute multiple times.

**Roman Urdu:** Effect token check karta hai aur `auth-failure` event sunta hai. Cleanup purana event listener hata deta hai taake memory leak ya duplicate calls na hon.

#### Initial API request — `useTodos.js`

```jsx
useEffect(() => {
  fetchTodos();
}, []);
```

The dashboard needs todos when it first appears, so the custom hook requests them from the backend.

**Roman Urdu:** Dashboard open hote hi todos backend se chahiye hotay hain. Is liye mount par `fetchTodos()` call hota hai.

In React Strict Mode, you may notice two development requests. Strict Mode intentionally tests effects. A production build does not perform this development-only check.

#### Keyboard shortcuts — `TodoDashboard.jsx`

```jsx
useEffect(() => {
  const handleShortcut = (event) => {
    // `/` focuses search and `N` focuses the new-task input.
  };

  window.addEventListener('keydown', handleShortcut);
  return () => window.removeEventListener('keydown', handleShortcut);
}, []);
```

**Why an effect?** A browser event listener is outside React and must be registered and cleaned up.

**Roman Urdu:** Keyboard listener browser ka global event hai. Effect usko register karta hai aur cleanup unmount par hata deta hai.

#### Modal focus and Escape key — `ConfirmModal.jsx`

```jsx
useEffect(() => {
  if (!open) return undefined;

  cancelRef.current?.focus();

  const handleKeyDown = (event) => {
    if (event.key === 'Escape' && !isLoading) onCancel();
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [open, isLoading, onCancel]);
```

This effect reacts when the dialog opens, its loading state changes, or its cancel function changes.

**Roman Urdu:** Modal open ho to cancel button focus hota hai. Escape press karne se modal close hota hai. Dependencies change hon to effect latest values ke saath dobara setup hota hai.

#### Toast event subscription — `Toast.jsx`

```jsx
useEffect(() => {
  const handleToastEvent = (event) => {
    // Add a new toast and schedule its removal.
  };

  window.addEventListener('app-toast', handleToastEvent);
  return () => window.removeEventListener('app-toast', handleToastEvent);
}, []);
```

Any module can dispatch an `app-toast` event. The provider listens and updates its state.

**Roman Urdu:** App ke kisi bhi hissa se toast event bheja ja sakta hai. `ToastProvider` us event ko sun kar notification show karta hai.

### Do not use an effect for everything

You do not need an effect for values that can be calculated while rendering.

Bad idea:

```jsx
const [completedCount, setCompletedCount] = useState(0);

useEffect(() => {
  setCompletedCount(todos.filter((todo) => todo.is_completed).length);
}, [todos]);
```

Better:

```jsx
const completedCount = todos.filter((todo) => todo.is_completed).length;
```

Or use `useMemo` if the calculation is expensive.

**Roman Urdu:** Jo value existing state se calculate ho sakti ho uske liye extra state aur effect mat banayein. Seedha calculate karein.

---

## 7. `useMemo`

### What does it do?

`useMemo` remembers the result of a calculation until its dependencies change.

```jsx
const result = useMemo(() => calculateSomething(input), [input]);
```

**Roman Urdu:** `useMemo` calculation ka result cache karta hai. Jab dependency change hoti hai tab calculation dobara chalti hai.

### Dashboard statistics

```jsx
const stats = useMemo(() => {
  const completed = todos.filter((todo) => todo.is_completed).length;
  return {
    total: todos.length,
    completed,
    pending: todos.length - completed,
  };
}, [todos]);
```

The statistics only need recalculation when `todos` changes.

**Roman Urdu:** Total, completed, aur pending counts sirf todos change hone par dobara calculate hotay hain.

### Filtered and sorted todos

```jsx
const visibleTodos = useMemo(() => {
  return todos
    .filter(/* status and search rules */)
    .sort(/* selected order */);
}, [todos, filter, query, sort]);
```

The list is recalculated when any relevant input changes:

- the todos;
- selected status filter;
- search query;
- sorting mode.

If unrelated state such as `deleteTarget` changes, React can reuse the previous list calculation.

**Roman Urdu:** Agar sirf delete modal open ho aur todos/filter/query/sort same hon, to `useMemo` purana calculated list result reuse kar sakta hai.

### Important warning

`useMemo` is a performance optimization, not a correctness tool. Your code should still be logically correct without it.

Do not wrap every calculation in `useMemo`. Simple calculations are usually cheaper than memoization.

**Roman Urdu:** Har chhoti calculation par `useMemo` lagana zaroori nahi. Yeh optimization hai, business logic ka replacement nahi.

---

## 8. `useRef`

### What does it do?

`useRef` creates an object that survives re-renders:

```jsx
const myRef = useRef(initialValue);
```

The object looks like:

```js
{ current: initialValue }
```

Changing `ref.current` does not cause a re-render.

**Roman Urdu:** `useRef` aik aisa box deta hai jo renders ke darmiyan same rehta hai. `ref.current` change karne se UI re-render nahi hoti.

### Modal cancel button

[`ConfirmModal.jsx`](./src/components/ui/ConfirmModal.jsx) contains:

```jsx
const cancelRef = useRef(null);
```

The ref is passed to the reusable `Button`:

```jsx
<Button ref={cancelRef}>Keep task</Button>
```

When the modal opens:

```jsx
cancelRef.current?.focus();
```

Now keyboard users immediately have focus inside the dialog.

**Roman Urdu:** Ref cancel button ke real DOM element ko point karta hai. Modal open hote hi `.focus()` call hota hai, jo accessibility improve karta hai.

### State versus ref

Use state when a change must update the screen.

```jsx
const [open, setOpen] = useState(false);
```

Use a ref when you need a DOM element or a mutable value that should not re-render the screen.

```jsx
const buttonRef = useRef(null);
```

**Roman Urdu:** UI change karni ho to state use karein. DOM element pakarna ho ya aisi value rakhni ho jis se UI update na ho, to ref use karein.

---

## 9. Custom hook: `useAuth`

### What is a custom hook?

A custom hook is a normal JavaScript function that:

- starts with the word `use`;
- can call other hooks;
- packages reusable stateful logic.

**Roman Urdu:** Custom hook normal JavaScript function hota hai jiska naam `use` se start hota hai. Yeh built-in hooks ko combine karke reusable logic banata hai.

`useAuth` is defined in [`src/hooks/useAuth.js`](./src/hooks/useAuth.js).

It manages:

- the current user;
- login/signup loading;
- authentication errors;
- login;
- signup;
- logout;
- browser token storage.

It returns:

```jsx
return {
  user,
  loading,
  error,
  signup,
  login,
  logout,
};
```

`App` consumes it like this:

```jsx
const {
  user,
  loading: authLoading,
  signup,
  login,
  logout,
} = useAuth();
```

### Why rename `loading`?

```jsx
loading: authLoading
```

This is JavaScript object destructuring with a new local name. It makes clear that this loading value belongs to authentication.

**Roman Urdu:** Object se `loading` nikal kar local naam `authLoading` rakha gaya hai, taake baad mein confusion na ho ke kis cheez ki loading hai.

### Why create this custom hook?

Without `useAuth`, `App` or `AuthForm` would contain API calls, token storage, loading logic, error handling, and user state all together.

With `useAuth`:

- components focus on UI;
- authentication logic stays in one place;
- future screens can reuse it;
- testing and maintenance become easier.

**Roman Urdu:** `useAuth` auth ka tamam logic aik jagah rakhta hai. UI component sirf display aur user interaction handle karta hai. Code clean aur reusable rehta hai.

---

## 10. Custom hook: `useTodos`

`useTodos` is defined in [`src/hooks/useTodos.js`](./src/hooks/useTodos.js).

It owns todo-related state:

```jsx
const [todos, setTodos] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

It exposes todo operations:

```jsx
return {
  todos,
  loading,
  error,
  addTodo,
  completeTodo,
  removeTodo,
  refresh: fetchTodos,
};
```

The dashboard uses it like this:

```jsx
const {
  todos,
  loading,
  error,
  addTodo,
  completeTodo,
  removeTodo,
  refresh,
} = useTodos();
```

### API state flow

```text
TodoDashboard
    │ calls addTodo / completeTodo / removeTodo
    ▼
useTodos
    │ calls todoApi
    ▼
Axios client
    │ sends HTTP request with auth token
    ▼
FastAPI backend
```

When the backend responds, `useTodos` updates state and React redraws the list.

**Roman Urdu:** Dashboard custom hook ka function call karta hai. Hook API ko request bhejta hai. Response milne par hook state update karta hai aur React task list dobara render kar deta hai.

### Why not call the API directly inside `TodoDashboard`?

Keeping server logic in `useTodos` separates responsibilities:

- `TodoDashboard`: presentation and interaction;
- `useTodos`: todo state and workflows;
- `todoApi`: HTTP endpoint details;
- `client.js`: shared Axios configuration.

**Roman Urdu:** Har file ki aik clear responsibility hai. Dashboard UI sambhalta hai, hook state/workflow, `todoApi` endpoints, aur `client.js` shared HTTP settings sambhalta hai.

---

## 11. `forwardRef`—related to hooks, but not a hook

[`Button.jsx`](./src/components/ui/Button.jsx) uses:

```jsx
const Button = React.forwardRef(function Button(props, ref) {
  return <button ref={ref} {...props} />;
});
```

`forwardRef` allows a parent component to send a ref through a custom component to a real DOM element.

Without `forwardRef`, this ref would stop at the custom `Button` component. With it, `ConfirmModal` can focus the actual HTML `<button>`.

**Roman Urdu:** `forwardRef` parent ka ref custom `Button` ke andar real HTML button tak pohanchata hai. Yeh khud hook nahi hai, lekin `useRef` ke saath commonly use hota hai.

---

## 12. How data moves through TodoFlow

### Login flow

```text
User submits AuthForm
        │
        ▼
App.handleLogin(email, password)
        │
        ▼
useAuth.login()
        │
        ▼
authApi.login()
        │
        ▼
Backend returns user + token
        │
        ▼
useAuth saves token and calls setUser()
        │
        ▼
App calls setIsLoggedIn(true)
        │
        ▼
TodoDashboard renders
```

**Roman Urdu:** Form se login data App ko milta hai, App custom hook ko call karta hai, hook API se token leta hai, token save karta hai, aur logged-in state true hone par dashboard render hota hai.

### Initial todo loading flow

```text
TodoDashboard renders
        │
        ▼
useTodos runs its effect
        │
        ▼
fetchTodos() calls GET /todos
        │
        ▼
setTodos(data)
        │
        ▼
React re-renders TodoDashboard
```

### Add task flow

```text
User submits new-task form
        │
        ▼
handleSubmit validates the title
        │
        ▼
addTodo(title, priority)
        │
        ▼
POST /todos
        │
        ▼
setTodos(previous => [...previous, newTodo])
        │
        ▼
New TodoItem appears
```

### Complete task flow

```text
User clicks task circle
        │
        ▼
handleComplete(todo.id)
        │
        ▼
PATCH /todos/{id}/complete
        │
        ▼
map() replaces only the updated todo
        │
        ▼
Task appears completed
```

### Delete task flow

```text
User clicks delete
        │
        ▼
setDeleteTarget(todo)
        │
        ▼
ConfirmModal opens
        │
        ▼
User confirms
        │
        ▼
DELETE /todos/{id}
        │
        ▼
filter() removes the todo from state
```

---

## 13. React patterns used in the project

### Props

Props send data or functions from parent to child:

```jsx
<TodoItem
  todo={todo}
  onComplete={handleComplete}
  onDelete={() => setDeleteTarget(todo)}
/>
```

The child receives them:

```jsx
function TodoItem({ todo, onComplete, onDelete }) {
  // ...
}
```

**Roman Urdu:** Props parent se child ko data aur functions dene ka tareeqa hain. Child props ko read karta hai; parent ki state ko direct change nahi karta.

### Controlled inputs

```jsx
<input
  value={email}
  onChange={(event) => setEmail(event.target.value)}
/>
```

The React state is the source of truth:

1. `value` comes from state.
2. The user types.
3. `onChange` runs.
4. State updates.
5. React renders the new value.

**Roman Urdu:** Controlled input mein input ki value state se aati hai. User type kare to `onChange` state update karta hai.

### Conditional rendering

```jsx
if (!isLoggedIn) {
  return <AuthForm />;
}

return <TodoDashboard />;
```

React can display different components based on state.

**Roman Urdu:** State ki value ke mutabiq different UI return ki ja sakti hai. Logged out user ko form, logged in user ko dashboard milta hai.

### Rendering lists and keys

```jsx
{visibleTodos.map((todo) => (
  <TodoItem key={todo.id} todo={todo} />
))}
```

The `key` helps React match each rendered component with its data. Use a stable unique ID, not the array index when items can be inserted, deleted, or reordered.

**Roman Urdu:** `key` React ko batati hai ke kaunsa UI item kis data item se related hai. Todo ID stable aur unique hai, is liye best key hai.

### Event handlers

Pass a function:

```jsx
<button onClick={handleRemove}>Delete</button>
```

Do not call it during rendering:

```jsx
// Wrong: runs immediately
<button onClick={handleRemove()}>Delete</button>
```

When arguments are needed, pass a wrapper function:

```jsx
<button onClick={() => handleComplete(todo.id)}>Complete</button>
```

**Roman Urdu:** `onClick` ko function dena hai, function ka result nahi. Argument dena ho to arrow function use karein.

### Async UI states

Network requests take time. TodoFlow tracks them:

```jsx
setCreating(true);
const result = await addTodo(title, priority);
setCreating(false);
```

This lets the UI:

- show a spinner;
- disable repeated clicks;
- display errors;
- give success feedback.

**Roman Urdu:** API request instant nahi hoti. Loading state se spinner aur disabled button dikhaya jata hai taake duplicate request na jaye.

---

## 14. Rules of Hooks

React hooks have important rules.

### Rule 1: Call hooks at the top level

Good:

```jsx
function Example() {
  const [count, setCount] = useState(0);
  // ...
}
```

Bad:

```jsx
function Example({ loggedIn }) {
  if (loggedIn) {
    const [count, setCount] = useState(0);
  }
}
```

Do not call hooks inside loops, conditions, nested functions, or event handlers.

**Roman Urdu:** Hooks component ke top level par call karein. `if`, loop, ya event handler ke andar hook call nahi karna.

### Rule 2: Call hooks only from React functions

Hooks can be called from:

- React components;
- custom hooks.

Do not call hooks from ordinary utility functions.

### Rule 3: Custom hook names start with `use`

Good:

```jsx
function useTodos() {}
```

The name tells React tooling that the function follows Hook rules.

### Why do these rules exist?

React identifies hooks by their call order. If hooks are called conditionally, their order can change between renders and React may connect state to the wrong hook.

**Roman Urdu:** React hooks ko unki call order se track karta hai. Conditional call se order badal sakta hai aur React galat state ko galat hook ke saath jor sakta hai.

---

## 15. Common beginner questions

### Why does `console.log` show the old state immediately after a setter?

```jsx
setFilter('completed');
console.log(filter); // may still show the previous value
```

State updates are scheduled for the next render. The current function still sees its current render's snapshot.

**Roman Urdu:** Setter foran current variable ko change nahi karta. React next render schedule karta hai. Current function ke paas purani render ki snapshot hoti hai.

### Why not use normal variables?

```jsx
let count = 0;
```

Changing a normal variable neither survives a re-render nor tells React to update the UI. State does both.

### Why is state split into many values?

Separate state is easier when values change independently. Related values can be grouped into an object, but then you must update that object immutably.

### Why does `useEffect` return a function?

That returned function is cleanup. It undoes the previous subscription, event listener, or timer.

### Is `useMemo` required?

No. It is an optimization. Start with correct, readable code; memoize calculations when it has a clear benefit.

### Is `localStorage` React state?

No. It is browser storage. Changing it does not automatically re-render React. This is why `useAuth` updates both `localStorage` and React state.

### Why are API functions outside components?

The separation makes components easier to read and keeps HTTP details reusable.

---

## 16. Practice exercises

Try these in order. Build and test the app after every exercise.

### Beginner

1. Change the default priority from `medium` to `low`.
2. Add a button that clears the search query.
3. Show the number of characters remaining instead of characters used.
4. Change the empty-state message for the completed filter.

### State practice

5. Add a `compactMode` boolean state.
6. Add a button that toggles it.
7. Pass it to `TodoItem` as a prop.
8. Use it to reduce task-row padding.

### Effect practice

9. Save the selected filter in `localStorage`.
10. Read it with a lazy `useState` initializer.
11. Use an effect to save it whenever the filter changes.

### Memo practice

12. Add a priority filter.
13. Include it in the `visibleTodos` calculation.
14. Add it to the `useMemo` dependency array.

### Custom hook practice

15. Create a `useKeyboardShortcut` custom hook.
16. Move the dashboard keyboard event effect into it.
17. Use it for `/` and `N` shortcuts.

### Important learning habit

After every change, explain these four things to yourself:

1. What state changed?
2. Which component re-rendered?
3. Which value came through props?
4. Did any effect run, and why?

**Roman Urdu:** Har change ke baad khud se poochhein: kaunsi state change hui, kaunsa component re-render hua, props kahan se aaye, aur effect kyun chala. Yeh habit React bohat jaldi samjha degi.

---

## 17. How to run the frontend

Open PowerShell in the `todo-frontend` directory:

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite, normally:

```text
http://127.0.0.1:5173
```

The frontend expects the FastAPI backend at:

```text
http://127.0.0.1:8000
```

You can override it with a `.env` file:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Build the production frontend:

```powershell
npm run build
```

---

## Recommended learning order

Do not try to memorize every hook at once.

1. Learn components and JSX.
2. Learn props.
3. Learn `useState` and controlled inputs.
4. Learn rendering lists with `map` and `key`.
5. Learn event handlers.
6. Learn `useEffect` and cleanup.
7. Learn custom hooks.
8. Learn `useRef`.
9. Learn `useMemo` last.

**Roman Urdu:** Sab kuch aik saath yaad karne ki zaroorat nahi. Pehle components, props, state, forms aur events samjhein. Uske baad effects aur custom hooks. `useMemo` akhir mein seekhna bilkul theek hai.

The best way to learn React is to make a small change, predict what will happen, run the app, and compare the result with your prediction.

**Roman Urdu:** React seekhne ka best tareeqa yeh hai: chhota change karein, pehle predict karein kya hoga, app run karein, phir result ko apni prediction se compare karein.
