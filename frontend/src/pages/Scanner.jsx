import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Switch } from '../components/ui/switch';
import { 
  ArrowLeft, Play, Loader2, RefreshCw, TrendingUp,
  Package, Search, BarChart3, Globe, Bot, Zap, AlertTriangle, Settings
} from 'lucide-react';
import { toast } from 'sonner';
import { runFullScan, scanSource, getScanStatus } from '../lib/api';

export default function Scanner() {
  const navigate = useNavigate();
  const [scanning, setScanning] = useState(false);
  const [scanningSource, setScanningSource] = useState(null);
  const [results, setResults] = useState(null);
  const [sourceResults, setSourceResults] = useState({});
  const [useAiBrowser, setUseAiBrowser] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);

  useEffect(() => {
    checkAiStatus();
  }, []);

  const checkAiStatus = async () => {
    try {
      const response = await getScanStatus();
      setAiStatus(response.data);
    } catch (error) {
      console.error('Failed to get AI status:', error);
    }
  };

  const handleFullScan = async () => {
    setScanning(true);
    try {
      const response = await runFullScan();
      const mode = response.data.scan_mode;
      if (mode === 'ai_powered') {
        toast.success('AI-powered scan complete!');
      } else {
        toast.success(`Scan complete! Found ${response.data.total_products} products (sample data)`);
      }
      setResults(response.data);
    } catch (error) {
      toast.error('Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleSourceScan = async (source) => {
    setScanningSource(source);
    try {
      const response = await scanSource(source);
      setSourceResults(prev => ({
        ...prev,
        [source]: response.data
      }));
      toast.success(`Found ${response.data.count} products from ${source}`);
    } catch (error) {
      toast.error(`Failed to scan ${source}`);
    } finally {
      setScanningSource(null);
    }
  };

  const sources = [
    { id: 'tiktok', name: 'TikTok', icon: <TrendingUp className="w-5 h-5" />, color: 'text-pink-500', bg: 'bg-pink-500/10', desc: 'Viral hashtags 10M+ views' },
    { id: 'amazon', name: 'Amazon', icon: <Package className="w-5 h-5" />, color: 'text-orange-500', bg: 'bg-orange-500/10', desc: 'Movers & Shakers' },
    { id: 'aliexpress', name: 'AliExpress', icon: <Globe className="w-5 h-5" />, color: 'text-red-500', bg: 'bg-red-500/10', desc: 'Hot products & pricing' },
    { id: 'google_trends', name: 'Google Trends', icon: <Search className="w-5 h-5" />, color: 'text-blue-500', bg: 'bg-blue-500/10', desc: 'Rising search terms' },
  ];

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

      <main className="p-6 max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Product Scanner</h1>
            <p className="text-muted-foreground">Scan multiple data sources for trending products</p>
          </div>
          <Button 
            onClick={handleFullScan}
            disabled={scanning}
            className="bg-primary text-black font-bold hover:bg-primary/90 px-8"
            data-testid="full-scan-btn"
          >
            {scanning ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {useAiBrowser ? 'AI Browsing...' : 'Scanning...'}
              </>
            ) : (
              <>
                {useAiBrowser ? <Bot className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                {useAiBrowser ? 'Run AI Browser Scan' : 'Run Full Scan'}
              </>
            )}
          </Button>
        </div>

        {/* AI Browser Mode Toggle */}
        <Card className={`mb-8 ${useAiBrowser ? 'bg-primary/10 border-primary/30' : 'bg-[#121212] border-white/5'}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl ${useAiBrowser ? 'bg-primary/20' : 'bg-white/5'} flex items-center justify-center`}>
                  <Bot className={`w-6 h-6 ${useAiBrowser ? 'text-primary' : 'text-muted-foreground'}`} />
                </div>
                <div>
                  <h3 className="font-bold flex items-center gap-2">
                    AI Browser Mode
                    {aiStatus?.is_ready ? (
                      <Badge className="bg-primary/20 text-primary">Ready</Badge>
                    ) : (
                      <Badge variant="outline" className="text-muted-foreground">Not Configured</Badge>
                    )}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {aiStatus?.is_ready 
                      ? 'AI will autonomously browse websites like a human (takes 5-10 min per source)'
                      : 'Add OPENAI_API_KEY to enable autonomous browsing'}
                  </p>
                </div>
              </div>
              <Switch
                checked={useAiBrowser}
                onCheckedChange={setUseAiBrowser}
                disabled={!aiStatus?.is_ready}
              />
            </div>
            
            {!aiStatus?.is_ready && (
              <div className="mt-4 p-3 bg-yellow-500/10 rounded-lg border border-yellow-500/20 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-yellow-500 font-medium">OpenAI API Key Required</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Go to Settings → Integrations to add your OpenAI API key and enable AI Browser mode.
                    This mode uses GPT-4 to control a real browser and extract data from websites.
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Source Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {sources.map((source) => (
            <Card key={source.id} className="bg-[#121212] border-white/5 hover:border-primary/30 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-10 h-10 rounded-lg ${source.bg} flex items-center justify-center`}>
                    <span className={source.color}>{source.icon}</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleSourceScan(source.id)}
                    disabled={scanningSource === source.id}
                  >
                    <RefreshCw className={`w-4 h-4 ${scanningSource === source.id ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
                <h3 className="font-bold">{source.name}</h3>
                <p className="text-xs text-muted-foreground mb-2">{source.desc}</p>
                <p className="text-sm text-muted-foreground">
                  {sourceResults[source.id] ? (
                    <span className="text-primary">{sourceResults[source.id].count} products</span>
                  ) : (
                    'Click to scan'
                  )}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Results */}
        {results && (
          <Card className="bg-[#121212] border-white/5">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  {results.scan_type === 'ai_browser_full' && <Bot className="w-5 h-5 text-primary" />}
                  Scan Results
                </span>
                <Badge className="bg-primary/20 text-primary font-mono">
                  {results.total_products || Object.keys(results.results || {}).length} {results.scan_type === 'ai_browser_full' ? 'sources scanned' : 'products found'}
                </Badge>
              </CardTitle>
              {results.fallback && (
                <CardDescription className="text-yellow-500">
                  Using mock data (AI Browser not configured)
                </CardDescription>
              )}
            </CardHeader>
            <CardContent>
              {results.scan_type === 'ai_browser_full' ? (
                // AI Browser Results
                <div className="space-y-4">
                  {Object.entries(results.results || {}).map(([source, data]) => (
                    <div key={source} className="p-4 bg-white/5 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-bold capitalize">{source.replace('_', ' ')}</h4>
                        {data.success ? (
                          <Badge className="bg-primary/20 text-primary">Success</Badge>
                        ) : (
                          <Badge variant="destructive">Error</Badge>
                        )}
                      </div>
                      {data.raw_result && (
                        <pre className="text-xs text-muted-foreground overflow-x-auto max-h-32 custom-scrollbar">
                          {data.raw_result.substring(0, 500)}...
                        </pre>
                      )}
                      {data.error && (
                        <p className="text-sm text-destructive">{data.error}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                // Mock Scanner Results
                <Tabs defaultValue="all">
                  <TabsList className="bg-[#0A0A0A] border border-white/5 mb-4">
                    <TabsTrigger value="all">All ({results.total_products})</TabsTrigger>
                    {Object.entries(results.source_stats || {}).map(([source, count]) => (
                      <TabsTrigger key={source} value={source}>
                        {source} ({count})
                      </TabsTrigger>
                    ))}
                  </TabsList>

                  <TabsContent value="all">
                    <div className="grid gap-3 max-h-96 overflow-y-auto custom-scrollbar">
                      {(results.products || []).map((product, i) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                          <div>
                            <p className="font-medium">{product.name}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="outline" className="text-xs">{product.source}</Badge>
                              {product.trend_data?.growth_percent && (
                                <span className="text-xs text-primary">+{product.trend_data.growth_percent}%</span>
                              )}
                              {product.trend_data?.views && (
                                <span className="text-xs text-muted-foreground">{(product.trend_data.views / 1000000).toFixed(1)}M views</span>
                              )}
                              {product.trend_data?.orders_30d && (
                                <span className="text-xs text-muted-foreground">{product.trend_data.orders_30d.toLocaleString()} orders</span>
                              )}
                            </div>
                          </div>
                          {product.trend_data?.price && (
                            <span className="font-mono text-primary">${product.trend_data.price}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </TabsContent>

                  {Object.keys(results.source_stats || {}).map((source) => (
                    <TabsContent key={source} value={source}>
                      <div className="grid gap-3 max-h-96 overflow-y-auto custom-scrollbar">
                        {(results.products || [])
                          .filter(p => p.source === source)
                          .map((product, i) => (
                            <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                              <div>
                                <p className="font-medium">{product.name}</p>
                                <div className="flex items-center gap-2 mt-1">
                                  {product.trend_data?.growth_percent && (
                                    <span className="text-xs text-primary">+{product.trend_data.growth_percent}%</span>
                                  )}
                                  {product.trend_data?.views && (
                                    <span className="text-xs text-muted-foreground">{(product.trend_data.views / 1000000).toFixed(1)}M views</span>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                      </div>
                    </TabsContent>
                  ))}
                </Tabs>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
