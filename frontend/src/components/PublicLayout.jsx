import { Link } from 'react-router-dom';
import { Zap } from 'lucide-react';
import { Button } from './ui/button';

export function PublicHeader() {
  return (
    <header className="border-b border-white/5">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
            <Zap className="w-6 h-6 text-primary" />
          </div>
          <span className="font-bold text-xl tracking-tight">DropSniper AI</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/pricing">
            <Button variant="ghost" className="text-muted-foreground hover:text-white">Pricing</Button>
          </Link>
          <Link to="/login">
            <Button variant="ghost" className="text-muted-foreground hover:text-white">Login</Button>
          </Link>
          <Link to="/register">
            <Button className="bg-primary text-black font-bold hover:bg-primary/90">Get Started</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}

export function PublicFooter() {
  return (
    <footer className="border-t border-white/5 py-8">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex flex-col items-center gap-4">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary" />
            <span className="font-bold">DropSniper AI</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <Link to="/pricing" className="hover:text-white">Pricing</Link>
            <Link to="/terms" className="hover:text-white">Terms</Link>
            <Link to="/privacy" className="hover:text-white">Privacy</Link>
            <Link to="/contact" className="hover:text-white">Contact</Link>
          </div>
          <div className="text-sm text-muted-foreground text-center">
            <p>© 2026 DropSniper AI. All rights reserved.</p>
            <p className="text-xs mt-1">by ARI Solutions Inc. ™</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
