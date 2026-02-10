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
  Loader2, Zap, Send, Mail, Bot, CheckCircle, XCircle, Key, Eye, EyeOff,
  TrendingUp, AlertTriangle, BarChart3, Shield
} from 'lucide-react';
import { toast } from 'sonner';
import {
  getFilterSettings, updateFilterSettings,
  getUserKeys, updateUserKeys, testTelegram, sendTelegramReport,
  getNotificationPreferences, updateNotificationPreferences
} from '../lib/api';

export default function Settings() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingKeys, setSavingKeys] = useState(false);
  const [savingNotifs, setSavingNotifs] = useState(false);
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

  const [notifPrefs, setNotifPrefs] = useState({
    daily_report: true,
    competition_alerts: true,
    trend_spike_alerts: true,
    scan_complete: true
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
      const [filtersRes, keysRes, notifsRes] = await Promise.allSettled([
        getFilterSettings(),
        getUserKeys(),
        getNotificationPreferences()
      ]);
      if (filtersRes.status === 'fulfilled') setFilters(filtersRes.value.data);
      if (keysRes.status === 'fulfilled') setKeysStatus(keysRes.value.data);
      if (notifsRes.status === 'fulfilled') setNotifPrefs(notifsRes.value.data);
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
      toast.success('Filters saved! Next scan will use these criteria.');
    } catch (error) {
      toast.error('Failed to save filters');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveNotifs = async () => {
    setSavingNotifs(true);
    try {
      await updateNotificationPreferences(notifPrefs);
      toast.success('Notification preferences saved!');
    } catch (error) {
      toast.error('Failed to save notification preferences');
    } finally {
      setSavingNotifs(false);
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

  const telegramReady = keysStatus.has_telegram_token && keysStatus.telegram_chat_id;
  const isElite = ['elite', 'agency', 'enterprise'].includes(user?.subscription_tier);

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
      <header className="border-b border-white/[0.06] bg-[#0A0A0A]/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 sm:px-6 h-14">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="text-muted-foreground hover:text-white gap-2 text-sm h-9"
          >
            <ArrowLeft className="w-4 h-4" />
            Dashboard
          </Button>
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-primary/10 border border-primary/20">
              <Zap className="w-3 h-3 text-primary" />
              <span className="text-xs font-semibold text-primary capitalize">{user?.subscription_tier || 'Free'}</span>
            </div>
            {user?.is_admin && (
              <Button
                onClick={() => navigate('/admin')}
                variant="ghost"
                size="sm"
                className="text-muted-foreground hover:text-primary gap-1.5 text-xs h-8"
              >
                <Shield className="w-3.5 h-3.5" />
                Admin
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
        <h1 className="text-2xl font-bold tracking-tight mb-6">Settings</h1>

        <Tabs defaultValue="api-keys">
          <TabsList className="bg-[#111] border border-white/[0.06] mb-6 h-10">
            <TabsTrigger value="api-keys" className="flex items-center gap-1.5 text-xs">
              <Key className="w-3.5 h-3.5" />
              API Keys
            </TabsTrigger>
            <TabsTrigger value="filters" className="flex items-center gap-1.5 text-xs">
              <Filter className="w-3.5 h-3.5" />
              Filters
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-1.5 text-xs">
              <Bell className="w-3.5 h-3.5" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="account" className="flex items-center gap-1.5 text-xs">
              <User className="w-3.5 h-3.5" />
              Account
            </TabsTrigger>
          </TabsList>

          {/* ─── API KEYS TAB ─── */}
          <TabsContent value="api-keys">
            <div className="space-y-4">
              {/* Status Cards */}
              <Card className="bg-[#111] border-white/[0.06]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Integration Status</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {/* OpenAI */}
                  <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-emerald-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">OpenAI API Key</p>
                        <p className="text-[11px] text-muted-foreground">
                          {keysStatus.has_openai_key ? keysStatus.openai_key_masked : 'Required for AI scanning'}
                        </p>
                      </div>
                    </div>
                    <Badge className={`text-[10px] ${keysStatus.has_openai_key ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' : 'bg-white/[0.04] text-white/40 border border-white/[0.06]'}`}>
                      {keysStatus.has_openai_key ? (
                        <><CheckCircle className="w-2.5 h-2.5 mr-1" />Connected</>
                      ) : (
                        <><XCircle className="w-2.5 h-2.5 mr-1" />Not Set</>
                      )}
                    </Badge>
                  </div>

                  {/* Telegram Bot */}
                  <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <Send className="w-4 h-4 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Telegram Bot</p>
                        <p className="text-[11px] text-muted-foreground">
                          {keysStatus.has_telegram_token ? keysStatus.telegram_token_masked : 'For daily reports & alerts'}
                        </p>
                      </div>
                    </div>
                    <Badge className={`text-[10px] ${keysStatus.has_telegram_token ? 'bg-blue-500/15 text-blue-400 border border-blue-500/20' : 'bg-white/[0.04] text-white/40 border border-white/[0.06]'}`}>
                      {keysStatus.has_telegram_token ? (
                        <><CheckCircle className="w-2.5 h-2.5 mr-1" />Connected</>
                      ) : (
                        <><XCircle className="w-2.5 h-2.5 mr-1" />Not Set</>
                      )}
                    </Badge>
                  </div>

                  {/* Chat ID */}
                  <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <User className="w-4 h-4 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Telegram Chat ID</p>
                        <p className="text-[11px] text-muted-foreground">
                          {keysStatus.telegram_chat_id || 'Your personal chat ID'}
                        </p>
                      </div>
                    </div>
                    <Badge className={`text-[10px] ${keysStatus.telegram_chat_id ? 'bg-blue-500/15 text-blue-400 border border-blue-500/20' : 'bg-white/[0.04] text-white/40 border border-white/[0.06]'}`}>
                      {keysStatus.telegram_chat_id ? (
                        <><CheckCircle className="w-2.5 h-2.5 mr-1" />Set</>
                      ) : (
                        <><XCircle className="w-2.5 h-2.5 mr-1" />Not Set</>
                      )}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Key Inputs */}
              <Card className="bg-[#111] border-white/[0.06]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Add or Update Keys</CardTitle>
                  <CardDescription className="text-xs">Stored securely, only used for your scans</CardDescription>
                </CardHeader>
                <CardContent className="space-y-5">
                  <div className="space-y-1.5">
                    <Label className="text-xs">OpenAI API Key</Label>
                    <p className="text-[11px] text-muted-foreground">
                      Get from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener" className="text-primary hover:underline">platform.openai.com/api-keys</a>
                    </p>
                    <div className="relative">
                      <Input
                        type={showOpenAiKey ? "text" : "password"}
                        placeholder="sk-..."
                        value={userKeys.openai_api_key}
                        onChange={(e) => setUserKeys({ ...userKeys, openai_api_key: e.target.value })}
                        className="bg-[#0A0A0A] border-white/[0.08] pr-10 h-9 text-sm"
                      />
                      <button
                        type="button"
                        onClick={() => setShowOpenAiKey(!showOpenAiKey)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                      >
                        {showOpenAiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <Label className="text-xs">Telegram Bot Token</Label>
                    <p className="text-[11px] text-muted-foreground">
                      Create via <a href="https://t.me/BotFather" target="_blank" rel="noopener" className="text-blue-400 hover:underline">@BotFather</a> on Telegram
                    </p>
                    <div className="relative">
                      <Input
                        type={showTelegramToken ? "text" : "password"}
                        placeholder="123456789:ABCdefGHI..."
                        value={userKeys.telegram_bot_token}
                        onChange={(e) => setUserKeys({ ...userKeys, telegram_bot_token: e.target.value })}
                        className="bg-[#0A0A0A] border-white/[0.08] pr-10 h-9 text-sm"
                      />
                      <button
                        type="button"
                        onClick={() => setShowTelegramToken(!showTelegramToken)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                      >
                        {showTelegramToken ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <Label className="text-xs">Telegram Chat ID</Label>
                    <p className="text-[11px] text-muted-foreground">
                      Message <a href="https://t.me/userinfobot" target="_blank" rel="noopener" className="text-blue-400 hover:underline">@userinfobot</a> to get your ID
                    </p>
                    <Input
                      placeholder="123456789"
                      value={userKeys.telegram_chat_id}
                      onChange={(e) => setUserKeys({ ...userKeys, telegram_chat_id: e.target.value })}
                      className="bg-[#0A0A0A] border-white/[0.08] h-9 text-sm"
                    />
                    <p className="text-[11px] text-amber-400/80">After saving, send /start to your bot first</p>
                  </div>

                  <Button
                    onClick={handleSaveKeys}
                    disabled={savingKeys}
                    className="w-full bg-gradient-to-r from-primary to-emerald-500 text-black font-bold hover:opacity-90 h-9 text-sm"
                  >
                    {savingKeys ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                    Save API Keys
                  </Button>
                </CardContent>
              </Card>

              {/* Test Telegram */}
              {telegramReady && (
                <Card className="bg-[#111] border-blue-500/15">
                  <CardContent className="p-4">
                    <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
                      <Send className="w-4 h-4 text-blue-400" />
                      Test Telegram
                    </h3>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleTestTelegram}
                        disabled={testingTelegram}
                        variant="outline"
                        size="sm"
                        className="flex-1 border-blue-500/20 text-blue-400 hover:bg-blue-500/10 h-8 text-xs"
                      >
                        {testingTelegram ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Send className="w-3.5 h-3.5 mr-1.5" />}
                        Test Message
                      </Button>
                      <Button
                        onClick={handleSendReport}
                        disabled={sendingReport}
                        size="sm"
                        className="flex-1 bg-blue-500 hover:bg-blue-600 h-8 text-xs"
                      >
                        {sendingReport ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Mail className="w-3.5 h-3.5 mr-1.5" />}
                        Send Report
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* ─── FILTERS TAB ─── */}
          <TabsContent value="filters">
            <Card className="bg-[#111] border-white/[0.06]">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Product Filters</CardTitle>
                <CardDescription className="text-xs">AI uses these to filter products during scans</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Label className="text-xs">Maximum Source Cost</Label>
                    <span className="font-mono text-primary text-sm font-semibold">${filters.max_source_cost}</span>
                  </div>
                  <Slider
                    value={[filters.max_source_cost]}
                    onValueChange={([value]) => setFilters({ ...filters, max_source_cost: value })}
                    max={50} min={5} step={1}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Label className="text-xs">Minimum Sell Price</Label>
                    <span className="font-mono text-primary text-sm font-semibold">${filters.min_sell_price}</span>
                  </div>
                  <Slider
                    value={[filters.min_sell_price]}
                    onValueChange={([value]) => setFilters({ ...filters, min_sell_price: value })}
                    max={100} min={20} step={5}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Label className="text-xs">Minimum Margin %</Label>
                    <span className="font-mono text-primary text-sm font-semibold">{filters.min_margin_percent}%</span>
                  </div>
                  <Slider
                    value={[filters.min_margin_percent]}
                    onValueChange={([value]) => setFilters({ ...filters, min_margin_percent: value })}
                    max={90} min={30} step={5}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Label className="text-xs">Maximum FB Ads (Competition)</Label>
                    <span className="font-mono text-primary text-sm font-semibold">{filters.max_fb_ads}</span>
                  </div>
                  <Slider
                    value={[filters.max_fb_ads]}
                    onValueChange={([value]) => setFilters({ ...filters, max_fb_ads: value })}
                    max={100} min={10} step={5}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Label className="text-xs">Maximum Shipping Days</Label>
                    <span className="font-mono text-primary text-sm font-semibold">{filters.max_shipping_days}d</span>
                  </div>
                  <Slider
                    value={[filters.max_shipping_days]}
                    onValueChange={([value]) => setFilters({ ...filters, max_shipping_days: value })}
                    max={30} min={5} step={1}
                  />
                </div>

                <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                  <div>
                    <Label className="text-xs">Exclude Trademark Risk</Label>
                    <p className="text-[11px] text-muted-foreground mt-0.5">Filter out products with potential IP issues</p>
                  </div>
                  <Switch
                    checked={filters.exclude_trademark_risk}
                    onCheckedChange={(checked) => setFilters({ ...filters, exclude_trademark_risk: checked })}
                  />
                </div>

                <Button
                  onClick={handleSaveFilters}
                  disabled={saving}
                  className="w-full bg-gradient-to-r from-primary to-emerald-500 text-black font-bold hover:opacity-90 h-9 text-sm"
                >
                  {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                  Save Filters
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* ─── NOTIFICATIONS TAB ─── */}
          <TabsContent value="notifications">
            <div className="space-y-4">
              <Card className="bg-[#111] border-white/[0.06]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Notification Preferences</CardTitle>
                  <CardDescription className="text-xs">
                    {telegramReady
                      ? 'Notifications sent via your Telegram bot'
                      : 'Configure Telegram in API Keys tab to enable notifications'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  {/* Daily Report */}
                  <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Mail className="w-4 h-4 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Daily Report</p>
                        <p className="text-[11px] text-muted-foreground">Automatic report at 7:00 AM Eastern</p>
                      </div>
                    </div>
                    <Switch
                      checked={notifPrefs.daily_report}
                      onCheckedChange={(checked) => setNotifPrefs({ ...notifPrefs, daily_report: checked })}
                      disabled={!telegramReady}
                    />
                  </div>

                  {/* Scan Complete */}
                  <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Scan Complete</p>
                        <p className="text-[11px] text-muted-foreground">Notify when a scan finishes</p>
                      </div>
                    </div>
                    <Switch
                      checked={notifPrefs.scan_complete}
                      onCheckedChange={(checked) => setNotifPrefs({ ...notifPrefs, scan_complete: checked })}
                      disabled={!telegramReady}
                    />
                  </div>

                  {/* Competition Alerts */}
                  <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                        <AlertTriangle className="w-4 h-4 text-amber-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Competition Alerts</p>
                        <p className="text-[11px] text-muted-foreground">When competitors add new products</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {!isElite && (
                        <Badge className="text-[10px] bg-white/[0.04] text-white/40 border border-white/[0.06]">Elite</Badge>
                      )}
                      <Switch
                        checked={notifPrefs.competition_alerts}
                        onCheckedChange={(checked) => setNotifPrefs({ ...notifPrefs, competition_alerts: checked })}
                        disabled={!telegramReady || !isElite}
                      />
                    </div>
                  </div>

                  {/* Trend Spike */}
                  <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-violet-500/10 flex items-center justify-center">
                        <TrendingUp className="w-4 h-4 text-violet-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Trend Spike Alerts</p>
                        <p className="text-[11px] text-muted-foreground">When products surge in search interest</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {!isElite && (
                        <Badge className="text-[10px] bg-white/[0.04] text-white/40 border border-white/[0.06]">Elite</Badge>
                      )}
                      <Switch
                        checked={notifPrefs.trend_spike_alerts}
                        onCheckedChange={(checked) => setNotifPrefs({ ...notifPrefs, trend_spike_alerts: checked })}
                        disabled={!telegramReady || !isElite}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Save + Info */}
              {!telegramReady && (
                <div className="p-3 bg-blue-500/[0.06] border border-blue-500/15 rounded-xl">
                  <p className="text-xs text-blue-400">
                    Configure your Telegram Bot Token and Chat ID in the <strong>API Keys</strong> tab to enable notifications.
                  </p>
                </div>
              )}

              <Button
                onClick={handleSaveNotifs}
                disabled={savingNotifs}
                className="w-full bg-gradient-to-r from-primary to-emerald-500 text-black font-bold hover:opacity-90 h-9 text-sm"
              >
                {savingNotifs ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Preferences
              </Button>
            </div>
          </TabsContent>

          {/* ─── ACCOUNT TAB ─── */}
          <TabsContent value="account">
            <Card className="bg-[#111] border-white/[0.06]">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Account Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                  <div>
                    <p className="text-[11px] text-muted-foreground uppercase tracking-wider">Name</p>
                    <p className="text-sm font-medium mt-0.5">{user?.name}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                  <div>
                    <p className="text-[11px] text-muted-foreground uppercase tracking-wider">Email</p>
                    <p className="text-sm font-medium mt-0.5">{user?.email}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                  <div>
                    <p className="text-[11px] text-muted-foreground uppercase tracking-wider">Subscription</p>
                    <p className="text-sm font-medium mt-0.5 capitalize text-primary">{user?.subscription_tier || 'Free'}</p>
                  </div>
                  {user?.is_admin && (
                    <Badge className="bg-primary/15 text-primary text-[10px] border border-primary/20">Admin</Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
