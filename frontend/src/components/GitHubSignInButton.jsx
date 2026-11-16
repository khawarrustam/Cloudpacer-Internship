import { Github } from 'lucide-react';
import { startGitHubOAuth } from '../features/auth/githubOAuth';


export default function GitHubSignInButton({ onError, disabled }) {
  const handleClick = () => {
    try {
      startGitHubOAuth();
    } catch (error) {
      onError(error.message);
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled}
      className="flex h-11 w-full items-center justify-center gap-3 rounded-lg bg-[#24292f] px-4 text-sm font-bold text-white transition hover:bg-black disabled:pointer-events-none disabled:opacity-60"
    >
      <Github className="h-5 w-5" aria-hidden="true" />
      Continue with GitHub
    </button>
  );
}
