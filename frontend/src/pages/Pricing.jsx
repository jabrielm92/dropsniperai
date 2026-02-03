import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  Zap, Check, ArrowLeft, Rocket, Target, Filter, 
  BarChart3, Users, Headphones
} from 'lucide-react';

export default function Pricing() {
  const plans = [
    {
      name: "Scout",
      price: 29,
      description: "Perfect for getting started",
      features: [
        "1 daily intelligence report",
        "5 products per day",
        "Email notifications",
        "Basic filters",
        "7-day history"
      ],
      cta: "Start Free Trial",
      popular: false
    },
    {
      name: "Hunter",
      price: 79,
      description: "For serious dropshippers",
      features: [
        "3 reports per day",
        "25 products per day",
        "Telegram + Email alerts",
        "Advanced filters",
        "Full supplier sourcing",
        "Launch kit generator",
        "30-day history"
      ],
      cta: "Start Free Trial",
      popular: true
    },
    {
      name: "Predator",
      price: 199,
      description: "For power sellers",
      features: [
        "Unlimited scans",
        "Unlimited products",
        "All notification channels",
        "Competitor tracking",
        "Saturation radar",
        "Priority AI processing",
        "API access",
        "Unlimited history"
      ],
      cta: "Start Free Trial",
      popular: false
    },
    {
      name: "Agency",
      price: 499,
      description: "For teams & agencies",
      features: [
        "Everything in Predator",
        "5 team seats",
        "White-label reports",
        "Custom integrations",
        "Dedicated success manager",
        "Priority support",
        "Custom training"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {/* Header */}
      <header className="border-b border-white/5">
        <div className="flex items-center justify-between px-6 md:px-12 py-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            <span className="font-bold text-xl">DropSniper AI</span>
          </Link>
          <Link to="/">
            <Button variant="ghost" className="text-muted-foreground hover:text-white">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
        </div>
      </header>

      <main className="px-6 md:px-12 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge className="bg-primary/10 text-primary border-primary/20 mb-4">Pricing</Badge>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight mb-4">
            Choose Your <span className="text-primary">Edge</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Start free for 7 days. Cancel anytime. All plans include core AI scanning features.
          </p>
        </div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto mb-16">
          {plans.map((plan, i) => (
            <Card 
              key={i} 
              className={`bg-[#121212] border-white/5 relative ${plan.popular ? 'border-primary/50 ring-1 ring-primary/20' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-primary text-black font-bold">Most Popular</Badge>
                </div>
              )}
              <CardHeader className="pt-8">
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{plan.description}</p>
              </CardHeader>
              <CardContent>
                <div className="mb-6">
                  <span className="text-4xl font-black">${plan.price}</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
                
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-2 text-sm">
                      <Check className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link to="/register">
                  <Button 
                    className={`w-full ${plan.popular ? 'bg-primary text-black font-bold hover:bg-primary/90' : 'bg-white/5 hover:bg-white/10'}`}
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features Comparison */}
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">All Plans Include</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-[#121212] border border-white/5 text-center">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Target className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-bold mb-2">AI Scout Agent</h3>
              <p className="text-sm text-muted-foreground">Automated product discovery from top platforms</p>
            </div>
            <div className="p-6 rounded-xl bg-[#121212] border border-white/5 text-center">
              <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center mx-auto mb-4">
                <Filter className="w-6 h-6 text-secondary" />
              </div>
              <h3 className="font-bold mb-2">Smart Filters</h3>
              <p className="text-sm text-muted-foreground">Customizable criteria for your niche</p>
            </div>
            <div className="p-6 rounded-xl bg-[#121212] border border-white/5 text-center">
              <div className="w-12 h-12 rounded-lg bg-yellow-500/10 flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-6 h-6 text-yellow-500" />
              </div>
              <h3 className="font-bold mb-2">Profit Calculator</h3>
              <p className="text-sm text-muted-foreground">Real margins with all fees included</p>
            </div>
          </div>
        </div>

        {/* FAQ or CTA */}
        <div className="text-center mt-16">
          <p className="text-muted-foreground mb-4">
            Questions? We're here to help.
          </p>
          <Button variant="outline" className="border-white/10">
            <Headphones className="w-4 h-4 mr-2" />
            Contact Support
          </Button>
        </div>
      </main>
    </div>
  );
}
