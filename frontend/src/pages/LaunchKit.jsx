import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Checkbox } from '../components/ui/checkbox';
import { 
  ArrowLeft, Copy, Download, Check, Rocket, Video, 
  Target, Hash, DollarSign, ListChecks, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import { getLaunchKit } from '../lib/api';

export default function LaunchKit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [kit, setKit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checklist, setChecklist] = useState([]);

  useEffect(() => {
    fetchKit();
  }, [id]);

  const fetchKit = async () => {
    try {
      const response = await getLaunchKit(id);
      setKit(response.data);
      setChecklist(response.data.launch_checklist || []);
    } catch (error) {
      toast.error('Failed to load launch kit');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const toggleChecklistItem = (index) => {
    const updated = [...checklist];
    updated[index].completed = !updated[index].completed;
    setChecklist(updated);
  };

  const completedCount = checklist.filter(item => item.completed).length;

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!kit) return null;

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
          <Button variant="outline" className="border-white/10">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </header>

      <main className="p-6 max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
              <Rocket className="w-6 h-6 text-primary" />
            </div>
            <div>
              <Badge className="bg-primary/10 text-primary border-primary/20 mb-1">Launch Kit Ready</Badge>
              <h1 className="text-2xl font-bold">{kit.product_name}</h1>
            </div>
          </div>
          <p className="text-muted-foreground">{kit.product_description}</p>
        </div>

        {/* Progress */}
        <Card className="bg-[#121212] border-white/5 mb-8">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold">Launch Progress</h3>
              <span className="text-sm text-muted-foreground">{completedCount}/{checklist.length} completed</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-3">
              <div 
                className="bg-primary h-3 rounded-full transition-all duration-300"
                style={{ width: `${(completedCount / checklist.length) * 100}%` }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="ads" className="mb-8">
          <TabsList className="bg-[#121212] border border-white/5 flex-wrap h-auto gap-1 p-1">
            <TabsTrigger value="ads" className="flex items-center gap-2">
              <Copy className="w-4 h-4" />
              Ad Copy
            </TabsTrigger>
            <TabsTrigger value="scripts" className="flex items-center gap-2">
              <Video className="w-4 h-4" />
              Video Scripts
            </TabsTrigger>
            <TabsTrigger value="targeting" className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Targeting
            </TabsTrigger>
            <TabsTrigger value="pricing" className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Pricing
            </TabsTrigger>
            <TabsTrigger value="checklist" className="flex items-center gap-2">
              <ListChecks className="w-4 h-4" />
              Checklist
            </TabsTrigger>
          </TabsList>

          {/* Ad Copy Tab */}
          <TabsContent value="ads" className="mt-6">
            <div className="grid gap-4">
              {kit.ad_copies?.map((ad, i) => (
                <Card key={i} className="bg-[#121212] border-white/5">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="capitalize">{ad.style}</Badge>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => copyToClipboard(`${ad.headline}\n\n${ad.body}\n\n${ad.cta}`)}
                      >
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <h3 className="text-lg font-bold mb-2">{ad.headline}</h3>
                    <p className="text-muted-foreground mb-3">{ad.body}</p>
                    <Badge className="bg-primary/10 text-primary">{ad.cta}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Video Scripts Tab */}
          <TabsContent value="scripts" className="mt-6">
            <div className="grid gap-4">
              {kit.video_scripts?.map((script, i) => (
                <Card key={i} className="bg-[#121212] border-white/5">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">{script.duration_seconds}s Script</Badge>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => copyToClipboard(`HOOK: ${script.hook}\n\nPROBLEM: ${script.problem}\n\nSOLUTION: ${script.solution}\n\nCTA: ${script.cta}`)}
                      >
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-xs text-primary font-mono mb-1">HOOK (0-3s)</p>
                      <p className="font-medium">{script.hook}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground font-mono mb-1">PROBLEM (3-8s)</p>
                      <p>{script.problem}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground font-mono mb-1">SOLUTION (8-13s)</p>
                      <p>{script.solution}</p>
                    </div>
                    <div>
                      <p className="text-xs text-primary font-mono mb-1">CTA (13-{script.duration_seconds}s)</p>
                      <p className="font-medium">{script.cta}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Targeting Tab */}
          <TabsContent value="targeting" className="mt-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-secondary" />
                    Target Audiences
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {kit.target_audiences?.map((audience, i) => (
                      <li key={i} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
                        <div className="w-6 h-6 rounded-full bg-secondary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-xs font-mono text-secondary">{i + 1}</span>
                        </div>
                        <span>{audience}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Hash className="w-5 h-5 text-primary" />
                    Hashtags
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {kit.hashtags?.map((tag, i) => (
                      <Badge 
                        key={i} 
                        variant="secondary" 
                        className="cursor-pointer hover:bg-primary/20 transition-colors"
                        onClick={() => copyToClipboard(tag)}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <Button 
                    variant="outline" 
                    className="w-full mt-4 border-white/10"
                    onClick={() => copyToClipboard(kit.hashtags?.join(' '))}
                  >
                    <Copy className="w-4 h-4 mr-2" />
                    Copy All Hashtags
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Pricing Tab */}
          <TabsContent value="pricing" className="mt-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle>Pricing Tiers</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {kit.pricing_tiers && Object.entries(kit.pricing_tiers).map(([tier, price], i) => (
                      <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                        <span className="capitalize font-medium">{tier.replace('_', ' ')}</span>
                        <span className="text-xl font-mono font-bold text-primary">${price.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-[#121212] border-white/5">
                <CardHeader>
                  <CardTitle>Upsell Suggestions</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {kit.upsell_suggestions?.map((suggestion, i) => (
                      <li key={i} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                        <Check className="w-5 h-5 text-primary flex-shrink-0" />
                        <span>{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Checklist Tab */}
          <TabsContent value="checklist" className="mt-6">
            <Card className="bg-[#121212] border-white/5">
              <CardHeader>
                <CardTitle>Launch Checklist</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {checklist.map((item, i) => (
                    <div 
                      key={i} 
                      className={`flex items-center gap-4 p-4 rounded-lg transition-colors cursor-pointer ${item.completed ? 'bg-primary/10' : 'bg-white/5 hover:bg-white/10'}`}
                      onClick={() => toggleChecklistItem(i)}
                    >
                      <Checkbox 
                        checked={item.completed}
                        className="data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                      />
                      <span className={item.completed ? 'line-through text-muted-foreground' : ''}>{item.task}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
