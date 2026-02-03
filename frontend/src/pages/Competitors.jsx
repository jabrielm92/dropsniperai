import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { 
  ArrowLeft, Plus, Trash2, RefreshCw, Eye, Bell, ExternalLink,
  TrendingUp, Package, DollarSign, AlertTriangle, Loader2, Search
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  getCompetitors, addCompetitor, getCompetitor, scanCompetitor, 
  removeCompetitor, getCompetitorAlerts 
} from '../lib/api';

export default function Competitors() {
  const navigate = useNavigate();
  const [competitors, setCompetitors] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [scanning, setScanningId] = useState(null);
  const [newUrl, setNewUrl] = useState('');
  const [selectedCompetitor, setSelectedCompetitor] = useState(null);
  const [competitorDetails, setCompetitorDetails] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [compRes, alertRes] = await Promise.all([
        getCompetitors(),
        getCompetitorAlerts()
      ]);
      setCompetitors(compRes.data);
      setAlerts(alertRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAddCompetitor = async (e) => {
    e.preventDefault();
    if (!newUrl.trim()) return;
    
    setAdding(true);
    try {
      const response = await addCompetitor(newUrl);
      toast.success(`Now monitoring ${response.data.store_data.store_name}`);
      setNewUrl('');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add competitor');
    } finally {
      setAdding(false);
    }
  };

  const handleScan = async (competitorId) => {
    setScanningId(competitorId);
    try {
      const response = await scanCompetitor(competitorId);
      if (response.data.changes.has_changes) {
        toast.success(`Found ${response.data.changes.added_count} new product(s)!`);
      } else {
        toast.info('No new products detected');
      }
      fetchData();
    } catch (error) {
      toast.error('Scan failed');
    } finally {
      setScanningId(null);
    }
  };

  const handleRemove = async (competitorId) => {
    try {
      await removeCompetitor(competitorId);
      toast.success('Competitor removed');
      fetchData();
      setSelectedCompetitor(null);
    } catch (error) {
      toast.error('Failed to remove');
    }
  };

  const handleViewDetails = async (competitor) => {
    setSelectedCompetitor(competitor);
    try {
      const response = await getCompetitor(competitor.id);
      setCompetitorDetails(response.data);
    } catch (error) {
      toast.error('Failed to load details');
    }
  };

  const unreadAlerts = alerts.filter(a => !a.is_read);

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
          {unreadAlerts.length > 0 && (
            <Badge className="bg-destructive text-white">
              {unreadAlerts.length} new alert(s)
            </Badge>
          )}
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Competitor Spy</h1>
            <p className="text-muted-foreground">Monitor competitor stores and get alerts when they add new products</p>
          </div>
        </div>

        {/* Add Competitor Form */}
        <Card className="bg-[#121212] border-white/5 mb-8">
          <CardContent className="p-6">
            <form onSubmit={handleAddCompetitor} className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Enter competitor store URL (e.g., https://coolstore.myshopify.com)"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  className="bg-[#0A0A0A] border-white/10 h-12"
                  data-testid="competitor-url-input"
                />
              </div>
              <Button 
                type="submit" 
                disabled={adding || !newUrl.trim()}
                className="bg-primary text-black font-bold hover:bg-primary/90 h-12 px-6"
                data-testid="add-competitor-btn"
              >
                {adding ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Competitor
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Competitors List */}
          <div className="lg:col-span-2">
            <h2 className="text-xl font-bold mb-4">Monitored Stores ({competitors.length})</h2>
            
            {competitors.length === 0 ? (
              <Card className="bg-[#121212] border-white/5">
                <CardContent className="p-12 text-center">
                  <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No competitors added yet</h3>
                  <p className="text-muted-foreground">Add your first competitor store to start monitoring</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {competitors.map((competitor) => (
                  <Card 
                    key={competitor.id}
                    className={`bg-[#121212] border-white/5 hover:border-primary/30 cursor-pointer transition-colors ${selectedCompetitor?.id === competitor.id ? 'border-primary/50' : ''}`}
                    onClick={() => handleViewDetails(competitor)}
                    data-testid={`competitor-card-${competitor.id}`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center">
                            <Package className="w-6 h-6 text-blue-500" />
                          </div>
                          <div>
                            <h3 className="font-bold">{competitor.store_name}</h3>
                            <p className="text-sm text-muted-foreground truncate max-w-xs">
                              {competitor.store_url}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          {competitor.new_products_count > 0 && (
                            <Badge className="bg-primary/20 text-primary">
                              {competitor.new_products_count} new
                            </Badge>
                          )}
                          <span className="text-sm text-muted-foreground">
                            {competitor.products_snapshot?.length || 0} products
                          </span>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleScan(competitor.id);
                            }}
                            disabled={scanning === competitor.id}
                          >
                            <RefreshCw className={`w-4 h-4 ${scanning === competitor.id ? 'animate-spin' : ''}`} />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-destructive hover:text-destructive"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRemove(competitor.id);
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar - Details or Alerts */}
          <div>
            {selectedCompetitor && competitorDetails ? (
              <Card className="bg-[#121212] border-white/5 sticky top-24">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{competitorDetails.competitor.store_name}</span>
                    <a 
                      href={competitorDetails.competitor.store_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary/80"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total Products</span>
                      <span className="font-mono">{competitorDetails.total_products}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Last Scanned</span>
                      <span className="font-mono text-xs">
                        {new Date(competitorDetails.competitor.last_scanned).toLocaleDateString()}
                      </span>
                    </div>
                    
                    <div className="border-t border-white/5 pt-4">
                      <h4 className="font-medium mb-3">Products</h4>
                      <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                        {competitorDetails.products.map((product, i) => (
                          <div key={i} className="flex justify-between items-center p-2 bg-white/5 rounded-lg">
                            <span className="text-sm truncate flex-1">{product.name}</span>
                            <span className="font-mono text-primary">${product.price}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="w-5 h-5 text-yellow-500" />
                    Recent Alerts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {alerts.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">No alerts yet</p>
                  ) : (
                    <div className="space-y-3">
                      {alerts.slice(0, 5).map((alert) => (
                        <div 
                          key={alert.id} 
                          className={`p-3 rounded-lg ${alert.is_read ? 'bg-white/5' : 'bg-primary/10 border border-primary/20'}`}
                        >
                          <div className="flex items-start gap-2">
                            <AlertTriangle className={`w-4 h-4 mt-0.5 ${alert.is_read ? 'text-muted-foreground' : 'text-primary'}`} />
                            <div>
                              <p className="text-sm font-medium">{alert.title}</p>
                              <p className="text-xs text-muted-foreground">{alert.message}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
