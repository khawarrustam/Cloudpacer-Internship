import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import App from './App';
import { store } from './app/store';
import { setUnauthorizedHandler } from './api/client';
import { ToastProvider } from './components/ui/Toast';
import { expireSession } from './features/auth/authSlice';
import './index.css';

setUnauthorizedHandler(() => {
  store.dispatch(expireSession());
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <ToastProvider>
        <App />
      </ToastProvider>
    </Provider>
  </React.StrictMode>,
);