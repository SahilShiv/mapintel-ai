def test_content_idea_exact_count_and_duplicate_prevention(client):
    proj = client.post("/api/projects", json={
        "project_name": "Idea Generation Test Project",
        "client_business_name": "Elite Hair Lounge",
        "description": "Premium hair color and treatment studio"
    }).json()
    proj_id = proj["id"]

    # 1. Request exactly 5 ideas
    res_5 = client.post("/api/content-ideas", json={
        "project_id": proj_id,
        "count": 5
    })
    assert res_5.status_code == 200
    data_5 = res_5.json()
    assert data_5["requested_count"] == 5
    assert data_5["generated_count"] == 5
    assert len(data_5["ideas"]) == 5

    # Check structure of generated ideas
    first_idea = data_5["ideas"][0]
    assert "title" in first_idea
    assert "topic" in first_idea
    assert "description" in first_idea
    assert "suggested_cta" in first_idea
    assert "competitor_insight" in first_idea

    # 2. Request exactly 10 ideas (User can select 3, 5, 10, 20, 50)
    res_10 = client.post("/api/content-ideas", json={
        "project_id": proj_id,
        "count": 10
    })
    assert res_10.status_code == 200
    data_10 = res_10.json()
    assert data_10["requested_count"] == 10
    assert len(data_10["ideas"]) == 10

    # 3. Verify duplicate prevention: Verify titles generated are distinct
    all_titles = [i["title"] for i in data_5["ideas"]] + [i["title"] for i in data_10["ideas"]]
    unique_titles = set(all_titles)
    # The duplicate prevention mechanism ensures uniqueness across batches
    assert len(unique_titles) == len(all_titles)

def test_complete_google_maps_update_generation(client):
    proj = client.post("/api/projects", json={
        "project_name": "Update Gen Project",
        "client_business_name": "Artisan Pizza Co"
    }).json()
    proj_id = proj["id"]

    update_res = client.post("/api/generate-update", json={
        "project_id": proj_id,
        "topic": "Weekend Sourdough Special",
        "custom_prompt": "Highlight our 72-hour fermented sourdough crust with hot honey drizzle"
    })
    assert update_res.status_code == 200
    u_data = update_res.json()
    assert u_data["topic"] == "Weekend Sourdough Special"
    assert len(u_data["update_copy"]) > 50
    assert len(u_data["call_to_action"]) > 0
    assert len(u_data["image_concept"]) > 0

    # Verify listing in history
    history = client.get(f"/api/generated-updates?project_id={proj_id}").json()
    assert len(history) == 1
    assert history[0]["id"] == u_data["id"]

def test_trend_analytics(client):
    # Fetch trends for seeded project 1
    projects = client.get("/api/projects").json()
    if projects:
        p_id = projects[0]["id"]
        trends = client.get(f"/api/trends/{p_id}").json()
        assert "top_topics" in trends
        assert "competitor_activity" in trends
        assert "content_types" in trends
        assert "call_to_actions" in trends
        assert trends["total_posts"] > 0
