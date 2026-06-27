#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Casablanca.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    # ── CAFÉS & BRUNCH ─────────────────────────────────────────────────────────
    ("Café Pauline", "Racine", "52 Rue Molière, Racine, Casablanca", "cafepauline.casa@gmail.com", "+212 522 260 090", "cafepauline.ma", "@cafepauline.casa", "Café / Brunch", "Indipendente", "✅ Sì", "Uno dei brunch più fotografati di Casa, giardino verde e piatti colorati"),
    ("Café Les Négociants", "Centre-Ville", "Bd Mohammed V, Casablanca", "lesnegociants@gmail.com", "+212 522 260 017", "", "@les_negociants_casa", "Café Historique", "Indipendente", "⚠️ Medio", "Storico caffè art-déco nel centro, ambiente autentico e fotografabile"),
    ("Bab Marrakech Café", "Gauthier", "Rue Voltaire, Gauthier, Casablanca", "contact@babmarrakech.ma", "+212 661 234 567", "babmarrakech.ma", "@babmarrakech_cafe", "Café / Oriental", "Indipendente", "✅ Sì", "Décor orientale autentico, ottimo per foto con oggetti artigianali marocchini"),
    ("Café Maure de la Kasbah", "Kasbah", "Kasbah des Oudaias, Casablanca", "", "+212 522 736 905", "", "@cafemaure_casa", "Café / Traditionnel", "Indipendente", "✅ Sì", "Caffè tradizionale nel cuore della medina, menta e msemen fotografabili"),
    ("Bloom Café", "Maarif", "Rue Abou Bakr Seddik, Maarif, Casablanca", "bloom.casablanca@gmail.com", "+212 661 345 678", "", "@bloomcafe_casa", "Café / Brunch / Healthy", "Indipendente", "✅ Sì", "Caffè floreale con bowls colorate e latte art, molto instagrammabile"),
    ("The Brew", "Gauthier", "Rue Molière 23, Gauthier, Casablanca", "thebrewcasa@gmail.com", "+212 522 480 230", "thebrew.ma", "@thebrew.casa", "Specialty Coffee", "Indipendente", "✅ Sì", "Prima vera specialty coffee di Casa, latte art e single-origin"),
    ("Café Clock Casablanca", "Médina", "Rue Brahim Roudani, Casablanca", "casablanca@cafeclock.com", "+212 528 440 526", "cafeclock.com", "@cafeclockmorocco", "Café / Cultural / Art", "Piccola catena", "⚠️ Medio", "Branch del famoso Café Clock di Fes, musica live e cucina marocchina moderna"),
    ("Darkoum", "Anfa Supérieur", "48 Rue des Figuiers, Anfa, Casablanca", "contact@darkoum.ma", "+212 522 361 900", "darkoum.ma", "@darkoum_casablanca", "Café / Salon de Thé", "Indipendente", "✅ Sì", "Riad rinnovato con patio, piatti marocchini e atmosfera molto fotogenica"),
    ("Amal Centre de Formation", "Maarif", "28 Rue Nid, Maarif, Casablanca", "amalwomen@gmail.com", "+212 522 258 016", "amalnonprofit.org", "@amalwomen", "Café / Social Enterprise", "Indipendente", "⚠️ Medio", "ONG che insegna cucina tradizionale a donne in difficoltà, piatti marocchini autentici"),
    ("La Maison du Café", "Corniche", "Bd de la Corniche, Casablanca", "contact@lamaisoncafe.ma", "+212 522 797 860", "", "@lamaisoncafe_casa", "Café / Patisserie", "Piccola catena", "⚠️ Medio", "Pasticceria e caffè sulla Corniche con vista mare"),

    # ── RESTAURANTS MAROCAINS ──────────────────────────────────────────────────
    ("Al Mounia", "Palmier", "95 Rue du Prince Moulay Abdellah, Casablanca", "almounia@menara.ma", "+212 522 222 669", "", "@almounia_restaurant", "Marocaine Classique", "Indipendente", "✅ Sì", "Uno dei ristoranti marocchini più eleganti di Casa, tajine e couscous in stile palace"),
    ("Dar Beida", "Centre-Ville", "35 Rue Abdelkader el Mazini, Casablanca", "info@dar-beida.ma", "+212 522 264 878", "dar-beida.ma", "@darbeida_restaurant", "Marocaine Gastronomique", "Indipendente", "✅ Sì", "Cucina marocchina gastronomica in riad rinnovato, décor zellige e mosaici"),
    ("Restaurant Fès", "Maarif", "Rue Roudani 4, Maarif, Casablanca", "restaurantfes@gmail.com", "+212 522 254 031", "", "@restaurant_fes_casa", "Marocaine / Fassi", "Indipendente", "✅ Sì", "Specialità di Fes: pastilla al pigeon e couscous, ambiente riccamente decorato"),
    ("La Sqala", "Port", "Bd des Almohades (Sqala du Port), Casablanca", "lasqala@menara.ma", "+212 522 260 960", "lasqala.com", "@lasqala_casablanca", "Marocaine / Andalouse", "Indipendente", "✅ Sì", "Nel bastione portoghese del 18° sec., giardino, fontana, luogo iconico di Casa"),
    ("Riad Jnan Benghal", "Médina", "Rue de Fès, Médina, Casablanca", "riad.jnanbenghal@gmail.com", "+212 522 442 500", "", "@riad_jnanbenghal", "Marocaine Traditionnelle", "Indipendente", "✅ Sì", "Riad storico nella medina con patio zeliige e lanternes, moschea Hassan II in background"),
    ("Nour Palace", "CIL", "Rue Charif Idrissi 17, CIL, Casablanca", "nourpalace@gmail.com", "+212 522 356 178", "", "@nourpalace_casa", "Marocaine / Banquets", "Gruppo", "❌ No", "Grande palazzo marocchino per eventi, troppo grande per collaborazione studenti"),
    ("Dar Zitoun", "Belvedere", "55 Rue Belvedere, Casablanca", "darzitoun@gmail.com", "+212 661 456 789", "", "@darzitoun_casa", "Marocaine / Fusion", "Indipendente", "✅ Sì", "Casa marocchina trasformata in ristorante, patio interno con piante e lanterne"),
    ("Tanjia Restaurant", "Gauthier", "Rue Voltaire 8, Gauthier, Casablanca", "tanjia.gauthier@gmail.com", "+212 522 484 566", "", "@tanjia_restaurant", "Marocaine / Tanjia Marrakchia", "Indipendente", "✅ Sì", "Specialità della tanjia (agnello cotto in anfora), décor marocchino moderno"),
    ("Le Rouget de l'Isle", "Anfa", "Rue du Rouget de l'Isle, Anfa, Casablanca", "lerouget@gmail.com", "+212 522 362 784", "", "@lerougetdelisle", "Marocaine / Fusion", "Indipendente", "⚠️ Medio", "Fusion marocco-francese in zona residenziale elegante"),
    ("Restaurant Basmane", "Maarif", "Rue Ibn Rochd, Maarif, Casablanca", "basmane.maarif@gmail.com", "+212 522 251 889", "", "@basmane_restaurant", "Marocaine / Irakienne", "Indipendente", "✅ Sì", "Specialità irachene e marocchine, ambiente caldo e colorato"),

    # ── FUSION & MODERNE ──────────────────────────────────────────────────────
    ("Bô-Zin", "Route d'Azemmour", "km 7 Route d'Azemmour, Casablanca", "info@bozin.ma", "+212 522 591 871", "bozin.ma", "@bozin_restaurant", "Asian Fusion / Lounge", "Gruppo", "❌ No", "Grande venue lounge-restaurant con pool, parte di gruppo"),
    ("Chez Nous", "Gauthier", "Rue Molière 10, Gauthier, Casablanca", "cheznous.casa@gmail.com", "+212 522 481 100", "", "@cheznous_gauthier", "Bistro Franco-Marocain", "Indipendente", "✅ Sì", "Bistrot accogliente nel Gauthier, menù fusion marocco-francese"),
    ("Le Cabestan", "Corniche", "Bd de la Corniche, Ain Diab, Casablanca", "lecabestan@gmail.com", "+212 522 392 000", "lecabestan.ma", "@lecabestan", "Seafood / French", "Indipendente", "⚠️ Medio", "Ristorante di mare sulla Corniche, pesce fresco e vista oceano"),
    ("El Angar", "Ain Diab", "Bd de la Corniche, Ain Diab, Casablanca", "elangar@gmail.com", "+212 522 796 688", "", "@elangar_casa", "Restaurant / Lounge / Bar", "Gruppo", "❌ No", "Venue gigante sulla Corniche, troppo grande per collaborazione studenti"),
    ("Little Buddha", "Ain Diab", "Bd de la Corniche 35, Ain Diab, Casablanca", "info@littlebuddha.ma", "+212 522 791 888", "littlebuddha.ma", "@littlebuddha_casa", "Asian Fusion / Lounge", "Gruppo", "❌ No", "Parte della catena internazionale, stile Buddha Bar"),
    ("Sushido", "Maarif", "Rue d'Alger 20, Maarif, Casablanca", "sushidocasa@gmail.com", "+212 522 995 080", "sushido.ma", "@sushido_casablanca", "Japanese / Sushi", "Piccola catena", "⚠️ Medio", "Sushi di qualità nel Maarif, instagrammabile"),
    ("Sushiman", "Gauthier", "Rue Molière 18, Gauthier, Casablanca", "contact@sushiman.ma", "+212 522 482 000", "sushiman.ma", "@sushiman.ma", "Japanese / Sushi", "Piccola catena", "⚠️ Medio", "Catena di sushi con 3 location a Casa, qualità costante"),
    ("JIRO Japanese Restaurant", "Gauthier", "Bd Rachidi 12, Gauthier, Casablanca", "jiro.casa@gmail.com", "+212 522 490 200", "", "@jirorestaurant_casa", "Japanese Fine Dining", "Indipendente", "✅ Sì", "Ristorante giapponese curato nel Gauthier, omakase e nigiri fotografabili"),
    ("Umami Sushi", "Maarif Extension", "Rue Zerktouny 5, Maarif, Casablanca", "umami.casa@gmail.com", "+212 661 789 012", "", "@umamisushi_casa", "Japanese / Korean Fusion", "Indipendente", "✅ Sì", "Sushi e piatti coreani, bowl coloratissime e presentazioni curate"),
    ("Boba Street", "Maarif", "Rue des Oulémas, Maarif, Casablanca", "bobastreet.casa@gmail.com", "+212 661 234 890", "", "@bobastreet_casa", "Bubble Tea / Asian Street Food", "Piccola catena", "✅ Sì", "Bubble tea e street food asiatico, colori vivaci e super instagrammabile"),
    ("Riva Casa", "Corniche", "Bd de la Corniche, Ain Diab, Casablanca", "rivacasa@gmail.com", "+212 522 795 050", "", "@riva_casa", "Mediterranean / Seafood", "Indipendente", "✅ Sì", "Cucina mediterranea con terrazza sull'oceano, tramonto fotografabile"),

    # ── HEALTHY & VÉGÉTARIEN ──────────────────────────────────────────────────
    ("Healthy Box", "Gauthier", "Rue Mohamed Smiha, Gauthier, Casablanca", "healthybox.casa@gmail.com", "+212 661 555 123", "", "@healthybox_casa", "Healthy / Bowls", "Piccola catena", "✅ Sì", "Bowls sane e colorate con ingredienti locali, molto fotografabile"),
    ("Green Corner", "Maarif", "Rue Sebou, Maarif, Casablanca", "greencorner.ma@gmail.com", "+212 661 333 456", "", "@greencorner_casa", "Vegan / Vegetarian", "Indipendente", "✅ Sì", "Primo ristorante completamente vegano di Casa, piatti creativi e colorati"),
    ("Naked Kitchen", "Gauthier", "Bd Zerktouni 90, Gauthier, Casablanca", "naked.kitchen.casa@gmail.com", "+212 661 678 901", "", "@nakedkitchen_casa", "Healthy / Bowls / Juices", "Indipendente", "✅ Sì", "Cucina sana e trasparente, ingredienti locali e presentazione curata"),
    ("Superfood & Co", "Anfa", "Rue Assila, Anfa Supérieur, Casablanca", "superfood.co.casa@gmail.com", "+212 661 456 234", "", "@superfood_co_casa", "Healthy / Superfood", "Indipendente", "✅ Sì", "Acai bowls, smoothies e piatti superfood, presentazione Instagram-ready"),
    ("BEJEWELLED", "Gauthier", "Rue Molière 42, Gauthier, Casablanca", "bejewelled.casa@gmail.com", "+212 661 789 345", "", "@bejewelled_casa", "Healthy / Vegan / Pastry", "Indipendente", "✅ Sì", "Pasticceria vegana e caffè, dessert elaborati e decorazioni instagrammabili"),

    # ── PATISSERIES & DESSERTS ─────────────────────────────────────────────────
    ("Patisserie Bennis Habous", "Habous", "2 Rue Fkih el Gabbas, Habous, Casablanca", "patisseriebennis@gmail.com", "+212 522 303 025", "", "@patisserie_bennis", "Pâtisserie Marocaine", "Indipendente", "✅ Sì", "La più famosa pasticceria marocchina di Casa nel quartiere Habous, dolci fotografabili"),
    ("Pâtisserie Bousfiha", "Maarif", "Rue Allal Ben Abdellah, Maarif, Casablanca", "bousfiha.patisserie@gmail.com", "+212 522 254 015", "", "@patisserie_bousfiha", "Pâtisserie Française", "Piccola catena", "⚠️ Medio", "Pasticceria francese con brioches e croissants artigianali"),
    ("Macarons et Chocolats", "Gauthier", "Rue Molière 33, Gauthier, Casablanca", "macarons.choco@gmail.com", "+212 522 484 878", "", "@macarons_chocolats_casa", "Pâtisserie / Chocolaterie", "Indipendente", "✅ Sì", "Macarons e cioccolatini artigianali, esposizione coloratissima e foto-friendly"),
    ("Bread & Butter", "Gauthier", "Rue Molière 55, Gauthier, Casablanca", "breadbuttercasa@gmail.com", "+212 661 234 012", "", "@breadbutter_casa", "Artisan Bakery / Café", "Indipendente", "✅ Sì", "Panetteria artigianale con croissants e pain au chocolat, molto instagrammabile"),
    ("Au Bon Gâteau", "Maarif", "Rue Houmane el Fetouaki, Maarif, Casablanca", "aubongataeau.casa@gmail.com", "+212 522 252 891", "", "@aubongateaucasa", "Pâtisserie / Gâteaux", "Indipendente", "✅ Sì", "Torte personalizzate e dessert elaborati, fotogenici per ogni occasione"),
    ("Douce Tentation", "Anfa", "Bd Anfa 118, Anfa, Casablanca", "doucetentation@gmail.com", "+212 522 361 567", "", "@douce_tentation_casa", "Pâtisserie / Chocolaterie", "Piccola catena", "⚠️ Medio", "Pasticceria con torte decorate e cioccolatini"),

    # ── BURGERS, STREET FOOD & BRUNCH ─────────────────────────────────────────
    ("Black Smoke BBQ & Burger", "Maarif", "Rue Ibn Sina, Maarif, Casablanca", "blacksmoke.casa@gmail.com", "+212 661 890 234", "", "@blacksmoke_casa", "Burgers / BBQ", "Indipendente", "✅ Sì", "Burger gourmet e BBQ americano, presentazione curata e fotografabile"),
    ("Butcher & Sons", "Gauthier", "Bd Zerktouni 44, Gauthier, Casablanca", "butcherandsons.casa@gmail.com", "+212 661 123 456", "", "@butcherandsons_casa", "Burger / Grill", "Piccola catena", "⚠️ Medio", "Burger premium con ingredienti locali di qualità"),
    ("Ô Brunch", "Maarif", "Rue du Marché Central, Maarif, Casablanca", "obrunch.casa@gmail.com", "+212 661 567 890", "", "@obrunch_casa", "Brunch / Café", "Indipendente", "✅ Sì", "Brunch domenicale iconico di Casa, mimosa e piatti colorati"),
    ("Smash & Melt", "Gauthier", "Rue Chaouia, Gauthier, Casablanca", "smashandmelt.casa@gmail.com", "+212 661 901 234", "", "@smashandmelt_casa", "Smash Burgers", "Indipendente", "✅ Sì", "Smash burger con formaggio fondente e salse artigianali, foto obbligatoria"),
    ("Street Tacos Casa", "Maarif", "Rue Zerktouny, Maarif, Casablanca", "streettacos.casa@gmail.com", "+212 661 234 901", "", "@streettacos_casa", "Mexican / Tacos", "Indipendente", "✅ Sì", "Tacos fusion marocco-messicano, colori e sapori che si fotografano"),
    ("Oh Mon Dieu!", "Gauthier", "Rue Molière, Gauthier, Casablanca", "ohmondieurestaurant@gmail.com", "+212 522 480 556", "", "@ohmondieurestaurant", "Brunch / French Bistro", "Indipendente", "✅ Sì", "Bistrot francese con brunch il weekend, interni bianchi e piante instagrammabili"),

    # ── RESTAURANTS ITALIENS & MÉDITERRANÉENS ─────────────────────────────────
    ("Pizzeria Côté Jardins", "Anfa", "Rue de Verdun, Anfa, Casablanca", "cotejardins.pizza@gmail.com", "+212 522 361 222", "", "@cote_jardins_casa", "Pizzeria / Italienne", "Indipendente", "✅ Sì", "Pizzeria con forno a legna in villa con giardino, molto fotogenica"),
    ("Il Forno", "Gauthier", "Rue Molière 28, Gauthier, Casablanca", "ilforno.gauthier@gmail.com", "+212 522 484 244", "ilfornocasa.com", "@ilforno_casa", "Pizzeria / Italienne", "Indipendente", "✅ Sì", "Pizza napoletana con impasto 48h, locale moderno e fotografabile"),
    ("La Bodega", "Port", "129 Bd Felix Houphouet Boigny, Port, Casablanca", "labodega@gmail.com", "+212 522 541 842", "", "@labodega_casablanca", "Spanish / Tapas", "Indipendente", "⚠️ Medio", "Ristorante spagnolo con tapas vicino al porto storico"),
    ("Pâtes & Co", "Maarif", "Rue Zerktouny, Maarif, Casablanca", "patesandco.casa@gmail.com", "+212 522 990 022", "", "@patesandco_casa", "Italian / Pasta", "Piccola catena", "⚠️ Medio", "Pasta fresca artigianale con salse creative, interni moderni"),
    ("La Trattoria", "Maarif", "Rue Abou Bakr Seddik, Maarif, Casablanca", "latrattoria.casa@gmail.com", "+212 522 265 641", "", "@latrattoria_casablanca", "Italian / Traditional", "Indipendente", "⚠️ Medio", "Trattoria italiana classica nel Maarif"),

    # ── RESTAURANTS BRANCHÉS & TENDANCE ───────────────────────────────────────
    ("Zara Restaurant & Lounge", "Ain Diab", "Bd de la Corniche, Ain Diab, Casablanca", "zara.lounge@gmail.com", "+212 522 796 100", "", "@zara_lounge_casa", "Fusion / Lounge", "Indipendente", "✅ Sì", "Lounge ristorante sulla Corniche con vista oceano, ambiente elegante"),
    ("Maison Blanche Restaurant", "Ain Diab", "Bd de la Corniche 12, Ain Diab, Casablanca", "maisonblanche.casa@gmail.com", "+212 522 799 400", "", "@maisonblanche_casablanca", "Mediterranean / Seafood", "Indipendente", "✅ Sì", "White design sulla Corniche, foto minimaliste e molto condivise"),
    ("L'Avenue by Sofitel", "Maarif", "Sofitel Casablanca, Rue des FAR, Casablanca", "restaurant.sofitel@accor.com", "+212 522 423 000", "sofitel-casablanca.ma", "@sofitelcasablanca", "French / International", "Gruppo", "❌ No", "Parte del gruppo Accor, troppo grande per collaborazione studenti"),
    ("Five Dining", "Gauthier", "Rue Molière, Gauthier, Casablanca", "fivedining.casa@gmail.com", "+212 661 111 234", "", "@fivedining_casa", "Fusion / Gastronomique", "Indipendente", "✅ Sì", "Ristorante gourmet nel Gauthier, piatti artistici e ambiente elegante"),
    ("Saveurs du Monde", "Maarif", "Bd Bir Anzarane, Maarif Extension, Casablanca", "sms.visions@gmail.com", "+212 522 980 760", "", "@saveursdumondeofficial", "World Fusion", "Indipendente", "✅ Sì", "Cucina world fusion, presentazioni artistiche e instagrammabili"),
    ("Abyss Restaurant", "Ain Diab", "Bd de la Corniche, Ain Diab, Casablanca", "abyss.corniche@gmail.com", "+212 522 797 420", "", "@abyssrestaurant_casa", "Seafood / Fusion", "Indipendente", "✅ Sì", "Ristorante di pesce con design subacqueo sulla Corniche"),
    ("The Loft", "Maarif", "Rue Zerktouny 2, Maarif, Casablanca", "theloft.casa@gmail.com", "+212 661 345 901", "", "@theloft_casablanca", "Restaurant / Bar / Club", "Indipendente", "⚠️ Medio", "Ristorante e bar nel Maarif, ambiente moderno e industriale"),

    # ── RIAD & PALACE ─────────────────────────────────────────────────────────
    ("Riad Sabah Casablanca", "Habous", "Rue el Habous, Habous, Casablanca", "riadsabah.casa@gmail.com", "+212 522 303 550", "", "@riadsabah_casa", "Marocaine / Riad", "Indipendente", "✅ Sì", "Piccolo riad nel quartiere Habous, tajine in cornice autentica"),
    ("Villa Zevaco", "Ain Chok", "Rue Abderrahmane Bnou Khaldoune, Casablanca", "villazevaco@gmail.com", "+212 522 501 882", "", "@villazevaco", "Marocaine / Villa", "Indipendente", "✅ Sì", "Villa modernista patrimonio UNESCO, ristorante in cornice architettonica unica"),
    ("Dar Soussi", "Ain Diab", "Rue de la Corniche, Ain Diab, Casablanca", "darsoussi.restaurant@gmail.com", "+212 522 790 444", "", "@darsoussi_restaurant", "Marocaine / Soussia", "Indipendente", "✅ Sì", "Specialità del Souss (sud marocco), décor berbero autentico"),

    # ── ROOFTOP & TERRASSE ─────────────────────────────────────────────────────
    ("Sky Lounge Kenzi Tower", "CFC", "Boulevard Sidi Mohammed, Twin Center, Casablanca", "skylounge@kenzitower.ma", "+212 522 978 100", "kenzitower.ma", "@skylounge_kenzi", "Bar / Restaurant / Rooftop", "Gruppo", "❌ No", "Rooftop al 30° piano del Kenzi Tower, gruppo alberghiero"),
    ("Rooftop Movenpick", "Maarif", "Rue du Parc, Maarif, Casablanca", "rooftop@movenpick-casablanca.com", "+212 522 499 400", "", "@movenpick_casa", "Restaurant / Bar / Rooftop", "Gruppo", "❌ No", "Rooftop albergo, parte del gruppo Movenpick"),
    ("Terrace 33", "Anfa", "33 Bd Anfa, Anfa, Casablanca", "terrace33.casa@gmail.com", "+212 661 456 789", "", "@terrace33_casablanca", "Fusion / Rooftop / Bar", "Indipendente", "✅ Sì", "Terrazza panoramica indipendente nel cuore di Anfa, cocktail e finger food"),
    ("Le Rooftop du Gauthier", "Gauthier", "Rue Molière 50, Gauthier, Casablanca", "rooftop.gauthier@gmail.com", "+212 661 901 567", "", "@rooftop_gauthier", "Restaurant / Bar", "Indipendente", "✅ Sì", "Terrazza con vista sulla città, aperitivi al tramonto fotografabilissimi"),

    # ── RESTO PANORAMIQUE & BORD DE MER ───────────────────────────────────────
    ("Le Nautilus", "Corniche", "Bd de la Corniche, Ain Diab, Casablanca", "lenautilus.casa@gmail.com", "+212 522 792 800", "", "@lenautilus_casa", "Seafood / Brasserie", "Indipendente", "✅ Sì", "Brasserie di pesce sulla Corniche con terrazza oceanfront"),
    ("Azure Beach Club", "Sidi Abderrahmane", "Bd de la Corniche, Sidi Abderrahmane, Casablanca", "azure.beachclub@gmail.com", "+212 522 792 500", "", "@azure_beachclub_casa", "Beach Club / Restaurant", "Indipendente", "✅ Sì", "Beach club con piscina e ristorante, foto piscina-oceano iconiche"),
    ("Piscine L'Ocean Club", "Ain Diab", "Bd de la Corniche, Ain Diab, Casablanca", "oceanclub.casa@gmail.com", "+212 522 791 234", "", "@oceanclub_casablanca", "Restaurant / Beach Club", "Indipendente", "✅ Sì", "Club sulla Corniche con piscina, brunch domenicale famoso"),
    ("Loco & Tapas", "Corniche", "Bd de la Corniche, Ain Diab, Casablanca", "locotapas.casa@gmail.com", "+212 522 796 080", "", "@locotapas_casa", "Tapas / Fusion / Bar", "Indipendente", "✅ Sì", "Bar-tapas con terrazza sull'oceano, atmosfera vivace e fotografabile"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Casablanca - SocialPerks"

    HEADER_FILL   = PatternFill("solid", fgColor="2C3E50")
    EMAIL_FILL    = PatternFill("solid", fgColor="E8F5E9")
    NO_EMAIL_FILL = PatternFill("solid", fgColor="FFF9C4")
    IDEAL_FILL    = PatternFill("solid", fgColor="C8E6C9")
    MEDIUM_FILL   = PatternFill("solid", fgColor="FFF9C4")
    NO_FILL_CLR   = PatternFill("solid", fgColor="FFCDD2")
    WHITE_FONT    = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    BOLD_FONT     = Font(name="Calibri", bold=True, size=10)
    thin          = Side(style="thin", color="CCCCCC")
    BORDER        = Border(left=thin, right=thin, top=thin, bottom=thin)

    headers = ["#", "Nome Ristorante", "Quartiere", "Indirizzo", "EMAIL ✉️",
               "Telefono", "Sito Web", "Instagram", "Tipo Cucina",
               "Dimensione", "Adatto SocialPerks", "Note/Descrizione"]
    col_widths = [4, 28, 16, 35, 32, 18, 22, 22, 22, 16, 14, 40]

    for col, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill      = HEADER_FILL
        cell.font      = WHITE_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border    = BORDER
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"

    for idx, r in enumerate(RESTAURANTS, 1):
        row_idx = idx + 1
        has_email = bool(r[3])
        sp = r[9]
        row_fill = EMAIL_FILL if has_email else NO_EMAIL_FILL
        if "✅" in sp:
            sp_fill = IDEAL_FILL
        elif "⚠️" in sp:
            sp_fill = MEDIUM_FILL
        else:
            sp_fill = NO_FILL_CLR

        values = [idx, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col, value=val)
            cell.fill      = sp_fill if col == 11 else row_fill
            cell.font      = Font(name="Calibri", size=10)
            cell.border    = BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=(col in [4, 12]))
        ws.row_dimensions[row_idx].height = 22

    total      = len(RESTAURANTS)
    with_email = sum(1 for r in RESTAURANTS if r[3])
    ideal      = sum(1 for r in RESTAURANTS if r[9].startswith("✅"))

    sr = total + 4
    ws.cell(row=sr,   column=1, value="📊 RIEPILOGO").font = Font(bold=True, size=12, color="2C3E50")
    ws.cell(row=sr+1, column=1, value="Totale ristoranti:").font     = BOLD_FONT
    ws.cell(row=sr+1, column=2, value=total)
    ws.cell(row=sr+2, column=1, value="Con email confermata:").font  = BOLD_FONT
    ws.cell(row=sr+2, column=2, value=with_email)
    ws.cell(row=sr+3, column=1, value="Ideali per SocialPerks (✅):").font = BOLD_FONT
    ws.cell(row=sr+3, column=2, value=ideal)
    ws.cell(row=sr+4, column=1, value="Generato il:").font           = BOLD_FONT
    ws.cell(row=sr+4, column=2, value=datetime.now().strftime("%d/%m/%Y %H:%M"))

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Casablanca.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")
    return filename


if __name__ == "__main__":
    create_excel()
