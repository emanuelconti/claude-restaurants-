"""Minimal i18n: a flat string table per language, no external dependency.

Covers the languages of the marketplaces already wired up (es/fr/de/it)
plus English as the default fallback. Add a language by adding a key to
LANGUAGES and a matching dict to TRANSLATIONS — every string missing from
a language falls back to English, so partial translations never break.
"""

from __future__ import annotations

from fastapi import Request

LANGUAGES = {
    "it": "Italiano",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
}
DEFAULT_LANG = "it"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "nav.login": "Log in",
        "nav.signup": "Sign up",
        "nav.logout": "Log out",
        "landing.title": "Find the deal before anyone else does.",
        "landing.lead": "Sowld scans second-hand marketplaces across Europe and flags only the underpriced listings.",
        "landing.cta_platform": "Go to the platform",
        "landing.cta_start": "Get started",
        "signup.title": "Create your account",
        "signup.email": "Email",
        "signup.password": "Password",
        "signup.submit": "Continue to payment",
        "signup.have_account": "Already have an account? Log in",
        "signup.error_duplicate": "That email is already registered.",
        "login.title": "Log in",
        "login.email": "Email",
        "login.password": "Password",
        "login.submit": "Log in",
        "login.no_account": "No account yet? Sign up",
        "login.error_invalid": "Wrong email or password.",
        "subscribe.title": "One last step",
        "subscribe.lead": "Your account is ready, but you need an active subscription to use the search.",
        "subscribe.cta": "Subscribe now",
        "dashboard.title": "Find a deal",
        "dashboard.manage_subscription": "Manage subscription",
        "dashboard.query_placeholder": "What are you after? E.g. \"road bike\"",
        "dashboard.location_placeholder": "Which city? E.g. \"Barcelona\"",
        "dashboard.submit": "Search",
        "dashboard.col_score": "Discount",
        "dashboard.col_title": "Title",
        "dashboard.col_price": "Price",
        "dashboard.col_fair_value": "Fair value",
        "dashboard.view_link": "View →",
        "dashboard.no_results": "No deals found this time. Try another search.",
        "dashboard.beta_notice": "Marked sources are still being rolled out — results may be limited for now.",
        "dashboard.beta_suffix": " (in development)",
        "error.stripe_not_configured": "Stripe is not configured on this server yet.",
        "error.anthropic_not_configured": "ANTHROPIC_API_KEY is not configured on this server.",
    },
    "es": {
        "nav.login": "Acceder",
        "nav.signup": "Registrarse",
        "nav.logout": "Salir",
        "landing.title": "Encuentra la oferta antes que nadie.",
        "landing.lead": "Sowld rastrea los mercados de segunda mano en Europa y solo te avisa de los anuncios infravalorados.",
        "landing.cta_platform": "Ir a la plataforma",
        "landing.cta_start": "Empezar ahora",
        "signup.title": "Crea tu cuenta",
        "signup.email": "Email",
        "signup.password": "Contraseña",
        "signup.submit": "Continuar al pago",
        "signup.have_account": "¿Ya tienes cuenta? Accede",
        "signup.error_duplicate": "Ese email ya está registrado.",
        "login.title": "Acceder",
        "login.email": "Email",
        "login.password": "Contraseña",
        "login.submit": "Acceder",
        "login.no_account": "¿No tienes cuenta? Regístrate",
        "login.error_invalid": "Email o contraseña incorrectos.",
        "subscribe.title": "Un último paso",
        "subscribe.lead": "Tu cuenta está lista, pero necesitas una suscripción activa para usar la búsqueda.",
        "subscribe.cta": "Suscribirse ahora",
        "dashboard.title": "Busca una oferta",
        "dashboard.manage_subscription": "Gestionar suscripción",
        "dashboard.query_placeholder": "¿Qué buscas? Ej. \"bici de carretera\"",
        "dashboard.location_placeholder": "¿En qué ciudad? Ej. \"Barcelona\"",
        "dashboard.submit": "Buscar",
        "dashboard.col_score": "Descuento",
        "dashboard.col_title": "Título",
        "dashboard.col_price": "Precio",
        "dashboard.col_fair_value": "Valor justo",
        "dashboard.view_link": "Ver →",
        "dashboard.no_results": "No se han encontrado ofertas esta vez. Prueba otra búsqueda.",
        "dashboard.beta_notice": "Las fuentes marcadas todavía se están implementando — los resultados pueden ser limitados por ahora.",
        "dashboard.beta_suffix": " (en desarrollo)",
        "error.stripe_not_configured": "Stripe todavía no está configurado en este servidor.",
        "error.anthropic_not_configured": "ANTHROPIC_API_KEY no está configurada en este servidor.",
    },
    "fr": {
        "nav.login": "Connexion",
        "nav.signup": "S'inscrire",
        "nav.logout": "Déconnexion",
        "landing.title": "Trouvez la bonne affaire avant tout le monde.",
        "landing.lead": "Sowld scrute les marketplaces d'occasion en Europe et ne vous signale que les annonces sous-évaluées.",
        "landing.cta_platform": "Accéder à la plateforme",
        "landing.cta_start": "Commencer",
        "signup.title": "Créez votre compte",
        "signup.email": "Email",
        "signup.password": "Mot de passe",
        "signup.submit": "Continuer vers le paiement",
        "signup.have_account": "Déjà un compte ? Connexion",
        "signup.error_duplicate": "Cet email est déjà utilisé.",
        "login.title": "Connexion",
        "login.email": "Email",
        "login.password": "Mot de passe",
        "login.submit": "Connexion",
        "login.no_account": "Pas encore de compte ? Inscrivez-vous",
        "login.error_invalid": "Email ou mot de passe incorrect.",
        "subscribe.title": "Une dernière étape",
        "subscribe.lead": "Votre compte est prêt, mais un abonnement actif est nécessaire pour utiliser la recherche.",
        "subscribe.cta": "S'abonner",
        "dashboard.title": "Trouver une affaire",
        "dashboard.manage_subscription": "Gérer l'abonnement",
        "dashboard.query_placeholder": "Que cherchez-vous ? Ex. \"vélo de route\"",
        "dashboard.location_placeholder": "Dans quelle ville ? Ex. \"Barcelone\"",
        "dashboard.submit": "Rechercher",
        "dashboard.col_score": "Remise",
        "dashboard.col_title": "Titre",
        "dashboard.col_price": "Prix",
        "dashboard.col_fair_value": "Juste valeur",
        "dashboard.view_link": "Voir →",
        "dashboard.no_results": "Aucune affaire trouvée cette fois. Essayez une autre recherche.",
        "dashboard.beta_notice": "Les sources marquées sont encore en cours de déploiement — les résultats peuvent être limités pour l'instant.",
        "dashboard.beta_suffix": " (en développement)",
        "error.stripe_not_configured": "Stripe n'est pas encore configuré sur ce serveur.",
        "error.anthropic_not_configured": "ANTHROPIC_API_KEY n'est pas configurée sur ce serveur.",
    },
    "de": {
        "nav.login": "Anmelden",
        "nav.signup": "Registrieren",
        "nav.logout": "Abmelden",
        "landing.title": "Finde das Schnäppchen vor allen anderen.",
        "landing.lead": "Sowld durchsucht Gebrauchtmarktplätze in ganz Europa und meldet dir nur unterbewertete Angebote.",
        "landing.cta_platform": "Zur Plattform",
        "landing.cta_start": "Jetzt starten",
        "signup.title": "Konto erstellen",
        "signup.email": "E-Mail",
        "signup.password": "Passwort",
        "signup.submit": "Weiter zur Zahlung",
        "signup.have_account": "Schon ein Konto? Anmelden",
        "signup.error_duplicate": "Diese E-Mail ist bereits registriert.",
        "login.title": "Anmelden",
        "login.email": "E-Mail",
        "login.password": "Passwort",
        "login.submit": "Anmelden",
        "login.no_account": "Noch kein Konto? Registrieren",
        "login.error_invalid": "E-Mail oder Passwort falsch.",
        "subscribe.title": "Ein letzter Schritt",
        "subscribe.lead": "Dein Konto ist bereit, aber du brauchst ein aktives Abo, um die Suche zu nutzen.",
        "subscribe.cta": "Jetzt abonnieren",
        "dashboard.title": "Schnäppchen finden",
        "dashboard.manage_subscription": "Abo verwalten",
        "dashboard.query_placeholder": "Wonach suchst du? Z. B. \"Rennrad\"",
        "dashboard.location_placeholder": "In welcher Stadt? Z. B. \"Berlin\"",
        "dashboard.submit": "Suchen",
        "dashboard.col_score": "Rabatt",
        "dashboard.col_title": "Titel",
        "dashboard.col_price": "Preis",
        "dashboard.col_fair_value": "Fairer Wert",
        "dashboard.view_link": "Ansehen →",
        "dashboard.no_results": "Diesmal keine Schnäppchen gefunden. Versuch eine andere Suche.",
        "dashboard.beta_notice": "Markierte Quellen befinden sich noch im Aufbau — Ergebnisse können momentan eingeschränkt sein.",
        "dashboard.beta_suffix": " (in Entwicklung)",
        "error.stripe_not_configured": "Stripe ist auf diesem Server noch nicht konfiguriert.",
        "error.anthropic_not_configured": "ANTHROPIC_API_KEY ist auf diesem Server nicht konfiguriert.",
    },
    "it": {
        "nav.login": "Accedi",
        "nav.signup": "Registrati",
        "nav.logout": "Esci",
        "landing.title": "Trova l'affare prima di chiunque altro.",
        "landing.lead": "Sowld cerca tra i marketplace dell'usato in Europa e ti segnala solo gli annunci sottoprezzati.",
        "landing.cta_platform": "Vai alla piattaforma",
        "landing.cta_start": "Inizia ora",
        "signup.title": "Crea il tuo account",
        "signup.email": "Email",
        "signup.password": "Password",
        "signup.submit": "Crea account",
        "signup.have_account": "Hai già un account? Accedi",
        "signup.error_duplicate": "Email già registrata.",
        "login.title": "Accedi",
        "login.email": "Email",
        "login.password": "Password",
        "login.submit": "Accedi",
        "login.no_account": "Non hai un account? Registrati",
        "login.error_invalid": "Email o password errati.",
        "subscribe.title": "Un ultimo passo",
        "subscribe.lead": "Il tuo account è pronto, ma serve un abbonamento attivo per usare la ricerca.",
        "subscribe.cta": "Abbonati ora",
        "dashboard.title": "Trova un affare",
        "dashboard.manage_subscription": "Gestisci abbonamento",
        "dashboard.query_placeholder": "Cosa cerchi? Es. \"bici da corsa\"",
        "dashboard.location_placeholder": "In che città? Es. \"Barcellona\"",
        "dashboard.submit": "Cerca",
        "dashboard.col_score": "Sconto",
        "dashboard.col_title": "Titolo",
        "dashboard.col_price": "Prezzo",
        "dashboard.col_fair_value": "Valore giusto",
        "dashboard.view_link": "Vedi →",
        "dashboard.no_results": "Nessun affare trovato questa volta. Prova un'altra ricerca.",
        "dashboard.beta_notice": "Le fonti contrassegnate sono ancora in fase di attivazione — i risultati potrebbero essere limitati per ora.",
        "dashboard.beta_suffix": " (in sviluppo)",
        "error.stripe_not_configured": "Stripe non è ancora configurato su questo server.",
        "error.anthropic_not_configured": "ANTHROPIC_API_KEY non è configurata su questo server.",
    },
}


def resolve_language(request: Request) -> str:
    """?lang= wins and is remembered; otherwise session, then browser, then default."""
    requested = request.query_params.get("lang")
    if requested in TRANSLATIONS:
        request.session["lang"] = requested
        return requested

    session_lang = request.session.get("lang")
    if session_lang in TRANSLATIONS:
        return session_lang

    accept_language = request.headers.get("accept-language", "")
    for part in accept_language.split(","):
        code = part.split(";")[0].strip().split("-")[0].lower()
        if code in TRANSLATIONS:
            return code

    return DEFAULT_LANG


def get_translator(lang: str):
    strings = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    fallback = TRANSLATIONS["en"]

    def t(key: str) -> str:
        return strings.get(key) or fallback.get(key) or key

    return t
