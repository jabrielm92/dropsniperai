import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import { 
  ArrowLeft, TrendingUp, TrendingDown, Minus, DollarSign, 
  Rocket, Package, Truck, Star, AlertTriangle, Check, X,
  ExternalLink, Copy, Loader2, Zap
} from 'lucide-react';
import { toast } from 'sonner';
import { getProduct, getProductBrief, generateLaunchKit } from '../lib/api';

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [brief, setBrief] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchProduct = useCallback(async () => {
    try {
      const [productRes, briefRes] = await Promise.all([
        getProduct(id),
        getProductBrief(id)
      ]);
      setProduct(productRes.data);
      setBrief(briefRes.data);
    } catch (error) {
      toast.error('Failed to load product');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    fetchProduct();
  }, [fetchProduct]);

  const handleGenerateLaunchKit = async () => {
    setGenerating(true);
    try {
      const response = await generateLaunchKit(id);
      toast.success('Launch kit generated!');
      navigate(`/launch-kit/${response.data.id}`);
    } catch (error) {
      toast.error('Failed to generate launch kit');
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <div className="animate-pulse text-primary">Loading product...</div>
      </div>
    );
  }

  if (!product) return null;

  const getTrendIcon = () => {
    if (product.trend_direction === 'up') return <TrendingUp className="w-5 h-5 text-primary" />;
    if (product.trend_direction === 'down') return <TrendingDown className="w-5 h-5 text-destructive" />;
    return <Minus className="w-5 h-5 text-yellow-500" />;
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-primary';
    if (score >= 70) return 'text-yellow-500';
    return 'text-destructive';
  };

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
            onClick={handleGenerateLaunchKit}
            disabled={generating}
            className="bg-primary text-black font-bold hover:bg-primary/90 btn-primary-glow"
            data-testid="generate-launch-kit-btn"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Rocket className="w-4 h-4 mr-2" />
                Generate Launch Kit
              </>
            )}
          </Button>
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto">
        {/* Product Header */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Image */}
          <div className="relative rounded-xl overflow-hidden bg-[#121212]">
            <img 
              src={product.image_url} 
              alt={product.name}
              className="w-full aspect-square object-cover"
            />
            <div className="absolute top-4 right-4">
              <Badge className={`${product.overall_score >= 85 ? 'score-high' : product.overall_score >= 70 ? 'score-medium' : 'score-low'} text-2xl font-mono px-4 py-2`}>
                {product.overall_score}
              </Badge>
            </div>
          </div>

          {/* Info */}
          <div>
            <div className="flex flex-wrap gap-2 mb-4">
              {product.source_platforms?.map((platform, i) => (
                <Badge key={i} variant="secondary" className="bg-secondary/10 text-secondary">
                  {platform}
                </Badge>
              ))}
              <Badge className={product.saturation_level === 'low' ? 'saturation-low' : product.saturation_level === 'medium' ? 'saturation-medium' : 'saturation-high'}>
                {product.saturation_level} competition
              </Badge>
            </div>

            <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
            <p className="text-muted-foreground mb-6">{product.description}</p>

            {/* Price Box */}
            <Card className="bg-[#121212] border-primary/20 mb-6">
              <CardContent className="p-6">
                <div className="grid grid-cols-3 gap-6 text-center">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Source Cost</p>
                    <p className="text-2xl font-mono font-bold">${product.source_cost.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Sell Price</p>
                    <p className="text-2xl font-mono font-bold text-primary">${product.recommended_price.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Margin</p>
                    <p className="text-2xl font-mono font-bold text-primary">{product.margin_percent}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Trend & Competition */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <Card className="bg-[#121212] border-white/5">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    {getTrendIcon()}
                    <div>
                      <p className="text-sm text-muted-foreground">Trend</p>
                      <p className={`font-mono font-bold ${product.trend_direction === 'up' ? 'text-primary' : product.trend_direction === 'down' ? 'text-destructive' : 'text-yellow-500'}`}>
                        {product.trend_percent > 0 ? '+' : ''}{product.trend_percent}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-[#121212] border-white/5">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <DollarSign className="w-5 h-5 text-secondary" />
                    <div>
                      <p className="text-sm text-muted-foreground">FB Ads</p>
                      <p className="font-mono font-bold">{product.active_fb_ads}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Scores Breakdown */}
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Trend Score</span>
                  <span className={getScoreColor(product.trend_score)}>{product.trend_score}</span>
                </div>
                <Progress value={product.trend_score} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Competition Score</span>
                  <span className={getScoreColor(product.competition_score)}>{product.competition_score}</span>
                </div>
                <Progress value={product.competition_score} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Profit Score</span>
                  <span className={getScoreColor(product.profit_score)}>{product.profit_score}</span>
                </div>
                <Progress value={product.profit_score} className="h-2" />
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="sourcing" className="mb-8">
          <TabsList className="bg-[#121212] border border-white/5">
            <TabsTrigger value="sourcing">Sourcing</TabsTrigger>
            <TabsTrigger value="validation">Validation</TabsTrigger>
            <TabsTrigger value="brief">Product Brief</TabsTrigger>
          </TabsList>

          <TabsContent value="sourcing" className="mt-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {product.suppliers?.map((supplier, i) => (
                <Card key={i} className={`bg-[#121212] border-white/5 ${i === 0 ? 'border-primary/30 ring-1 ring-primary/20' : ''}`}>
                  {i === 0 && (
                    <div className="px-4 py-2 bg-primary/10 border-b border-primary/20">
                      <span className="text-xs font-mono text-primary">BEST OPTION</span>
                    </div>
                  )}
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold">{supplier.name}</h3>
                      <Badge variant="outline" className="text-xs">{supplier.platform}</Badge>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Unit Cost</span>
                        <span className="font-mono">${supplier.unit_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Shipping</span>
                        <span className="font-mono">${supplier.shipping_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Delivery</span>
                        <span className="font-mono">{supplier.shipping_days} days</span>
                      </div>
                      <div className="flex justify-between items-center pt-2 border-t border-white/5">
                        <span className="text-muted-foreground">Rating</span>
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                          <span className="font-mono">{supplier.rating}</span>
                          <span className="text-xs text-muted-foreground">({supplier.total_orders.toLocaleString()})</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="validation" className="mt-6">
            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="font-bold mb-4">Validation Checklist</h3>
                    {brief && (
                      <>
                        <div className="flex items-center gap-3">
                          {brief.trademark_clear ? <Check className="w-5 h-5 text-primary" /> : <X className="w-5 h-5 text-destructive" />}
                          <span>Trademark Clear</span>
                        </div>
                        <div className="flex items-center gap-3">
                          {brief.supplier_verified ? <Check className="w-5 h-5 text-primary" /> : <X className="w-5 h-5 text-destructive" />}
                          <span>Supplier Verified</span>
                        </div>
                        <div className="flex items-center gap-3">
                          {brief.shipping_reasonable ? <Check className="w-5 h-5 text-primary" /> : <X className="w-5 h-5 text-destructive" />}
                          <span>Reasonable Shipping</span>
                        </div>
                        <div className="flex items-center gap-3">
                          {brief.competition_acceptable ? <Check className="w-5 h-5 text-primary" /> : <X className="w-5 h-5 text-destructive" />}
                          <span>Acceptable Competition</span>
                        </div>
                        <div className="flex items-center gap-3">
                          {brief.trend_positive ? <Check className="w-5 h-5 text-primary" /> : <X className="w-5 h-5 text-destructive" />}
                          <span>Positive Trend</span>
                        </div>
                        <div className="flex items-center gap-3">
                          {product.can_demo_video ? <Check className="w-5 h-5 text-primary" /> : <X className="w-5 h-5 text-destructive" />}
                          <span>Demo Video Potential</span>
                        </div>
                      </>
                    )}
                  </div>
                  <div>
                    <h3 className="font-bold mb-4">Market Stats</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                        <span className="text-muted-foreground">Shopify Stores</span>
                        <span className="font-mono">{product.shopify_stores}</span>
                      </div>
                      <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                        <span className="text-muted-foreground">Active FB Ads</span>
                        <span className="font-mono">{product.active_fb_ads}</span>
                      </div>
                      <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                        <span className="text-muted-foreground">Search Volume</span>
                        <span className="font-mono">{product.search_volume.toLocaleString()}/mo</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="brief" className="mt-6">
            {brief && (
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle>Profit Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-4 bg-white/5 rounded-lg text-center">
                        <p className="text-xs text-muted-foreground mb-1">Unit Cost</p>
                        <p className="text-xl font-mono font-bold">${brief.unit_cost.toFixed(2)}</p>
                      </div>
                      <div className="p-4 bg-white/5 rounded-lg text-center">
                        <p className="text-xs text-muted-foreground mb-1">Shipping</p>
                        <p className="text-xl font-mono font-bold">${brief.shipping_cost.toFixed(2)}</p>
                      </div>
                      <div className="p-4 bg-white/5 rounded-lg text-center">
                        <p className="text-xs text-muted-foreground mb-1">Total Cost</p>
                        <p className="text-xl font-mono font-bold">${brief.total_cost.toFixed(2)}</p>
                      </div>
                      <div className="p-4 bg-primary/10 rounded-lg text-center border border-primary/20">
                        <p className="text-xs text-muted-foreground mb-1">Sell Price</p>
                        <p className="text-xl font-mono font-bold text-primary">${brief.recommended_price.toFixed(2)}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-4 bg-white/5 rounded-lg text-center">
                        <p className="text-xs text-muted-foreground mb-1">Gross Margin</p>
                        <p className="text-xl font-mono font-bold text-primary">${brief.gross_margin.toFixed(2)}</p>
                      </div>
                      <div className="p-4 bg-white/5 rounded-lg text-center">
                        <p className="text-xs text-muted-foreground mb-1">Est. Ad CPA</p>
                        <p className="text-xl font-mono font-bold">${brief.estimated_ad_cpa.toFixed(2)}</p>
                      </div>
                      <div className="p-4 bg-primary/10 rounded-lg text-center border border-primary/20">
                        <p className="text-xs text-muted-foreground mb-1">Net Profit</p>
                        <p className="text-xl font-mono font-bold text-primary">${brief.net_profit_per_unit.toFixed(2)}</p>
                      </div>
                      <div className="p-4 bg-white/5 rounded-lg text-center">
                        <p className="text-xs text-muted-foreground mb-1">Break-even ROAS</p>
                        <p className="text-xl font-mono font-bold">{brief.break_even_roas}x</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
