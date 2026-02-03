import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Slider } from '../components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { 
  ArrowLeft, Save, Filter, Bell, User, CreditCard, 
  Loader2, Zap, Send, Mail, Bot, CheckCircle, XCircle, Key
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  getFilterSettings, updateFilterSettings, getIntegrationsStatus,
  connectTelegram, sendTelegramReport, getTelegramStatus
} from '../lib/api';

export default function Settings() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [connectingTelegram, setConnectingTelegram] = useState(false);
  const [sendingReport, setSendingReport] = useState(false);
  
  const [filters, setFilters] = useState({
    max_source_cost: 15,
    min_sell_price: 35,
    min_margin_percent: 60,
    max_fb_ads: 50,
    max_shipping_days: 15,
    exclude_trademark_risk: true
  });

  const [notifications, setNotifications] = useState({
    daily_report_email: true,
    daily_report_telegram: false,
    alert_competition: true,
    alert_trends: true
  });

  const [telegramChatId, setTelegramChatId] = useState('');
  const [integrations, setIntegrations] = useState(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const [filtersRes, integrationsRes] = await Promise.all([
        getFilterSettings(),
        getIntegrationsStatus()
      ]);
      setFilters(filtersRes.data);
      setIntegrations(integrationsRes.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveFilters = async () => {
    setSaving(true);
    try {
      await updateFilterSettings(filters);
      toast.success('Filter settings saved!');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleConnectTelegram = async () => {
    if (!telegramChatId.trim()) {
      toast.error('Please enter your Telegram Chat ID');
      return;
    }
    
    setConnectingTelegram(true);
    try {
      const response = await connectTelegram(telegramChatId);
      if (response.data.success) {
        toast.success('Telegram connected! Check your Telegram for a confirmation message.');
        fetchSettings();
      }
    } catch (error) {
      toast.error('Failed to connect Telegram');
    } finally {
      setConnectingTelegram(false);
    }
  };

  const handleSendTestReport = async () => {
    setSendingReport(true);
    try {
      await sendTelegramReport();
      toast.success('Daily report sent to Telegram!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send report');
    } finally {
      setSendingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0A0A0A]/80 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/dashboard')}
            className="text-muted-foreground hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      <main className="p-6 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <Tabs defaultValue="integrations">
          <TabsList className="bg-[#121212] border border-white/5 mb-6">
            <TabsTrigger value="integrations" className="flex items-center gap-2">
              <Key className="w-4 h-4" />
              Integrations
            </TabsTrigger>
            <TabsTrigger value="filters" className="flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filters
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-2">
              <Bell className="w-4 h-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="account" className="flex items-center gap-2">
              <User className="w-4 h-4" />
              Account
            </TabsTrigger>
          </TabsList>

          {/* Integrations Tab */}
          <TabsContent value="integrations">
            <div className="space-y-6">
              {/* Integration Status Overview */}
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle>Integration Status</CardTitle>
                  <CardDescription>Configure your API keys and connections</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* AI Browser Agent */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Bot className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">AI Browser Agent</p>
                        <p className="text-xs text-muted-foreground">Autonomous browsing with GPT-4</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {integrations?.ai_browser?.is_ready ? (
                        <Badge className="bg-primary/20 text-primary">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Ready
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-muted-foreground">
                          <XCircle className="w-3 h-3 mr-1" />
                          Not Configured
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* OpenAI */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                        <Zap className="w-5 h-5 text-green-500" />
                      </div>
                      <div>
                        <p className="font-medium">OpenAI API</p>
                        <p className="text-xs text-muted-foreground">Powers AI browser and ad copy generation</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {integrations?.openai_configured ? (
                        <Badge className="bg-green-500/20 text-green-500">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-muted-foreground">
                          <XCircle className="w-3 h-3 mr-1" />
                          Add Key
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Telegram */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <Send className="w-5 h-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="font-medium">Telegram Bot</p>
                        <p className="text-xs text-muted-foreground">Daily reports and alerts</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {integrations?.telegram?.configured ? (
                        <Badge className="bg-blue-500/20 text-blue-500">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-muted-foreground">
                          <XCircle className="w-3 h-3 mr-1" />
                          Add Token
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Stripe */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                        <CreditCard className="w-5 h-5 text-purple-500" />
                      </div>
                      <div>
                        <p className="font-medium">Stripe Payments</p>
                        <p className="text-xs text-muted-foreground">Subscription billing</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {integrations?.stripe_configured ? (
                        <Badge className="bg-purple-500/20 text-purple-500">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-muted-foreground">
                          <XCircle className="w-3 h-3 mr-1" />
                          Add Key
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* How to Configure */}
              <Card className="bg-[#121212] border-primary/20">
                <CardHeader>
                  <CardTitle>How to Add API Keys</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <div className="p-4 bg-white/5 rounded-lg">
                    <p className="font-mono text-primary mb-2">1. OpenAI API Key</p>
                    <p className="text-muted-foreground">
                      Get from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener" className="text-primary hover:underline">platform.openai.com/api-keys</a>
                      <br />Add to backend/.env: <code className="text-xs bg-black/50 px-1 rounded">OPENAI_API_KEY=sk-...</code>
                    </p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg">
                    <p className="font-mono text-blue-500 mb-2">2. Telegram Bot Token</p>
                    <p className="text-muted-foreground">
                      Message <a href="https://t.me/BotFather" target="_blank" rel="noopener" className="text-blue-500 hover:underline">@BotFather</a> on Telegram → /newbot
                      <br />Add to backend/.env: <code className="text-xs bg-black/50 px-1 rounded">TELEGRAM_BOT_TOKEN=123456:ABC...</code>
                    </p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg">
                    <p className="font-mono text-purple-500 mb-2">3. Stripe Keys</p>
                    <p className="text-muted-foreground">
                      Get from <a href="https://dashboard.stripe.com/apikeys" target="_blank" rel="noopener" className="text-purple-500 hover:underline">dashboard.stripe.com/apikeys</a>
                      <br />Add to backend/.env: <code className="text-xs bg-black/50 px-1 rounded">STRIPE_SECRET_KEY=sk_...</code>
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Telegram Setup */}
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Send className="w-5 h-5 text-blue-500" />
                    Connect Your Telegram
                  </CardTitle>
                  <CardDescription>Receive daily reports directly in Telegram</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Your Telegram Chat ID</Label>
                    <p className="text-xs text-muted-foreground mb-2">
                      Message <a href="https://t.me/userinfobot" target="_blank" rel="noopener" className="text-blue-500 hover:underline">@userinfobot</a> on Telegram to get your Chat ID
                    </p>
                    <div className="flex gap-2">
                      <Input 
                        placeholder="e.g., 123456789" 
                        value={telegramChatId}
                        onChange={(e) => setTelegramChatId(e.target.value)}
                        className="bg-[#0A0A0A] border-white/10"
                      />
                      <Button 
                        onClick={handleConnectTelegram}
                        disabled={connectingTelegram}
                        className="bg-blue-500 hover:bg-blue-600"
                      >
                        {connectingTelegram ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Connect'}
                      </Button>
                    </div>
                  </div>
                  
                  {user?.telegram_chat_id && (
                    <div className="pt-4 border-t border-white/5">
                      <Button 
                        onClick={handleSendTestReport}
                        disabled={sendingReport}
                        variant="outline"
                        className="w-full border-blue-500/30 text-blue-500 hover:bg-blue-500/10"
                      >
                        {sendingReport ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <Send className="w-4 h-4 mr-2" />
                        )}
                        Send Test Daily Report
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Filters Tab */}
          <TabsContent value="filters">
            <Card className="bg-[#121212] border-white/5">
              <CardHeader>
                <CardTitle>Product Filters</CardTitle>
                <CardDescription>Configure criteria for the AI to filter products</CardDescription>
              </CardHeader>
              <CardContent className="space-y-8">
                {/* Max Source Cost */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Label>Maximum Source Cost</Label>
                    <span className="font-mono text-primary">${filters.max_source_cost}</span>
                  </div>
                  <Slider
                    value={[filters.max_source_cost]}
                    onValueChange={([value]) => setFilters({ ...filters, max_source_cost: value })}
                    max={50}
                    min={5}
                    step={1}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground mt-2">Products above this cost will be filtered out</p>
                </div>

                {/* Min Sell Price */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Label>Minimum Sell Price</Label>
                    <span className="font-mono text-primary">${filters.min_sell_price}</span>
                  </div>
                  <Slider
                    value={[filters.min_sell_price]}
                    onValueChange={([value]) => setFilters({ ...filters, min_sell_price: value })}
                    max={100}
                    min={20}
                    step={5}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground mt-2">Minimum recommended selling price</p>
                </div>

                {/* Min Margin */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Label>Minimum Margin %</Label>
                    <span className="font-mono text-primary">{filters.min_margin_percent}%</span>
                  </div>
                  <Slider
                    value={[filters.min_margin_percent]}
                    onValueChange={([value]) => setFilters({ ...filters, min_margin_percent: value })}
                    max={90}
                    min={30}
                    step={5}
                    className="w-full"
                  />
                </div>

                {/* Max FB Ads */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Label>Maximum FB Ads (Competition)</Label>
                    <span className="font-mono text-primary">{filters.max_fb_ads}</span>
                  </div>
                  <Slider
                    value={[filters.max_fb_ads]}
                    onValueChange={([value]) => setFilters({ ...filters, max_fb_ads: value })}
                    max={100}
                    min={10}
                    step={5}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground mt-2">Products with more active ads will be flagged as high competition</p>
                </div>

                {/* Max Shipping Days */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Label>Maximum Shipping Days</Label>
                    <span className="font-mono text-primary">{filters.max_shipping_days} days</span>
                  </div>
                  <Slider
                    value={[filters.max_shipping_days]}
                    onValueChange={([value]) => setFilters({ ...filters, max_shipping_days: value })}
                    max={30}
                    min={5}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Trademark Risk */}
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <Label>Exclude Trademark Risk</Label>
                    <p className="text-xs text-muted-foreground mt-1">Filter out products with potential IP issues</p>
                  </div>
                  <Switch
                    checked={filters.exclude_trademark_risk}
                    onCheckedChange={(checked) => setFilters({ ...filters, exclude_trademark_risk: checked })}
                  />
                </div>

                <Button 
                  onClick={handleSaveFilters} 
                  disabled={saving}
                  className="w-full bg-primary text-black font-bold hover:bg-primary/90"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Save Filters
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <Card className="bg-[#121212] border-white/5">
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>Choose how you want to receive updates</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Email Notifications */}
                <div className="space-y-4">
                  <h3 className="font-medium flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    Email Notifications
                  </h3>
                  
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span>Daily Report Email</span>
                    <Switch
                      checked={notifications.daily_report_email}
                      onCheckedChange={(checked) => setNotifications({ ...notifications, daily_report_email: checked })}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span>Competition Alerts</span>
                    <Switch
                      checked={notifications.alert_competition}
                      onCheckedChange={(checked) => setNotifications({ ...notifications, alert_competition: checked })}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span>Trend Change Alerts</span>
                    <Switch
                      checked={notifications.alert_trends}
                      onCheckedChange={(checked) => setNotifications({ ...notifications, alert_trends: checked })}
                    />
                  </div>
                </div>

                <Button className="w-full bg-primary text-black font-bold hover:bg-primary/90">
                  <Save className="w-4 h-4 mr-2" />
                  Save Preferences
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Account Tab */}
          <TabsContent value="account">
            <div className="space-y-6">
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle>Account Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-muted-foreground">Name</Label>
                    <p className="font-medium">{user?.name}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Email</Label>
                    <p className="font-medium">{user?.email}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Subscription</Label>
                    <p className="font-medium capitalize text-primary">{user?.subscription_tier || 'Free'}</p>
                  </div>
                  {user?.telegram_chat_id && (
                    <div>
                      <Label className="text-muted-foreground">Telegram Chat ID</Label>
                      <p className="font-medium font-mono">{user.telegram_chat_id}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-[#121212] border-primary/20">
                <CardContent className="p-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                      <Zap className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-bold">Upgrade to Pro</h3>
                      <p className="text-sm text-muted-foreground">Unlock unlimited scans & launch kits</p>
                    </div>
                  </div>
                  <Button 
                    className="w-full bg-primary text-black font-bold hover:bg-primary/90"
                    onClick={() => navigate('/pricing')}
                  >
                    View Plans
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
