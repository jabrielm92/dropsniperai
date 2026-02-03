import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  ArrowLeft, Play, Loader2, RefreshCw, TrendingUp,
  Package, Search, BarChart3, Globe
} from 'lucide-react';
import { toast } from 'sonner';
import { runFullScan, scanSource } from '../lib/api';

export default function Scanner() {
  const navigate = useNavigate();
  const [scanning, setScanning] = useState(false);
  const [scanningSource, setScanningSource] = useState(null);
  const [results, setResults] = useState(null);
  const [sourceResults, setSourceResults] = useState({});

  const handleFullScan = async () => {
    setScanning(true);
    try {
      const response = await runFullScan();
      setResults(response.data);
      toast.success(`Scan complete! Found ${response.data.total_products} products`);
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
    { id: 'tiktok', name: 'TikTok', icon: <TrendingUp className="w-5 h-5" />, color: 'text-pink-500', bg: 'bg-pink-500/10' },
    { id: 'amazon', name: 'Amazon', icon: <Package className="w-5 h-5" />, color: 'text-orange-500', bg: 'bg-orange-500/10' },
    { id: 'aliexpress', name: 'AliExpress', icon: <Globe className="w-5 h-5" />, color: 'text-red-500', bg: 'bg-red-500/10' },
    { id: 'google_trends', name: 'Google Trends', icon: <Search className="w-5 h-5" />, color: 'text-blue-500', bg: 'bg-blue-500/10' },
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
                Scanning...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run Full Scan
              </>
            )}
          </Button>
        </div>

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
                <p className="text-sm text-muted-foreground">
                  {sourceResults[source.id] ? `${sourceResults[source.id].count} products` : 'Click to scan'}
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
                <span>Scan Results</span>
                <Badge className="bg-primary/20 text-primary font-mono">
                  {results.total_products} products found
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="all">
                <TabsList className="bg-[#0A0A0A] border border-white/5 mb-4">
                  <TabsTrigger value="all">All ({results.total_products})</TabsTrigger>
                  {Object.entries(results.source_stats).map(([source, count]) => (
                    <TabsTrigger key={source} value={source}>
                      {source} ({count})
                    </TabsTrigger>
                  ))}
                </TabsList>

                <TabsContent value="all">
                  <div className="grid gap-3 max-h-96 overflow-y-auto custom-scrollbar">
                    {results.products.map((product, i) => (
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

                {Object.keys(results.source_stats).map((source) => (
                  <TabsContent key={source} value={source}>
                    <div className="grid gap-3 max-h-96 overflow-y-auto custom-scrollbar">
                      {results.products
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
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
