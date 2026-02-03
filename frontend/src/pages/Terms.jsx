import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Zap, ArrowLeft } from 'lucide-react';

export default function Terms() {
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
              <ArrowLeft className="w-4 h-4 mr-2" />Back
            </Button>
          </Link>
        </div>
      </header>

      <main className="px-6 md:px-12 py-16 max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
        <p className="text-muted-foreground mb-8">Last updated: February 2026</p>

        <div className="prose prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-bold mb-4">1. Acceptance of Terms</h2>
            <p className="text-muted-foreground leading-relaxed">
              By accessing or using DropSniper AI ("Service"), you agree to be bound by these Terms of Service. If you do not agree to these terms, do not use the Service. We reserve the right to modify these terms at any time, and your continued use constitutes acceptance of any changes.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. Description of Service</h2>
            <p className="text-muted-foreground leading-relaxed">
              DropSniper AI is a product research tool for e-commerce sellers. We provide AI-powered product discovery, trend analysis, competitor monitoring, and launch kit generation. The Service is provided "as is" and product recommendations are for informational purposes only.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. Account Registration</h2>
            <p className="text-muted-foreground leading-relaxed">
              You must provide accurate information when creating an account. You are responsible for maintaining the security of your account credentials. You must be at least 18 years old to use this Service. One person or entity may not maintain multiple free accounts.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. Subscription and Billing</h2>
            <p className="text-muted-foreground leading-relaxed">
              Paid subscriptions are billed monthly in advance. You may cancel at any time, and cancellation takes effect at the end of your billing period. We offer a 24-hour free trial for new users. Refunds are available within 7 days of purchase. Prices are subject to change with 30 days notice.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">5. Acceptable Use</h2>
            <p className="text-muted-foreground leading-relaxed">
              You agree not to: (a) use the Service for any illegal purpose; (b) attempt to gain unauthorized access to our systems; (c) resell or redistribute Service data without permission; (d) use automated tools to scrape our platform; (e) violate any applicable laws or regulations.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">6. Intellectual Property</h2>
            <p className="text-muted-foreground leading-relaxed">
              All content, features, and functionality of the Service are owned by DropSniper AI and protected by copyright, trademark, and other intellectual property laws. You may not copy, modify, or distribute our content without written permission.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">7. Disclaimer of Warranties</h2>
            <p className="text-muted-foreground leading-relaxed">
              THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND. WE DO NOT GUARANTEE THAT ANY PRODUCT RECOMMENDATIONS WILL RESULT IN SALES OR PROFITS. E-COMMERCE SUCCESS DEPENDS ON MANY FACTORS BEYOND OUR CONTROL.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">8. Limitation of Liability</h2>
            <p className="text-muted-foreground leading-relaxed">
              IN NO EVENT SHALL DROPSNIPER AI BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING FROM YOUR USE OF THE SERVICE. OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT PAID BY YOU IN THE PAST 12 MONTHS.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">9. Termination</h2>
            <p className="text-muted-foreground leading-relaxed">
              We may terminate or suspend your account at any time for violation of these terms. Upon termination, your right to use the Service ceases immediately. You may terminate your account at any time by contacting support.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">10. Contact</h2>
            <p className="text-muted-foreground leading-relaxed">
              For questions about these Terms, contact us at dropsniperai@arisolutionsinc.com
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
