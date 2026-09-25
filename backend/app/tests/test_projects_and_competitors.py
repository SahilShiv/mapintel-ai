def test_create_and_get_project(client):
    res = client.post("/api/projects", json={
        "project_name": "Test Salon Intelligence",
        "client_business_name": "Glow Hair Salon",
        "google_maps_url": "https://maps.google.com/?cid=123",
        "description": "Test salon project",
        "keywords": ["salon", "hair cut", "hair spa"]
    })
    assert res.status_code == 201
    data = res.json()
    assert data["project_name"] == "Test Salon Intelligence"
    assert data["client_business_name"] == "Glow Hair Salon"
    project_id = data["id"]

    # Verify get by id
    get_res = client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 200
    p_data = get_res.json()
    assert len(p_data["keywords"]) == 3
    assert p_data["keywords_count"] == 3

def test_add_competitor_manually(client):
    proj_res = client.post("/api/projects", json={
        "project_name": "Bistro Project",
        "client_business_name": "Bistro Client"
    })
    proj_id = proj_res.json()["id"]

    comp_res = client.post(f"/api/projects/{proj_id}/competitors", json={
        "business_name": "Competitor Gourmet One",
        "google_maps_url": "https://maps.google.com/place/comp1"
    })
    assert comp_res.status_code == 201
    comp_data = comp_res.json()
    assert comp_data["business_name"] == "Competitor Gourmet One"
    assert comp_data["project_id"] == proj_id

    # Verify listing
    comps = client.get(f"/api/projects/{proj_id}/competitors").json()
    assert len(comps) == 1
    assert comps[0]["business_name"] == "Competitor Gourmet One"

def test_keyword_management(client):
    proj = client.post("/api/projects", json={
        "project_name": "Keywords Test",
        "client_business_name": "Test Client"
    }).json()

    # Add keyword
    kw_res = client.post(f"/api/projects/{proj['id']}/keywords", json={"keyword": "best pizza in town"})
    assert kw_res.status_code == 201
    kw_id = kw_res.json()["id"]

    # Delete keyword
    del_res = client.delete(f"/api/projects/{proj['id']}/keywords/{kw_id}")
    assert del_res.status_code == 204

    # Verify deleted
    kws = client.get(f"/api/projects/{proj['id']}/keywords").json()
    assert len(kws) == 0
