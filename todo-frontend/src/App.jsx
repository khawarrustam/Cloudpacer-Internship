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

  //Normal thunk dispatch resolved Promise deta hai chahe request fulfilled ho ya rejected, kyun ke result ek Redux action hota hai. .unwrap():

  // fulfilled par original payload return karta hai;
  // rejected par rejectWithValue wala error throw karta hai;
  // component mein normal try/catch possible banata hai.

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