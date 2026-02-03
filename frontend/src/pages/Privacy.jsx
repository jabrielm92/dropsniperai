import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Zap, ArrowLeft } from 'lucide-react';

export default function Privacy() {
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
        <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
        <p className="text-muted-foreground mb-8">Last updated: February 2026</p>

        <div className="prose prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-bold mb-4">1. Information We Collect</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">We collect information you provide directly:</p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Account information (name, email, password)</li>
              <li>Payment information (processed by Stripe)</li>
              <li>API keys you choose to store (OpenAI, Telegram)</li>
              <li>Product preferences and filter settings</li>
              <li>Competitor stores you choose to monitor</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. How We Use Your Information</h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Provide and improve our Service</li>
              <li>Process payments and manage subscriptions</li>
              <li>Send product recommendations and alerts</li>
              <li>Communicate about your account</li>
              <li>Analyze usage to improve features</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. Data Storage and Security</h2>
            <p className="text-muted-foreground leading-relaxed">
              Your data is stored securely using industry-standard encryption. API keys are encrypted at rest. We use MongoDB Atlas with enterprise-grade security. Payment data is handled entirely by Stripe and never stored on our servers.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. Third-Party Services</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">We use the following third-party services:</p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li><strong>Stripe</strong> - Payment processing</li>
              <li><strong>MongoDB Atlas</strong> - Database hosting</li>
              <li><strong>Vercel/Railway</strong> - Application hosting</li>
              <li><strong>OpenAI</strong> - AI features (using your provided key)</li>
              <li><strong>Telegram</strong> - Notifications (using your provided token)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">5. Your API Keys</h2>
            <p className="text-muted-foreground leading-relaxed">
              Any API keys you provide (OpenAI, Telegram) are stored encrypted and used solely to provide features you request. Keys are never shared with third parties and can be deleted at any time from your Settings page.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">6. Data Retention</h2>
            <p className="text-muted-foreground leading-relaxed">
              We retain your data for as long as your account is active. Upon account deletion, we remove your personal data within 30 days. Anonymized analytics data may be retained longer.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">7. Your Rights</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">You have the right to:</p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Access your personal data</li>
              <li>Correct inaccurate data</li>
              <li>Delete your account and data</li>
              <li>Export your data</li>
              <li>Opt out of marketing communications</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">8. Cookies</h2>
            <p className="text-muted-foreground leading-relaxed">
              We use essential cookies for authentication and session management. We do not use tracking cookies for advertising. You can disable cookies in your browser settings.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">9. Children's Privacy</h2>
            <p className="text-muted-foreground leading-relaxed">
              Our Service is not intended for users under 18 years of age. We do not knowingly collect data from children.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">10. Changes to This Policy</h2>
            <p className="text-muted-foreground leading-relaxed">
              We may update this Privacy Policy from time to time. We will notify you of significant changes via email or in-app notification.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">11. Contact Us</h2>
            <p className="text-muted-foreground leading-relaxed">
              For privacy-related questions, contact us at privacy@dropsniper.ai
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
