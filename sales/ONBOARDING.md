# ONBOARDING — dal pagamento al giorno 1

1. **Conferma pagamento ricevuta** (webhook Stripe test → vedi `payments/README.md`) →
   invio automatico email di benvenuto (template in `payments/emails/welcome.md`).
2. **Raccolta materiali dal cliente** (form breve, 5 campi max):
   - Accesso/permesso a vedere Google Business e Instagram (no credenziali, solo visualizzazione)
   - Orari reali di apertura e fasce percepite come "calme"
   - Scontrino medio approssimativo (per stimare il valore di uno slot pieno)
   - Eventuali promozioni passate e risultati (se noti)
   - Referente unico per la comunicazione durante il pilota
3. **Kickoff call 15 min** entro 48h dal pagamento — usare `sales/DISCOVERY_CALL.md` come
   base se non già fatta in fase di vendita.
4. **Setup interno**: creare riga cliente nella pipeline (`docs/STATUS.md` / CRM), impostare
   promemoria per report settimana 1, 2, 3, 4.
