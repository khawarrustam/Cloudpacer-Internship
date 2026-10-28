# TodoFlow Frontend

TodoFlow's frontend is a responsive React application powered by Redux Toolkit,
Axios, Tailwind CSS, and Vite. It communicates with the DDD API by default.

## Capabilities

- Firebase-backed signup and login through the backend
- Create, search, filter, sort, complete, and delete todos
- Persistent browser session storage
- Per-action loading states and user-friendly API errors
- Keyboard shortcuts and accessible dialogs/forms
- Memoized derived state through Redux selectors

## Technology

| Technology | Responsibility |
|---|---|
| React | Component rendering and local interaction state |
| Redux Toolkit | Shared authentication, todo, and view state |
| Axios | API client and authorization headers |
| Tailwind CSS | Responsive styling |
| Vite | Development server and production builds |

## Application flow

```text
App or TodoDashboard
    |-- useSelector -----------> reads Redux state
    |
    `-- dispatch(action)
            |
            v
        async thunk -> API module -> DDD backend
            |
            v
        reducer updates Redux state
            |
            `-------------> useSelector re-renders component
```

Components do not call Axios directly. `App.jsx` and `TodoDashboard.jsx` use
Redux hooks directly, API details remain in `src/api`, and selectors prepare
data for rendering.

## Project structure

```text
frontend/
|-- src/
|   |-- api/                 # Axios client and endpoint modules
|   |-- app/                 # Redux store configuration
|   |-- components/
|   |   |-- AuthForm.jsx
|   |   |-- TodoDashboard.jsx
|   |   |-- TodoItem.jsx
|   |   |-- todos/
|   |   |   |-- AddTodoForm.jsx
|   |   |   `-- TodoListPanel.jsx
|   |   `-- ui/              # Button, input, modal, and toast only
|   |-- features/
|   |   |-- auth/            # Session state and persistence
|   |   |-- todos/           # Todo thunks, reducers, and selectors
|   |   `-- taskView/        # Filter, search, and sort state
|   |-- hooks/               # Keyboard shortcut behavior
|   |-- App.jsx
|   `-- main.jsx
|-- package.json
`-- vite.config.js
```

## Requirements

- Node.js 18+
- npm
- The DDD backend running on port `8000`

## Installation

From the repository root:

```powershell
cd frontend
npm ci
```

## Running locally

Start the DDD backend first, then run:

```powershell
npm run dev
```

Open <http://localhost:5173>.

## Configuration

The default API URL is `http://127.0.0.1:8000`. To use another backend URL,
create `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Restart the Vite development server after changing environment values.

## Redux state

| Slice | Owns |
|---|---|
| `auth` | Current user and authentication request status |
| `todos` | Server todo records and mutation loading states |
| `taskView` | Search query, selected filter, and sort order |

Local component state is reserved for short-lived UI values such as form
fields, modal visibility, and focus behavior. Server data has one source of
truth in Redux.

## Important files

- `src/main.jsx` — application providers and session-expiry wiring
- `src/app/store.js` — root Redux store
- `src/api/client.js` — Axios base URL, bearer token, and `401` handling
- `src/features/auth/authSlice.js` — authentication thunks and session state
- `src/features/todos/todosSlice.js` — todo request lifecycle
- `src/features/todos/todosSelectors.js` — memoized stats and visible todos
- `src/App.jsx` — direct authentication selectors and dispatch calls
- `src/components/TodoDashboard.jsx` — direct todo selectors and dispatch calls

## Available commands

| Command | Purpose |
|---|---|
| `npm run dev` | Start the Vite development server |
| `npm run build` | Create a production build in `dist` |
| `npm run preview` | Preview the production build locally |

## Production build

```powershell
npm run build
npm run preview
```

Generated `dist` output is excluded from Git.

## Troubleshooting

- **Network error:** confirm the DDD API is running at the configured URL.
- **CORS error:** use `localhost:5173` or `127.0.0.1:5173`, both allowed by the
  DDD backend.
- **Login fails:** verify Firebase Authentication through the backend.
- **Session expires:** a backend `401` clears local session data automatically.
- **Environment change is ignored:** restart `npm run dev`.

## Related documentation

- [Repository run guide](../README.md)
- [DDD backend documentation](../backend/DDD/README.md)
- [Redux Toolkit learning guide](REDUX_TOOLKIT_GUIDE.md)
- [Architecture comparison](../docs/architecture.md)
