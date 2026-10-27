import { useDispatch, useSelector } from 'react-redux';
import {
  loginUser,
  logoutUser,
  selectAuthStatus,
  selectCurrentUser,
  selectIsAuthenticated,
  signupUser,
} from '../features/auth/authSlice';

// English: This hook gives components a small authentication API.
// Roman Urdu: Component ko login, signup aur logout ka seedha interface milta hai.
export function useAuth() {
  const dispatch = useDispatch();
  const user = useSelector(selectCurrentUser);
  const isLoggedIn = useSelector(selectIsAuthenticated);
  const status = useSelector(selectAuthStatus);

  // English: unwrap lets this hook use normal try/catch with a Redux thunk.
  // Roman Urdu: unwrap Redux thunk ke sath normal try/catch use karne deta hai.
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

  const logout = () => dispatch(logoutUser());

  // English: App.jsx receives only the auth values and actions it needs.
  // Roman Urdu: App.jsx ko sirf zaroori auth values aur actions milte hain.
  return {
    user,
    isLoggedIn,
    loading: status === 'loading',
    login,
    signup,
    logout,
  };
}
