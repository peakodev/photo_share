import asyncio
from os import getcwd

import pytest
from urllib.request import urlopen
from urllib.parse import quote_plus

from app.repository.users import get_user_by_email
from app.models import User


def test_create_post_with_tags(client, token, user):
    test_description = "new post"
    test_tags = "new, post"
    test_file_bstring = str
    headers = {"Authorization": f"Bearer {token}"}
    with open(f"{getcwd()}\\tests\\user-default.png","rb") as file:
            test_file_bstring = file.read()
    test_file = {"file": ("user-default.png",test_file_bstring)}
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"api/posts/create?description={quote_plus(test_description)}&tags={quote_plus(test_tags)}",
                           headers=headers,
                           files=test_file)
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == test_description
    assert data["user"]["email"] == user["email"]
    assert data["tags"][0]["text"] == "new"
    assert data["tags"][1]["text"] == "post"
    post_picture_bstring = urlopen(data["photo_url"]).read()
    assert post_picture_bstring == test_file_bstring

def test_create_post_without_tags(client, token, user):
    test_description = "new post"
    test_file_bstring = str
    headers = {"Authorization": f"Bearer {token}"}
    with open(f"{getcwd()}\\tests\\user-default.png","rb") as file:
            test_file_bstring = file.read()
    test_file = {"file": ("user-default.png",test_file_bstring)}
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"api/posts/create?description={quote_plus(test_description)}",
                           headers=headers,
                           files=test_file)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == user["email"]
    assert data["description"] == test_description
    assert data["tags"] == []
    post_picture_bstring = urlopen(data["photo_url"]).read()
    assert post_picture_bstring == test_file_bstring

def test_get_posts(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    limit = 10
    offset = 0

    response = client.get(f"api/posts/?limit={limit}&offset={offset}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == 1

def test_get_all_posts(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    limit = 10
    offset = 0

    response = client.get(f"api/posts/?limit={limit}&offset={offset}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == 1

def test_get_post_user_unauthorized(client):
    response = client.get("api/posts/1")
    assert response.status_code == 200

def test_get_post_user_authorized(client, token):
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("api/posts/1", headers=headers)
    assert response.status_code == 200

def test_get_post_user_authorized_post_not_found(client, token):
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("api/posts/10", headers=headers)
    assert response.status_code == 404 
    
def test_find_post_user_not_unauthorized(client):
    test_string = "not_found"

    response = client.get(f"api/posts/find/?find_str={test_string}")
    assert response.status_code == 401

def test_find_post_user_authorized_post_not_found(client, token):
    test_string = "not_found"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"api/posts/find/?find_str={test_string}", headers=headers)
    assert response.status_code == 404

def test_find_post_user_authorized_post_found(client, token):
    test_string = "new"
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"api/posts/find/?find_str={test_string}", headers=headers)
    assert response.status_code == 200

def test_update_post_user_not_unauthorized(client):
    post_id = 1
    new_description = "wow"

    response = client.put(f"api/posts/{post_id}?description={quote_plus(new_description)}")
    assert response.status_code == 401

def test_update_post_user_authorized_post_not_found(client, token):
    post_id = 10
    new_description = "wow"
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(f"api/posts/{post_id}?description={quote_plus(new_description)}", headers=headers)
    assert response.status_code == 404

def test_update_post_owner_authorized_update_description(client, token):
    post_id = 1
    new_description = "wow"
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(f"api/posts/{post_id}?description={quote_plus(new_description)}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == new_description

def  test_update_post_owner_authorized_update_tags(client, token):
    post_id = 2
    new_tests = "super, star"
    expected_result = ["super", "star"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(f"api/posts/{post_id}?tags={quote_plus(new_tests)}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tags"][0] == expected_result[0]
    assert data["tags"][1] == expected_result[1]
    with pytest.raises(IndexError):
        data["tags"][2]

def test_update_post_owner_authorized_update_file(client, token):
    post_id = 1
    test_file_bstring = str
    with open(f"{getcwd()}\\tests\\user-default.png","rb") as file:
            test_file_bstring = file.read()
    test_file = {"file": ("user-default.png",test_file_bstring)}
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(f"api/posts/{post_id}", headers=headers, files=test_file)
    assert response.status_code == 200

def test_delete_post_user_owner(client, token):
    post_id = 2
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(f'api/posts/{post_id}', headers=headers)
    assert response.status_code == 200

def test_update_post_user_not_owner(client, user, token, session):
    post_id = 1
    new_description = "wow"
    headers = {"Authorization": f"Bearer {token}"}
    user= asyncio.run(get_user_by_email(user["email"], session))
    fake_user = User(id=1,
                      first_name="name",
                      last_name="lastname",
                      email="fake@email.com",
                      password="password",
                      refresh_token = 'test_token')
    user.id = 2
    session.add(fake_user)
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.put(f"api/posts/{post_id}?description={quote_plus(new_description)}", headers=headers)

    session.delete(fake_user)
    session.commit()
    user.id = 1
    session.add(user)
    session.commit()
    session.refresh(user)

    assert response.status_code == 403

def test_update_post_user_not_owner(client, user, token, session):
    post_id = 1
    headers = {"Authorization": f"Bearer {token}"}
    user= asyncio.run(get_user_by_email(user["email"], session))
    fake_user = User(id=1,
                      first_name="name",
                      last_name="lastname",
                      email="fake@email.com",
                      password="password",
                      refresh_token = 'test_token')
    user.id = 2
    session.add(fake_user)
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.delete(f'api/posts/{post_id}', headers=headers)

    session.delete(fake_user)
    session.commit()
    user.id = 1
    session.add(user)
    session.commit()
    session.refresh(user)

    assert response.status_code == 403

def test_delete_post_user_not_owner(client, token, session, user):
    post_id = 1
    headers = {"Authorization": f"Bearer {token}"}
    user= asyncio.run(get_user_by_email(user["email"], session))
    fake_user = User(id=1,
                      first_name="name",
                      last_name="lastname",
                      email="fake@email.com",
                      password="password",
                      refresh_token = 'test_token')
    user.id = 2
    session.add(fake_user)
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.delete(f'api/posts/{post_id}', headers=headers)

    session.delete(fake_user)
    session.commit()
    user.id = 1
    session.add(user)
    session.commit()
    session.refresh(user)

    assert response.status_code == 403

    




#pytest tests/routes/test_routes_posts.py