import AuthForm from './components/AuthForm';
import TodoDashboard from './components/TodoDashboard';
import { useAuth } from './hooks/useAuth';

export default function App() {
  const { user, isLoggedIn, loading, login, signup, logout } = useAuth();

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
