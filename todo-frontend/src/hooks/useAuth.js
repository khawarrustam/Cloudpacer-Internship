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

  return {
    user,
    isLoggedIn,
    loading: status === 'loading',
    login,
    signup,
    logout,
  };
}
