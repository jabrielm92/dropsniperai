import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { 
  Rocket, Target, Filter, CheckCircle, TrendingUp, DollarSign, 
  Zap, BarChart3, Shield, Clock, ArrowRight, Play, Star
} from 'lucide-react';

export default function Landing() {
  const features = [
    {
      icon: <Target className="w-6 h-6" />,
      title: "The Scout",
      description: "AI scans TikTok, Amazon, AliExpress & Google Trends daily for viral products before they saturate."
    },
    {
      icon: <Filter className="w-6 h-6" />,
      title: "The Filter",
      description: "Ruthlessly eliminates losers. Only products with 2.5x+ margins and low competition make the cut."
    },
    {
      icon: <CheckCircle className="w-6 h-6" />,
      title: "The Validator",
      description: "Checks trademarks, supplier ratings, competition levels & shipping times automatically."
    },
    {
      icon: <DollarSign className="w-6 h-6" />,
      title: "The Sourcer",
      description: "Finds the cheapest, most reliable suppliers across AliExpress, CJ, 1688 & Alibaba."
    },
    {
      icon: <Rocket className="w-6 h-6" />,
      title: "The Launcher",
      description: "Generates ad copy, video scripts, targeting & complete launch kits. You just click approve."
    }
  ];

  const stats = [
    { value: "2,847+", label: "Products Scanned Daily" },
    { value: "94%", label: "Accuracy Rate" },
    { value: "$20", label: "Monthly Cost vs $2k+ Testing" },
    { value: "24hrs", label: "From Trend to Launch-Ready" }
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0A] relative overflow-hidden">
      {/* Noise overlay */}
      <div className="noise-overlay fixed inset-0 pointer-events-none" />
      
      {/* Hero Section */}
      <section className="relative">
        {/* Background image with overlay */}
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1740922989961-e46ea88a3838?w=1920)' }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0A0A0A]/50 via-[#0A0A0A]/80 to-[#0A0A0A]" />
        
        {/* Navigation */}
        <nav className="relative z-10 flex items-center justify-between px-6 md:px-12 py-6">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            <span className="font-bold text-xl tracking-tight">ProductScout AI</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/pricing">
              <Button variant="ghost" className="text-muted-foreground hover:text-white">
                Pricing
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="ghost" className="text-muted-foreground hover:text-white">
                Login
              </Button>
            </Link>
            <Link to="/register">
              <Button className="bg-primary text-black font-bold hover:bg-primary/90 btn-primary-glow">
                Get Started
              </Button>
            </Link>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 px-6 md:px-12 pt-20 pb-32">
          <div className="max-w-4xl">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-sm font-mono text-primary">AI-Powered Product Research</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-black tracking-tight leading-none mb-6">
              Stop Guessing.
              <br />
              <span className="text-primary">Start Winning.</span>
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-10 leading-relaxed">
              AI agents scout, filter, validate & prepare winning products while you sleep. 
              Wake up to launch-ready opportunities with full profit calculations and supplier sourcing.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/register">
                <Button size="lg" className="bg-primary text-black font-bold text-lg px-8 py-6 hover:bg-primary/90 btn-primary-glow">
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="border-white/20 text-white hover:bg-white/5 px-8 py-6">
                <Play className="w-5 h-5 mr-2" />
                Watch Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 px-6 md:px-12 py-16 border-y border-white/5">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, i) => (
            <div key={i} className="text-center md:text-left">
              <div className="text-3xl md:text-4xl font-black text-primary mb-2">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 px-6 md:px-12 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              5 AI Agents Working <span className="text-primary">24/7</span>
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              A full product research team that never sleeps. Each agent specializes in one critical task.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <div 
                key={i}
                className="group p-6 rounded-xl bg-[#121212] border border-white/5 hover:border-primary/30 transition-all duration-300 card-hover"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <span className="text-primary">{feature.icon}</span>
                </div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </div>
            ))}
            
            {/* CTA Card */}
            <div className="p-6 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/30 flex flex-col justify-center">
              <h3 className="text-xl font-bold mb-2">Ready to Print $$$?</h3>
              <p className="text-muted-foreground mb-4">Join thousands of sellers finding winners daily.</p>
              <Link to="/register">
                <Button className="w-full bg-primary text-black font-bold hover:bg-primary/90">
                  Get Started Free
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 px-6 md:px-12 py-24 bg-[#0d0d0d]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              From Trend to Store in <span className="text-primary">24 Hours</span>
            </h2>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: "01", title: "Scout Scans", desc: "AI browses TikTok, Amazon & more at 7AM daily" },
              { step: "02", title: "Filter Applies", desc: "Only 2.5x+ margin products with low competition pass" },
              { step: "03", title: "You Approve", desc: "Review top 5 picks with full profit calculations" },
              { step: "04", title: "Launch Ready", desc: "Get ad copy, scripts & supplier info instantly" }
            ].map((item, i) => (
              <div key={i} className="relative">
                <div className="text-6xl font-black text-white/5 absolute -top-4 -left-2">{item.step}</div>
                <div className="relative z-10 pt-8">
                  <h3 className="text-lg font-bold mb-2">{item.title}</h3>
                  <p className="text-muted-foreground text-sm">{item.desc}</p>
                </div>
                {i < 3 && (
                  <ArrowRight className="hidden md:block absolute top-1/2 -right-4 w-6 h-6 text-primary/50" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonial */}
      <section className="relative z-10 px-6 md:px-12 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex justify-center gap-1 mb-6">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="w-6 h-6 fill-primary text-primary" />
            ))}
          </div>
          <blockquote className="text-2xl md:text-3xl font-medium mb-8 leading-relaxed">
            "I went from spending 10 hours a week on product research to 10 minutes. 
            Found 3 winners in my first month that did <span className="text-primary">$47k combined</span>."
          </blockquote>
          <div className="flex items-center justify-center gap-4">
            <img 
              src="https://images.unsplash.com/photo-1573167869536-fc0e3afd9577?w=100&h=100&fit=crop" 
              alt="Sarah J."
              className="w-12 h-12 rounded-full object-cover"
            />
            <div className="text-left">
              <div className="font-bold">Sarah J.</div>
              <div className="text-sm text-muted-foreground">Dropshipping Store Owner</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-6 md:px-12 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-5xl font-black tracking-tight mb-6">
            Stop Scrolling. <span className="text-primary">Start Scaling.</span>
          </h2>
          <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
            6 months from now, there'll be two types of sellers: those who automated their research early, 
            and those still guessing at 2AM.
          </p>
          <Link to="/register">
            <Button size="lg" className="bg-primary text-black font-bold text-lg px-12 py-6 hover:bg-primary/90 btn-primary-glow">
              Get Started Free
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
          <p className="text-sm text-muted-foreground mt-4">No credit card required. 7-day free trial.</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 md:px-12 py-12 border-t border-white/5">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary" />
            <span className="font-bold">ProductScout AI</span>
          </div>
          <div className="text-sm text-muted-foreground">
            © 2026 ProductScout AI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
