import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent } from '../components/ui/card';
import { 
  Rocket, Target, Filter, CheckCircle, TrendingUp, DollarSign, 
  Zap, BarChart3, Shield, Clock, ArrowRight, Play, Star,
  Send, Bell, LineChart, Store, Package, Users, Globe,
  Smartphone, MessageSquare, Eye, Search, Layers
} from 'lucide-react';

export default function Landing() {
  const features = [
    { icon: <Target className="w-6 h-6" />, title: "AI Scout", description: "Scans TikTok, Amazon, AliExpress & Google Trends 24/7 for viral products before saturation." },
    { icon: <Filter className="w-6 h-6" />, title: "Smart Filter", description: "Eliminates losers instantly. Only 2.5x+ margin products with low competition pass through." },
    { icon: <CheckCircle className="w-6 h-6" />, title: "Auto Validator", description: "Checks trademarks, supplier ratings, competition levels & shipping times automatically." },
    { icon: <DollarSign className="w-6 h-6" />, title: "Profit Calculator", description: "Real-time profit calculations including all fees, shipping, and ad costs." },
    { icon: <Rocket className="w-6 h-6" />, title: "Launch Kit", description: "Generates ad copy, video scripts, targeting & complete launch kits instantly." },
    { icon: <Store className="w-6 h-6" />, title: "Competitor Spy", description: "Monitor competitor stores. Get alerts when they add new products." },
    { icon: <BarChart3 className="w-6 h-6" />, title: "Saturation Radar", description: "See exactly how saturated each niche is before you commit." },
    { icon: <LineChart className="w-6 h-6" />, title: "Google Trends", description: "Real-time trend data integration. Catch waves before they peak." },
  ];

  const stats = [
    { value: "10,000+", label: "Products Analyzed Daily" },
    { value: "94%", label: "Winner Accuracy Rate" },
    { value: "<$80", label: "Monthly vs $2k+ Testing" },
    { value: "24hrs", label: "From Trend to Launch" }
  ];

  const testimonials = [
    {
      quote: "I went from spending 10 hours a week on product research to 10 minutes. Found 3 winners in my first month that did $47k combined.",
      author: "Sarah J.",
      role: "Full-time Dropshipper",
      avatar: "https://images.unsplash.com/photo-1573167869536-fc0e3afd9577?w=100&h=100&fit=crop",
      result: "$47k in 30 days"
    },
    {
      quote: "The niche finder is incredible. It showed me pet accessories were oversaturated but pet tech had room. My store hit $12k first month.",
      author: "Marcus T.",
      role: "Side Hustle Seller",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop",
      result: "$12k first month"
    },
    {
      quote: "We manage 8 stores for clients. DropSniper cut our research time by 80%. The ROI is insane - it paid for itself day one.",
      author: "Jessica & Team",
      role: "E-commerce Agency",
      avatar: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&h=100&fit=crop",
      result: "80% time saved"
    }
  ];

  const telegramFeatures = [
    { icon: <Bell />, text: "Daily winning products at 7AM" },
    { icon: <TrendingUp />, text: "Trend alerts before saturation" },
    { icon: <Eye />, text: "Competitor activity notifications" },
    { icon: <Package />, text: "New supplier deals & updates" },
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0A] relative overflow-hidden">
      {/* Hero Section */}
      <section className="relative">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent" />
        
        <nav className="relative z-10 flex items-center justify-between px-6 md:px-12 py-6">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            <span className="font-bold text-xl tracking-tight">DropSniper AI</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/pricing" className="hidden sm:block">
              <Button variant="ghost" className="text-muted-foreground hover:text-white">Pricing</Button>
            </Link>
            <Link to="/login">
              <Button variant="ghost" className="text-muted-foreground hover:text-white">Login</Button>
            </Link>
            <Link to="/register">
              <Button className="bg-primary text-black font-bold hover:bg-primary/90">Get Started</Button>
            </Link>
          </div>
        </nav>

        <div className="relative z-10 px-6 md:px-12 pt-16 pb-24">
          <div className="max-w-5xl mx-auto text-center">
            <Badge className="bg-primary/10 text-primary border-primary/20 mb-6">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse mr-2" />
              AI-Powered Product Research
            </Badge>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-black tracking-tight leading-[1.1] mb-6">
              Stop Guessing Products.
              <br />
              <span className="text-primary">Start Printing Money.</span>
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed">
              AI agents scout, filter, validate & prepare winning dropshipping products while you sleep. 
              Wake up to launch-ready opportunities with profit calculations, supplier sourcing, and ad copy done.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link to="/register">
                <Button size="lg" className="bg-primary text-black font-bold text-lg px-8 py-6 hover:bg-primary/90">
                  Start Free 24-Hour Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Link to="/pricing">
                <Button size="lg" variant="outline" className="border-white/20 text-white hover:bg-white/5 px-8 py-6">
                  View Pricing
                </Button>
              </Link>
            </div>
            
            <p className="text-sm text-muted-foreground">
              ✓ No credit card required &nbsp; ✓ Cancel anytime &nbsp; ✓ 2,500+ sellers trust us
            </p>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="relative z-10 px-6 md:px-12 py-12 border-y border-white/5 bg-[#0d0d0d]">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, i) => (
            <div key={i} className="text-center">
              <div className="text-3xl md:text-4xl font-black text-primary mb-1">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative z-10 px-6 md:px-12 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="bg-white/5 text-white border-white/10 mb-4">Features</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Everything You Need to <span className="text-primary">Find Winners</span>
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              A complete product research suite powered by AI. No more manual searching.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature, i) => (
              <div key={i} className="p-5 rounded-xl bg-[#121212] border border-white/5 hover:border-primary/30 transition-all">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-3">
                  <span className="text-primary">{feature.icon}</span>
                </div>
                <h3 className="font-bold mb-1">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Telegram Section */}
      <section className="relative z-10 px-6 md:px-12 py-24 bg-gradient-to-b from-[#0A0A0A] to-[#0d1a0f]">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 mb-4">
                <Send className="w-3 h-3 mr-1" />
                Telegram Integration
              </Badge>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Winners Delivered to Your <span className="text-blue-400">Phone</span>
              </h2>
              <p className="text-muted-foreground mb-6">
                Connect your Telegram and receive daily winning products, trend alerts, and competitor updates directly to your phone. Never miss an opportunity.
              </p>
              <ul className="space-y-3 mb-8">
                {telegramFeatures.map((item, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
                      {item.icon}
                    </div>
                    <span>{item.text}</span>
                  </li>
                ))}
              </ul>
              <Link to="/register">
                <Button className="bg-blue-500 hover:bg-blue-600 text-white font-bold">
                  <Send className="w-4 h-4 mr-2" />
                  Connect Telegram Free
                </Button>
              </Link>
            </div>
            
            {/* Mock Telegram Message */}
            <div className="bg-[#1a1a1a] rounded-2xl p-4 border border-white/10">
              <div className="flex items-center gap-3 mb-4 pb-3 border-b border-white/10">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <div className="font-bold">DropSniper AI Bot</div>
                  <div className="text-xs text-muted-foreground">Online</div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="bg-[#262626] rounded-lg p-3 max-w-[85%]">
                  <div className="text-sm font-bold text-primary mb-1">🎯 Daily Report Ready</div>
                  <div className="text-sm text-muted-foreground">
                    Scanned 2,847 products overnight.<br/>
                    <span className="text-white">5 winners</span> passed all filters.
                  </div>
                </div>
                <div className="bg-[#262626] rounded-lg p-3 max-w-[85%]">
                  <div className="text-sm font-bold text-green-400 mb-1">💰 Top Pick: LED Book Lamp</div>
                  <div className="text-xs text-muted-foreground">
                    Score: 94 | Cost: $11.40 | Sell: $44.99<br/>
                    Margin: 68% | FB Ads: 34 | Trend: ↑180%
                  </div>
                </div>
                <div className="bg-[#262626] rounded-lg p-3 max-w-[85%]">
                  <div className="text-sm font-bold text-yellow-400 mb-1">⚠️ Competitor Alert</div>
                  <div className="text-xs text-muted-foreground">
                    TrendyStore added 3 new products
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 px-6 md:px-12 py-24 bg-[#0d0d0d]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="bg-white/5 text-white border-white/10 mb-4">How It Works</Badge>
            <h2 className="text-3xl md:text-4xl font-bold">
              From Zero to Launch in <span className="text-primary">4 Steps</span>
            </h2>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: "01", title: "Connect", desc: "Sign up and connect your Telegram in 30 seconds", icon: <Smartphone /> },
              { step: "02", title: "AI Scans", desc: "Our AI browses TikTok, Amazon & more at 7AM daily", icon: <Search /> },
              { step: "03", title: "You Pick", desc: "Review top 5 validated products with full data", icon: <Target /> },
              { step: "04", title: "Launch", desc: "Export to Shopify with ad copy & supplier info", icon: <Rocket /> }
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-4 text-primary">
                  {item.icon}
                </div>
                <div className="text-xs text-primary font-mono mb-2">STEP {item.step}</div>
                <h3 className="text-lg font-bold mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="relative z-10 px-6 md:px-12 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="bg-white/5 text-white border-white/10 mb-4">Testimonials</Badge>
            <h2 className="text-3xl md:text-4xl font-bold">
              Loved by <span className="text-primary">2,500+ Sellers</span>
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <Card key={i} className="bg-[#121212] border-white/5">
                <CardContent className="p-6">
                  <div className="flex gap-1 mb-4">
                    {[...Array(5)].map((_, j) => (
                      <Star key={j} className="w-4 h-4 fill-primary text-primary" />
                    ))}
                  </div>
                  <blockquote className="text-sm mb-4 leading-relaxed">"{t.quote}"</blockquote>
                  <div className="flex items-center gap-3">
                    <img src={t.avatar} alt={t.author} className="w-10 h-10 rounded-full object-cover" />
                    <div>
                      <div className="font-bold text-sm">{t.author}</div>
                      <div className="text-xs text-muted-foreground">{t.role}</div>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-white/5">
                    <Badge className="bg-primary/10 text-primary text-xs">{t.result}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Export Section */}
      <section className="relative z-10 px-6 md:px-12 py-24 bg-[#0d0d0d]">
        <div className="max-w-6xl mx-auto text-center">
          <Badge className="bg-white/5 text-white border-white/10 mb-4">One-Click Export</Badge>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Launch on <span className="text-primary">Shopify or WooCommerce</span> Instantly
          </h2>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Export winning products directly to your store with one click. Product data, images, descriptions, and pricing all included.
          </p>
          <div className="flex justify-center gap-4">
            <div className="px-6 py-3 rounded-lg bg-[#96bf48]/10 border border-[#96bf48]/20 text-[#96bf48] font-bold">
              Shopify
            </div>
            <div className="px-6 py-3 rounded-lg bg-[#7f54b3]/10 border border-[#7f54b3]/20 text-[#7f54b3] font-bold">
              WooCommerce
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 px-6 md:px-12 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-5xl font-black mb-6">
            Ready to Find Your <span className="text-primary">First Winner?</span>
          </h2>
          <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
            Join 2,500+ dropshippers who automated their product research. Start your free 24-hour trial today.
          </p>
          <Link to="/register">
            <Button size="lg" className="bg-primary text-black font-bold text-lg px-12 py-6 hover:bg-primary/90">
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
          <p className="text-sm text-muted-foreground mt-4">No credit card required</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 md:px-12 py-12 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary" />
              <span className="font-bold">DropSniper AI</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <Link to="/pricing" className="hover:text-white">Pricing</Link>
              <Link to="/terms" className="hover:text-white">Terms</Link>
              <Link to="/privacy" className="hover:text-white">Privacy</Link>
            </div>
            <div className="text-sm text-muted-foreground">
              © 2026 DropSniper AI. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
