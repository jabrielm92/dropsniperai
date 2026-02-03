import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  ArrowLeft, Play, Loader2, RefreshCw, TrendingUp,
  Package, Search, Globe, Bot, AlertTriangle, Settings
} from 'lucide-react';
import { toast } from 'sonner';
import { runFullScan, scanSource, getScanStatus } from '../lib/api';

export default function Scanner() {
  const navigate = useNavigate();
  const [scanning, setScanning] = useState(false);
  const [scanningSource, setScanningSource] = useState(null);
  const [results, setResults] = useState(null);
  const [sourceResults, setSourceResults] = useState({});
  const [scanStatus, setScanStatus] = useState(null);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const response = await getScanStatus();
      setScanStatus(response.data);
    } catch (error) {
      console.error('Failed to get scan status:', error);
    }
  };

  const handleFullScan = async () => {
    if (!scanStatus?.ai_scanning_available) {
      toast.error('Add your OpenAI API key in Settings first');
      return;
    }
    
    setScanning(true);
    try {
      const response = await runFullScan();
      toast.success(`Scan complete! Found ${response.data.total_products} products`);
      setResults(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleSourceScan = async (source) => {
    if (!scanStatus?.ai_scanning_available) {
      toast.error('Add your OpenAI API key in Settings first');
      return;
    }
    
    setScanningSource(source);
    try {
      const response = await scanSource(source);
      setSourceResults(prev => ({
        ...prev,
        [source]: response.data
      }));
      toast.success(`Found ${response.data.count} products from ${source}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to scan ${source}`);
    } finally {
      setScanningSource(null);
    }
  };

  const sources = [
    { id: 'tiktok', name: 'TikTok', icon: <TrendingUp className="w-5 h-5" />, color: 'text-pink-500', bg: 'bg-pink-500/10', desc: 'Viral products with 10M+ views' },
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
        {/* Run Full Scan - Primary CTA */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Product Scanner</h1>
          <p className="text-muted-foreground mb-6">AI-powered scanning across multiple data sources</p>
          
          <Button 
            onClick={handleFullScan}
            disabled={scanning || !scanStatus?.ai_scanning_available}
            className="bg-primary text-black font-bold hover:bg-primary/90 px-12 py-6 text-lg"
            data-testid="full-scan-btn"
          >
            {scanning ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Scanning All Sources...
              </>
            ) : (
              <>
                <Bot className="w-5 h-5 mr-2" />
                Run Full AI Scan
              </>
            )}
          </Button>
        </div>

        {/* Status Banner */}
        {!scanStatus?.ai_scanning_available && (
          <Card className="mb-8 bg-yellow-500/10 border-yellow-500/30">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-500" />
                  <div>
                    <p className="font-medium text-yellow-500">OpenAI API Key Required</p>
                    <p className="text-sm text-muted-foreground">Add your key in Settings to enable AI scanning</p>
                  </div>
                </div>
                <Button 
                  variant="outline"
                  onClick={() => navigate('/settings')}
                  className="border-yellow-500/30 text-yellow-500"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Add API Key
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {results && (
          <Card className="bg-[#121212] border-white/5 mb-8">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Bot className="w-5 h-5 text-primary" />
                  Scan Results
                </span>
                <Badge className="bg-primary/20 text-primary font-mono">
                  {results.total_products} products found
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 max-h-[500px] overflow-y-auto custom-scrollbar">
                {(results.products || []).map((product, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium">{product.name}</p>
                        <Badge variant="outline" className="text-xs capitalize">{product.source}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{product.why_trending || product.category}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs">
                        {product.estimated_views && (
                          <span className="text-muted-foreground">{(product.estimated_views / 1000000).toFixed(1)}M views</span>
                        )}
                        {product.source_cost && (
                          <span className="text-muted-foreground">Cost: ${product.source_cost}</span>
                        )}
                        {product.recommended_price && (
                          <span className="text-primary">Sell: ${product.recommended_price}</span>
                        )}
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      {product.trend_score && (
                        <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                          product.trend_score >= 80 ? 'bg-primary/20 text-primary' :
                          product.trend_score >= 60 ? 'bg-yellow-500/20 text-yellow-500' :
                          'bg-white/10 text-muted-foreground'
                        }`}>
                          {product.trend_score}
                        </div>
                      )}
                      {product.margin_percent && (
                        <p className="text-xs text-muted-foreground mt-1">{product.margin_percent}% margin</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Individual Source Scans */}
        <div className="text-center mb-4">
          <p className="text-sm text-muted-foreground">Or scan individual sources:</p>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {sources.map((source) => (
            <Card key={source.id} className="bg-[#121212] border-white/5 hover:border-primary/30 transition-colors">
              <CardContent className="p-4 text-center">
                <div className={`w-12 h-12 rounded-lg ${source.bg} flex items-center justify-center mx-auto mb-3`}>
                  <span className={source.color}>{source.icon}</span>
                </div>
                <h3 className="font-bold mb-1">{source.name}</h3>
                <p className="text-xs text-muted-foreground mb-3">{source.desc}</p>
                
                {sourceResults[source.id] ? (
                  <p className="text-sm text-primary font-medium mb-2">{sourceResults[source.id].count} products</p>
                ) : null}
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSourceScan(source.id)}
                  disabled={scanningSource === source.id || !scanStatus?.ai_scanning_available}
                  className="w-full"
                >
                  {scanningSource === source.id ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <RefreshCw className="w-4 h-4 mr-1" />
                      Scan
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
