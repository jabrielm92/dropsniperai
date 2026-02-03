import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { 
  Sparkles, Bot, Send, ChevronRight, ChevronLeft, Check, 
  ExternalLink, Eye, EyeOff, Loader2, X, Rocket
} from 'lucide-react';
import { toast } from 'sonner';
import { updateUserKeys, testTelegram } from '../lib/api';

const steps = [
  { id: 'welcome', title: 'Welcome', icon: Sparkles },
  { id: 'openai', title: 'OpenAI', icon: Bot },
  { id: 'telegram', title: 'Telegram', icon: Send },
  { id: 'complete', title: 'Complete', icon: Rocket }
];

export default function SetupWizard({ onComplete, onSkip }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [showKey, setShowKey] = useState(false);
  const [showToken, setShowToken] = useState(false);
  
  const [keys, setKeys] = useState({
    openai_api_key: '',
    telegram_bot_token: '',
    telegram_chat_id: ''
  });

  const handleSaveOpenAI = async () => {
    if (!keys.openai_api_key) {
      toast.error('Please enter your OpenAI API key');
      return;
    }
    setSaving(true);
    try {
      await updateUserKeys({ openai_api_key: keys.openai_api_key });
      toast.success('OpenAI key saved!');
      setCurrentStep(2);
    } catch (error) {
      toast.error('Failed to save key');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveTelegram = async () => {
    if (!keys.telegram_bot_token || !keys.telegram_chat_id) {
      toast.error('Please enter both bot token and chat ID');
      return;
    }
    setSaving(true);
    try {
      await updateUserKeys({ 
        telegram_bot_token: keys.telegram_bot_token,
        telegram_chat_id: keys.telegram_chat_id 
      });
      toast.success('Telegram configured!');
      setCurrentStep(3);
    } catch (error) {
      toast.error('Failed to save Telegram settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestTelegram = async () => {
    setTesting(true);
    try {
      await testTelegram();
      toast.success('Test message sent! Check your Telegram');
    } catch (error) {
      toast.error('Failed to send test message');
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg bg-[#0A0A0A] border-white/10" data-testid="setup-wizard">
        {/* Progress */}
        <div className="px-6 pt-6">
          <div className="flex items-center justify-between mb-2">
            {steps.map((step, i) => (
              <div key={step.id} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors
                  ${i < currentStep ? 'bg-primary text-black' : i === currentStep ? 'bg-primary/20 text-primary border border-primary' : 'bg-white/5 text-muted-foreground'}`}>
                  {i < currentStep ? <Check className="w-4 h-4" /> : i + 1}
                </div>
                {i < steps.length - 1 && (
                  <div className={`w-12 h-0.5 mx-1 ${i < currentStep ? 'bg-primary' : 'bg-white/10'}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <CardContent className="p-6">
          {/* Welcome Step */}
          {currentStep === 0 && (
            <div className="text-center py-4">
              <div className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Welcome to DropSniper AI!</h2>
              <p className="text-muted-foreground mb-6">
                Let's get you set up in under 2 minutes. Connect your API keys to unlock AI-powered product discovery.
              </p>
              <div className="space-y-3 text-left mb-6 bg-white/5 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <Bot className="w-5 h-5 text-green-500" />
                  <span className="text-sm">OpenAI key enables AI browser scanning</span>
                </div>
                <div className="flex items-center gap-3">
                  <Send className="w-5 h-5 text-blue-500" />
                  <span className="text-sm">Telegram sends daily reports & alerts</span>
                </div>
              </div>
              <div className="flex gap-3">
                <Button variant="outline" className="flex-1 border-white/10" onClick={onSkip}>
                  Skip for now
                </Button>
                <Button className="flex-1 bg-primary text-black font-bold" onClick={() => setCurrentStep(1)}>
                  Get Started
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          )}

          {/* OpenAI Step */}
          {currentStep === 1 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-green-500" />
                </div>
                <div>
                  <h3 className="font-bold">Connect OpenAI</h3>
                  <p className="text-sm text-muted-foreground">Powers AI browser scanning</p>
                </div>
              </div>

              <div className="bg-white/5 rounded-lg p-4 mb-4">
                <p className="text-sm mb-3">
                  <strong>How to get your key:</strong>
                </p>
                <ol className="text-sm text-muted-foreground space-y-2">
                  <li>1. Go to OpenAI Platform</li>
                  <li>2. Navigate to API Keys section</li>
                  <li>3. Click "Create new secret key"</li>
                  <li>4. Copy and paste below</li>
                </ol>
                <a 
                  href="https://platform.openai.com/api-keys" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-primary text-sm mt-3 hover:underline"
                >
                  Open OpenAI Platform <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              <div className="space-y-2 mb-6">
                <Label>OpenAI API Key</Label>
                <div className="relative">
                  <Input
                    type={showKey ? "text" : "password"}
                    placeholder="sk-..."
                    value={keys.openai_api_key}
                    onChange={(e) => setKeys({ ...keys, openai_api_key: e.target.value })}
                    className="bg-[#121212] border-white/10 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                  >
                    {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex gap-3">
                <Button variant="outline" className="border-white/10" onClick={() => setCurrentStep(0)}>
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Back
                </Button>
                <Button 
                  variant="ghost" 
                  className="text-muted-foreground" 
                  onClick={() => setCurrentStep(2)}
                >
                  Skip
                </Button>
                <Button 
                  className="flex-1 bg-primary text-black font-bold" 
                  onClick={handleSaveOpenAI}
                  disabled={saving}
                >
                  {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  Save & Continue
                </Button>
              </div>
            </div>
          )}

          {/* Telegram Step */}
          {currentStep === 2 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Send className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-bold">Connect Telegram</h3>
                  <p className="text-sm text-muted-foreground">Receive daily reports & alerts</p>
                </div>
              </div>

              <div className="bg-white/5 rounded-lg p-4 mb-4">
                <p className="text-sm mb-3"><strong>Setup steps:</strong></p>
                <ol className="text-sm text-muted-foreground space-y-2">
                  <li>1. Message <a href="https://t.me/BotFather" target="_blank" rel="noopener" className="text-blue-500 hover:underline">@BotFather</a> → /newbot</li>
                  <li>2. Copy the bot token it gives you</li>
                  <li>3. Message <a href="https://t.me/userinfobot" target="_blank" rel="noopener" className="text-blue-500 hover:underline">@userinfobot</a> to get your Chat ID</li>
                </ol>
              </div>

              <div className="space-y-4 mb-6">
                <div className="space-y-2">
                  <Label>Bot Token</Label>
                  <div className="relative">
                    <Input
                      type={showToken ? "text" : "password"}
                      placeholder="123456789:ABCdefGHI..."
                      value={keys.telegram_bot_token}
                      onChange={(e) => setKeys({ ...keys, telegram_bot_token: e.target.value })}
                      className="bg-[#121212] border-white/10 pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowToken(!showToken)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                    >
                      {showToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Chat ID</Label>
                  <Input
                    placeholder="123456789"
                    value={keys.telegram_chat_id}
                    onChange={(e) => setKeys({ ...keys, telegram_chat_id: e.target.value })}
                    className="bg-[#121212] border-white/10"
                  />
                </div>
              </div>

              <div className="flex gap-3">
                <Button variant="outline" className="border-white/10" onClick={() => setCurrentStep(1)}>
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Back
                </Button>
                <Button 
                  variant="ghost" 
                  className="text-muted-foreground" 
                  onClick={() => setCurrentStep(3)}
                >
                  Skip
                </Button>
                <Button 
                  className="flex-1 bg-primary text-black font-bold" 
                  onClick={handleSaveTelegram}
                  disabled={saving}
                >
                  {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  Save & Continue
                </Button>
              </div>
            </div>
          )}

          {/* Complete Step */}
          {currentStep === 3 && (
            <div className="text-center py-4">
              <div className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center mx-auto mb-4">
                <Rocket className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-2xl font-bold mb-2">You're All Set!</h2>
              <p className="text-muted-foreground mb-6">
                Your DropSniper AI is ready. Start discovering winning products now!
              </p>
              
              <div className="space-y-3 text-left mb-6">
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-green-500" />
                    <span className="text-sm">OpenAI</span>
                  </div>
                  <Badge className={keys.openai_api_key ? "bg-green-500/20 text-green-500" : "bg-white/10 text-muted-foreground"}>
                    {keys.openai_api_key ? "Connected" : "Skipped"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Send className="w-4 h-4 text-blue-500" />
                    <span className="text-sm">Telegram</span>
                  </div>
                  <Badge className={keys.telegram_bot_token ? "bg-blue-500/20 text-blue-500" : "bg-white/10 text-muted-foreground"}>
                    {keys.telegram_bot_token ? "Connected" : "Skipped"}
                  </Badge>
                </div>
              </div>

              <Button className="w-full bg-primary text-black font-bold" onClick={onComplete}>
                Go to Dashboard
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          )}
        </CardContent>

        {/* Close button */}
        <button 
          onClick={onSkip}
          className="absolute top-4 right-4 text-muted-foreground hover:text-white"
          data-testid="wizard-close"
        >
          <X className="w-5 h-5" />
        </button>
      </Card>
    </div>
  );
}
