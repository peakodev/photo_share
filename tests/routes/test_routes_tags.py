import pytest
from app.models.tag import Tag
from urllib.parse import quote_plus

def test_create_tag_in_db(client):
    test_sting_tag = "base_tag"
    encode_string = quote_plus(test_sting_tag)
    response = client.post(f'api/tags?text={encode_string}')
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == test_sting_tag

def test_get_all_tags(client, session):
    response = client.get("api/tags/all_tags/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
def test_search_tag_by_text_not_found(client):
    response = client.get("api/tags/tag_value/not_found")
    assert response.status_code == 404

def test_search_tag_by_text_found(client, session):
    test_tag = Tag(id=2, text="new_tag")
    session.add(test_tag)
    session.commit()
    response = client.get(f"api/tags/tag_value/{test_tag.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == test_tag.text

def test_search_tag_by_id_not_found(client):
    responce = client.get(f"api/tags/tag_id/10")
    assert responce.status_code == 404

def test_search_tag_by_id_found(client, session):
    test_tag = Tag(id=3, text="hello")
    session.add(test_tag)
    session.commit()

    response = client.get(f"api/tags/tag_id/{test_tag.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == test_tag.text

def test_create_tags_by_string(client):
    test_string = "first, second, third, fourth, fifth, sixth"
    encode_string = quote_plus(test_string)
    result_in_list = ["first", "second", "third", "fourth", "fifth", "sixth" ]

    response = client.post(f"/api/tags/tags_by_string?string={encode_string}")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["text"] == result_in_list[0]
    assert data[1]["text"] == result_in_list[1]
    assert data[2]["text"] == result_in_list[2]
    assert data[3]["text"] == result_in_list[3]
    assert data[4]["text"] == result_in_list[4]
    with pytest.raises(IndexError):
        data[5]

    



#pytest tests/routes/test_routes_tags.py