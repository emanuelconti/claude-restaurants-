// Vercel serverless function — crea una Stripe Checkout Session in modalità TEST.
// Richiede STRIPE_SECRET_KEY come environment variable (mai hardcoded).
// Non collegata a nessun account reale finché non configuri le env var su Vercel.
//
// Deploy: piazza questo file in /api/create-checkout-session.js in un progetto Vercel
// (Node runtime). Nessuna dipendenza a pagamento: usa il pacchetto ufficiale "stripe" (free/OSS).

const Stripe = require('stripe');

const PRICE_CATALOG = {
  pilot_essential: { amount: 49000, name: 'SocialPerks — Pilota Essenziale (4 settimane)' },
  pilot_standard: { amount: 120000, name: 'SocialPerks — Pilota Standard (4 settimane)' },
};

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const secretKey = process.env.STRIPE_SECRET_KEY;
  if (!secretKey) {
    // Fail loudly instead of silently — no test/live key means no real checkout should happen.
    res.status(500).json({ error: 'STRIPE_SECRET_KEY non configurata. Vedi payments/README.md.' });
    return;
  }

  const { productId, customerEmail, businessName } = req.body || {};
  const product = PRICE_CATALOG[productId];
  if (!product) {
    res.status(400).json({ error: `productId sconosciuto: ${productId}` });
    return;
  }

  const stripe = Stripe(secretKey);

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      payment_method_types: ['card'],
      customer_email: customerEmail,
      line_items: [
        {
          price_data: {
            currency: 'eur',
            product_data: { name: product.name },
            unit_amount: product.amount,
          },
          quantity: 1,
        },
      ],
      metadata: { businessName: businessName || '' },
      success_url: process.env.SUCCESS_URL || 'http://localhost:3000/success.html',
      cancel_url: process.env.CANCEL_URL || 'http://localhost:3000/cancel.html',
    });

    res.status(200).json({ url: session.url });
  } catch (err) {
    // Log server-side, never leak Stripe internals to the client.
    console.error('Stripe checkout session error:', err.message);
    res.status(500).json({ error: 'Impossibile creare la sessione di pagamento. Riprova più tardi.' });
  }
};
