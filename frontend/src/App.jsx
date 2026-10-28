import AuthForm from './components/AuthForm';
import TodoDashboard from './components/TodoDashboard';
import { useAuth } from './hooks/useAuth';

export default function App() {
  // English: useAuth reads login data from Redux and dispatches auth actions.
  // Roman Urdu: useAuth login data Redux se leta aur auth actions dispatch karta hai.
  const { user, isLoggedIn, loading, login, signup, logout } = useAuth();

  // English: Redux decides which main screen should be visible.
  // Roman Urdu: Redux decide karta hai konsi main screen dikhani hai.
  if (!isLoggedIn) {
    return (
      <AuthForm
        onLogin={login}
        onSignup={signup}
        loading={loading}
      />
    );
  }

  return (
    <TodoDashboard
      user={user}
      onLogout={logout}
    />
  );
}
