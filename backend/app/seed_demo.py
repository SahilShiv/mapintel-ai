import json
from datetime import datetime, timezone, timedelta
from backend.app.database import engine, SessionLocal, Base
from backend.app.models.project import Project, Competitor, Keyword
from backend.app.models.post import Post, PostMedia, PostAnalysis
from backend.app.models.scraping import ScrapingJob, ScrapingJobItem
from backend.app.models.content import GeneratedIdea, GeneratedUpdate
from backend.app.services.fingerprint import generate_post_fingerprint, generate_idea_semantic_hash

def seed_database():
    print("Creating database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_projects = db.query(Project).count()
        if existing_projects > 0:
            print(f"Database already contains {existing_projects} projects. Skipping seed.")
            return

        print("Seeding realistic demo dataset (50+ clean Google Maps updates across 4 industries)...")

        now = datetime.now(timezone.utc)

        # -------------------------------------------------------------------------
        # PROJECT 1: PREMIER DEMO - SALON & SPA IN THANE WEST
        # -------------------------------------------------------------------------
        p1_facts = {
            "business_name": "Ravi's Family Salon",
            "location": "Panchpakhadi, Thane West, Maharashtra",
            "services": [
                "Precision Haircuts & Styling",
                "Botanical Moisture Hair Spa",
                "Keratin & Cysteine Smoothening",
                "Balayage & Global Color",
                "Gentlemen's Beard Sculpting",
                "Hydra Glow Skin Facials"
            ],
            "facilities": [
                "Dedicated client parking slots available",
                "Air-conditioned private styling suites",
                "Sanitized premium tools"
            ],
            "consultation_policy": "Complimentary hair texture & scalp micro-camera analysis before chemical services"
        }

        p1 = Project(
            project_name="Ravi's Family Salon - Thane WEST",
            client_business_name="Ravi's Family Salon",
            google_maps_url="https://www.google.com/maps/place/Ravi's+Family+Salon+Thane+West",
            description="Premier family salon & wellness lounge located at Panchpakhadi, Thane West. Specializes in advanced hair styling, organic botanical spas, and festive groom/bridal care.",
            verified_facts=json.dumps(p1_facts, indent=2)
        )
        db.add(p1)
        db.flush()

        kws_p1 = ["salon in Thane West", "hair spa Thane", "keratin treatment Thane", "balayage specialist Thane", "best bridal salon Thane"]
        for k in kws_p1:
            db.add(Keyword(project_id=p1.id, keyword=k))

        # 4 Competitors for Premier Demo Project
        c1_1 = Competitor(project_id=p1.id, business_name="Enrich Beauty Lounge - Thane West", google_maps_url="https://www.google.com/maps/place/Enrich+Thane+West", place_identifier="ChIJz2_12345", status="active", total_posts=5, scraping_status="completed", last_scraped_at=now - timedelta(hours=3))
        c1_2 = Competitor(project_id=p1.id, business_name="Toni & Guy Hairdressing - Thane West", google_maps_url="https://www.google.com/maps/place/Toni+Guy+Thane", place_identifier="ChIJz2_67890", status="active", total_posts=5, scraping_status="completed", last_scraped_at=now - timedelta(hours=4))
        c1_3 = Competitor(project_id=p1.id, business_name="Jawed Habib Hair Studio - Thane West", google_maps_url="https://www.google.com/maps/place/Jawed+Habib+Thane", place_identifier="ChIJz2_11223", status="active", total_posts=5, scraping_status="completed", last_scraped_at=now - timedelta(hours=5))
        c1_4 = Competitor(project_id=p1.id, business_name="Naturals Salon & Spa - Thane West", google_maps_url="https://www.google.com/maps/place/Naturals+Thane+West", place_identifier="ChIJz2_44556", status="active", total_posts=4, scraping_status="completed", last_scraped_at=now - timedelta(hours=6))
        db.add_all([c1_1, c1_2, c1_3, c1_4])
        db.flush()

        posts_p1_data = [
            # Enrich Beauty Lounge
            (c1_1, "Hair Care Tips", "Tip", "Monsoon humidity making your tresses unmanageable? Our Senior Hair Stylists swear by our Argan Oil Moisture Infusion. Locks in hydration without weighing down fine hair. Book your session this week and enjoy a complimentary scalp micro-camera check!", "Book Appointment", ["hair care tips", "monsoon hair", "argan oil", "frizz free"], "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=800&q=80", 2),
            (c1_1, "Festival Offer", "Offer", "Festive Sparkle Package! Get Flat 30% OFF on all Keratin, Cysteine, and Hair Botox treatments this weekend only. Flaunt red-carpet ready gloss all season long. Slots fill fast—call to reserve!", "Call Now", ["festival offer", "keratin discount", "hair botox", "salon discount"], "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80", 6),
            (c1_1, "Before / After Transformation", "Showcase", "From brassy yellow to rich caramel sun-kissed balayage! Master Colorist Rahul spent 4 hours hand-painting these dimensional ribbons using ammonia-free Italian pigments. Swipe left to see the dramatic before.", "View Portfolio", ["balayage", "before after", "hair transformation", "hair color"], "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?auto=format&fit=crop&w=800&q=80", 12),
            (c1_1, "Skin Glow Treatment", "Product Update", "Introducing the 9-Step Korean Glass Skin Facial at Enrich. Unclog pores with ultrasound scrubber, infuse antioxidant peptides, and reveal radiant dewiness. Special introductory price ₹1,999.", "Book Now", ["glass skin", "korean facial", "glow treatment", "hydra facial"], "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=800&q=80", 18),
            (c1_1, "Hair Care Tips", "Tip", "Why you should never brush wet hair without a leave-in detangler: Wet hair follicles are at their weakest and stretch up to 30% before snapping. Ask your stylist for our botanical detangling serum.", "Learn More", ["hair care tips", "hair health", "brushing tips"], "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=800&q=80", 25),

            # Toni & Guy Hairdressing
            (c1_2, "Before / After Transformation", "Showcase", "Edgy textured French Bob transformation for our lovely guest Maya. Paired with a deep espresso gloss for mirror-like shine. Precision cutting at its finest.", "Book Appointment", ["french bob", "short haircut", "precision cut", "before after"], "https://images.unsplash.com/photo-1605497788044-5a32c7078486?auto=format&fit=crop&w=800&q=80", 4),
            (c1_2, "Festival Offer", "Offer", "Wedding Season Kickoff! Book any full bridal package and receive a complimentary pre-wedding grooming session for your bestie. Limited to the first 20 bookings.", "Claim Offer", ["bridal package", "wedding makeup", "pre bridal offer"], "https://images.unsplash.com/photo-1519699047748-de8e457a634e?auto=format&fit=crop&w=800&q=80", 9),
            (c1_2, "Hair Care Tips", "Tip", "Color longevity secret: Wait 72 hours after coloring before shampooing. It takes up to three days for the cuticle layer to fully seal, trapping color molecules deep within the cortex.", "Learn More", ["color care", "color maintenance", "salon secrets"], "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=800&q=80", 15),
            (c1_2, "Product Update", "Product Update", "Now stocking the full Olaplex Professional No. 1 to No. 9 lineup. Rebuild broken disulfide bonds from chemical bleaching right at our wash stations.", "Order Online", ["olaplex", "bond repair", "hair treatment"], "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?auto=format&fit=crop&w=800&q=80", 22),
            (c1_2, "Behind-the-scenes", "Showcase", "Behind the chair with Artistic Director Vikram prepping models for Mumbai Fashion Week. Trends this year: natural textures, copper gloss, and soft curtain bangs.", "View Portfolio", ["behind the scenes", "fashion week", "curtain bangs"], "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?auto=format&fit=crop&w=800&q=80", 30),

            # Jawed Habib Hair Studio
            (c1_3, "Festival Offer", "Offer", "Super Saver Midweek Deal! Flat 40% OFF on Hair Spa + Haircut Combo every Tuesday and Wednesday between 11 AM and 4 PM. Beat the weekend rush!", "Book Now", ["hair spa deal", "midweek offer", "budget salon"], "https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?auto=format&fit=crop&w=800&q=80", 5),
            (c1_3, "Men's Grooming", "Product Update", "Gentlemen, elevate your grooming routine. Hot towel beard sculpting, scalp massage, and precision fade haircuts available with master barbers.", "Call Now", ["mens haircut", "beard trim", "hot towel shave"], "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=800&q=80", 11),
            (c1_3, "Hair Care Tips", "Tip", "Struggling with dandruff? Avoid washing hair with boiling hot water, which dries out the scalp and accelerates flaking. Use lukewarm water with our tea-tree clarifying shampoo.", "Learn More", ["dandruff care", "scalp health", "tea tree"], "https://images.unsplash.com/photo-1519735777090-ec97162dc266?auto=format&fit=crop&w=800&q=80", 19),
            (c1_3, "Before / After Transformation", "Showcase", "Severe heat damage repaired! Swipe to witness how our Nano-Keratin sealant resurrected elasticity and bounce in chemically compromised hair.", "View Portfolio", ["keratin repair", "heat damage", "before after"], "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?auto=format&fit=crop&w=800&q=80", 26),
            (c1_3, "Festival Offer", "Offer", "Student Special: Flash your college ID card and get 20% off all global hair colors and highlights. Valid through this month.", "Get Directions", ["student discount", "hair color offer", "thane students"], "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11?auto=format&fit=crop&w=800&q=80", 34),

            # Naturals Salon & Spa
            (c1_4, "Festival Offer", "Offer", "Pre-Festive Head-to-Toe Pampering: Get an organic facial, foot reflexology, and Moroccan oil hair spa bundle at flat 25% off this week.", "Book Now", ["organic facial", "moroccan oil spa", "salon bundle"], "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80", 3),
            (c1_4, "Hair Care Tips", "Tip", "Preventing split ends between cuts: Apply 2 drops of jojoba oil to dry ends before sleeping to seal moisture against rough pillow friction.", "Learn More", ["split ends", "jojoba oil", "hair health"], "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80", 10),
            (c1_4, "Skin Glow Treatment", "Product Update", "Detoxify your skin after long daily commutes with our Green Tea Herbal Clay Mask. Tightens pores and restores clarity.", "Claim Offer", ["green tea facial", "herbal clay", "skin detox"], "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=800&q=80", 17),
            (c1_4, "Before / After Transformation", "Showcase", "Brilliant honey blonde balayage highlight session for college graduate Ritu. Seamless transitions with zero demarcation lines.", "View Portfolio", ["honey blonde", "balayage highlights", "before after"], "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?auto=format&fit=crop&w=800&q=80", 28),
        ]

        # -------------------------------------------------------------------------
        # PROJECT 2: RESTAURANT & CAFE
        # -------------------------------------------------------------------------
        p2_facts = {
            "business_name": "The Rustic Fork Bistro",
            "cuisine": "Artisanal Italian & Craft Pizzeria",
            "features": ["Handcrafted 72-hour sourdough pizzas", "Fresh extruded pasta made daily", "Outdoor pet-friendly garden patio"],
            "parking": "Valet parking available on weekends"
        }
        p2 = Project(
            project_name="Rustic Fork Bistro Intelligence",
            client_business_name="The Rustic Fork Bistro",
            google_maps_url="https://www.google.com/maps/place/Rustic+Fork+Bandra",
            description="Artisanal wood-fired sourdough pizzas, fresh pasta, and craft cocktails in Pali Hill, Bandra.",
            verified_facts=json.dumps(p2_facts, indent=2)
        )
        db.add(p2)
        db.flush()

        kws_p2 = ["woodfired pizza Bandra", "brunch in Bandra", "italian restaurant Bandra", "craft cocktails Mumbai", "outdoor dining"]
        for k in kws_p2:
            db.add(Keyword(project_id=p2.id, keyword=k))

        c2_1 = Competitor(project_id=p2.id, business_name="Gustoso Bandra", google_maps_url="https://www.google.com/maps/place/Gustoso+Bandra", place_identifier="ChIJr_111", status="active", total_posts=5, scraping_status="completed", last_scraped_at=now - timedelta(hours=6))
        c2_2 = Competitor(project_id=p2.id, business_name="Pizza By The Bay", google_maps_url="https://www.google.com/maps/place/Pizza+Bay+Bandra", place_identifier="ChIJr_222", status="active", total_posts=5, scraping_status="completed", last_scraped_at=now - timedelta(hours=7))
        c2_3 = Competitor(project_id=p2.id, business_name="Ray's Cafe & Pizzeria", google_maps_url="https://www.google.com/maps/place/Rays+Cafe+Bandra", place_identifier="ChIJr_333", status="active", total_posts=4, scraping_status="completed", last_scraped_at=now - timedelta(hours=8))
        db.add_all([c2_1, c2_2, c2_3])
        db.flush()

        posts_p2_data = [
            (c2_1, "Weekend Brunch", "Event", "Sunday Jazz Brunch on the terrace! Free-flowing artisanal mimosas, live acoustic bossa nova, and hand-rolled gnocchi with fresh summer black truffles. 12 PM - 4 PM. Reserve your table.", "Reserve Table", ["sunday brunch", "jazz brunch", "truffle pasta", "bandra brunch"], "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80", 3),
            (c2_1, "Chef Special", "Product Update", "Direct from our wood stone oven: The Burrata Vesuvio pizza featuring 72-hour fermented sourdough, San Marzano cherry tomatoes, and creamy fresh Puglia burrata.", "Order Online", ["burrata pizza", "sourdough pizza", "chef special"], "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80", 7),
            (c2_1, "Happy Hours", "Offer", "Aperitivo Evenings! Buy 1 Get 1 on all barrel-aged negronis, spritzes, and antipasti platters from 5 PM to 8 PM Tuesday through Friday.", "Get Directions", ["happy hour", "aperitivo", "cocktail offer", "bandra bar"], "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=800&q=80", 13),
            (c2_1, "Event", "Event", "Wine Tasting Masterclass: Tour the vineyards of Tuscany with Sommelier Marco this Thursday evening. 5 rare vintages paired with artisanal cheeses.", "Book Now", ["wine tasting", "sommelier", "italian wine"], "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80", 20),
            (c2_1, "Chef Special", "Product Update", "Fresh dessert alert: Torta Caprese with dark Belgian chocolate and roasted almond flour, served warm with vanilla gelato.", "Order Online", ["torta caprese", "dessert", "gelato"], "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80", 27),

            (c2_2, "Chef Special", "Product Update", "The Quattro Formaggi with spicy hot honey drizzle is back on our specials board! Made with smoked provolone, gorgonzola, parmesan, and fior di latte.", "Order Online", ["hot honey pizza", "four cheese", "gourmet pizza"], "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80", 5),
            (c2_2, "Happy Hours", "Offer", "Sunset sips by the promenade: Enjoy 20% off all craft beer pitchers and wood-fired garlic bread baskets until 7:30 PM daily.", "Call Now", ["craft beer", "sunset drinks", "happy hour bandra"], "https://images.unsplash.com/photo-1608278049100-34907993a408?auto=format&fit=crop&w=800&q=80", 10),
            (c2_2, "Weekend Brunch", "Event", "Pancake towers and espresso tonics! Bring your dogs to our pet-friendly garden patio this Saturday morning.", "Reserve Table", ["pet friendly cafe", "weekend pancakes", "outdoor seating"], "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80", 17),
            (c2_2, "Festival Offer", "Offer", "Family Feast Bundle: Order any 2 large pizzas and get a classic tiramisu + 1.5L Italian soda completely free. Use code FAMFEAST.", "Claim Offer", ["family pizza offer", "free dessert", "pizza delivery"], "https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?auto=format&fit=crop&w=800&q=80", 24),
            (c2_2, "Behind-the-scenes", "Showcase", "Meet Chef Antonio checking the hydration level on today's sourdough poolish. 72 hours of patience for that airy, crispy leopard crust.", "Learn More", ["sourdough crust", "behind the scenes", "pizza master"], "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=800&q=80", 31),

            (c2_3, "Chef Special", "Product Update", "Fresh handmade Tagliolini al Limone with Sorrento lemons, salted butter, and cracked pink peppercorns. Light, zesty, and unforgettable.", "Order Online", ["handmade pasta", "lemon pasta", "italian dining"], "https://images.unsplash.com/photo-1621996346565-e3d5d6281682?auto=format&fit=crop&w=800&q=80", 8),
            (c2_3, "Weekend Brunch", "Event", "Live Jazz Duet this Friday evening from 8 PM onwards. Candlelight, acoustic double bass, and authentic Roman thin-crust pizza.", "Reserve Table", ["live jazz", "candlelight dinner", "roman pizza"], "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80", 16),
            (c2_3, "Happy Hours", "Offer", "Thursday Ladies Night: Complimentary signature Italian cocktail with every main course order. Tag your girls and head over!", "Book Now", ["ladies night", "cocktail offer", "thursday night"], "https://images.unsplash.com/photo-1544148103-0773bf10d330?auto=format&fit=crop&w=800&q=80", 23),
            (c2_3, "Tip", "Tip", "Why sourdough pizza doesn't leave you bloated: Extended fermentation breaks down gluten and phytates, rendering the crust easily digestible and probiotic-friendly.", "Learn More", ["healthy pizza", "digestible crust", "sourdough benefits"], "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=800&q=80", 29)
        ]

        # -------------------------------------------------------------------------
        # PROJECT 3: DENTAL CLINIC & HEALTHCARE
        # -------------------------------------------------------------------------
        p3_facts = {
            "business_name": "Apex Dental Aesthetics",
            "services": ["Digital 3D Intraoral Scans", "Invisible Clear Aligners", "Laser Teeth Whitening", "Single-visit Ceramic Crowns"],
            "sterilization": "Hospital-grade Class B autoclaving protocols"
        }
        p3 = Project(
            project_name="Apex Dental Competitor Monitor",
            client_business_name="Apex Dental Aesthetics",
            google_maps_url="https://www.google.com/maps/place/Apex+Dental+Powai",
            description="Specialized multispecialty dental clinic in Hiranandani Powai focusing on painless aligners, veneers, and dental implants.",
            verified_facts=json.dumps(p3_facts, indent=2)
        )
        db.add(p3)
        db.flush()

        kws_p3 = ["dentist in Powai", "clear aligners Mumbai", "teeth whitening Powai", "dental implants", "painless dentistry"]
        for k in kws_p3:
            db.add(Keyword(project_id=p3.id, keyword=k))

        c3_1 = Competitor(project_id=p3.id, business_name="Dentzz Dental Care", google_maps_url="https://www.google.com/maps/place/Dentzz+Powai", place_identifier="ChIJd_111", status="active", total_posts=5, scraping_status="completed", last_scraped_at=now - timedelta(hours=9))
        c3_2 = Competitor(project_id=p3.id, business_name="Clove Dental Powai", google_maps_url="https://www.google.com/maps/place/Clove+Powai", place_identifier="ChIJd_222", status="active", total_posts=4, scraping_status="completed", last_scraped_at=now - timedelta(hours=10))
        c3_3 = Competitor(project_id=p3.id, business_name="Smilekraft Aesthetic Clinic", google_maps_url="https://www.google.com/maps/place/Smilekraft+Powai", place_identifier="ChIJd_333", status="active", total_posts=4, scraping_status="completed", last_scraped_at=now - timedelta(hours=11))
        db.add_all([c3_1, c3_2, c3_3])
        db.flush()

        posts_p3_data = [
            (c3_1, "Teeth Whitening", "Offer", "Laser Smile Brightening Special! Transform coffee, tea, and tobacco stains up to 6 shades lighter in just 45 minutes. Enamel-safe with zero sensitivity guarantee. Book consultation for 25% off this week.", "Book Consultation", ["laser whitening", "teeth whitening", "smile glow", "cosmetic dentist"], "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80", 3),
            (c3_1, "Clear Aligners", "Product Update", "Say goodbye to metal brackets! Transparent, custom 3D printed aligners gently straighten teeth with zero lifestyle interruption. Schedule your digital 3D iTero scan today.", "Schedule Scan", ["clear aligners", "invisible braces", "itero scan"], "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=800&q=80", 8),
            (c3_1, "Before / After Transformation", "Showcase", "Porcelain veneer smile makeover! Client had severe gaps and fluorosis discoloration. Completed in just 2 painless appointments with ultra-thin ceramic veneers.", "View Portfolio", ["veneers before after", "smile makeover", "ceramic veneers"], "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?auto=format&fit=crop&w=800&q=80", 14),
            (c3_1, "Tip", "Tip", "Did you know that brushing immediately after drinking lemon water or citrus juice causes acid erosion? Wait at least 30 minutes to allow saliva to remineralize your enamel.", "Learn More", ["dental health tip", "enamel care", "oral hygiene"], "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80", 21),
            (c3_1, "Festival Offer", "Offer", "World Oral Health Month: Complimentary digital dental X-ray and ultrasonic cleaning with every family consultation through end of month.", "Call Now", ["family dental offer", "free cleaning", "oral health month"], "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=800&q=80", 28),

            (c3_2, "Clear Aligners", "Offer", "Aligner Open Day this Saturday! Get a free 3D smile simulation, meet our Orthodontic specialists, and avail ₹15,000 instant festive cashback on comprehensive treatments.", "Book Now", ["aligner open day", "free 3d simulation", "orthodontist"], "https://images.unsplash.com/photo-1629909615184-74f495363b67?auto=format&fit=crop&w=800&q=80", 4),
            (c3_2, "Dental Implants", "Product Update", "Missing tooth affecting your chewing and confidence? Our computer-guided titanium dental implants feel and function exactly like natural teeth. Lifetime warranty included.", "Learn More", ["dental implant", "guided implant", "tooth replacement"], "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80", 11),
            (c3_2, "Tip", "Tip", "Why bleeding gums are an urgent red flag: Healthy gums never bleed during normal brushing. Bleeding is the earliest sign of gingivitis. Early intervention prevents bone loss!", "Call Today", ["gum health", "gingivitis", "periodontist"], "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80", 18),
            (c3_2, "Before / After Transformation", "Showcase", "Full mouth rehabilitation for a 52-year-old patient. Recovered natural bite alignment and pain-free chewing in 10 days.", "View Portfolio", ["full mouth rehab", "before after dental", "dental restoration"], "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?auto=format&fit=crop&w=800&q=80", 26),

            (c3_3, "Teeth Whitening", "Offer", "Bridal Smile Prep: Couple discount on laser teeth whitening and ceramic polishing. Shine together on your big day!", "Book Consultation", ["bridal dental", "wedding smile", "couple dental offer"], "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80", 6),
            (c3_3, "Clear Aligners", "Product Update", "Teens and young adults love our invisible aligners for sports and social confidence. Removable for meals, photos, and brushing.", "Schedule Scan", ["teen aligners", "invisible braces", "confident smile"], "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=800&q=80", 15),
            (c3_3, "Tip", "Tip", "Floss before or after brushing? Studies prove flossing BEFORE brushing dislodges plaque so fluoride from toothpaste reaches interdental crevices more effectively.", "Learn More", ["flossing tip", "brushing order", "prevent cavities"], "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80", 22),
            (c3_3, "Before / After Transformation", "Showcase", "Composite bonding closed a prominent diastema (front tooth gap) in just 30 minutes without drilling or anesthesia.", "View Portfolio", ["composite bonding", "gap closure", "cosmetic dentistry"], "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?auto=format&fit=crop&w=800&q=80", 30)
        ]

        # -------------------------------------------------------------------------
        # PROJECT 4: FITNESS & GYM
        # -------------------------------------------------------------------------
        p4_facts = {
            "business_name": "IronForge Performance Studio",
            "disciplines": ["CrossFit Affiliate", "Olympic Weightlifting", "Functional HIIT", "Mobility Conditioning"],
            "trainers": "Certified CSCS Strength and Conditioning Specialists"
        }
        p4 = Project(
            project_name="IronForge Fitness Andheri",
            client_business_name="IronForge Performance Studio",
            google_maps_url="https://www.google.com/maps/place/IronForge+Andheri",
            description="Functional strength, CrossFit, HIIT, and personal athletic conditioning facility in Andheri West.",
            verified_facts=json.dumps(p4_facts, indent=2)
        )
        db.add(p4)
        db.flush()

        kws_p4 = ["gym in Andheri West", "crossfit Mumbai", "personal trainer Andheri", "HIIT workout", "strength gym"]
        for k in kws_p4:
            db.add(Keyword(project_id=p4.id, keyword=k))

        c4_1 = Competitor(project_id=p4.id, business_name="Gold's Gym Andheri", google_maps_url="https://www.google.com/maps/place/Golds+Gym+Andheri", place_identifier="ChIJf_111", status="active", total_posts=4, scraping_status="completed", last_scraped_at=now - timedelta(hours=12))
        c4_2 = Competitor(project_id=p4.id, business_name="Cult.fit Andheri West", google_maps_url="https://www.google.com/maps/place/Cult+Fit+Andheri", place_identifier="ChIJf_222", status="active", total_posts=4, scraping_status="completed", last_scraped_at=now - timedelta(hours=13))
        c4_3 = Competitor(project_id=p4.id, business_name="CrossFit Myden", google_maps_url="https://www.google.com/maps/place/Crossfit+Myden", place_identifier="ChIJf_333", status="active", total_posts=4, scraping_status="completed", last_scraped_at=now - timedelta(hours=14))
        db.add_all([c4_1, c4_2, c4_3])
        db.flush()

        posts_p4_data = [
            (c4_1, "Membership Discount", "Offer", "New Year Transformation Challenge! Sign up for an Annual Membership and get 3 months free + 5 one-on-one personal training sessions and a body DEXA scan. Limited to 50 passes.", "Claim Pass", ["gym discount", "annual membership", "personal trainer offer"], "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80", 2),
            (c4_1, "HIIT Training", "Tip", "Why progressive overload is non-negotiable for fat loss: Adding 1 rep or 1 kg per week forces your metabolic rate to remain elevated for 48 hours post-workout.", "Learn More", ["progressive overload", "fat loss tip", "strength training"], "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80", 7),
            (c4_1, "Before / After Transformation", "Showcase", "Member Spotlight: Rohit dropped 14 kg and lowered body fat from 28% to 14% in 16 weeks under Coach Sarah's periodized nutrition and hypertrophy plan.", "View Story", ["member transformation", "weight loss results", "fitness motivation"], "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?auto=format&fit=crop&w=800&q=80", 15),
            (c4_1, "Product Update", "Product Update", "Upgraded our strength floor with 6 Olympic lifting platforms and calibrated Eleiko plates. Ready for your personal bests!", "Get Directions", ["olympic lifting", "eleiko plates", "strength gym"], "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80", 24),

            (c4_2, "HIIT Training", "Event", "Burn 700 calories in our 45-minute Sunrise Burn class tomorrow at 6:30 AM! High-octane music, certified trainers, and zero boring treadmills.", "Book Class", ["hiit class", "group fitness", "calorie burn"], "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80", 4),
            (c4_2, "Membership Discount", "Offer", "Try 2 free trial classes this week! No credit card required. Experience boxing conditioning, yoga flow, and athletic strength.", "Claim Trial", ["free trial class", "cult workout", "boxing conditioning"], "https://images.unsplash.com/photo-1549060279-7e168fcee0c2?auto=format&fit=crop&w=800&q=80", 10),
            (c4_2, "Tip", "Tip", "Hydration tip: If your workout exceeds 45 minutes of heavy sweating, plain water isn't enough. Replenish sodium and potassium electrolytes to stave off muscle cramping.", "Read Guide", ["electrolyte tip", "hydration", "workout recovery"], "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80", 19),
            (c4_2, "Before / After Transformation", "Showcase", "From feeling winded on stairs to running a half-marathon! Congratulations Ananya on your inspiring 6-month endurance journey.", "View Portfolio", ["endurance transformation", "marathon training", "client story"], "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?auto=format&fit=crop&w=800&q=80", 27),

            (c4_3, "HIIT Training", "Event", "Community Saturday WOD (Workout of the Day): Partner kettlebell & rowing challenge followed by protein smoothie bar on the turf. Open to all levels.", "Join Event", ["crossfit wod", "community workout", "kettlebell"], "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=800&q=80", 5),
            (c4_3, "Membership Discount", "Offer", "Student & Corporate athletic pass: 20% off all quarterly memberships with valid business or college ID.", "Sign Up", ["student gym offer", "corporate fitness", "crossfit discount"], "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80", 12),
            (c4_3, "Tip", "Tip", "Mobility routine for squat depth: Spend 2 minutes daily in a goblet squat hold to stretch ankle dorsiflexion and open adductor tight spots.", "Watch Video", ["mobility drill", "squat depth", "functional fitness"], "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80", 20),
            (c4_3, "Before / After Transformation", "Showcase", "Strength milestone: 38-year-old software architect Priya nailed her first strict pull-up after 12 weeks of lat activation drills!", "View Story", ["first pullup", "calisthenics", "strength milestone"], "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?auto=format&fit=crop&w=800&q=80", 29)
        ]

        all_projects_data = [
            (p1, posts_p1_data),
            (p2, posts_p2_data),
            (p3, posts_p3_data),
            (p4, posts_p4_data)
        ]

        total_seeded_posts = 0

        for project, post_list in all_projects_data:
            for comp, topic, ctype, text, cta, keywords, img_url, days_ago in post_list:
                pub_date = now - timedelta(days=days_ago)
                post_url = f"{comp.google_maps_url}#post-{total_seeded_posts + 1}"
                fp = generate_post_fingerprint(
                    post_url=post_url,
                    source_post_id=f"demo_post_{total_seeded_posts + 1}",
                    competitor_name=comp.business_name,
                    post_text=text,
                    published_date=pub_date,
                    profile_url=comp.google_maps_url
                )

                post = Post(
                    project_id=project.id,
                    competitor_id=comp.id,
                    competitor_name=comp.business_name,
                    google_maps_profile_url=comp.google_maps_url,
                    post_url=post_url,
                    post_text=text,
                    published_date=pub_date,
                    call_to_action=cta,
                    detected_keywords=",".join(keywords),
                    industry_topic=topic,
                    content_type=ctype,
                    source_information="SEEDED",
                    source_type="SEEDED",
                    is_valid=True,
                    fingerprint=fp,
                    scraped_at=now - timedelta(days=days_ago, hours=1)
                )
                db.add(post)
                db.flush()

                # Add Media
                media = PostMedia(
                    post_id=post.id,
                    media_type="image",
                    media_url=img_url,
                    thumbnail_url=img_url,
                    caption=f"{topic} - {comp.business_name}"
                )
                db.add(media)

                # Pre-populate PostAnalysis for instant trend & analysis readiness
                analysis = PostAnalysis(
                    post_id=post.id,
                    main_topic=topic,
                    sub_topic=f"{ctype} Campaign",
                    keywords=json.dumps(keywords),
                    content_type=ctype,
                    call_to_action=cta,
                    offer_pattern="Discount Promotion" if ctype == "Offer" else None,
                    sentiment="positive",
                    ai_provider="seed_dataset",
                    analyzed_at=now - timedelta(days=days_ago)
                )
                db.add(analysis)

                total_seeded_posts += 1

        # -------------------------------------------------------------------------
        # Seed Past Scraping Job History with valid_posts
        # -------------------------------------------------------------------------
        job1 = ScrapingJob(
            project_id=p1.id,
            job_type="DEMO",
            start_time=now - timedelta(hours=3),
            end_time=now - timedelta(hours=2, minutes=58),
            status="Completed",
            competitors_processed=4,
            total_competitors=4,
            posts_found=19,
            valid_posts=19,
            new_posts=19,
            duplicates_skipped=0,
            images_downloaded=19,
            failures=0,
            captcha_detected=False
        )
        db.add(job1)
        db.flush()

        for comp, count in [(c1_1, 5), (c1_2, 5), (c1_3, 5), (c1_4, 4)]:
            item = ScrapingJobItem(
                job_id=job1.id,
                competitor_id=comp.id,
                competitor_name=comp.business_name,
                status="SUCCESS",
                posts_found=count,
                valid_posts=count,
                new_posts=count,
                duplicates_skipped=0,
                log_message=f"Successfully extracted {count} verified updates for {comp.business_name}",
                timestamp=now - timedelta(hours=3)
            )
            db.add(item)

        # -------------------------------------------------------------------------
        # Seed Initial Generated Ideas & Updates with verified facts
        # -------------------------------------------------------------------------
        idea1 = GeneratedIdea(
            project_id=p1.id,
            title="Monsoon Humidity Hair Therapy Showcase",
            topic="Hair Care Tips",
            description="Highlight our restorative organic moisture spa for frizzy monsoon hair, with a complimentary scalp consultation for first-time visitors.",
            relevant_keywords="monsoon hair care, botanical hair spa, frizz control, thane salon",
            suggested_cta="Book Appointment",
            competitor_insight="Competitors run generic discounts; emphasizing scalp diagnostics differentiates Ravi's Family Salon as a trusted local authority.",
            ai_provider="gemini",
            model_used="gemini-2.5-flash",
            semantic_hash=generate_idea_semantic_hash("Monsoon Humidity Hair Therapy Showcase", "Hair Care Tips", "Highlight our restorative organic moisture spa for frizzy monsoon hair"),
            created_at=now - timedelta(days=1)
        )
        db.add(idea1)
        db.flush()

        update1 = GeneratedUpdate(
            project_id=p1.id,
            idea_id=idea1.id,
            topic="Hair Care Tips",
            update_copy="🌿 Don't Let Monsoon Humidity Dull Your Hair! 🌿\n\nAt Ravi's Family Salon, our experienced styling team provides customized botanical moisture treatments to protect cuticles, restore natural shine, and manage frizz.\n\n✨ Why clients choose us:\n• Dedicated team providing personalized hair care consultations\n• Clean, sanitized private styling suites\n• Convenient client parking in Panchpakhadi, Thane West\n\n👉 Reserve your appointment today!\n\n#ThaneWest #HairCareTips #RavisFamilySalon #GoogleMapsUpdate",
            relevant_keywords="hair care tips, botanical hair treatment, best salon in thane, hair spa thane",
            call_to_action="Book Appointment",
            image_concept="Close-up high-definition shot of glossy, healthy brunette tresses after botanical treatment in a luminous salon setting with eco-minimalist plant decor.",
            ai_provider="gemini",
            model_used="gemini-2.5-flash",
            created_at=now - timedelta(days=1)
        )
        db.add(update1)

        db.commit()
        print(f"Seed completed successfully! Seeded 4 projects and {total_seeded_posts} realistic Google Maps updates.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
