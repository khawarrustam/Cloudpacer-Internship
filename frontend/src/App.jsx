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
  // English: useDispatch gives this component the Redux dispatch function.
  // Roman Urdu: useDispatch is component ko Redux dispatch function deta hai.
  const dispatch = useDispatch();

  // English: useSelector reads only the authentication values required by this UI.
  // Roman Urdu: useSelector store se sirf woh auth values read karta hai jo UI ko chahiye.
  const user = useSelector(selectCurrentUser);
  const isLoggedIn = useSelector(selectIsAuthenticated);
  const status = useSelector(selectAuthStatus);

  // English: unwrap turns a dispatched thunk into a normal Promise for try/catch.
  // Roman Urdu: unwrap dispatched thunk ko normal Promise banata hai taa-ke try/catch chale.
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

  // English: Authentication state decides which main screen is rendered.
  // Roman Urdu: Login state decide karti hai ke auth form show ho ya todo dashboard.
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
