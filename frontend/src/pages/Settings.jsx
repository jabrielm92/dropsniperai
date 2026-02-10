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
  ArrowLeft, Save, Filter, Bell, User, 
  Loader2, Zap, Send, Mail, Bot, CheckCircle, XCircle, Key, Eye, EyeOff, Trash2
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  getFilterSettings, updateFilterSettings, getIntegrationsStatus,
  getUserKeys, updateUserKeys, testTelegram, sendTelegramReport
} from '../lib/api';

export default function Settings() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingKeys, setSavingKeys] = useState(false);
  const [testingTelegram, setTestingTelegram] = useState(false);
  const [sendingReport, setSendingReport] = useState(false);
  
  const [filters, setFilters] = useState({
    max_source_cost: 15,
    min_sell_price: 35,
    min_margin_percent: 60,
    max_fb_ads: 50,
    max_shipping_days: 15,
    exclude_trademark_risk: true
  });

  const [userKeys, setUserKeys] = useState({
    openai_api_key: '',
    telegram_bot_token: '',
    telegram_chat_id: ''
  });

  const [keysStatus, setKeysStatus] = useState({});
  const [showOpenAiKey, setShowOpenAiKey] = useState(false);
  const [showTelegramToken, setShowTelegramToken] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const [filtersRes, keysRes] = await Promise.all([
        getFilterSettings(),
        getUserKeys()
      ]);
      setFilters(filtersRes.data);
      setKeysStatus(keysRes.data);
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

  const handleSaveKeys = async () => {
    setSavingKeys(true);
    try {
      const keysToUpdate = {};
      if (userKeys.openai_api_key) keysToUpdate.openai_api_key = userKeys.openai_api_key;
      if (userKeys.telegram_bot_token) keysToUpdate.telegram_bot_token = userKeys.telegram_bot_token;
      if (userKeys.telegram_chat_id) keysToUpdate.telegram_chat_id = userKeys.telegram_chat_id;
      
      await updateUserKeys(keysToUpdate);
      toast.success('API keys saved securely!');
      // Clear inputs and refresh status
      setUserKeys({ openai_api_key: '', telegram_bot_token: '', telegram_chat_id: '' });
      fetchSettings();
    } catch (error) {
      toast.error('Failed to save keys');
    } finally {
      setSavingKeys(false);
    }
  };

  const handleTestTelegram = async () => {
    setTestingTelegram(true);
    try {
      const response = await testTelegram();
      if (response.data.success) {
        toast.success('Test message sent! Check your Telegram.');
      } else {
        toast.error('Failed to send test message. Check your bot token and chat ID.');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to test Telegram');
    } finally {
      setTestingTelegram(false);
    }
  };

  const handleSendReport = async () => {
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
          {user?.is_admin && (
            <Button 
              onClick={() => navigate('/admin')}
              variant="outline"
              className="border-primary/30 text-primary"
            >
              Admin Panel
            </Button>
          )}
        </div>
      </header>

      <main className="p-6 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <Tabs defaultValue="api-keys">
          <TabsList className="bg-[#121212] border border-white/5 mb-6">
            <TabsTrigger value="api-keys" className="flex items-center gap-2">
              <Key className="w-4 h-4" />
              API Keys
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

          {/* API Keys Tab */}
          <TabsContent value="api-keys">
            <div className="space-y-6">
              {/* Status Overview */}
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle>Your API Keys</CardTitle>
                  <CardDescription>Configure your own API keys to power the AI features</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* OpenAI Status */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                        <Bot className="w-5 h-5 text-green-500" />
                      </div>
                      <div>
                        <p className="font-medium">OpenAI API Key</p>
                        <p className="text-xs text-muted-foreground">
                          {keysStatus.has_openai_key ? keysStatus.openai_key_masked : 'Not configured'}
                        </p>
                      </div>
                    </div>
                    {keysStatus.has_openai_key ? (
                      <Badge className="bg-green-500/20 text-green-500">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Connected
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-muted-foreground">
                        <XCircle className="w-3 h-3 mr-1" />
                        Not Set
                      </Badge>
                    )}
                  </div>

                  {/* Telegram Bot Status */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <Send className="w-5 h-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="font-medium">Telegram Bot Token</p>
                        <p className="text-xs text-muted-foreground">
                          {keysStatus.has_telegram_token ? keysStatus.telegram_token_masked : 'Not configured'}
                        </p>
                      </div>
                    </div>
                    {keysStatus.has_telegram_token ? (
                      <Badge className="bg-blue-500/20 text-blue-500">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Connected
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-muted-foreground">
                        <XCircle className="w-3 h-3 mr-1" />
                        Not Set
                      </Badge>
                    )}
                  </div>

                  {/* Telegram Chat ID Status */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <User className="w-5 h-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="font-medium">Telegram Chat ID</p>
                        <p className="text-xs text-muted-foreground">
                          {keysStatus.telegram_chat_id || 'Not configured'}
                        </p>
                      </div>
                    </div>
                    {keysStatus.telegram_chat_id ? (
                      <Badge className="bg-blue-500/20 text-blue-500">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Set
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-muted-foreground">
                        <XCircle className="w-3 h-3 mr-1" />
                        Not Set
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Add/Update Keys */}
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle>Add or Update Keys</CardTitle>
                  <CardDescription>Your keys are stored securely and only used for your scans</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* OpenAI Key Input */}
                  <div className="space-y-2">
                    <Label>OpenAI API Key</Label>
                    <p className="text-xs text-muted-foreground mb-2">
                      Get from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener" className="text-primary hover:underline">platform.openai.com/api-keys</a>
                    </p>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          type={showOpenAiKey ? "text" : "password"}
                          placeholder="sk-..."
                          value={userKeys.openai_api_key}
                          onChange={(e) => setUserKeys({ ...userKeys, openai_api_key: e.target.value })}
                          className="bg-[#0A0A0A] border-white/10 pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowOpenAiKey(!showOpenAiKey)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                        >
                          {showOpenAiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Telegram Bot Token Input */}
                  <div className="space-y-2">
                    <Label>Telegram Bot Token</Label>
                    <p className="text-xs text-muted-foreground mb-2">
                      Create a bot via <a href="https://t.me/BotFather" target="_blank" rel="noopener" className="text-blue-500 hover:underline">@BotFather</a> on Telegram
                    </p>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          type={showTelegramToken ? "text" : "password"}
                          placeholder="123456789:ABCdefGHI..."
                          value={userKeys.telegram_bot_token}
                          onChange={(e) => setUserKeys({ ...userKeys, telegram_bot_token: e.target.value })}
                          className="bg-[#0A0A0A] border-white/10 pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowTelegramToken(!showTelegramToken)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                        >
                          {showTelegramToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Telegram Chat ID Input */}
                  <div className="space-y-2">
                    <Label>Telegram Chat ID</Label>
                    <p className="text-xs text-muted-foreground mb-2">
                      Message <a href="https://t.me/userinfobot" target="_blank" rel="noopener" className="text-blue-500 hover:underline">@userinfobot</a> to get YOUR personal ID (not the bot's ID)
                    </p>
                    <Input
                      placeholder="123456789"
                      value={userKeys.telegram_chat_id}
                      onChange={(e) => setUserKeys({ ...userKeys, telegram_chat_id: e.target.value })}
                      className="bg-[#0A0A0A] border-white/10"
                    />
                    <p className="text-xs text-yellow-500">⚠️ After saving, you must START a conversation with your bot first (send /start to it)</p>
                  </div>

                  <Button 
                    onClick={handleSaveKeys}
                    disabled={savingKeys}
                    className="w-full bg-primary text-black font-bold hover:bg-primary/90"
                  >
                    {savingKeys ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        Save API Keys
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Test Telegram */}
              {keysStatus.has_telegram_token && keysStatus.telegram_chat_id && (
                <Card className="bg-[#121212] border-blue-500/20">
                  <CardContent className="p-6">
                    <h3 className="font-bold mb-4 flex items-center gap-2">
                      <Send className="w-5 h-5 text-blue-500" />
                      Test Your Telegram Bot
                    </h3>
                    <div className="flex gap-3">
                      <Button 
                        onClick={handleTestTelegram}
                        disabled={testingTelegram}
                        variant="outline"
                        className="flex-1 border-blue-500/30 text-blue-500 hover:bg-blue-500/10"
                      >
                        {testingTelegram ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                        Send Test Message
                      </Button>
                      <Button 
                        onClick={handleSendReport}
                        disabled={sendingReport}
                        className="flex-1 bg-blue-500 hover:bg-blue-600"
                      >
                        {sendingReport ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Mail className="w-4 h-4 mr-2" />}
                        Send Daily Report
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
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
                  />
                </div>

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
                  />
                </div>

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
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Label>Maximum FB Ads</Label>
                    <span className="font-mono text-primary">{filters.max_fb_ads}</span>
                  </div>
                  <Slider
                    value={[filters.max_fb_ads]}
                    onValueChange={([value]) => setFilters({ ...filters, max_fb_ads: value })}
                    max={100}
                    min={10}
                    step={5}
                  />
                </div>

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
                  />
                </div>

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
                  {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                  Save Filters
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <Card className="bg-[#121212] border-white/5">
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>Notifications are sent via your Telegram bot when configured</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <p className="font-medium">Daily Report via Telegram</p>
                    <p className="text-xs text-muted-foreground mt-1">Sent automatically at 7:00 AM Eastern</p>
                  </div>
                  <Badge className={keysStatus.has_telegram_token && keysStatus.telegram_chat_id ? 'bg-primary/20 text-primary' : 'bg-white/5 text-muted-foreground'}>
                    {keysStatus.has_telegram_token && keysStatus.telegram_chat_id ? 'Active' : 'Setup Required'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <p className="font-medium">Competition Alerts</p>
                    <p className="text-xs text-muted-foreground mt-1">Get notified when competitors add new products</p>
                  </div>
                  <Badge className="bg-white/5 text-muted-foreground">Elite Plan</Badge>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <p className="font-medium">Trend Spike Alerts</p>
                    <p className="text-xs text-muted-foreground mt-1">Alerts when tracked products surge in search interest</p>
                  </div>
                  <Badge className="bg-white/5 text-muted-foreground">Elite Plan</Badge>
                </div>
                {!(keysStatus.has_telegram_token && keysStatus.telegram_chat_id) && (
                  <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <p className="text-sm text-blue-400">
                      Configure your Telegram Bot Token and Chat ID in the <strong>API Keys</strong> tab to enable notifications.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Account Tab */}
          <TabsContent value="account">
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
                {user?.is_admin && (
                  <div>
                    <Label className="text-muted-foreground">Role</Label>
                    <Badge className="bg-primary/20 text-primary">Admin</Badge>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
