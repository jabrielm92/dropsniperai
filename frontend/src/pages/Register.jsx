import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Zap, ArrowLeft, Loader2, Check } from 'lucide-react';
import { toast } from 'sonner';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await register(name, email, password);
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const benefits = [
    "AI-powered product discovery",
    "Daily intelligence reports",
    "Full supplier sourcing",
    "Launch kit generator",
    "Profit calculator",
    "7-day free trial"
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0A] flex">
      {/* Left side - Visual */}
      <div className="hidden lg:flex flex-1 bg-[#0d0d0d] flex-col justify-center p-12">
        <div className="max-w-md">
          <h2 className="text-3xl font-bold mb-8">
            Join <span className="text-primary">10,000+</span> sellers finding winners daily
          </h2>
          <ul className="space-y-4">
            {benefits.map((benefit, i) => (
              <li key={i} className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                  <Check className="w-4 h-4 text-primary" />
                </div>
                <span className="text-muted-foreground">{benefit}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex flex-col justify-center px-8 md:px-16 lg:px-24">
        <Link to="/" className="inline-flex items-center gap-2 text-muted-foreground hover:text-white mb-12 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to home
        </Link>
        
        <div className="max-w-md">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
              <Zap className="w-7 h-7 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Create your account</h1>
              <p className="text-muted-foreground">Start finding winners today</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="bg-[#121212] border-white/10 h-12"
                data-testid="register-name-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-[#121212] border-white/10 h-12"
                data-testid="register-email-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="bg-[#121212] border-white/10 h-12"
                data-testid="register-password-input"
              />
              <p className="text-xs text-muted-foreground">Minimum 6 characters</p>
            </div>

            <Button 
              type="submit" 
              className="w-full h-12 bg-primary text-black font-bold hover:bg-primary/90 btn-primary-glow"
              disabled={loading}
              data-testid="register-submit-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            By signing up, you agree to our Terms of Service and Privacy Policy
          </p>

          <p className="mt-6 text-center text-muted-foreground">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
