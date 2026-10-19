# TodoFlow DDD + Frontend Enhancement Prompt

You are improving an existing Todo application with a React/Vite/Tailwind frontend and a FastAPI backend organized with Domain-Driven Design and Onion Architecture.

## Current-state findings

- The backend already has clear domain, application, infrastructure, and presentation layers for creating, listing, and completing todos.
- The frontend calls `DELETE /todos/{id}`, but the backend has no matching delete use case or route.
- Completion currently mutates and saves a todo before the router verifies ownership. Authorization must happen before any state change.
- The authentication screen uses a clean indigo product style, while the dashboard switches to an unrelated terminal/cyberpunk visual language.
- Priority values return from the API in uppercase, while the frontend badge mapping expects lowercase.
- The dashboard lacks search, sorting, refresh feedback, useful dates, and a strong mobile task-management experience.

## Goal

Turn the project into a polished, coherent productivity product named **TodoFlow** while preserving its educational DDD/Onion structure and existing API behavior.

## Product and visual direction

- Use a calm, premium editorial workspace aesthetic: warm off-white canvas, white surfaces, near-black ink, cobalt blue as the primary accent, and lime/green for progress.
- Keep the design focused and functional, with crisp borders, generous spacing, subtle shadows, and restrained motion.
- Use one consistent design system across authentication, navigation, dashboard, forms, task rows, modals, and toasts.
- Avoid generic dashboard clutter, excessive gradients, glassmorphism, and cyberpunk terminology.
- Make the experience responsive from small phones through desktop screens and respect reduced-motion preferences.

## Frontend requirements

1. Redesign the authentication screen and dashboard as one coherent TodoFlow experience.
2. Add a welcoming dashboard header with the current date and a meaningful progress summary.
3. Improve quick task capture with an accessible priority selector, title validation, character feedback, and clear pending state.
4. Add client-side search, status filters, priority-aware sorting, and an explicit refresh action.
5. Show task metadata such as priority and created/completed dates, with readable completed styling.
6. Improve empty, loading, and error states and give errors a retry action.
7. Make destructive actions accessible: persistent access on touch screens, confirmation dialog semantics, Escape-to-close, and sensible focus behavior.
8. Normalize priority casing at the UI boundary.
9. Preserve the existing hooks/API separation and do not add unnecessary dependencies.

## DDD/backend requirements

1. Add `DeleteTodoCommand` and `DeleteTodoUseCase` in the application layer.
2. Extend the repository port and both adapters with secure owner-scoped lookup and deletion.
3. Add `owner_uid` to completion and deletion commands so authorization is enforced before mutation.
4. Expose `DELETE /todos/{todo_id}` with a `204 No Content` response.
5. Wire the new use case in the composition root through dependency injection.
6. Preserve domain invariants and map not-found/domain failures to appropriate HTTP responses.
7. Add focused tests proving owner isolation, completion behavior, deletion, and not-found behavior.

## Acceptance criteria

- The frontend production build succeeds.
- Backend tests pass without requiring Firebase or network access.
- A user cannot complete or delete another user's task.
- Delete works end-to-end against the DDD API contract.
- Search, filter, sort, refresh, create, complete, and delete states are represented in the UI.
- The interface is visually coherent, keyboard accessible, and usable on mobile.

