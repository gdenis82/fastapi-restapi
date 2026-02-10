import pytest


@pytest.mark.asyncio
async def test_api_key_required(client):
    response = await client.get("/buildings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_key_invalid(client):
    response = await client.get("/buildings", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_buildings(client, auth_headers, seed_data):
    response = await client.get("/buildings", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8


@pytest.mark.asyncio
async def test_get_organization(client, auth_headers, seed_data):
    org_id = seed_data["organizations"]["org1"]
    response = await client.get(f"/organizations/{org_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == org_id


@pytest.mark.asyncio
async def test_by_building(client, auth_headers, seed_data):
    building_id = seed_data["buildings"]["b1"]
    response = await client.get(f"/organizations/by-building/{building_id}", headers=auth_headers)
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert ids == {
        seed_data["organizations"]["org2"],
        seed_data["organizations"]["org4"],
        seed_data["organizations"]["org7"],
    }


@pytest.mark.asyncio
async def test_by_activity(client, auth_headers, seed_data):
    activity_id = seed_data["activities"]["meat"]
    response = await client.get(f"/organizations/by-activity/{activity_id}", headers=auth_headers)
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert ids == {
        seed_data["organizations"]["org1"],
        seed_data["organizations"]["org2"],
        seed_data["organizations"]["org5"],
        seed_data["organizations"]["org9"],
    }


@pytest.mark.asyncio
async def test_by_activity_tree(client, auth_headers, seed_data):
    activity_id = seed_data["activities"]["food"]
    response = await client.get(f"/organizations/by-activity-tree/{activity_id}", headers=auth_headers)
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert ids == {
        seed_data["organizations"]["org1"],
        seed_data["organizations"]["org2"],
        seed_data["organizations"]["org5"],
        seed_data["organizations"]["org6"],
        seed_data["organizations"]["org7"],
        seed_data["organizations"]["org8"],
        seed_data["organizations"]["org9"],
        seed_data["organizations"]["org10"],
    }


@pytest.mark.asyncio
async def test_by_activity_name(client, auth_headers, seed_data):
    response = await client.get(
        "/organizations/by-activity-name",
        headers=auth_headers,
        params={"name": "Food", "include_children": True},
    )
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert ids == {
        seed_data["organizations"]["org1"],
        seed_data["organizations"]["org2"],
        seed_data["organizations"]["org5"],
        seed_data["organizations"]["org6"],
        seed_data["organizations"]["org7"],
        seed_data["organizations"]["org8"],
        seed_data["organizations"]["org9"],
        seed_data["organizations"]["org10"],
    }


@pytest.mark.asyncio
async def test_search_by_name(client, auth_headers, seed_data):
    response = await client.get("/organizations/search", headers=auth_headers, params={"name": "Auto"})
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert ids == {seed_data["organizations"]["org3"]}


@pytest.mark.asyncio
async def test_nearby(client, auth_headers, seed_data):
    response = await client.get(
        "/organizations/near",
        headers=auth_headers,
        params={"lat": 55.76, "lon": 37.63, "radius_km": 10},
    )
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert ids == {
        seed_data["organizations"]["org1"],
        seed_data["organizations"]["org2"],
        seed_data["organizations"]["org4"],
        seed_data["organizations"]["org5"],
        seed_data["organizations"]["org6"],
        seed_data["organizations"]["org7"],
        seed_data["organizations"]["org8"],
        seed_data["organizations"]["org9"],
        seed_data["organizations"]["org10"],
    }


@pytest.mark.asyncio
async def test_within_rect(client, auth_headers, seed_data):
    response = await client.get(
        "/organizations/within-rect",
        headers=auth_headers,
        params={"min_lat": 55.7, "max_lat": 55.8, "min_lon": 37.5, "max_lon": 37.7},
    )
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert ids == {
        seed_data["organizations"]["org1"],
        seed_data["organizations"]["org2"],
        seed_data["organizations"]["org4"],
        seed_data["organizations"]["org5"],
        seed_data["organizations"]["org6"],
        seed_data["organizations"]["org7"],
        seed_data["organizations"]["org8"],
        seed_data["organizations"]["org9"],
        seed_data["organizations"]["org10"],
    }


@pytest.mark.asyncio
async def test_health(client, auth_headers):
    response = await client.get("/health", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
