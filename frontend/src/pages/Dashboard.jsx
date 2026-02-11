import { useState, useEffect, useCallback, useRef } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import SetupWizard from '../components/SetupWizard';
import {
  Zap, LogOut, Settings, TrendingUp, TrendingDown, Minus,
  Target, AlertTriangle, Rocket, BarChart3,
  Package, Filter, Clock, ChevronRight, RefreshCw, Search, Shield, Sparkles, Play, Loader2,
  X, CheckCircle2, XCircle, Radio, Eye, DollarSign, Crosshair, Activity,
  ArrowUpRight, Percent, Globe, ShoppingCart
} from 'lucide-react';
import { toast } from 'sonner';
import { getDailyReport, getTodayProducts, getStats, seedData, getUserKeys, runFullScan, getScanStatus, getFullScanStreamUrl } from '../lib/api';

// Source icon mapping
const SOURCE_ICONS = {
  tiktok: Globe,
  amazon: ShoppingCart,
  aliexpress: Package,
  google_trends: TrendingUp,
};

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const upgradeToastShown = useRef(false);
  const [report, setReport] = useState(null);
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [showWizard, setShowWizard] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState(null);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [scanSteps, setScanSteps] = useState([]);
  const [scanStats, setScanStats] = useState({ scraped: 0, enriched: 0, validated: 0, ready: 0 });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      await seedData();
      const [reportRes, productsRes, statsRes, keysRes, scanStatusRes] = await Promise.allSettled([
        getDailyReport(),
        getTodayProducts(),
        getStats(),
        getUserKeys(),
        getScanStatus()
      ]);
      if (reportRes.status === 'fulfilled') setReport(reportRes.value.data);
      if (productsRes.status === 'fulfilled') setProducts(productsRes.value.data.products || productsRes.value.data);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (scanStatusRes.status === 'fulfilled') setScanStatus(scanStatusRes.value.data);

      if (keysRes.status === 'fulfilled') {
        const wizardKey = `setupWizardDismissed_${user?.id}`;
        const wizardDismissed = localStorage.getItem(wizardKey);
        if (!wizardDismissed && !keysRes.value.data.has_openai_key && !keysRes.value.data.has_telegram_token) {
          setShowWizard(true);
        }
      }

      const failures = [reportRes, productsRes, statsRes, keysRes, scanStatusRes].filter(r => r.status === 'rejected');
      if (failures.length === 5) {
        toast.error('Failed to load dashboard data');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (searchParams.get('upgraded') === 'true' && !upgradeToastShown.current) {
      upgradeToastShown.current = true;
      toast.success('Subscription activated! Welcome to DropSniper AI.');
      setSearchParams({}, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  const handleRefresh = async () => {
    setSeeding(true);
    await fetchData();
    setSeeding(false);
    toast.success('Data refreshed!');
  };

  const handleRunScan = () => {
    if (!scanStatus?.ai_scanning_available) {
      toast.error('Add your OpenAI API key in Settings first');
      navigate('/settings');
      return;
    }

    setScanning(true);
    setScanSteps([]);
    setScanStats({ scraped: 0, enriched: 0, validated: 0, ready: 0 });
    // Do NOT auto-open modal - user clicks the activity button

    const url = getFullScanStreamUrl();
    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        setScanSteps(prev => {
          const existing = prev.findIndex(s => s.step === data.step);
          if (existing >= 0) {
            const updated = [...prev];
            updated[existing] = data;
            return updated;
          }
          return [...prev, { ...data, timestamp: new Date().toLocaleTimeString() }];
        });

        // Update running stats based on step data
        const sourceSteps = ['tiktok', 'amazon', 'aliexpress', 'google_trends'];
        setScanStats(prev => {
          const next = { ...prev };
          if (data.status === 'done' && data.count !== undefined) {
            if (sourceSteps.includes(data.step)) {
              // Source scan completed - add to scraped count
              next.scraped = prev.scraped + (data.count || 0);
            } else if (data.step === 'ai_enrichment') {
              next.enriched = data.count || prev.enriched;
              next.validated = data.count || prev.validated;
            }
          }
          if (data.step === 'complete') {
            next.ready = data.total_products || 0;
            next.enriched = next.enriched || data.total_products || 0;
            next.validated = next.validated || data.total_products || 0;
          }
          return next;
        });

        if (data.step === 'complete') {
          eventSource.close();
          setScanning(false);
          toast.success(`Scan complete! Found ${data.total_products} products`);
          fetchData();
        }
      } catch (e) {
        console.error('SSE parse error:', e);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setScanning(false);
      setScanSteps(prev => [...prev, { step: 'error', status: 'error', message: 'Connection lost. Scan may still be running.', timestamp: new Date().toLocaleTimeString() }]);
    };
  };

  const getGreeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getTrendIcon = (direction) => {
    if (direction === 'up') return <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />;
    if (direction === 'down') return <TrendingDown className="w-3.5 h-3.5 text-red-400" />;
    return <Minus className="w-3.5 h-3.5 text-amber-400" />;
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'from-emerald-500 to-emerald-600';
    if (score >= 70) return 'from-amber-500 to-amber-600';
    return 'from-red-500 to-red-600';
  };

  const getScoreBorder = (score) => {
    if (score >= 85) return 'border-emerald-500/30';
    if (score >= 70) return 'border-amber-500/30';
    return 'border-red-500/30';
  };

  const getSaturationStyle = (level) => {
    if (level === 'low') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    if (level === 'medium') return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    return 'bg-red-500/10 text-red-400 border-red-500/20';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <div className="text-center">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Zap className="w-8 h-8 text-primary" />
          </div>
          <p className="text-muted-foreground text-sm">Loading your command center...</p>
        </div>
      </div>
    );
  }

  const handleWizardComplete = () => {
    setShowWizard(false);
    localStorage.setItem(`setupWizardDismissed_${user?.id}`, 'true');
    fetchData();
  };

  const handleWizardSkip = () => {
    setShowWizard(false);
    localStorage.setItem(`setupWizardDismissed_${user?.id}`, 'true');
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {showWizard && (
        <SetupWizard onComplete={handleWizardComplete} onSkip={handleWizardSkip} />
      )}

      {/* ─── HEADER ─── */}
      <header className="border-b border-white/[0.06] bg-[#0A0A0A]/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 sm:px-6 h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2.5 shrink-0">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-emerald-600 flex items-center justify-center shadow-lg shadow-primary/20">
              <Zap className="w-5 h-5 text-black" />
            </div>
            <span className="font-bold text-lg hidden sm:block tracking-tight">DropSniper<span className="text-primary">AI</span></span>
          </Link>

          {/* Center: Run Scanner CTA */}
          <div className="flex items-center gap-2">
            <Button
              onClick={handleRunScan}
              disabled={scanning}
              className="bg-gradient-to-r from-primary to-emerald-500 text-black font-bold hover:opacity-90 transition-opacity px-5 h-9 text-sm shadow-lg shadow-primary/25"
              data-testid="run-scan-btn"
            >
              {scanning ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-1.5 fill-current" />
                  Run Scanner
                </>
              )}
            </Button>
          </div>

          {/* Right actions */}
          <div className="flex items-center gap-1">
            {/* Activity Button - always visible when scan has run */}
            {(scanSteps.length > 0 || scanning) && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowActivityModal(true)}
                className={`relative h-9 w-9 rounded-lg ${scanning ? 'text-primary bg-primary/10' : 'text-muted-foreground hover:text-primary'}`}
                title="Scanner Activity"
              >
                <Activity className={`w-[18px] h-[18px] ${scanning ? 'animate-pulse' : ''}`} />
                {scanning && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full animate-ping" />
                )}
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={handleRefresh}
              disabled={seeding}
              className="h-9 w-9 rounded-lg text-muted-foreground hover:text-white"
            >
              <RefreshCw className={`w-[18px] h-[18px] ${seeding ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                localStorage.removeItem(`setupWizardDismissed_${user?.id}`);
                setShowWizard(true);
              }}
              className="h-9 w-9 rounded-lg text-muted-foreground hover:text-primary"
              title="Setup Wizard"
              data-testid="setup-wizard-btn"
            >
              <Sparkles className="w-[18px] h-[18px]" />
            </Button>
            {user?.is_admin && (
              <Link to="/admin">
                <Button variant="ghost" size="icon" className="h-9 w-9 rounded-lg text-muted-foreground hover:text-primary" data-testid="admin-link">
                  <Shield className="w-[18px] h-[18px]" />
                </Button>
              </Link>
            )}
            <Link to="/settings">
              <Button variant="ghost" size="icon" className="h-9 w-9 rounded-lg text-muted-foreground hover:text-white">
                <Settings className="w-[18px] h-[18px]" />
              </Button>
            </Link>
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-primary/10 border border-primary/20 ml-1">
              <Zap className="w-3 h-3 text-primary" />
              <span className="text-xs font-semibold text-primary capitalize">{user?.subscription_tier || 'Free'}</span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="h-9 w-9 rounded-lg text-muted-foreground hover:text-red-400 ml-1"
              data-testid="logout-btn"
            >
              <LogOut className="w-[18px] h-[18px]" />
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-4 sm:px-6 py-6 space-y-6">

        {/* ─── WELCOME + QUICK ACTIONS ─── */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
              {getGreeting()}, <span className="bg-gradient-to-r from-primary to-emerald-400 bg-clip-text text-transparent">{user?.name?.split(' ')[0] || 'Scout'}</span>
            </h1>
            <p className="text-sm text-muted-foreground mt-1 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
          </div>

          {/* Quick Actions - moved to top */}
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/scanner')}
              className="h-8 border-white/[0.08] bg-white/[0.02] hover:bg-primary/10 hover:border-primary/30 hover:text-primary text-xs gap-1.5"
            >
              <Crosshair className="w-3.5 h-3.5" />
              Scanner
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/competitors')}
              className="h-8 border-white/[0.08] bg-white/[0.02] hover:bg-blue-500/10 hover:border-blue-500/30 hover:text-blue-400 text-xs gap-1.5"
            >
              <Eye className="w-3.5 h-3.5" />
              Competitors
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/saturation')}
              className="h-8 border-white/[0.08] bg-white/[0.02] hover:bg-amber-500/10 hover:border-amber-500/30 hover:text-amber-400 text-xs gap-1.5"
            >
              <BarChart3 className="w-3.5 h-3.5" />
              Saturation
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/settings')}
              className="h-8 border-white/[0.08] bg-white/[0.02] hover:bg-purple-500/10 hover:border-purple-500/30 hover:text-purple-400 text-xs gap-1.5"
            >
              <Filter className="w-3.5 h-3.5" />
              Filters
            </Button>
          </div>
        </div>

        {/* ─── STATS ROW ─── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <Card className="bg-[#111] border-white/[0.06] hover:border-primary/20 transition-colors group cursor-pointer" onClick={() => navigate('/products')}>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center group-hover:from-primary/30 transition-all">
                <Package className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{stats?.total_products || 0}</p>
                <p className="text-[11px] text-muted-foreground uppercase tracking-wider">Products</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#111] border-white/[0.06] hover:border-blue-500/20 transition-colors group cursor-pointer" onClick={() => navigate('/launch-kits')}>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-500/5 flex items-center justify-center group-hover:from-blue-500/30 transition-all">
                <Rocket className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{stats?.total_launch_kits || 0}</p>
                <p className="text-[11px] text-muted-foreground uppercase tracking-wider">Launch Kits</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#111] border-white/[0.06] hover:border-amber-500/20 transition-colors group cursor-pointer" onClick={() => navigate('/boards')}>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500/20 to-amber-500/5 flex items-center justify-center group-hover:from-amber-500/30 transition-all">
                <BarChart3 className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{stats?.total_boards || 0}</p>
                <p className="text-[11px] text-muted-foreground uppercase tracking-wider">Boards</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#111] border-white/[0.06] hover:border-purple-500/20 transition-colors group cursor-pointer" onClick={() => navigate('/settings')}>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-500/5 flex items-center justify-center group-hover:from-purple-500/30 transition-all">
                <Zap className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <p className="text-2xl font-bold capitalize">{stats?.subscription_tier || 'Free'}</p>
                <p className="text-[11px] text-muted-foreground uppercase tracking-wider">Plan</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* ─── DAILY INTELLIGENCE REPORT ─── */}
        {report && (
          <Card className="bg-gradient-to-r from-[#111] via-[#0f1a10] to-[#111] border-primary/10 overflow-hidden" data-testid="daily-report-card">
            <CardContent className="p-5">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center">
                  <Target className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1">
                  <h2 className="text-base font-bold">Daily Intelligence</h2>
                  <p className="text-xs text-muted-foreground">Overnight scan results</p>
                </div>
                {report.alerts && report.alerts.length > 0 && (
                  <Badge variant="outline" className="border-amber-500/30 text-amber-400 text-xs gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    {report.alerts.length} alert{report.alerts.length > 1 ? 's' : ''}
                  </Badge>
                )}
              </div>

              <div className="grid grid-cols-4 gap-3">
                <div className="bg-white/[0.03] rounded-xl p-3 text-center border border-white/[0.04]">
                  <p className="text-xl sm:text-2xl font-black tabular-nums">{report.products_scanned?.toLocaleString()}</p>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-0.5">Scanned</p>
                </div>
                <div className="bg-white/[0.03] rounded-xl p-3 text-center border border-white/[0.04]">
                  <p className="text-xl sm:text-2xl font-black tabular-nums">{report.passed_filters}</p>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-0.5">Filtered</p>
                </div>
                <div className="bg-white/[0.03] rounded-xl p-3 text-center border border-white/[0.04]">
                  <p className="text-xl sm:text-2xl font-black tabular-nums">{report.fully_validated}</p>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-0.5">Validated</p>
                </div>
                <div className="bg-primary/[0.08] rounded-xl p-3 text-center border border-primary/20">
                  <p className="text-xl sm:text-2xl font-black text-primary tabular-nums">{report.ready_to_launch}</p>
                  <p className="text-[10px] text-primary/70 uppercase tracking-wider mt-0.5">Ready</p>
                </div>
              </div>

              {report.alerts && report.alerts.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/[0.04] space-y-1.5">
                  {report.alerts.map((alert, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                      <span className="font-medium text-white">{alert.product}:</span>
                      <span className="text-muted-foreground">{alert.message}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* ─── TOP OPPORTUNITIES ─── */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold">Top Opportunities</h2>
              <p className="text-xs text-muted-foreground">Highest scoring products ready for launch</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="text-muted-foreground hover:text-primary gap-1 text-xs h-8"
              onClick={() => navigate('/products')}
            >
              View All
              <ChevronRight className="w-3.5 h-3.5" />
            </Button>
          </div>

          {products.length === 0 ? (
            <Card className="bg-[#111] border-white/[0.06] border-dashed">
              <CardContent className="py-12 text-center">
                <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <Target className="w-6 h-6 text-primary/50" />
                </div>
                <p className="font-medium mb-1">No products yet</p>
                <p className="text-sm text-muted-foreground mb-4">Run your first scan to discover trending products</p>
                <Button
                  onClick={handleRunScan}
                  disabled={scanning}
                  size="sm"
                  className="bg-primary text-black font-semibold hover:bg-primary/90"
                >
                  <Play className="w-3.5 h-3.5 mr-1.5 fill-current" />
                  Run First Scan
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {products.slice(0, 5).map((product, index) => (
                <Card
                  key={product.id || index}
                  className={`bg-[#111] border-white/[0.06] hover:${getScoreBorder(product.overall_score)} cursor-pointer overflow-hidden group transition-all duration-200 hover:shadow-lg hover:shadow-black/20 hover:-translate-y-0.5`}
                  onClick={() => navigate(`/product/${product.id}`)}
                  data-testid={`product-card-${index}`}
                >
                  {/* Image / Placeholder */}
                  <div className="relative h-40 overflow-hidden">
                    {product.image_url && !product.image_url.includes('google.com/search') ? (
                      <img
                        src={product.image_url}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                      />
                    ) : null}
                    <div
                      className="w-full h-full bg-gradient-to-br from-white/[0.04] to-white/[0.01] flex items-center justify-center"
                      style={{ display: (product.image_url && !product.image_url.includes('google.com/search')) ? 'none' : 'flex' }}
                    >
                      <div className="text-center px-6">
                        <Package className="w-7 h-7 mx-auto mb-2 text-white/20" />
                        <p className="text-xs text-white/40 line-clamp-2">{product.name}</p>
                      </div>
                    </div>

                    {/* Score badge */}
                    <div className="absolute top-2.5 right-2.5">
                      <div className={`bg-gradient-to-r ${getScoreColor(product.overall_score)} text-white font-mono font-bold text-sm px-2.5 py-0.5 rounded-lg shadow-lg`}>
                        {product.overall_score}
                      </div>
                    </div>

                    {/* Source pills */}
                    <div className="absolute bottom-2.5 left-2.5 flex gap-1.5">
                      {(product.source_platforms || (product.source ? [product.source] : [])).slice(0, 2).map((platform, i) => (
                        <span key={i} className="bg-black/70 backdrop-blur-md text-[10px] text-white/80 px-2 py-0.5 rounded-md font-medium">
                          {platform}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Content */}
                  <CardContent className="p-3.5 space-y-3">
                    <h3 className="font-semibold text-sm leading-tight line-clamp-1">{product.name}</h3>

                    {/* Pricing row */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-muted-foreground">Cost</span>
                        <span className="font-mono font-semibold text-sm">${(product.source_cost || 0).toFixed(2)}</span>
                      </div>
                      <ArrowUpRight className="w-3 h-3 text-muted-foreground" />
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono font-semibold text-sm text-primary">${(product.recommended_price || 0).toFixed(2)}</span>
                        <span className="text-xs text-muted-foreground">Sell</span>
                      </div>
                    </div>

                    {/* Bottom row */}
                    <div className="flex items-center justify-between pt-2 border-t border-white/[0.04]">
                      <div className="flex items-center gap-1">
                        {getTrendIcon(product.trend_direction)}
                        <span className={`font-mono text-xs ${product.trend_direction === 'up' ? 'text-emerald-400' : product.trend_direction === 'down' ? 'text-red-400' : 'text-amber-400'}`}>
                          {product.trend_percent > 0 ? '+' : ''}{product.trend_percent || 0}%
                        </span>
                      </div>
                      <Badge variant="outline" className={`${getSaturationStyle(product.saturation_level)} text-[10px] h-5 px-1.5 border`}>
                        {product.saturation_level || 'medium'}
                      </Badge>
                      <span className="text-[11px] text-muted-foreground font-mono">{product.margin_percent || 0}%</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* ─── SCANNER ACTIVITY MODAL ─── */}
      {showActivityModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm" onClick={(e) => { if (e.target === e.currentTarget && !scanning) setShowActivityModal(false); }}>
          <div className="bg-[#0f0f0f] border border-white/[0.08] rounded-2xl w-full max-w-xl mx-4 shadow-2xl shadow-black/50 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.06]">
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${scanning ? 'bg-primary/20' : 'bg-white/[0.06]'}`}>
                  <Activity className={`w-5 h-5 ${scanning ? 'text-primary animate-pulse' : 'text-white/60'}`} />
                </div>
                <h2 className="text-base font-bold">Scanner Activity</h2>
              </div>
              <div className="flex items-center gap-2">
                <Badge className={`text-xs font-semibold px-2.5 py-0.5 ${scanning ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-white/[0.06] text-white/60 border border-white/10'}`}>
                  {scanning ? 'Running' : 'Complete'}
                </Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowActivityModal(false)}
                  className="h-8 w-8 rounded-lg text-white/40 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-4 gap-2 px-5 py-4 border-b border-white/[0.06]">
              <div className="bg-[#161616] rounded-xl p-3 text-center border border-white/[0.04]">
                <Search className="w-4 h-4 mx-auto mb-1.5 text-cyan-400" />
                <p className="text-lg font-bold tabular-nums">{scanStats.scraped}</p>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Scraped</p>
              </div>
              <div className="bg-[#161616] rounded-xl p-3 text-center border border-white/[0.04]">
                <Sparkles className="w-4 h-4 mx-auto mb-1.5 text-violet-400" />
                <p className="text-lg font-bold tabular-nums">{scanStats.enriched}</p>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Enriched</p>
              </div>
              <div className="bg-[#161616] rounded-xl p-3 text-center border border-white/[0.04]">
                <CheckCircle2 className="w-4 h-4 mx-auto mb-1.5 text-emerald-400" />
                <p className="text-lg font-bold tabular-nums">{scanStats.validated}</p>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Validated</p>
              </div>
              <div className="bg-[#161616] rounded-xl p-3 text-center border border-primary/20">
                <Rocket className="w-4 h-4 mx-auto mb-1.5 text-primary" />
                <p className="text-lg font-bold tabular-nums text-primary">{scanStats.ready}</p>
                <p className="text-[10px] text-primary/60 uppercase tracking-wider">Ready</p>
              </div>
            </div>

            {/* Activity Log */}
            <div className="px-5 py-3 border-b border-white/[0.06]">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wider text-white/40">Activity Log</p>
                <p className="text-xs text-white/30">{scanSteps.length} events</p>
              </div>
            </div>

            <ScrollArea className="max-h-[45vh]">
              <div className="px-5 py-3 space-y-1">
                {scanSteps.length === 0 && scanning && (
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-primary/[0.04]">
                    <Loader2 className="w-4 h-4 text-primary animate-spin shrink-0" />
                    <p className="text-sm text-primary/80">Initializing scanner...</p>
                  </div>
                )}
                {scanSteps.map((step, i) => {
                  const SourceIcon = SOURCE_ICONS[step.source] || Target;
                  return (
                    <div
                      key={step.step + i}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                        step.status === 'scanning' ? 'bg-primary/[0.04]' :
                        step.status === 'error' ? 'bg-red-500/[0.04]' :
                        'hover:bg-white/[0.02]'
                      }`}
                    >
                      {/* Timestamp */}
                      <span className="text-[11px] text-white/25 font-mono tabular-nums shrink-0 w-16">
                        {step.timestamp || ''}
                      </span>

                      {/* Source icon */}
                      <div className={`w-6 h-6 rounded-md flex items-center justify-center shrink-0 ${
                        step.status === 'error' ? 'bg-red-500/10' : 'bg-white/[0.04]'
                      }`}>
                        <SourceIcon className="w-3 h-3 text-white/40" />
                      </div>

                      {/* Status icon */}
                      <div className="shrink-0">
                        {step.status === 'scanning' && <Loader2 className="w-3.5 h-3.5 text-primary animate-spin" />}
                        {step.status === 'done' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                        {step.status === 'error' && <XCircle className="w-3.5 h-3.5 text-red-400" />}
                      </div>

                      {/* Message */}
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm truncate ${
                          step.status === 'scanning' ? 'text-primary/80' :
                          step.status === 'error' ? 'text-red-400/80' :
                          'text-white/70'
                        }`}>
                          {step.message}
                        </p>
                      </div>

                      {/* Count badge */}
                      {step.status === 'done' && step.count !== undefined && (
                        <span className="text-xs font-mono text-white/30 bg-white/[0.04] px-1.5 py-0.5 rounded shrink-0">
                          {step.count}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </ScrollArea>

            {/* Footer */}
            {!scanning && scanSteps.length > 0 && (
              <div className="px-5 py-4 border-t border-white/[0.06]">
                <Button
                  onClick={() => { setShowActivityModal(false); navigate('/products'); }}
                  className="w-full bg-gradient-to-r from-primary to-emerald-500 text-black font-bold hover:opacity-90 transition-opacity h-10"
                >
                  View Results
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
