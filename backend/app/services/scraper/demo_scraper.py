import random
import time
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from backend.app.services.scraper.base import BaseScraper, ScrapedPost, ScrapeResult

DEMO_UPDATE_TEMPLATES = [
    {
        "pattern": "Salon / Beauty",
        "keywords": ["hair care", "keratin treatment", "hair spa", "monsoon hair", "balayage", "salon offers"],
        "posts": [
            {
                "topic": "Hair Care Tips",
                "content_type": "Tip",
                "text": "Tired of frizzy hair this monsoon? Our senior stylists recommend our customized Botanical Deep Moisture Spa. Get silky, manageable tresses in just 45 minutes! Book your slot this week and enjoy a complimentary scalp analysis.",
                "cta": "Book Appointment",
                "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=800&q=80"
            },
            {
                "topic": "Festival Offer",
                "content_type": "Offer",
                "text": "Festive Glam Days are here! Get Flat 30% OFF on all Keratin & Botox Hair Treatments until Sunday. Limited slots available daily to ensure individual care and safety. Call now or walk in to reserve your spot.",
                "cta": "Call Now",
                "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80"
            },
            {
                "topic": "Before / After Transformation",
                "content_type": "Showcase",
                "text": "Stunning caramel balayage transformation by our master colorist Priya! Swipe to see the brassy before vs seamless blended tone after. Done using ammonia-free Italian organic color pigments.",
                "cta": "View Portfolio",
                "image": "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?auto=format&fit=crop&w=800&q=80"
            },
            {
                "topic": "Skin Glow Treatment",
                "content_type": "Product Update",
                "text": "Introducing the 7-Step Korean Hydra Glow Facial at our studio. Unclog pores, infuse hyaluronic acid, and walk out with an unmatched glass skin radiance. Suitable for all sensitive skin types.",
                "cta": "Book Now",
                "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=800&q=80"
            }
        ]
    },
    {
        "pattern": "Restaurant / Cafe",
        "keywords": ["woodfired pizza", "happy hours", "weekend brunch", "craft beer", "chef special", "gourmet dining"],
        "posts": [
            {
                "topic": "Weekend Brunch",
                "content_type": "Event",
                "text": "Sundays are meant for slow mornings and endless pancakes! Join our lavish Weekend Garden Brunch with live acoustic jazz, sourdough benedicts, and unlimited artisanal mocktails from 11 AM to 4 PM.",
                "cta": "Reserve Table",
                "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80"
            },
            {
                "topic": "Chef Special",
                "content_type": "Product Update",
                "text": "Fresh from our wood-fired oven: The Truffle Burrata Neapolitan Pizza with 48-hour fermented dough, San Marzano sauce, and wild forest mushrooms. Available exclusively this weekend!",
                "cta": "Order Online",
                "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80"
            },
            {
                "topic": "Happy Hours",
                "content_type": "Offer",
                "text": "Beat the weekday blues with 1-for-1 on all craft cocktails and appetizers every Tuesday to Friday between 5 PM and 8 PM. Bring your squad for great rooftop vibes!",
                "cta": "Get Directions",
                "image": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=800&q=80"
            }
        ]
    },
    {
        "pattern": "Dental Clinic / Healthcare",
        "keywords": ["teeth whitening", "clear aligners", "painless dentistry", "dental implants", "smile makeover", "oral hygiene"],
        "posts": [
            {
                "topic": "Teeth Whitening",
                "content_type": "Offer",
                "text": "Brighten your smile up to 5 shades in a single 45-minute laser session! Safe on enamel, zero sensitivity. Special 25% discount for first-time consultations this month.",
                "cta": "Book Consultation",
                "image": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80"
            },
            {
                "topic": "Clear Aligners",
                "content_type": "Product Update",
                "text": "Straighten your teeth invisibly without metal brackets or food restrictions. Book your 3D digital oral scan and get a free simulation of your future smile within 10 minutes!",
                "cta": "Schedule Scan",
                "image": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=800&q=80"
            }
        ]
    },
    {
        "pattern": "Fitness / Gym",
        "keywords": ["HIIT training", "personal trainer", "crossfit", "strength conditioning", "membership discount", "weight loss"],
        "posts": [
            {
                "topic": "Membership Discount",
                "content_type": "Offer",
                "text": "Transform your health before the year ends! Sign up for our 6-Month All-Access Gym Pass and get 2 free personal training sessions plus a body composition DEXA scan.",
                "cta": "Sign Up",
                "image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80"
            },
            {
                "topic": "HIIT Training",
                "content_type": "Tip",
                "text": "Why 25 minutes of high-intensity interval training burns more calories than 60 minutes of steady cardio: EPOC (Excess Post-Exercise Oxygen Consumption). Join Coach Mark's morning burner at 7 AM!",
                "cta": "Join Class",
                "image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80"
            }
        ]
    }
]

class DemoGoogleMapsScraper(BaseScraper):
    """
    Realistic demo scraping engine that yields authentic Google Maps posts
    with deterministic stable data for repeatable duplicate detection testing.
    """

    def __init__(self, simulate_captcha: bool = False, delay_seconds: float = 0.8):
        self.simulate_captcha = simulate_captcha
        self.delay_seconds = delay_seconds

    def scrape_competitor(
        self,
        competitor_id: Optional[int],
        competitor_name: str,
        google_maps_url: str,
        job_id: Optional[int] = None
    ) -> ScrapeResult:
        # Realistic time step for UI progress display
        time.sleep(self.delay_seconds)

        if self.simulate_captcha:
            return ScrapeResult(
                competitor_id=competitor_id,
                competitor_name=competitor_name,
                status="captcha_required",
                posts_found=0,
                error_message="Simulated Google Maps security checkpoint / CAPTCHA triggered.",
                log_message=f"Manual intervention required for {competitor_name}",
                captcha_detected=True
            )

        # Match template by competitor name or round-robin
        name_lower = competitor_name.lower()
        selected_category = DEMO_UPDATE_TEMPLATES[0] # Salon default
        if any(w in name_lower for w in ["cafe", "restaurant", "bistro", "pizza", "dining", "grill", "bar"]):
            selected_category = DEMO_UPDATE_TEMPLATES[1]
        elif any(w in name_lower for w in ["dental", "clinic", "dentist", "smile", "teeth", "care"]):
            selected_category = DEMO_UPDATE_TEMPLATES[2]
        elif any(w in name_lower for w in ["fit", "gym", "crossfit", "workout", "studio"]):
            selected_category = DEMO_UPDATE_TEMPLATES[3]

        posts: List[ScrapedPost] = []
        base_date = datetime.now(timezone.utc) - timedelta(days=2)

        for idx, item in enumerate(selected_category["posts"]):
            post_date = base_date - timedelta(days=idx * 7)
            # Create a stable post URL and ID tied to competitor_name and idx
            slug = competitor_name.lower().replace(" ", "-")
            post_url = f"https://www.google.com/maps/place/{slug}/post/demo-{idx+1}?entry=ttu"
            
            p = ScrapedPost(
                post_url=post_url,
                post_text=item["text"],
                published_date=post_date,
                media_urls=[item["image"]],
                call_to_action=item["cta"],
                source_post_id=f"demo_{slug}_{idx+1}",
                detected_keywords=selected_category["keywords"][:4],
                industry_topic=item["topic"],
                content_type=item["content_type"]
            )
            posts.append(p)

        return ScrapeResult(
            competitor_id=competitor_id,
            competitor_name=competitor_name,
            status="success",
            posts_found=len(posts),
            posts=posts,
            log_message=f"Extracted {len(posts)} authentic updates for {competitor_name}"
        )
