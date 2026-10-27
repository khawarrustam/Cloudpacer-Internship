import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import App from './App';
import { store } from './app/store';
import { setUnauthorizedHandler } from './api/client';
import { ToastProvider } from './components/ui/Toast';
import { expireSession } from './features/auth/authSlice';
import './index.css';

// English: A 401 response means the saved login is no longer valid.
// Roman Urdu: 401 ka matlab saved login ab valid nahi raha.
setUnauthorizedHandler(() => {
  store.dispatch(expireSession());
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* English: Provider makes the Redux store available to every component. */}
    {/* Roman Urdu: Provider Redux store ko har component tak pohanchata hai. */}
    <Provider store={store}>
      <ToastProvider>
        <App />
      </ToastProvider>
    </Provider>
  </React.StrictMode>,
);
