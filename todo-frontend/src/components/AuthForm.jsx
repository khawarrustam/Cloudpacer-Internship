import React, { useState } from 'react';
import { ArrowRight, CheckSquare2, Eye, EyeOff, Lock, Mail, User } from 'lucide-react';
import Button from './ui/Button';
import Input from './ui/Input';
import { toast } from './ui/Toast';

export default function AuthForm({ onSignup, onLogin, loading }) {
  // ============================================================================
  // HOOKS USED IN THIS COMPONENT:
  // - useState: Manages local, isolated component state across renders.
  //   [Roman Urdu]: Component ke andar local state sambhalne ke liye useState use hota hai.
  // ============================================================================

  // Hook: useState
  // What it does: Tracks whether the current view is "Sign In" (true) or "Create Account" (false).
  // Why it is here: Allows users to seamlessly switch between Login and Signup modes without leaving the page.
  // Roman Urdu: Yeh track karta hai ke user Login form par hai ya Signup form par; baghair page reload kiye screen badal deta hai.
  const [isLogin, setIsLogin] = useState(true);

  // Hook: useState
  // What it does: Stores the text entered into the email field.
  // Why it is here: Powers a controlled input for two-way data binding, sending the email payload on form submit.
  // Roman Urdu: Email input ki value ko state me store karta hai taake form submit hone par backend ko bheji ja sake.
  const [email, setEmail] = useState('');

  // Hook: useState
  // What it does: Stores the text entered into the password field.
  // Why it is here: Implements a controlled input to safely pass password credentials to authentication handlers.
  // Roman Urdu: Password input ki value save karta hai taake login ya signup API call me use ho sake.
  const [password, setPassword] = useState('');

  // Hook: useState
  // What it does: Stores the full display name during user registration.
  // Why it is here: Required only in signup mode (when !isLogin) to create a user profile with their name.
  // Roman Urdu: Signup ke waqt user ka naam save karta hai; login ke waqt iski zaroorat nahi hoti.
  const [name, setName] = useState('');

  // Hook: useState
  // What it does: Toggles password input type between 'password' (masked) and 'text' (visible).
  // Why it is here: Enhances user experience by allowing users to verify their typed password before submitting.
  // Roman Urdu: Password ko hide/show karne ke liye boolean flag hai taake user apna typed password dekh sake.
  const [showPassword, setShowPassword] = useState(false);

  // Hook: useState
  // What it does: Stores authentication or validation error messages returned by API responses.
  // Why it is here: Triggers re-rendering to display inline error alerts when authentication fails.
  // Roman Urdu: Jab login ya signup fail ho jaye toh backend ka error message screen par laal alert me show karta hai.
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (isLogin) {
      const result = await onLogin(email, password);
      if (result.success) {
        toast.success('Signed in successfully.');
        return;
      }
      setError(result.error);
      return;
    }

    const result = await onSignup(email, password, name);
    if (result.success) {
      toast.success('Account created successfully.');
      return;
    }
    setError(result.error);
  };

  return (
    <main className="grid min-h-screen bg-[var(--bg-main)] px-4 py-8 lg:grid-cols-[1fr_480px] lg:px-0 lg:py-0">
      <section className="hidden border-r border-[var(--border)] bg-indigo-600 text-white lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/20 text-white shadow-sm ring-1 ring-white/30">
            <CheckSquare2 className="h-6 w-6" />
          </div>
          <span className="text-base font-bold text-white">
            Todo<span className="text-indigo-200">Flow</span>
          </span>
        </div>

        <div className="max-w-lg space-y-6">
          <p className="text-xs font-bold uppercase tracking-wider text-indigo-200">Productivity workspace</p>
          <h1 className="text-5xl font-bold leading-tight tracking-tight text-white">
            Keep your day focused without losing the details.
          </h1>
          <p className="text-lg leading-relaxed text-indigo-100">
            A clean task dashboard backed by your DDD FastAPI service, built for quick capture and steady execution.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 text-sm">
          {['Secure auth', 'Real tasks', 'Fast flow'].map((item) => (
            <div key={item} className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/10 px-4 py-3 font-medium text-indigo-50 backdrop-blur">
              <div className="h-1.5 w-1.5 rounded-full bg-indigo-300" />
              {item}
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto flex w-full max-w-md items-center justify-center lg:max-w-none">
        <div className="w-full rounded-2xl border border-[var(--border)] bg-white p-8 shadow-xl sm:p-12 lg:mx-12">
          <div className="mb-8 lg:hidden">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 text-white">
                <CheckSquare2 className="h-6 w-6" />
              </div>
              <span className="text-base font-bold text-slate-950">
                Todo<span className="text-indigo-600">Flow</span>
              </span>
            </div>
          </div>

          <div className="mb-10">
            <h2 className="text-3xl font-bold tracking-tight text-slate-950">
              {isLogin ? 'Welcome back' : 'Create account'}
            </h2>
            <p className="mt-2 text-sm text-slate-500">
              {isLogin ? 'Sign in to continue managing your tasks.' : 'Start organizing your tasks in a focused workspace.'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLogin && (
              <Input
                label="Name"
                icon={User}
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            )}

            <Input
              label="Email"
              icon={Mail}
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <div className="relative">
              <Input
                label="Password"
                icon={Lock}
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                className="absolute right-3 top-[34px] flex h-8 w-8 items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>

            {error && (
              <div className="rounded-md border border-red-100 bg-red-50 px-3 py-2 text-sm font-medium text-red-700">
                {error}
              </div>
            )}

            <Button type="submit" size="lg" isLoading={loading} className="w-full py-4 text-base">
              {isLogin ? 'Sign In' : 'Create Account'}
              <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-slate-500">
            {isLogin ? "Don't have an account?" : 'Already have an account?'}
            <button
              type="button"
              onClick={() => {
                setIsLogin((value) => !value);
                setError(null);
              }}
              className="ml-2 font-semibold text-indigo-600 transition-colors hover:text-indigo-700"
            >
              {isLogin ? 'Create account' : 'Sign in'}
            </button>
          </p>
        </div>
      </section>
    </main>
  );
}
