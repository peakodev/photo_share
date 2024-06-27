import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Comment, Post, User, Role
from app.schemas.comments import CommentCreate, CommentUpdate
from app.repository.comments import get_comment_by_id, get_comments_by_post, create_comment, update_comment, \
    delete_comment
from app.repository.users import get_user_by_email


@pytest.mark.asyncio
async def test_create_comment(client, session: Session, token: str, user: dict):
    # get the user from database, to have a proper id
    user = await get_user_by_email(user["email"], session)
    post = Post(id=1, description="This is a test post", user_id=user.id)
    session.add(post)
    session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    comment_data = {"post_id": post.id, "text": "This is a test comment"}
    response = client.post("api/comments/create", json=comment_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == comment_data["text"]
    assert data["post_id"] == comment_data["post_id"]


@pytest.mark.asyncio
async def test_get_comment_by_id(client: TestClient, session: Session, token: str, user: dict):
    # get the user from database, to have a proper id
    user = await get_user_by_email(user["email"], session)

    comment = Comment(text="Test comment", post_id=1, user_id=user.id)
    session.add(comment)
    session.commit()

    response = client.get(f"api/comments/{comment.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == comment.text


@pytest.mark.asyncio
async def test_get_comments_by_post(client: TestClient, session: Session, token: str, user: dict):
    user = await get_user_by_email(user["email"], session)

    post = Post(id=10, description="This is a test post", user_id=user.id)
    session.add(post)
    session.commit()

    comments = [Comment(text=f"Test comment {i}", post_id=post.id, user_id=user.id) for i in range(5)]
    session.add_all(comments)
    session.commit()

    response = client.get(f"api/comments/post/{post.id}?offset=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_update_comment(client: TestClient, session: Session, token: str, user: dict):
    user = await get_user_by_email(user["email"], session)

    comment = Comment(text="Old comment", post_id=1, user_id=user.id)
    session.add(comment)
    session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    updated_data = {"text": "Updated comment"}
    response = client.put(f"api/comments/{comment.id}", json=updated_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == updated_data["text"]


@pytest.mark.asyncio
async def test_delete_comment_unauthorized(client: TestClient, session: Session, token: str, user: dict):
    user = await get_user_by_email(user["email"], session)

    comment = Comment(text="Test comment", post_id=1, user_id=user.id)
    session.add(comment)
    session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"api/comments/{comment.id}", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_authorized(client: TestClient, session: Session, admin_token: str, user: dict):
    user = await get_user_by_email(user["email"], session)

    comment = Comment(text="Test comment", post_id=1, user_id=user.id)
    session.add(comment)
    session.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"api/comments/{comment.id}", headers=headers)
    assert response.status_code == 200

    data = response.json()

