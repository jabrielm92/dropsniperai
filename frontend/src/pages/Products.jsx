import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  ArrowLeft, Package, TrendingUp, TrendingDown, Minus,
  Search, Loader2, ArrowUpRight, Calendar, Filter
} from 'lucide-react';
import { toast } from 'sonner';
import { getTodayProducts, getProductHistory } from '../lib/api';

export default function Products() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('today'); // today | history
  const [searchQuery, setSearchQuery] = useState('');

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const res = view === 'today'
        ? await getTodayProducts()
        : await getProductHistory(30);
      const data = res.data.products || res.data || [];
      setProducts(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load products:', error);
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  }, [view]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const filtered = products.filter(p =>
    !searchQuery || p.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.category?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.source?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const sorted = [...filtered].sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0));

  const getTrendIcon = (dir) => {
    if (dir === 'up') return <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />;
    if (dir === 'down') return <TrendingDown className="w-3.5 h-3.5 text-red-400" />;
    return <Minus className="w-3.5 h-3.5 text-amber-400" />;
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'from-emerald-500 to-emerald-600';
    if (score >= 70) return 'from-amber-500 to-amber-600';
    return 'from-red-500 to-red-600';
  };

  const getSaturationStyle = (level) => {
    if (level === 'low') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    if (level === 'medium') return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    return 'bg-red-500/10 text-red-400 border-red-500/20';
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      <header className="border-b border-white/5 bg-[#0A0A0A]/80 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="text-muted-foreground hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Dashboard
          </Button>
          <h1 className="text-lg font-bold">All Products</h1>
          <div className="flex items-center gap-2">
            <Button
              variant={view === 'today' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setView('today')}
              className={view === 'today' ? 'bg-primary text-black' : 'border-white/10'}
            >
              Today
            </Button>
            <Button
              variant={view === 'history' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setView('history')}
              className={view === 'history' ? 'bg-primary text-black' : 'border-white/10'}
            >
              <Calendar className="w-3.5 h-3.5 mr-1" />
              30 Days
            </Button>
          </div>
        </div>
      </header>

      <main className="p-6 max-w-[1400px] mx-auto">
        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search products by name, category, or source..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-[#111] border border-white/[0.08] rounded-xl text-sm focus:outline-none focus:border-primary/40 placeholder:text-white/30"
          />
        </div>

        {/* Count */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-muted-foreground">
            {sorted.length} product{sorted.length !== 1 ? 's' : ''} found
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
          </div>
        ) : sorted.length === 0 ? (
          <Card className="bg-[#111] border-white/[0.06] border-dashed">
            <CardContent className="py-16 text-center">
              <Package className="w-10 h-10 mx-auto mb-3 text-white/20" />
              <p className="font-medium mb-1">No products found</p>
              <p className="text-sm text-muted-foreground mb-4">Run a scan to discover trending products</p>
              <Button
                onClick={() => navigate('/scanner')}
                size="sm"
                className="bg-primary text-black font-semibold"
              >
                Go to Scanner
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {sorted.map((product, index) => (
              <Card
                key={product.id || index}
                className="bg-[#111] border-white/[0.06] hover:border-primary/20 cursor-pointer overflow-hidden group transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5"
                onClick={() => navigate(`/product/${product.id}`)}
              >
                {/* Image */}
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

                  {product.overall_score && (
                    <div className="absolute top-2.5 right-2.5">
                      <div className={`bg-gradient-to-r ${getScoreColor(product.overall_score)} text-white font-mono font-bold text-sm px-2.5 py-0.5 rounded-lg shadow-lg`}>
                        {product.overall_score}
                      </div>
                    </div>
                  )}

                  <div className="absolute bottom-2.5 left-2.5 flex gap-1.5">
                    {(product.source_platforms || (product.source ? [product.source] : [])).slice(0, 2).map((p, i) => (
                      <span key={i} className="bg-black/70 backdrop-blur-md text-[10px] text-white/80 px-2 py-0.5 rounded-md font-medium">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>

                <CardContent className="p-3.5 space-y-3">
                  <h3 className="font-semibold text-sm leading-tight line-clamp-1">{product.name}</h3>

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
      </main>
    </div>
  );
}
