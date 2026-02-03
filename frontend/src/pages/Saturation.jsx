import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { 
  ArrowLeft, AlertTriangle, TrendingUp, TrendingDown, Minus,
  Target, BarChart3, Loader2, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { getSaturationOverview, getNicheSaturation } from '../lib/api';

export default function Saturation() {
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [niches, setNiches] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [overviewRes, nichesRes] = await Promise.all([
        getSaturationOverview(),
        getNicheSaturation()
      ]);
      setOverview(overviewRes.data);
      setNiches(nichesRes.data);
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to load saturation data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getSaturationColor = (score) => {
    if (score < 30) return 'text-primary';
    if (score < 60) return 'text-yellow-500';
    return 'text-destructive';
  };

  const getSaturationBg = (score) => {
    if (score < 30) return 'bg-primary';
    if (score < 60) return 'bg-yellow-500';
    return 'bg-destructive';
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
          <Button 
            variant="outline" 
            className="border-white/10"
            onClick={() => { setLoading(true); fetchData(); }}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Saturation Radar</h1>
          <p className="text-muted-foreground">Track market saturation and find untapped opportunities</p>
        </div>

        {/* Overview Stats */}
        {overview && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-primary/20 to-primary/5 border-primary/30">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-primary/20 flex items-center justify-center">
                    <TrendingUp className="w-7 h-7 text-primary" />
                  </div>
                  <div>
                    <p className="text-4xl font-black text-primary">{overview.stats.low_competition}</p>
                    <p className="text-sm text-muted-foreground">Low Competition</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-yellow-500/20 to-yellow-500/5 border-yellow-500/30">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-yellow-500/20 flex items-center justify-center">
                    <Minus className="w-7 h-7 text-yellow-500" />
                  </div>
                  <div>
                    <p className="text-4xl font-black text-yellow-500">{overview.stats.medium_competition}</p>
                    <p className="text-sm text-muted-foreground">Medium Competition</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-destructive/20 to-destructive/5 border-destructive/30">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-destructive/20 flex items-center justify-center">
                    <AlertTriangle className="w-7 h-7 text-destructive" />
                  </div>
                  <div>
                    <p className="text-4xl font-black text-destructive">{overview.stats.high_competition}</p>
                    <p className="text-sm text-muted-foreground">High Competition</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Niche Saturation */}
          <Card className="bg-[#121212] border-white/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-500" />
                Niche Saturation Levels
              </CardTitle>
            </CardHeader>
            <CardContent>
              {niches && Object.entries(niches).length > 0 ? (
                <div className="space-y-6">
                  {Object.entries(niches)
                    .sort(([,a], [,b]) => a.saturation_score - b.saturation_score)
                    .map(([category, data]) => (
                    <div key={category}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{category}</span>
                        <span className={`font-mono ${getSaturationColor(data.saturation_score)}`}>
                          {data.saturation_score}%
                        </span>
                      </div>
                      <Progress 
                        value={data.saturation_score} 
                        className="h-3"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>{data.total_products} products</span>
                        <span>{data.avg_fb_ads} avg FB ads</span>
                        <span>{data.avg_stores} avg stores</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No niche data available</p>
              )}
            </CardContent>
          </Card>

          {/* Products by Saturation */}
          <div className="space-y-6">
            {/* Low Competition - Opportunities */}
            <Card className="bg-[#121212] border-primary/20">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-primary" />
                  Low Competition Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent>
                {overview?.overview.low.length > 0 ? (
                  <div className="space-y-2">
                    {overview.overview.low.slice(0, 5).map((product) => (
                      <div 
                        key={product.id}
                        className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-primary/10 cursor-pointer transition-colors"
                        onClick={() => navigate(`/product/${product.id}`)}
                      >
                        <div>
                          <p className="font-medium">{product.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {product.fb_ads} FB ads • {product.shopify_stores} stores
                          </p>
                        </div>
                        <Badge className="bg-primary/20 text-primary">
                          {product.trend_direction === 'up' ? <TrendingUp className="w-3 h-3" /> : 
                           product.trend_direction === 'down' ? <TrendingDown className="w-3 h-3" /> : 
                           <Minus className="w-3 h-3" />}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">No low competition products</p>
                )}
              </CardContent>
            </Card>

            {/* High Competition - Avoid */}
            <Card className="bg-[#121212] border-destructive/20">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-destructive" />
                  Saturated Markets - Proceed with Caution
                </CardTitle>
              </CardHeader>
              <CardContent>
                {overview?.overview.high.length > 0 ? (
                  <div className="space-y-2">
                    {overview.overview.high.slice(0, 5).map((product) => (
                      <div 
                        key={product.id}
                        className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-destructive/10 cursor-pointer transition-colors"
                        onClick={() => navigate(`/product/${product.id}`)}
                      >
                        <div>
                          <p className="font-medium">{product.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {product.fb_ads} FB ads • {product.shopify_stores} stores
                          </p>
                        </div>
                        <Badge className="bg-destructive/20 text-destructive">
                          <AlertTriangle className="w-3 h-3" />
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">No highly saturated products</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
