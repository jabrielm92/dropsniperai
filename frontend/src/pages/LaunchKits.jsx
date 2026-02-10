import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  ArrowLeft, Rocket, Loader2, Clock, ChevronRight, Package
} from 'lucide-react';
import { toast } from 'sonner';
import { getLaunchKits } from '../lib/api';

export default function LaunchKits() {
  const navigate = useNavigate();
  const [kits, setKits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchKits();
  }, []);

  const fetchKits = async () => {
    try {
      const res = await getLaunchKits();
      setKits(res.data.kits || res.data || []);
    } catch (error) {
      console.error('Failed to load launch kits:', error);
      toast.error('Failed to load launch kits');
    } finally {
      setLoading(false);
    }
  };

  const getStatusStyle = (status) => {
    if (status === 'ready') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    if (status === 'launched') return 'bg-primary/10 text-primary border-primary/20';
    return 'bg-white/5 text-white/60 border-white/10';
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
          <h1 className="text-lg font-bold">Launch Kits</h1>
          <div className="w-24" />
        </div>
      </header>

      <main className="p-6 max-w-[1200px] mx-auto">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
          </div>
        ) : kits.length === 0 ? (
          <Card className="bg-[#111] border-white/[0.06] border-dashed">
            <CardContent className="py-16 text-center">
              <Rocket className="w-10 h-10 mx-auto mb-3 text-white/20" />
              <p className="font-medium mb-1">No launch kits yet</p>
              <p className="text-sm text-muted-foreground mb-4">
                Generate a launch kit from any product detail page
              </p>
              <Button
                onClick={() => navigate('/products')}
                size="sm"
                className="bg-primary text-black font-semibold"
              >
                <Package className="w-3.5 h-3.5 mr-1.5" />
                Browse Products
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {kits.map((kit, index) => (
              <Card
                key={kit.id || index}
                className="bg-[#111] border-white/[0.06] hover:border-blue-500/20 cursor-pointer transition-all group"
                onClick={() => navigate(`/launch-kit/${kit.id}`)}
              >
                <CardContent className="p-5">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-500/5 flex items-center justify-center shrink-0">
                          <Rocket className="w-5 h-5 text-blue-400" />
                        </div>
                        <div className="min-w-0">
                          <h3 className="font-semibold truncate">{kit.product_name || 'Untitled Kit'}</h3>
                          <p className="text-xs text-muted-foreground truncate">{kit.product_description || 'No description'}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 mt-3 text-xs text-muted-foreground">
                        <Badge variant="outline" className={`${getStatusStyle(kit.status)} text-[10px] h-5 px-1.5 border capitalize`}>
                          {kit.status || 'draft'}
                        </Badge>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {kit.created_at ? new Date(kit.created_at).toLocaleDateString() : 'Unknown'}
                        </span>
                        {kit.ad_copies?.length > 0 && (
                          <span>{kit.ad_copies.length} ad cop{kit.ad_copies.length === 1 ? 'y' : 'ies'}</span>
                        )}
                        {kit.video_scripts?.length > 0 && (
                          <span>{kit.video_scripts.length} video script{kit.video_scripts.length === 1 ? '' : 's'}</span>
                        )}
                      </div>
                    </div>

                    <ChevronRight className="w-5 h-5 text-white/20 group-hover:text-primary transition-colors shrink-0 ml-4" />
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
