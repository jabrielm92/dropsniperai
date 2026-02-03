import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  Zap, Check, ArrowLeft, X, Sparkles, Clock
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { createCheckoutSession } from '../lib/api';
import { toast } from 'sonner';

export default function Pricing() {
  const { user } = useAuth();

  const handleSubscribe = async (tier) => {
    if (!user) {
      window.location.href = '/register';
      return;
    }
    try {
      const response = await createCheckoutSession(
        tier,
        `${window.location.origin}/dashboard?upgraded=true`,
        `${window.location.origin}/pricing`
      );
      window.location.href = response.data.checkout_url;
    } catch (error) {
      toast.error('Failed to start checkout');
    }
  };

  const plans = [
    {
      name: "Sniper",
      price: 29,
      period: "month",
      description: "Perfect for getting started",
      features: [
        { text: "10 products per day", included: true },
        { text: "Daily intelligence report", included: true },
        { text: "Basic product filters", included: true },
        { text: "Email notifications", included: true },
        { text: "7-day history", included: true },
        { text: "Telegram alerts", included: false },
        { text: "Competitor tracking", included: false },
        { text: "Launch kit generator", included: false },
        { text: "Shopify/WooCommerce export", included: false },
      ],
      cta: "Start 24-Hour Trial",
      popular: false,
      active: true,
      tier: "sniper"
    },
    {
      name: "Elite",
      price: 79,
      period: "month",
      description: "For serious dropshippers",
      features: [
        { text: "Unlimited products", included: true },
        { text: "Daily intelligence report", included: true },
        { text: "Advanced filters", included: true },
        { text: "Telegram + Email alerts", included: true },
        { text: "Unlimited history", included: true },
        { text: "Competitor tracking (10 stores)", included: true },
        { text: "Launch kit generator", included: true },
        { text: "Shopify/WooCommerce export", included: true },
        { text: "Saturation radar", included: true },
        { text: "Google Trends integration", included: true },
      ],
      cta: "Start 24-Hour Trial",
      popular: true,
      active: true,
      tier: "elite"
    },
    {
      name: "Agency",
      price: 149,
      period: "month",
      description: "For teams & agencies",
      features: [
        { text: "Everything in Elite", included: true },
        { text: "5 team seats", included: true },
        { text: "White-label reports", included: true },
        { text: "API access", included: true },
        { text: "Priority support", included: true },
        { text: "Custom integrations", included: false },
      ],
      cta: "Join Waitlist",
      popular: false,
      active: false,
      tier: "agency"
    },
    {
      name: "Enterprise",
      price: null,
      period: "custom",
      description: "For large operations",
      features: [
        { text: "Everything in Agency", included: true },
        { text: "Unlimited team seats", included: true },
        { text: "Custom integrations", included: true },
        { text: "Dedicated success manager", included: true },
        { text: "SLA guarantee", included: true },
        { text: "Custom training", included: true },
      ],
      cta: "Contact Sales",
      popular: false,
      active: false,
      tier: "enterprise"
    }
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
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

      <main className="px-6 md:px-12 py-16 max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <Badge className="bg-primary/10 text-primary border-primary/20 mb-4">Simple Pricing</Badge>
          <h1 className="text-4xl md:text-5xl font-black mb-4">
            Find Winners. <span className="text-primary">Pay Less.</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Start with a 24-hour free trial. Cancel anytime.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <Card 
              key={plan.name}
              className={`relative bg-[#121212] border-white/5 overflow-hidden ${
                plan.popular ? 'border-primary/50 ring-1 ring-primary/20' : ''
              } ${!plan.active ? 'opacity-75' : ''}`}
            >
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-primary text-black text-xs font-bold px-3 py-1 rounded-bl-lg">
                  MOST POPULAR
                </div>
              )}
              {!plan.active && (
                <div className="absolute top-0 left-0 right-0 bg-yellow-500/20 text-yellow-500 text-xs font-bold px-3 py-1 text-center flex items-center justify-center gap-1">
                  <Clock className="w-3 h-3" />
                  COMING SOON
                </div>
              )}
              
              <CardContent className={`p-6 ${!plan.active ? 'pt-10' : ''}`}>
                <h3 className="text-xl font-bold mb-1">{plan.name}</h3>
                <p className="text-sm text-muted-foreground mb-4">{plan.description}</p>
                
                <div className="mb-6">
                  {plan.price ? (
                    <>
                      <span className="text-4xl font-black">${plan.price}</span>
                      <span className="text-muted-foreground">/{plan.period}</span>
                    </>
                  ) : (
                    <span className="text-2xl font-bold">Custom</span>
                  )}
                </div>

                <Button 
                  className={`w-full mb-6 font-bold ${
                    plan.popular 
                      ? 'bg-primary text-black hover:bg-primary/90' 
                      : plan.active 
                        ? 'bg-white text-black hover:bg-white/90'
                        : 'bg-yellow-500/20 text-yellow-500 hover:bg-yellow-500/30'
                  }`}
                  onClick={() => plan.active && handleSubscribe(plan.tier)}
                  disabled={!plan.active}
                >
                  {plan.cta}
                </Button>

                <ul className="space-y-3">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      {feature.included ? (
                        <Check className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      ) : (
                        <X className="w-4 h-4 text-muted-foreground/50 mt-0.5 flex-shrink-0" />
                      )}
                      <span className={feature.included ? '' : 'text-muted-foreground/50'}>
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {[
              { q: "How does the 24-hour trial work?", a: "Start any paid plan free for 24 hours. If you don't cancel, you'll be charged. No commitment, cancel anytime." },
              { q: "Can I change plans later?", a: "Yes! Upgrade or downgrade anytime. Changes take effect immediately with prorated billing." },
              { q: "What payment methods do you accept?", a: "We accept all major credit cards through Stripe. Enterprise plans can use invoicing." },
              { q: "Is there a refund policy?", a: "Yes, we offer a 7-day money-back guarantee on all plans. No questions asked." }
            ].map((faq, i) => (
              <div key={i} className="p-4 rounded-lg bg-[#121212] border border-white/5">
                <h3 className="font-bold mb-2">{faq.q}</h3>
                <p className="text-sm text-muted-foreground">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
