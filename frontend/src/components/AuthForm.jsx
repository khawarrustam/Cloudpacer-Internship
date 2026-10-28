import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import Button from './ui/Button';
import Input from './ui/Input';
import { toast } from './ui/Toast';

export default function AuthForm({ onSignup, onLogin, loading }) {
  // Form values temporary hain, is liye local state mein hain; Redux ki zaroorat nahi.
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    // Browser reload roko aur current mode ke mutabiq login ya signup call karo.
    event.preventDefault();
    setError(null);

    const result = isLogin
      ? await onLogin(email, password)
      : await onSignup(email, password, name);

    if (!result.success) {
      setError(result.error);
      return;
    }

    toast.success(isLogin ? 'Welcome back.' : 'Account created.');
  };

  const switchMode = () => {
    setIsLogin((current) => !current);
    setError(null);
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <section className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-white p-6 shadow-[var(--shadow-md)] sm:p-8">
        <header className="mb-7">
          <p className="text-sm font-extrabold text-[var(--primary)]">TodoFlow</p>
          <h1 className="mt-2 text-2xl font-extrabold">
            {isLogin ? 'Sign in' : 'Create an account'}
          </h1>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">
            {isLogin
              ? 'Continue managing your tasks.'
              : 'Create an account to start your task list.'}
          </p>
        </header>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <Input
              label="Name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          )}

          <Input
            label="Email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <div className="relative">
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              autoComplete={isLogin ? 'current-password' : 'new-password'}
              minLength={6}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword((current) => !current)}
              className="absolute right-2 top-8 rounded-lg p-2 text-[var(--text-muted)] hover:bg-stone-100"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>

          {error && (
            <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
              {error}
            </p>
          )}

          <Button type="submit" size="lg" className="w-full" isLoading={loading}>
            {isLogin ? 'Sign in' : 'Create account'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-[var(--text-secondary)]">
          {isLogin ? 'Need an account?' : 'Already have an account?'}
          <button
            type="button"
            onClick={switchMode}
            className="ml-2 font-bold text-[var(--primary)]"
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </section>
    </main>
  );
}
