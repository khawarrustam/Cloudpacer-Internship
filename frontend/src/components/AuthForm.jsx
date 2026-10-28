import React, { useState } from 'react';
import { ArrowRight, Check, Eye, EyeOff, Layers3, Lock, Mail, ShieldCheck, Sparkles, User } from 'lucide-react';
import Button from './ui/Button';
import Input from './ui/Input';
import { toast } from './ui/Toast';

export default function AuthForm({ onSignup, onLogin, loading }) {
  // English: Input text stays local because it is only needed by this form.
  // Roman Urdu: Input text local hai kyun ke sirf is form ko chahiye.
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    // English: These functions dispatch Redux actions through useAuth.
    // Roman Urdu: Yeh functions useAuth ke through Redux actions dispatch karte hain.
    const result = isLogin ? await onLogin(email, password) : await onSignup(email, password, name);
    if (result.success) {
      toast.success(isLogin ? 'Welcome back to TodoFlow.' : 'Your workspace is ready.');
    } else {
      setError(result.error);
    }
  };

  const switchMode = () => {
    setIsLogin((current) => !current);
    setError(null);
  };

  return (
    <main className="min-h-screen bg-[var(--bg-main)] p-3 sm:p-5">
      <div className="mx-auto grid min-h-[calc(100vh-24px)] max-w-7xl overflow-hidden rounded-[2rem] border border-black/5 bg-white shadow-[0_24px_80px_rgba(23,25,23,0.12)] sm:min-h-[calc(100vh-40px)] lg:grid-cols-[1.1fr_0.9fr]">
        <section className="relative hidden overflow-hidden bg-[#171917] p-12 text-white lg:flex lg:flex-col lg:justify-between">
          <div className="absolute -right-20 -top-20 h-80 w-80 rounded-full bg-blue-600/25 blur-3xl" />
          <div className="relative flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-[#171917]"><Check className="h-5 w-5" strokeWidth={3} /></span>
            <div><p className="font-extrabold">TodoFlow</p><p className="font-mono text-[9px] uppercase tracking-[0.18em] text-white/45">Quiet productivity</p></div>
          </div>

          <div className="relative max-w-xl">
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#99adff]">Less noise. More movement.</p>
            <h1 className="mt-5 text-5xl font-extrabold leading-[1.08] tracking-[-0.055em] xl:text-6xl">Plan lightly.<br />Finish clearly.</h1>
            <p className="mt-6 max-w-lg text-base leading-7 text-white/60">A focused home for the tasks that deserve your attention today — powered by a clean DDD architecture underneath.</p>

            <div className="mt-10 max-w-md rounded-3xl border border-white/10 bg-white/[0.06] p-5 backdrop-blur">
              <div className="flex items-center justify-between"><span className="text-xs font-bold text-white/55">Today</span><span className="rounded-full bg-[#b7e4b0] px-2.5 py-1 text-[9px] font-extrabold uppercase tracking-wider text-[#17391d]">In focus</span></div>
              <div className="mt-5 space-y-3">
                {[
                  { text: 'Finish the product walkthrough', done: true },
                  { text: 'Review API ownership rules', done: false },
                  { text: 'Polish the responsive states', done: false },
                ].map((task) => (
                  <div key={task.text} className="flex items-center gap-3 rounded-2xl bg-white/[0.07] px-4 py-3">
                    <span className={['flex h-5 w-5 items-center justify-center rounded-full border', task.done ? 'border-[#b7e4b0] bg-[#b7e4b0] text-[#17391d]' : 'border-white/30'].join(' ')}>{task.done && <Check className="h-3 w-3" strokeWidth={3} />}</span>
                    <span className={['text-xs font-semibold', task.done ? 'text-white/35 line-through' : 'text-white/80'].join(' ')}>{task.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="relative flex gap-6 text-[10px] font-bold uppercase tracking-[0.12em] text-white/40">
            <span className="flex items-center gap-2"><ShieldCheck className="h-3.5 w-3.5 text-[#b7e4b0]" />Secure sign-in</span>
            <span className="flex items-center gap-2"><Layers3 className="h-3.5 w-3.5 text-[#99adff]" />DDD powered</span>
          </div>
        </section>

        <section className="flex items-center justify-center p-6 sm:p-10 lg:p-14">
          <div className="w-full max-w-md">
            <div className="mb-12 flex items-center gap-3 lg:hidden">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--text-primary)] text-white"><Check className="h-5 w-5" strokeWidth={3} /></span>
              <div><p className="font-extrabold">TodoFlow</p><p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[var(--text-muted)]">Quiet productivity</p></div>
            </div>

            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--primary-soft)] text-[var(--primary)]"><Sparkles className="h-4 w-4" /></span>
            <h2 className="mt-6 text-3xl font-extrabold tracking-[-0.04em]">{isLogin ? 'Welcome back.' : 'Create your space.'}</h2>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{isLogin ? 'Sign in to pick up where you left off.' : 'A calmer way to keep your day moving.'}</p>

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              {!isLogin && <Input label="Your name" icon={User} placeholder="Rana Khawar" value={name} onChange={(event) => setName(event.target.value)} required />}
              <Input label="Email address" icon={Mail} type="email" autoComplete="email" placeholder="you@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required />
              <div className="relative">
                <Input label="Password" icon={Lock} type={showPassword ? 'text' : 'password'} autoComplete={isLogin ? 'current-password' : 'new-password'} minLength={6} placeholder="At least 6 characters" value={password} onChange={(event) => setPassword(event.target.value)} required />
                <button type="button" onClick={() => setShowPassword((current) => !current)} aria-label={showPassword ? 'Hide password' : 'Show password'} className="absolute right-2.5 top-[30px] flex h-9 w-9 items-center justify-center rounded-lg text-[var(--text-muted)] hover:bg-stone-100 hover:text-[var(--text-secondary)]">
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>

              {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div>}
              <Button type="submit" size="lg" isLoading={loading} className="w-full">{isLogin ? 'Sign in to TodoFlow' : 'Create my workspace'}<ArrowRight className="h-4 w-4" /></Button>
            </form>

            <p className="mt-7 text-center text-sm text-[var(--text-secondary)]">
              {isLogin ? 'New to TodoFlow?' : 'Already have an account?'}
              <button type="button" onClick={switchMode} className="ml-2 font-extrabold text-[var(--primary)] hover:text-[var(--primary-hover)]">{isLogin ? 'Create an account' : 'Sign in'}</button>
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
