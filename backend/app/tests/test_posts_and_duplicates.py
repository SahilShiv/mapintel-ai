from datetime import datetime, timezone
from backend.app.services.fingerprint import generate_post_fingerprint

def test_fingerprint_generation_stability():
    fp1 = generate_post_fingerprint(
        post_url="https://www.google.com/maps/place/test/post/123",
        competitor_name="Super Salon",
        post_text="Get 20% off on hair spa this week!",
        published_date=datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
    )
    fp2 = generate_post_fingerprint(
        post_url="https://www.google.com/maps/place/test/post/123",
        competitor_name="Super Salon",
        post_text="Get 20% off on hair spa this week!",
        published_date=datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
    )
    assert fp1 == fp2

def test_duplicate_detection_across_repeated_scrapes(client):
    # Create project and competitor
    proj = client.post("/api/projects", json={
        "project_name": "Dupe Test Project",
        "client_business_name": "Client X"
    }).json()
    proj_id = proj["id"]

    comp = client.post(f"/api/projects/{proj_id}/competitors", json={
        "business_name": "Competitor Dupe Alpha",
        "google_maps_url": "https://maps.google.com/place/dupe-alpha"
    }).json()

    # Run initial scrape (should insert new posts)
    scrape1 = client.post("/api/scrape", json={
        "project_id": proj_id,
        "mode": "demo",
        "sync": True
    }).json()
    assert scrape1["status"] == "Completed"
    assert scrape1["new_posts"] > 0
    assert scrape1["duplicates_skipped"] == 0
    initial_new_posts = scrape1["new_posts"]

    # Verify repository has posts
    posts_res1 = client.get(f"/api/posts?project_id={proj_id}").json()
    assert posts_res1["total"] == initial_new_posts

    # Run second scrape (MUST detect duplicates and skip all identical posts!)
    scrape2 = client.post("/api/scrape", json={
        "project_id": proj_id,
        "mode": "demo",
        "sync": True
    }).json()
    assert scrape2["status"] == "Completed"
    assert scrape2["new_posts"] == 0
    assert scrape2["duplicates_skipped"] == initial_new_posts

    # Verify repository total did NOT increase
    posts_res2 = client.get(f"/api/posts?project_id={proj_id}").json()
    assert posts_res2["total"] == initial_new_posts

def test_existing_data_remains_available_after_failed_or_captcha_scrape(client):
    proj = client.post("/api/projects", json={
        "project_name": "Failure Resilience Project",
        "client_business_name": "Resilient Client"
    }).json()
    proj_id = proj["id"]

    client.post(f"/api/projects/{proj_id}/competitors", json={
        "business_name": "Test Salon Competitor",
        "google_maps_url": "https://maps.google.com/place/resilient"
    })

    # Initial successful scrape
    client.post("/api/scrape", json={"project_id": proj_id, "mode": "demo", "sync": True})
    initial_total = client.get(f"/api/posts?project_id={proj_id}").json()["total"]
    assert initial_total > 0

    # Trigger a scrape with simulated CAPTCHA
    captcha_job = client.post(f"/api/scrape/demo?project_id={proj_id}&simulate_captcha=true&sync=true").json()
    assert captcha_job["status"] == "Manual Intervention Required"
    assert captcha_job["captcha_detected"] is True

    # Crucial assertion: Existing repository data remains fully intact and available
    after_posts = client.get(f"/api/posts?project_id={proj_id}").json()
    assert after_posts["total"] == initial_total
