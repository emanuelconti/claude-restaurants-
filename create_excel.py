#!/usr/bin/env python3
"""Genera Excel con contatti ristoranti Parigi per SocialPerks."""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

# ─── DATI RISTORANTI ────────────────────────────────────────────────────────
# Colonne: Nome, Arrondissement, Indirizzo, Email, Telefono, Sito Web,
#          Instagram, Tipo, Dimensione, AdattoSocialPerks, Note

RESTAURANTS = [
    # ── CON EMAIL CONFERMATA ──────────────────────────────────────────────
    ("Breizh Café Le Marais", "75003", "109 Rue Vieille du Temple", "contact@breizhcafe.com", "+33 1 42 72 13 77", "breizhcafe.com", "@breizhcafe", "Crêperie / Bretagne-Japon", "Indipendente", "✅ Sì", "Molto instagrammabile, clientela giovane"),
    ("Breizh Café Batignolles", "75017", "Rue Legendre", "creperie.paris17@breizhcafe.com", "+33 1 40 07 11 69", "breizhcafe.com", "@breizhcafe", "Crêperie / Bretagna-Japon", "Piccola catena", "✅ Sì", "Clientela trendy, ideale per content creation"),
    ("Le Choupinet", "75006", "58 Boulevard Saint-Michel", "contact@lechoupinet.com", "+33 1 42 03 09 93", "lechoupinet.com", "@lechoupinet", "Brasserie / Café", "Indipendente", "✅ Sì", "Decor rattan, terrasse Luxembourg, molto fotogenico"),
    ("Dar Mima", "75005", "1 Rue des Fossés Saint-Bernard (IMA Rooftop)", "contact@darmima-restaurant.com", "+33 1 85 14 79 25", "darmima-restaurant.com", "@darmima_paris", "Oriental / Marocchino", "Indipendente", "✅ Sì", "Rooftop con vista Notre-Dame, super instagrammabile"),
    ("Monsieur Bleu", "75116", "20 Avenue de New York (Palais de Tokyo)", "privatisation@monsieurbleu.com", "+33 1 47 20 90 47", "monsieurbleu.com", "@monsieurbleu", "Francese contemporaneo", "Piccola catena", "⚠️ Medio", "Email eventi/privatizzazione, medio-grande"),
    ("Ober Mamma", "75011", "107 Boulevard Richard Lenoir", "ober.mamma@bigmamma.com", "+33 1 58 30 62 62", "bigmammagroup.com", "@obermamma", "Italiano / Pizzeria", "Gruppo Big Mamma", "⚠️ Medio", "Catena in crescita, potrebbero collaborare"),
    ("SORA Restaurant", "75116", "70 Rue de Longchamp", "contact@sora-restaurant.com", "+33 1 45 62 50 75", "sora-restaurant.com", "@sora_restaurant_paris", "Giapponese / Fusion", "Indipendente", "✅ Sì", "Elegante, design curato, clientela premium"),
    ("Bouillon Pigalle", "75018", "22 Boulevard Clichy", "reservation@bouillonlesite.com", "+33 7 81 51 83 10", "bouillonlesite.com", "@bouillonpigalle", "Brasserie francese classica", "Piccola catena", "✅ Sì", "Trendy, prezzi accessibili, molto fotografato"),
    ("Mokonuts", "75011", "5 Rue Saint-Bernard", "reservations@mokonuts.com", "+33 9 80 81 82 85", "mokonuts.com", "@mokonuts", "Fusion / Colazione", "Indipendente", "✅ Sì", "Famoso per cookies, brunch cult, clientela foodie"),
    ("Derrière", "75003", "69 Rue des Gravilliers", "evenements@gabrielledestrees.com", "+33 1 44 61 91 95", "derriere-resto.com", "@restaurantderriere", "Francese / Concept", "Indipendente", "✅ Sì", "Appartamento nascosto, super instagrammabile"),
    ("Le Mary Celeste", "75003", "1 Rue Commines", "reservations@lemaryceleste.com", "+33 1 36 38 04 72", "lemaryceleste.com", "@lemaryceleste", "Bar à manger / Cocktail", "Gruppo Quixotic", "✅ Sì", "Natural wine, oysters, cocktail bar cult"),
    ("Clown Bar", "75011", "114 Rue Amelot", "gestion@clownbar.fr", "+33 1 43 55 87 35", "clownbar.fr", "@clownbarparis", "Bistrot gastronomico", "Indipendente", "✅ Sì", "Décor Belle Époque, molto fotogenico"),
    ("Double Dragon", "75011", "52 Rue Saint-Maur", "Charlene@restoreve.com", "+33 1 71 32 41 95", "doubledragonparis.com", "@doubledragon_paris", "Pan-asiatico", "Indipendente", "✅ Sì", "Fusion asiatica, murales Instagram-worthy"),
    ("Le Perchoir Ménilmontant", "75011", "14 Rue Crespin du Gast", "menilmontant@leperchoir.fr", "+33 1 89 71 14 61", "leperchoir.fr", "@leperchoir", "Bar / Rooftop", "Gruppo Perchoir", "✅ Sì", "Rooftop iconico, vista panoramica Parigi"),
    ("Le Perchoir Porte de Versailles", "75015", "2 Avenue de la Porte de la Plaine", "pdv@leperchoir.fr", "+33 1 76 35 11 80", "leperchoir.fr", "@leperchoir", "Bar / Rooftop", "Gruppo Perchoir", "✅ Sì", "Secondo rooftop del gruppo"),
    ("Café Kitsuné", "75001", "51 Galerie de Montpensier (Palais Royal)", "customerservice@maisonkitsune.fr", "+33 1 40 15 62 31", "maisonkitsune.com", "@cafekitsune", "Café / Coffee specialty", "Maison Kitsuné", "✅ Sì", "Estetica curatissima, clientela moda"),
    ("La REcyclerie", "75018", "83 Boulevard Ornano", "contact@larecyclerie.com", "+33 1 42 57 58 49", "larecyclerie.com", "@larecyclerie", "Eco-resto / Concept", "Indipendente", "✅ Sì", "Stazione dismessa, giardino urbano, unico"),
    ("Verjus", "75001", "52 Rue de Richelieu", "verjusparis@gmail.com", "+33 1 42 97 54 40", "verjusparis.com", "@verjusparis", "Americano-Francese / Wine bar", "Indipendente", "✅ Sì", "American-owned, tasting menu, bello esteticamente"),
    ("Ten Belles", "75010", "10 Rue de la Grange aux Belles", "info@tenbelles.com", "+33 9 83 08 86 69", "tenbelles.com", "@tenbelles", "Café / Specialty coffee", "Piccola catena", "✅ Sì", "Famoso coffee shop Canal Saint-Martin"),
    ("Le Comptoir du Relais", "75006", "9 Carrefour de l'Odéon", "hotelrsg@camdeborde.com", "+33 1 44 27 07 97", "hotel-paris-relais-saint-germain.com", "@lecomptoirdurelais", "Bistrot francese", "Indipendente", "✅ Sì", "Bistrot emblematico, Yves Camdeborde"),
    ("Mama Shelter Paris East", "75011", "109 Rue de Bagnolet", "food.pariseast@mamashelter.com", "+33 1 43 48 48 48", "mamashelter.com", "@mamashelter", "Bar / Restaurant fusion", "Catena Mama Shelter", "⚠️ Medio", "Hotel trendy, clientela giovane"),
    ("Mama Shelter Paris West", "75020", "48 Rue de la Roquette (area)", "fo.pariswest@mamashelter.com", "+33 1 43 48 48 48", "mamashelter.com", "@mamashelter", "Bar / Restaurant fusion", "Catena Mama Shelter", "⚠️ Medio", "Hotel lifestyle"),
    ("Bistrot Paul Bert", "75011", "18 Rue Paul Bert", "bistrotpaulbert@gmail.com", "+33 1 43 72 24 01", "bistrotpaulbert.fr", "@bistrotpaulbert", "Bistrot classico", "Indipendente", "✅ Sì", "Steakhouse cult, décor vintage"),
    ("Semilla", "75006", "54 Rue de Seine", "semillaparisrestaurant@gmail.com", "+33 1 43 54 34 50", "semillaparis.com", "@semillaparis", "Bistrot moderno", "Indipendente", "✅ Sì", "Saint-Germain trendy, molto curato"),
    ("L'Ami Jean", "75007", "27 Rue Malar", "contact@lamijean.fr", "+33 1 47 05 86 89", "lamijean.fr", "@amijeanparis", "Basco-francese", "Indipendente", "✅ Sì", "Stéphane Jego, autentico, molto amato"),
    ("Bob's Juice Bar", "75010", "15 Rue Lucien Sampaix", "contact@bobsjuicebar.com", "+33 9 50 06 36 18", "bobsjuicebar.com", "@bobsjuicebar", "Veggie / Healthy café", "Indipendente", "✅ Sì", "Cult veggie République area, très photographié"),
    ("Mun Rooftop", "75008", "52 Avenue des Champs-Élysées", "contact@munparis.com", "+33 1 40 70 57 05", "restaurant-mun.com", "@mun_paris", "Giapponese / Rooftop", "Paris Society", "⚠️ Medio", "Rooftop iconico Champs-Élysées"),
    ("Créatures / Balcon GL", "75009", "25 Rue de la Chaussée d'Antin (Galeries Lafayette)", "reservation@creatures-paris.com", "+33 1 42 82 34 56", "creatures-paris.com", "@creatures_restaurant", "Vegetariano / Rooftop", "Galeries Lafayette", "⚠️ Medio", "Rooftop GL, concept vegetariano"),
    ("OGATA", "75003", "16 Rue Debelleyme", "reservation@ogata.com", "+33 1 80 97 76 80", "ogata.com/paris", "@ogata_paris", "Giapponese gastronomico", "Indipendente", "✅ Sì", "Estetica minimalista giapponese, molto fotogenico"),
    ("ROOF - Hôtel Madame Rêve", "75001", "48 Rue du Louvre", "contact@madamereve.com", "+33 1 80 40 77 70", "madamereve.com", "@madamereve_paris", "Cocktail bar / Rooftop", "Boutique hotel", "✅ Sì", "Rooftop élégant vista Paris"),
    ("Maxim's de Paris", "75008", "3 Rue Royale", "contact@restaurant-maxims.com", "+33 1 42 65 27 94", "maxims-de-paris.com", "@maximsdeparis", "Francese classico / Art Nouveau", "Indipendente", "⚠️ Medio", "Icona parigina, décor Belle Époque"),
    ("Kinugawa", "75001", "9 Rue du Mont Thabor", "contact@kinugawa.fr", "+33 1 42 60 65 07", "kinu-gawa.com", "@kinugawa_paris", "Giapponese raffinato", "Piccola catena", "✅ Sì", "Giapponese premium, clientela moda"),
    ("Le Grand Bain", "75020", "14 Rue Dénoyez", "contact@legrandbainparis.com", "+33 9 83 02 72 02", "legrandbainparis.com", "@legrandbain", "Wine bar / Bistrot", "Indipendente", "✅ Sì", "Rue Dénoyez street art, natural wine, molto cool"),
    ("Bus Toqué", "75008", "Départ Rond-Point Champs-Élysées", "contact@bustoque.fr", "+33 6 21 40 20 41", "bustoque.fr", "@bustoque", "Concept / Bus gourmet", "Indipendente", "✅ Sì", "Restaurant sur un bus - unique et hyper Instagrammable"),
    ("Girafe", "75016", "1 Place du Trocadéro", "contact@girafe-restaurant.com", "+33 1 40 62 70 61", "girafe-restaurant.com", "@girafe_paris", "Francese / Méditerranée", "Paris Society", "⚠️ Medio", "Vista Tour Eiffel, très élégant"),
    ("La Suite Girafe", "75016", "1 Place du Trocadéro", "contact@lasuitegirafe.com", "+33 1 40 62 70 61", "girafe-restaurant.com", "@lasuitegirafe", "Bar / Cocktail", "Paris Society", "⚠️ Medio", "Cocktail bar elegante al Trocadéro"),
    ("Les Ombres", "75007", "27 Quai Jacques Chirac (Musée Branly)", "lesombres@musiam-paris.com", "+33 1 47 53 68 00", "lesombres-restaurant.com", "@les_ombres", "Francese contemporaneo", "Musée Branly", "⚠️ Medio", "Rooftop con vista Tour Eiffel, supervisione Ducasse"),
    ("Café de l'Homme", "75116", "17 Place du Trocadéro", "reservation@cafedelhomme.com", "+33 1 44 05 30 15", "cafedelhomme.com", "@cafedelhomme", "Francese / Brasserie", "Indipendente", "✅ Sì", "Vista Tour Eiffel, terrasse iconique"),
    ("Wild & The Moon", "75003", "55 Rue Charlot (+ altre sedi)", "contact@wildandthemoon.com", "+33 1 86 95 40 44", "wildandthemoon.com", "@wildandthemoon", "Vegan / Healthy / Café", "Piccola catena", "✅ Sì", "Estetica minimal chic, molto IG-friendly"),
    ("BeauCoCo Paris", "75009", "1 Place Jacques Rouché (Opéra Garnier)", "contact@beaucoco-paris.com", "+33 1 42 68 86 80", "restaurant-beaucoco.com", "@beaucoco_paris", "Francese / Brasserie teatro", "Opéra Garnier", "⚠️ Medio", "Luogo iconico, grandioso décor"),
    ("Madame Brasserie", "75007", "Tour Eiffel (1° piano)", "reservation.web@madamebrasserie.com", "+33 1 83 77 77 78", "restaurants-toureiffel.com", "@madame_brasserie", "Francese brasserie", "Sté Exploitation Tour Eiffel", "⚠️ Medio", "Torre Eiffel - location unica"),
    ("Le Poulbot", "75018", "Rue Lamarck (Montmartre)", "lepoulbot.reservations@gmail.com", "+33 1 42 23 32 07", "lepoulbot.com", "@lepoulbot", "Francese classico", "Indipendente", "✅ Sì", "Montmartre, clientela turistica e locale"),
    ("Le Moulin de la Galette", "75018", "83 Rue Lepic (Montmartre)", "contact@lemoulindelagalette.com", "+33 1 46 06 84 77", "lemoulindelagalette.fr", "@moulindelagalette", "Francese classico / Brasserie", "Indipendente", "✅ Sì", "Icona di Montmartre, très photogénique"),
    ("Santa Lyna", "75003", "96 Boulevard de Sébastopol", "contact@santalyna.fr", "+33 9 71 07 94 38", "santalyna.fr", "@santalyna.fr", "Brunch californiano", "Indipendente", "✅ Sì", "Brunch instagrammabile, décor curato"),
    ("Bon Bouquet Café", "75009", "30 Rue Le Peletier", "contact@bonbouquetcafe.fr", "+33 9 71 07 94 35", "bonbouquetcafe.fr", "@bonbouquet.fr", "Brunch / Matcha bar", "Indipendente", "✅ Sì", "Décor tropical, brunch colorato"),
    ("Kafkaf", "75011", "7 Rue Keller", "contact@kafkaf.fr", "+33 9 71 07 94 36", "kafkaf.fr", "@kafkaf.fr", "Brunch Marrakech / Café", "Indipendente", "✅ Sì", "Ispirato Marrakech, colori vivaci, Instagram cult"),
    # ── SENZA EMAIL DIRETTA MA CON CONTATTO ──────────────────────────────
    ("Pink Mamma", "75009", "20bis Rue de Douai", "", "+33 1 42 81 26 67", "bigmammagroup.com", "@pinkmamma", "Italiano / Pizzeria", "Gruppo Big Mamma", "⚠️ Medio", "4 piani instagrammabili, clientela giovane, catena"),
    ("East Mamma", "75011", "133 Rue du Faubourg Saint-Antoine", "", "+33 1 43 56 56 00", "bigmammagroup.com", "@eastmamma", "Italiano / Pizzeria", "Gruppo Big Mamma", "⚠️ Medio", "Decor industriale chic"),
    ("Mamma Primi", "75017", "71 Rue de Lévis", "", "+33 1 40 54 41 60", "bigmammagroup.com", "@mammaprimiparis", "Italiano / Pasta bar", "Gruppo Big Mamma", "⚠️ Medio", "Pasta bar concept"),
    ("Septime", "75011", "80 Rue de Charonne", "", "+33 1 43 67 38 29", "septime-charonne.fr", "@septime_paris", "Francese bistronomico", "Indipendente", "⚠️ Medio", "1 stella Michelin, prenotazioni difficili"),
    ("Clamato", "75011", "80 Rue Charonne", "", "+33 1 43 72 74 53", "clamato-charonne.fr", "@clamato_paris", "Seafood / Small plates", "Indipendente", "✅ Sì", "No reservation - walk-in only, super trendy"),
    ("La Marine", "75010", "55bis Quai de Valmy", "", "+33 1 42 39 69 81", "lamarinecanalsaintmartin.com", "@lamarineparis10", "Brasserie / Canal", "Indipendente", "✅ Sì", "Terrasse Canal Saint-Martin iconique"),
    ("HolyBelly", "75010", "19 Rue Lucien Sampaix", "", "+33 1 82 28 00 80", "holybellycafe.com", "@holybellycafe", "Café australiano / Brunch", "Indipendente", "✅ Sì", "Melbourne vibes, brunch cult, 93K followers IG"),
    ("Frenchie", "75002", "5 Rue du Nil", "", "+33 1 40 39 96 19", "frenchie-restaurant.com", "@frenchieGJ", "Francese contemporaneo", "Gruppo Frenchie", "⚠️ Medio", "Greg Marchand, molto rinomato"),
    ("Café Charlot", "75003", "38 Rue de Bretagne", "", "+33 1 44 54 03 30", "lecharlot-paris.com", "@cafecharlotparis", "Brasserie / Café", "Indipendente", "✅ Sì", "Marais iconic, terrasse animée"),
    ("Chez Janou", "75003", "2 Rue Roger Verlomme", "", "+33 1 42 72 28 41", "chezjanou.com", "@chezjanou", "Provençal / Pastis bar", "Indipendente", "✅ Sì", "80+ pastis, giardino, molto fotogenico"),
    ("Daroco", "75002", "6 Rue Vivienne", "", "+33 1 42 21 93 71", "daroco.com", "@daroco_paris", "Italiano / Ex-atelier JPG", "Indipendente", "✅ Sì", "Ex-atelier Jean-Paul Gaultier, soffitti a specchi"),
    ("Café Suédois", "75003", "11 Rue Payenne", "", "+33 1 44 78 80 11", "institsuedois.fr", "@cafesuedois", "Scandinavo / Café", "Institut Culturel Suédois", "✅ Sì", "Giardino segreto, hôtel particulier 16° sec."),
    ("La Maison Rose", "75018", "2 Rue de l'Abreuvoir (Montmartre)", "", "+33 1 42 57 66 75", "", "@lamaisonrose_montmartre", "Café / Bistrot", "Indipendente", "✅ Sì", "Edificio rosa più fotografato di Montmartre"),
    ("Le Baratin", "75020", "3 Rue Jouye Rouve", "", "+33 1 43 49 39 70", "", "@lebaratin", "Bistrot franco-argentin", "Indipendente", "✅ Sì", "Raquel Carena, inventore bistronomy"),
    ("Aux Deux Amis", "75011", "45 Rue Oberkampf", "", "+33 1 58 30 38 13", "", "@auxdeuxamis", "Wine bar / Tapas", "Indipendente", "✅ Sì", "Natural wine, small plates, Oberkampf trendy"),
    ("Fragments", "75003", "76 Rue des Tournelles", "", "", "fragments-paris.com", "@fragmentsparis", "Café / Porridge-bowl", "Indipendente", "✅ Sì", "Marais Haut, specialty coffee, luminoso"),
    ("Shuzo Tropical Izakaya", "75011", "44 Rue Saint-Sébastien", "", "", "shuzo.fr", "@shuzo_paris", "Giapponese-colombiano / Izakaya", "Indipendente", "✅ Sì", "Mural DJ musica, molto Instagram-worthy"),
    ("Le Gentil", "75007", "26 Rue Surcouf", "", "", "restaurantlegentil.com", "@legentilparis", "Francese gastronomico", "Indipendente", "✅ Sì", "Piccolo, raffinato, 7° arr."),
    ("Café de Luce", "75018", "2 Rue des Trois Frères (Montmartre)", "", "", "cafedeluce.com", "@cafedeluce.montmartre", "Bistrot / Café", "Indipendente", "✅ Sì", "Chef Amandine Chaignot, place du Théâtre de l'Atelier"),
    ("Bob's Bake Shop", "75003", "12 Rue Lucien Sampaix", "", "", "bobsbakeshop.fr", "@bobsbakeshop", "Boulangerie / Café", "Indipendente", "✅ Sì", "Brunch americano, aesthetic cupcakes"),
    ("Shinko", "75008", "21 Rue Vignon (Madeleine)", "", "+33 1 44 70 92 91", "shinkoparis.fr", "@shinko_paris", "Giapponese / All-you-can-eat", "Piccola catena", "⚠️ Medio", "Semi-gastronomico giapponese"),
    ("Circonstances", "75002", "174 Rue Montmartre", "", "+33 1 42 36 17 05", "", "@circonstances_paris", "Bistronome", "Indipendente", "✅ Sì", "Ex-chef Savoy, qualità/prezzo eccellente"),
    ("Candelaria", "75003", "52 Rue de Saintonge", "", "+33 1 42 74 41 28", "candelaria-paris.com", "@candelariaparis", "Messicano / Taqueria / Cocktail", "Gruppo Quixotic", "✅ Sì", "Speakeasy bar nascosto, très instagrammable"),
    ("Café de la Nouvelle Mairie", "75005", "19 Rue des Fossés Saint-Jacques", "", "+33 1 44 07 04 41", "", "@cafenouvellemaire", "Wine bar / Bistrot", "Indipendente", "✅ Sì", "Premier bar à vins naturels de Paris"),
    ("Ob-La-Di", "75003", "54 Rue de Saintonge", "", "", "", "@obladiparis", "Brunch / Café californiano", "Indipendente", "✅ Sì", "Nord-Marais, avocado toast instagrammabili"),
    ("Le Grand Colbert", "75002", "2 Rue Vivienne", "", "+33 1 42 86 87 88", "legrandcolbert.fr", "@legrandcolbert", "Brasserie Belle Époque", "Indipendente", "✅ Sì", "Décor 1900, film cult 'Something's Gotta Give'"),
    ("Loulou", "75001", "107 Rue de Rivoli (Musée des Arts Déco)", "", "+33 1 42 60 41 96", "loulou-paris.com", "@loulou_paris", "Méditerranéen / Terrasse jardins Tuileries", "Indipendente", "✅ Sì", "Vista Jardin des Tuileries, molto fotogenico"),
    ("Le Flandrin", "75016", "4 Place Tattegrain", "", "+33 1 45 04 34 69", "leflandrin.com", "@leflandrin", "Brasserie / Café", "Indipendente", "✅ Sì", "Terrasse La Muette, clientela chic 16e"),
    ("Rosa Bonheur", "75019", "2 Allée de la Cascade (Buttes-Chaumont)", "", "+33 1 42 00 00 45", "rosabonheur.fr", "@rosabonheur", "Bar-tapas / Guinguette", "Piccola catena", "✅ Sì", "Parc Buttes-Chaumont, LGBTQ+ friendly, très animé"),
    ("Elmer", "75003", "30 Rue Notre-Dame de Nazareth", "", "+33 1 43 56 22 95", "elmer-restaurant.fr", "@elmer_paris", "Bistrot moderno / Seafood", "Indipendente", "✅ Sì", "Marais nord, Simon Horwitz chef"),
    ("LouLou Montmartre", "75018", "8 Rue Lamarck", "", "+33 1 42 55 04 55", "louloumontmartre.com", "@louloumontmartre", "Bistrot / Brasserie", "Indipendente", "✅ Sì", "Montmartre, cucina maison, belvedere"),
    ("Le Consulat", "75018", "18 Rue Norvins (Montmartre)", "", "+33 1 46 06 15 82", "", "@leconsulat_montmartre", "Bistrot tradizionale", "Indipendente", "✅ Sì", "Facciata più fotografata di Montmartre"),
    ("Lockwood", "75002", "73 Rue d'Aboukir", "", "+33 1 77 32 97 21", "lockwoodparis.com", "@lockwoodparis", "Coffee / Tapas / Cocktail", "Indipendente", "✅ Sì", "Multi-format: coffee-aperitivo-cocktail"),
    ("Brasserie Lipp", "75006", "151 Boulevard Saint-Germain", "", "+33 1 45 48 53 91", "brasserie-lipp.fr", "@brasserie_lipp", "Brasserie alsaziana classica", "Indipendente", "⚠️ Medio", "Istituzione parigina, grandioso"),
    ("Le Train Bleu", "75012", "Place Louis Armand (Gare de Lyon)", "", "+33 1 43 43 09 06", "le-train-bleu.com", "@letrainbleu", "Brasserie monumentale", "Indipendente", "✅ Sì", "Décor soffitti affrescati, très instagrammable"),
    ("Café de Flore", "75006", "172 Boulevard Saint-Germain", "", "+33 1 45 48 55 26", "cafedeflore.fr", "@cafedeflore", "Café / Brasserie iconique", "Indipendente", "⚠️ Medio", "Storico café dei filosofi, iconico"),
    ("La Bonne Franquette", "75018", "18 Rue Saint-Rustique (Montmartre)", "", "+33 1 42 52 02 42", "labonnefranquette.com", "@labonnefranquette", "Bistrot / Terrasse", "Indipendente", "✅ Sì", "Muro di edera, Renoir setting"),
    ("Pink Flamingo Pizza", "75003", "105 Rue Vieille du Temple", "", "+33 1 42 71 28 20", "pinkflamingopizza.com", "@pinkflamingopizza", "Pizzeria / Concept", "Piccola catena", "✅ Sì", "Pizze originali consegnate al canale in barca"),
    ("Café Procope", "75006", "13 Rue de l'Ancienne Comédie", "", "+33 1 40 46 79 00", "procope.com", "@leprocope", "Brasserie storica", "Indipendente", "⚠️ Medio", "Il più antico caffè di Parigi (1686)"),
    ("Au Pied de Fouet", "75007", "45 Rue de Babylone", "", "+33 1 47 05 12 27", "aupieddefouet.fr", "@aupieddefouet", "Bistrot classico", "Indipendente", "✅ Sì", "Autentico, molto fotogenico, cucina maison"),
    ("Septime La Cave", "75011", "3 Rue Basfroi", "", "+33 1 43 67 14 87", "septime-lacave.fr", "@septime_lacave", "Wine bar", "Gruppo Septime", "✅ Sì", "Cave à vins naturels, selezione eccezionale"),
    ("Le 6 Paul Bert", "75011", "6 Rue Paul Bert", "", "+33 1 43 79 14 32", "", "@le6paulbert", "Bistrot / Wine bar", "Indipendente", "✅ Sì", "Sorella di Bistrot Paul Bert"),
    ("Holybelly 5", "75010", "5 Rue Lucien Sampaix", "", "+33 1 82 28 00 80", "holybellycafe.com", "@holybellycafe", "Café australiano / Brunch", "Indipendente", "✅ Sì", "Secondo locale HolyBelly, all-day brunch"),
    ("Le Bab", "75001", "78 Rue Jean-Jacques Rousseau", "", "+33 9 51 84 42 64", "lebab.fr", "@lebab_paris", "Kebab gastronomico", "Indipendente", "✅ Sì", "Kebab haut de gamme, très photogénique"),
    ("Barbouze", "75009", "24 Rue du Faubourg Montmartre", "", "", "barbouze-paris.com", "@barbouze_paris", "Bar / Bistrot / Brunch", "Indipendente", "✅ Sì", "Cocktail bar et restaurant, ambiance cave"),
    ("Baranaan", "75010", "7 Rue du Faubourg Saint-Martin", "", "+33 1 40 38 97 57", "baranaan.com", "@baranaan_paris", "Indien-pakistanais / Street food", "Indipendente", "✅ Sì", "Street food indien, cocktails, ambiance unique"),
    ("Le Barnum", "75002", "34 Rue du Sentier", "", "", "", "@lebarnum_paris", "Café / Brunch / Bar", "Indipendente", "✅ Sì", "Concept multifunzionale, decor circo vintage"),
    ("Café du Commerce", "75015", "51 Rue du Commerce", "", "+33 1 45 75 03 27", "lecafeducommerce.com", "@cafeducommerce", "Brasserie / Patio interiore", "Indipendente", "✅ Sì", "Patio interiore spettacolare su 3 piani"),
    ("L'Oiseau Blanc (Peninsula)", "75116", "19 Avenue Kléber", "benoitlegros@peninsula.com", "+33 1 58 12 67 50", "peninsula.com/paris", "@thepeninsulaparis", "Alta cucina / Rooftop", "The Peninsula", "❌ No", "Fine dining 2 Michelin stars, troppo esclusivo"),
    ("Café Oberkampf", "75011", "3 Rue Neuve Popincourt", "", "", "cafeoberkampf.com", "@cafeoberkampf", "Café / Brunch", "Indipendente", "✅ Sì", "Istituzione brunch Oberkampf"),
    ("Le Cornichon", "75011", "34 Rue Gerbier", "", "+33 1 43 67 30 96", "", "@lecornichon", "Bistrot 70s vintage", "Indipendente", "✅ Sì", "Décor vintage anni 70, ottimo rapporto Q/P"),
]

def create_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ristoranti Parigi - SocialPerks"

    # ── Colori ──────────────────────────────────────────────────────────────
    HEADER_FILL = PatternFill("solid", fgColor="2C3E50")
    EMAIL_FILL  = PatternFill("solid", fgColor="E8F5E9")
    NO_EMAIL_FILL = PatternFill("solid", fgColor="FFF9C4")
    IDEAL_FILL  = PatternFill("solid", fgColor="D5F5E3")
    MEDIUM_FILL = PatternFill("solid", fgColor="FDEBD0")
    NO_FILL     = PatternFill("solid", fgColor="FADBD8")

    HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    BOLD_FONT   = Font(name="Calibri", bold=True, size=10)
    NORMAL_FONT = Font(name="Calibri", size=10)

    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    headers = [
        "#", "Nome Ristorante", "Arr.", "Indirizzo", "EMAIL ✉️",
        "Telefono", "Sito Web", "Instagram", "Tipo Cucina",
        "Dimensione", "Adatto SocialPerks", "Note / Descrizione"
    ]
    col_widths = [4, 30, 6, 32, 36, 18, 28, 22, 24, 18, 16, 50]

    # ── Header row ──────────────────────────────────────────────────────────
    ws.row_dimensions[1].height = 22
    for col_idx, (header, width) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.freeze_panes = "A2"

    # ── Data rows ──────────────────────────────────────────────────────────
    for row_idx, resto in enumerate(RESTAURANTS, 2):
        nome, arr, addr, email, tel, sito, insta, tipo, dim, adatto, note = resto

        row_data = [
            row_idx - 1, nome, arr, addr, email, tel, sito, insta, tipo, dim, adatto, note
        ]

        has_email = bool(email)
        adatto_code = adatto[0]  # ✅ ⚠️ ❌

        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = NORMAL_FONT
            cell.alignment = Alignment(vertical="center", wrap_text=(col_idx == 12))
            cell.border = border

            # Colora la riga in base a email e adattabilità
            if col_idx == 5:  # colonna email
                if has_email:
                    cell.fill = EMAIL_FILL
                    cell.font = Font(name="Calibri", size=10, color="1B5E20")
                else:
                    cell.fill = NO_EMAIL_FILL
            elif col_idx == 11:  # colonna adatto
                if adatto_code == "✅":
                    cell.fill = IDEAL_FILL
                elif adatto_code == "⚠️":
                    cell.fill = MEDIUM_FILL
                else:
                    cell.fill = NO_FILL
            else:
                if has_email and adatto_code == "✅":
                    cell.fill = PatternFill("solid", fgColor="F0FFF0")

        ws.row_dimensions[row_idx].height = 22

    # ── Summary box ─────────────────────────────────────────────────────────
    total = len(RESTAURANTS)
    with_email = sum(1 for r in RESTAURANTS if r[3])
    ideal = sum(1 for r in RESTAURANTS if r[9].startswith("✅"))

    summary_row = total + 4
    ws.cell(row=summary_row, column=1, value="📊 RIEPILOGO").font = Font(bold=True, size=12, color="2C3E50")
    ws.cell(row=summary_row+1, column=1, value=f"Totale ristoranti:").font = BOLD_FONT
    ws.cell(row=summary_row+1, column=2, value=total)
    ws.cell(row=summary_row+2, column=1, value=f"Con email confermata:").font = BOLD_FONT
    ws.cell(row=summary_row+2, column=2, value=with_email)
    ws.cell(row=summary_row+3, column=1, value=f"Ideali per SocialPerks (✅):").font = BOLD_FONT
    ws.cell(row=summary_row+3, column=2, value=ideal)
    ws.cell(row=summary_row+4, column=1, value=f"Generato il:").font = BOLD_FONT
    ws.cell(row=summary_row+4, column=2, value=datetime.now().strftime("%d/%m/%Y %H:%M"))

    # ── Second sheet: istruzioni ─────────────────────────────────────────
    ws2 = wb.create_sheet("Guida Outreach SocialPerks")
    istruzioni = [
        ("GUIDA OUTREACH SOCIALPERKS - PARIGI", True, 16),
        ("", False, 11),
        ("🎯 STRATEGIA DI CONTATTO", True, 13),
        ("", False, 11),
        ("1. PRIMA SCELTA: Ristoranti con email ✅ verde", False, 11),
        ("   → Manda email personalizzata con la proposta SocialPerks", False, 11),
        ("   → Oggetto consigliato: 'Collaboration SocialPerks x [Nome Ristorante] - Content Creation Étudiants'", False, 11),
        ("", False, 11),
        ("2. SECONDA SCELTA: Contatta via Instagram DM", False, 11),
        ("   → Molti ristoranti indipendenti rispondono meglio via IG", False, 11),
        ("   → Usa account IG professionale SocialPerks per il DM", False, 11),
        ("", False, 11),
        ("3. PER RISTORANTI SENZA EMAIL:", False, 11),
        ("   → Vai sul sito ufficiale > pagina 'Contact' per trovare l'email", False, 11),
        ("   → Oppure chiama il numero di telefono", False, 11),
        ("", False, 11),
        ("📝 TEMPLATE EMAIL CONSIGLIATO", True, 13),
        ("", False, 11),
        ("Objet: Proposition de collaboration – SocialPerks & [Nom du restaurant]", False, 11),
        ("", False, 11),
        ("Bonjour,", False, 11),
        ("", False, 11),
        ("Je me permets de vous contacter au nom de SocialPerks, une startup qui connecte", False, 11),
        ("des étudiants passionnés de photographie et de création de contenu avec des restaurants", False, 11),
        ("parisiens qui méritent plus de visibilité sur Instagram.", False, 11),
        ("", False, 11),
        ("Notre proposition est simple : nous vous envoyons des étudiants talentueux qui créent", False, 11),
        ("du contenu photo/vidéo professionnel pour vos réseaux sociaux, en échange d'un repas", False, 11),
        ("offert ou d'un geste commercial.", False, 11),
        ("", False, 11),
        ("Seriez-vous disponible pour un appel rapide de 15 minutes cette semaine ?", False, 11),
        ("", False, 11),
        ("Bien cordialement,", False, 11),
        ("[Votre nom] - SocialPerks", False, 11),
        ("", False, 11),
        ("🏆 RISTORANTI PRIORITÀ ASSOLUTA PER SOCIALPERKS", True, 13),
        ("(Instagrammabili + Indipendenti + Email confermata)", False, 11),
        ("", False, 11),
        ("1. Dar Mima (rooftop IMA, vista Notre-Dame) → contact@darmima-restaurant.com", False, 11),
        ("2. Le Grand Bain (Belleville, rue street art) → contact@legrandbainparis.com", False, 11),
        ("3. Double Dragon (pan-Asian, murales IG) → Charlene@restoreve.com", False, 11),
        ("4. OGATA (minimalismo giapponese) → reservation@ogata.com", False, 11),
        ("5. Mokonuts (brunch cult, cookies IG) → reservations@mokonuts.com", False, 11),
        ("6. Le Mary Celeste (oyster bar trendy) → reservations@lemaryceleste.com", False, 11),
        ("7. Clown Bar (Belle Époque, Michelin) → gestion@clownbar.fr", False, 11),
        ("8. La REcyclerie (eco, giardino urbano) → contact@larecyclerie.com", False, 11),
        ("9. Verjus (franco-americano chic) → verjusparis@gmail.com", False, 11),
        ("10. Ten Belles (specialty coffee cult) → info@tenbelles.com", False, 11),
        ("11. Derrière (appartamento nascosto) → evenements@gabrielledestrees.com", False, 11),
        ("12. Wild & The Moon (vegan estetico) → contact@wildandthemoon.com", False, 11),
        ("13. Shuzo Izakaya (colombo-giapponese) → via IG @shuzo_paris", False, 11),
        ("14. Café de Luce (Montmartre, Chaignot) → via cafedeluce.com", False, 11),
        ("15. Circonstances (bistronome qualità) → via IG @circonstances_paris", False, 11),
    ]

    for i, (text, bold, size) in enumerate(istruzioni, 1):
        cell = ws2.cell(row=i, column=1, value=text)
        cell.font = Font(name="Calibri", bold=bold, size=size,
                         color="2C3E50" if bold else "333333")
        cell.alignment = Alignment(wrap_text=True)

    ws2.column_dimensions["A"].width = 100

    # ── Save ────────────────────────────────────────────────────────────────
    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Paris.xlsx"
    wb.save(filename)
    print(f"✅ File creato: {filename}")
    print(f"   Totale: {total} ristoranti")
    print(f"   Con email: {with_email}")
    print(f"   Ideali SocialPerks: {ideal}")
    return filename

if __name__ == "__main__":
    create_excel()
