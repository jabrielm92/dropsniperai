import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import SetupWizard from '../components/SetupWizard';
import { 
  Zap, LogOut, Settings, TrendingUp, TrendingDown, Minus,
  Target, AlertTriangle, Rocket, BarChart3, 
  Package, Filter, Clock, ChevronRight, RefreshCw, Search, Shield, Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { getDailyReport, getTodayProducts, getStats, seedData, getUserKeys } from '../lib/api';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [showWizard, setShowWizard] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      await seedData();
      const [reportRes, productsRes, statsRes, keysRes] = await Promise.all([
        getDailyReport(),
        getTopProducts(8),
        getStats(),
        getUserKeys()
      ]);
      setReport(reportRes.data);
      setProducts(productsRes.data);
      setStats(statsRes.data);
      
      // Show wizard if user hasn't configured any keys and hasn't dismissed it
      const wizardDismissed = localStorage.getItem('setupWizardDismissed');
      if (!wizardDismissed && !keysRes.data.has_openai_key && !keysRes.data.has_telegram_token) {
        setShowWizard(true);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

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

  const getTrendIcon = (direction) => {
    if (direction === 'up') return <TrendingUp className="w-4 h-4 text-primary" />;
    if (direction === 'down') return <TrendingDown className="w-4 h-4 text-destructive" />;
    return <Minus className="w-4 h-4 text-yellow-500" />;
  };

  const getSaturationClass = (level) => {
    if (level === 'low') return 'bg-primary/15 text-primary';
    if (level === 'medium') return 'bg-yellow-500/15 text-yellow-500';
    return 'bg-destructive/15 text-destructive';
  };

  const getScoreClass = (score) => {
    if (score >= 85) return 'bg-primary/20 text-primary border-primary/30';
    if (score >= 70) return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30';
    return 'bg-destructive/20 text-destructive border-destructive/30';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Zap className="w-7 h-7 text-primary" />
          </div>
          <p className="text-muted-foreground">Loading your command center...</p>
        </div>
      </div>
    );
  }

  const handleWizardComplete = () => {
    setShowWizard(false);
    localStorage.setItem('setupWizardDismissed', 'true');
    fetchData(); // Refresh to get updated key status
  };

  const handleWizardSkip = () => {
    setShowWizard(false);
    localStorage.setItem('setupWizardDismissed', 'true');
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {/* Setup Wizard */}
      {showWizard && (
        <SetupWizard onComplete={handleWizardComplete} onSkip={handleWizardSkip} />
      )}
      
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0A0A0A]/80 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <span className="font-bold text-xl hidden sm:block">DropSniper AI</span>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={handleRefresh}
              disabled={seeding}
              className="text-muted-foreground hover:text-white"
            >
              <RefreshCw className={`w-5 h-5 ${seeding ? 'animate-spin' : ''}`} />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => {
                localStorage.removeItem('setupWizardDismissed');
                setShowWizard(true);
              }}
              className="text-muted-foreground hover:text-primary"
              title="Setup Wizard"
              data-testid="setup-wizard-btn"
            >
              <Sparkles className="w-5 h-5" />
            </Button>
            {user?.is_admin && (
              <Link to="/admin">
                <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary" data-testid="admin-link">
                  <Shield className="w-5 h-5" />
                </Button>
              </Link>
            )}
            <Link to="/settings">
              <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-white">
                <Settings className="w-5 h-5" />
              </Button>
            </Link>
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/20">
              <span className="text-sm font-medium text-primary capitalize">{user?.subscription_tier || 'Free'}</span>
            </div>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={handleLogout}
              className="text-muted-foreground hover:text-destructive"
              data-testid="logout-btn"
            >
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="p-6">
        {/* Welcome & Date */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Good morning, <span className="text-primary">{user?.name?.split(' ')[0] || 'Scout'}</span>
          </h1>
          <p className="text-muted-foreground flex items-center gap-2">
            <Clock className="w-4 h-4" />
            {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
          </p>
        </div>

        {/* Daily Report Summary */}
        {report && (
          <Card className="bg-gradient-to-r from-[#121212] to-[#0d1a0f] border-primary/20 mb-8" data-testid="daily-report-card">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                  <Target className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-xl font-bold">Daily Intelligence Report</h2>
                  <p className="text-sm text-muted-foreground">Overnight scan complete</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                <div>
                  <p className="text-3xl font-black text-white">{report.products_scanned.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">Products Scanned</p>
                </div>
                <div>
                  <p className="text-3xl font-black text-white">{report.passed_filters}</p>
                  <p className="text-sm text-muted-foreground">Passed Filters</p>
                </div>
                <div>
                  <p className="text-3xl font-black text-white">{report.fully_validated}</p>
                  <p className="text-sm text-muted-foreground">Fully Validated</p>
                </div>
                <div>
                  <p className="text-3xl font-black text-primary">{report.ready_to_launch}</p>
                  <p className="text-sm text-muted-foreground">Ready to Launch</p>
                </div>
              </div>

              {report.alerts && report.alerts.length > 0 && (
                <div className="border-t border-white/5 pt-4">
                  <p className="text-sm font-medium mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    Alerts on Your Products
                  </p>
                  <div className="space-y-2">
                    {report.alerts.map((alert, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span className="font-medium text-white">{alert.product}:</span>
                        <span>{alert.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-[#121212] border-white/5">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Package className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.total_products || 0}</p>
                <p className="text-xs text-muted-foreground">Products</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#121212] border-white/5">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Rocket className="w-6 h-6 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.total_launch_kits || 0}</p>
                <p className="text-xs text-muted-foreground">Launch Kits</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#121212] border-white/5">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-yellow-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.total_boards || 0}</p>
                <p className="text-xs text-muted-foreground">Boards</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-[#121212] border-white/5">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <Filter className="w-6 h-6 text-purple-500" />
              </div>
              <div>
                <p className="text-2xl font-bold capitalize">{stats?.subscription_tier || 'Free'}</p>
                <p className="text-xs text-muted-foreground">Plan</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Top Opportunities */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold">Top Opportunities</h2>
              <p className="text-muted-foreground">Highest scoring products ready for launch</p>
            </div>
            <Button variant="outline" className="border-white/10 hover:border-primary/30">
              View All
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map((product, index) => (
              <Card 
                key={product.id}
                className="bg-[#121212] border-white/5 hover:border-primary/30 cursor-pointer overflow-hidden group"
                onClick={() => navigate(`/product/${product.id}`)}
                data-testid={`product-card-${index}`}
              >
                <div className="relative">
                  <img 
                    src={product.image_url} 
                    alt={product.name}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 right-3">
                    <Badge className={`${getScoreClass(product.overall_score)} font-mono text-lg px-3 py-1 border`}>
                      {product.overall_score}
                    </Badge>
                  </div>
                  <div className="absolute bottom-3 left-3 flex gap-2">
                    {product.source_platforms?.slice(0, 2).map((platform, i) => (
                      <Badge key={i} variant="secondary" className="bg-black/60 backdrop-blur text-xs">
                        {platform}
                      </Badge>
                    ))}
                  </div>
                </div>
                <CardContent className="p-4">
                  <h3 className="font-bold text-lg mb-2 line-clamp-1">{product.name}</h3>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Source Cost</p>
                      <p className="font-mono font-bold">${product.source_cost.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Sell Price</p>
                      <p className="font-mono font-bold text-primary">${product.recommended_price.toFixed(2)}</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      {getTrendIcon(product.trend_direction)}
                      <span className={`font-mono text-sm ${product.trend_direction === 'up' ? 'text-primary' : product.trend_direction === 'down' ? 'text-destructive' : 'text-yellow-500'}`}>
                        {product.trend_percent > 0 ? '+' : ''}{product.trend_percent}%
                      </span>
                    </div>
                    <Badge className={`${getSaturationClass(product.saturation_level)} text-xs`}>
                      {product.saturation_level}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>{product.active_fb_ads} FB Ads</span>
                    <span>{product.margin_percent}% margin</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <Card className="bg-[#121212] border-white/5">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Button 
                variant="outline" 
                className="h-auto py-4 px-6 justify-start border-white/10 hover:border-primary/30 hover:bg-primary/5"
                onClick={() => navigate('/scanner')}
              >
                <Target className="w-5 h-5 mr-3 text-primary" />
                <div className="text-left">
                  <p className="font-medium">Run Scanner</p>
                  <p className="text-xs text-muted-foreground">Scan all sources</p>
                </div>
              </Button>
              <Button 
                variant="outline" 
                className="h-auto py-4 px-6 justify-start border-white/10 hover:border-blue-500/30 hover:bg-blue-500/5"
                onClick={() => navigate('/competitors')}
              >
                <Search className="w-5 h-5 mr-3 text-blue-500" />
                <div className="text-left">
                  <p className="font-medium">Competitor Spy</p>
                  <p className="text-xs text-muted-foreground">Monitor stores</p>
                </div>
              </Button>
              <Button 
                variant="outline" 
                className="h-auto py-4 px-6 justify-start border-white/10 hover:border-yellow-500/30 hover:bg-yellow-500/5"
                onClick={() => navigate('/saturation')}
              >
                <BarChart3 className="w-5 h-5 mr-3 text-yellow-500" />
                <div className="text-left">
                  <p className="font-medium">Saturation Radar</p>
                  <p className="text-xs text-muted-foreground">Find opportunities</p>
                </div>
              </Button>
              <Button 
                variant="outline" 
                className="h-auto py-4 px-6 justify-start border-white/10 hover:border-purple-500/30 hover:bg-purple-500/5"
                onClick={() => navigate('/settings')}
              >
                <Filter className="w-5 h-5 mr-3 text-purple-500" />
                <div className="text-left">
                  <p className="font-medium">Configure Filters</p>
                  <p className="text-xs text-muted-foreground">Customize criteria</p>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
