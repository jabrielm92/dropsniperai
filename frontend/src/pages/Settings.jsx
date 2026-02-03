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
import { 
  ArrowLeft, Save, Filter, Bell, User, CreditCard, 
  Loader2, Zap, Send, Mail
} from 'lucide-react';
import { toast } from 'sonner';
import { getFilterSettings, updateFilterSettings } from '../lib/api';

export default function Settings() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
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

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await getFilterSettings();
      setFilters(response.data);
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

        <Tabs defaultValue="filters">
          <TabsList className="bg-[#121212] border border-white/5 mb-6">
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
                {/* Telegram Setup */}
                <div className="p-4 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                      <Send className="w-5 h-5 text-blue-500" />
                    </div>
                    <div>
                      <h3 className="font-medium">Telegram Bot</h3>
                      <p className="text-xs text-muted-foreground">Connect for instant alerts</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Input 
                      placeholder="Enter Telegram Chat ID" 
                      className="bg-[#0A0A0A] border-white/10"
                    />
                    <Button variant="outline" className="border-white/10">
                      Connect
                    </Button>
                  </div>
                </div>

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
