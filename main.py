from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
import json
import os
from uuid import UUID, uuid4

app = FastAPI()

# In-memory database
db = []


class UserCreate(BaseModel):
    name: str
    email: str


class User(UserCreate):
    id: UUID


@app.get("/users")
def get_users():
    return db


@app.get("/users/{user_id}")
def get_user(user_id: UUID):
    for user in db:
        if user['id'] == user_id:
            return user
    return {"message": "User not found"}


@app.post("/users")
def create_user(user: UserCreate):
    user_id = uuid4()
    user_data = User(id=user_id, **user.dict())
    db.append(user_data.dict())
    return {"id": str(user_id), "message": "User created successfully"}


@app.put("/users/{user_id}")
def update_user(user_id: UUID, user: UserCreate):
    for i, db_user in enumerate(db):
        if db_user['id'] == user_id:
            user_data = user.dict()
            user_data['id'] = user_id
            db[i] = user_data
            return {"message": "User updated successfully"}
    return {"message": "User not found"}


@app.delete("/users/{user_id}")
def delete_user(user_id: UUID):
    for i, user in enumerate(db):
        if user['id'] == user_id:
            del db[i]
            return {"message": "User deleted successfully"}
    return {"message": "User not found"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="User Database",
        version="1.0.0",
        description="This API manages a simple User database",
        routes=app.routes,
        servers=[{"url": "http://127.0.0.1:8000"}]
    )
    file_path = os.path.join(os.getcwd(), "openapi.json")
    with open(file_path, "w") as file:
        file.write(json.dumps(openapi_schema, indent=2))
    app.openapi_schema = openapi_schema
    return app.openapi_schema


custom_openapi()

app.openapi = custom_openapi
