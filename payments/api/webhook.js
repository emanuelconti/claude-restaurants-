// Vercel serverless function — riceve gli eventi webhook di Stripe (modalità TEST finché
// STRIPE_SECRET_KEY è una chiave sk_test_...).
// Registra lo stato del pagamento e prepara (non invia automaticamente) l'email di
// onboarding — l'invio reale resta un checkpoint umano finché non è validato il flusso.

const Stripe = require('stripe');

// Vercel: disabilita il body parsing di default per poter verificare la firma raw del webhook.
module.exports.config = { api: { bodyParser: false } };

function buffer(readable) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    readable.on('data', (chunk) => chunks.push(chunk));
    readable.on('end', () => resolve(Buffer.concat(chunks)));
    readable.on('error', reject);
  });
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).send('Method not allowed');
    return;
  }

  const secretKey = process.env.STRIPE_SECRET_KEY;
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secretKey || !webhookSecret) {
    console.error('Stripe non configurato: mancano STRIPE_SECRET_KEY o STRIPE_WEBHOOK_SECRET.');
    res.status(500).send('Stripe non configurato');
    return;
  }

  const stripe = Stripe(secretKey);
  const sig = req.headers['stripe-signature'];
  const rawBody = await buffer(req);

  let event;
  try {
    event = stripe.webhooks.constructEvent(rawBody, sig, webhookSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    res.status(400).send(`Webhook Error: ${err.message}`);
    return;
  }

  // Idempotency guard: in produzione, controlla event.id contro uno storico
  // (es. tabella Supabase) prima di processare, per evitare doppie registrazioni
  // se Stripe reinvia lo stesso evento.

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object;
      console.log('✅ Pagamento completato:', {
        email: session.customer_email,
        amount: session.amount_total,
        businessName: session.metadata && session.metadata.businessName,
      });
      // TODO (checkpoint): qui si aggancerebbe la scrittura su un DB reale (es. Supabase)
      // e l'invio dell'email di onboarding (vedi payments/emails/welcome.md) — non
      // automatizzato di default, per evitare invii accidentali prima che il flusso sia
      // stato verificato end-to-end in modalità test.
      break;
    }
    default:
      console.log(`Evento Stripe non gestito: ${event.type}`);
  }

  res.status(200).json({ received: true });
};
