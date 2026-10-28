import AuthForm from './components/AuthForm';
import TodoDashboard from './components/TodoDashboard';
import { useDispatch, useSelector } from 'react-redux';
import {
  loginUser,
  logoutUser,
  selectAuthStatus,
  selectCurrentUser,
  selectIsAuthenticated,
  signupUser,
} from './features/auth/authSlice';

export default function App() {
  // dispatch Redux ko action bhejta hai; thunk ho to API work bhi start hota hai.
  const dispatch = useDispatch();

  // useSelector store se sirf woh auth values read karta hai jo UI ko chahiye.
  const user = useSelector(selectCurrentUser);
  const isLoggedIn = useSelector(selectIsAuthenticated);
  const status = useSelector(selectAuthStatus);

  // unwrap() thunk ko normal Promise banata hai, is liye success/error yahan handle hota hai.
  const runAuthAction = async (action) => {
    try {
      await dispatch(action).unwrap();
      return { success: true };
    } catch (error) {
      return { success: false, error };
    }
  };

  const login = (email, password) => (
    runAuthAction(loginUser({ email, password }))
  );

  const signup = (email, password, displayName) => (
    runAuthAction(signupUser({ email, password, displayName }))
  );

  // Login state decide karti hai ke auth form show ho ya todo dashboard.
  if (!isLoggedIn) {
    return (
      <AuthForm
        onLogin={login}
        onSignup={signup}
        loading={status === 'loading'}
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
