import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Zap, ArrowLeft, Loader2, Check, Mail } from 'lucide-react';
import { toast } from 'sonner';
import { PublicFooter } from '../components/PublicLayout';
import api from '../lib/api';

export default function Register() {
  const [step, setStep] = useState('form'); // form, verify, complete
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [verificationCode, setVerificationCode] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.password) {
      toast.error('Please fill in all fields');
      return;
    }
    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      // Send verification code
      await api.post('/verify/send', { email: formData.email, name: formData.name });
      toast.success('Verification code sent to your email');
      setStep('verify');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send verification code');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (verificationCode.length !== 6) {
      toast.error('Please enter the 6-digit code');
      return;
    }

    setLoading(true);
    try {
      // Verify code
      await api.post('/verify/check', { email: formData.email, code: verificationCode });
      
      // Now register the user
      await register(formData.email, formData.password, formData.name);
      
      toast.success('Email verified! Choose your plan to continue.');
      
      // Redirect to pricing page
      navigate('/pricing?signup=true');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid verification code');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    try {
      await api.post('/verify/resend', { email: formData.email, name: formData.name });
      toast.success('New code sent!');
    } catch (error) {
      toast.error('Failed to resend code');
    } finally {
      setResending(false);
    }
  };

  const benefits = [
    "AI-powered product discovery",
    "Daily intelligence reports",
    "Full supplier sourcing",
    "Launch kit generator",
    "Profit calculator",
    "24-hour free trial"
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0A] flex flex-col">
      <div className="flex-1 flex">
        {/* Left side - Visual */}
        <div className="hidden lg:flex flex-1 bg-[#0d0d0d] flex-col justify-center p-12">
          <div className="max-w-md">
            <h2 className="text-3xl font-bold mb-8">
              Use the system <span className="text-primary">top sellers</span> utilize to scale over and over
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

          {step === 'form' && (
            <>
              <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                  <Zap className="w-7 h-7 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">Create your account</h1>
                  <p className="text-muted-foreground">Start finding winners today</p>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5 max-w-sm">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="bg-[#121212] border-white/10 h-12"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="bg-[#121212] border-white/10 h-12"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="bg-[#121212] border-white/10 h-12"
                    required
                  />
                  <p className="text-xs text-muted-foreground">Minimum 6 characters</p>
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 bg-primary text-black font-bold text-base hover:bg-primary/90"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Sending code...
                    </>
                  ) : (
                    'Continue'
                  )}
                </Button>
              </form>

              <p className="mt-6 text-center text-xs text-muted-foreground max-w-sm">
                By signing up, you agree to our <Link to="/terms" className="text-primary hover:underline">Terms of Service</Link> and <Link to="/privacy" className="text-primary hover:underline">Privacy Policy</Link>
              </p>

              <p className="mt-6 text-center text-muted-foreground max-w-sm">
                Already have an account?{' '}
                <Link to="/login" className="text-primary hover:underline font-medium">
                  Sign in
                </Link>
              </p>
            </>
          )}

          {step === 'verify' && (
            <>
              <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                  <Mail className="w-7 h-7 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">Check your email</h1>
                  <p className="text-muted-foreground">We sent a code to {formData.email}</p>
                </div>
              </div>

              <form onSubmit={handleVerify} className="space-y-5 max-w-sm">
                <div className="space-y-2">
                  <Label htmlFor="code">Verification Code</Label>
                  <Input
                    id="code"
                    type="text"
                    placeholder="000000"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    className="bg-[#121212] border-white/10 h-14 text-center text-2xl tracking-[0.5em] font-mono"
                    maxLength={6}
                    required
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 bg-primary text-black font-bold text-base hover:bg-primary/90"
                  disabled={loading || verificationCode.length !== 6}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Verifying...
                    </>
                  ) : (
                    'Verify Email'
                  )}
                </Button>
              </form>

              <p className="mt-6 text-center text-muted-foreground max-w-sm">
                Didn't receive the code?{' '}
                <button 
                  onClick={handleResend} 
                  disabled={resending}
                  className="text-primary hover:underline font-medium disabled:opacity-50"
                >
                  {resending ? 'Sending...' : 'Resend'}
                </button>
              </p>

              <button 
                onClick={() => setStep('form')} 
                className="mt-4 text-sm text-muted-foreground hover:text-white"
              >
                ← Back to signup
              </button>
            </>
          )}
        </div>
      </div>
      
      <PublicFooter />
    </div>
  );
}
