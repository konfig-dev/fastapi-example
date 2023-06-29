from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.openapi.utils import get_openapi
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import json
import os
from uuid import UUID, uuid4

app = FastAPI()

# In-memory database
db = []

# API key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

class UserCreate(BaseModel):
    name: str
    email: str

class User(UserCreate):
    id: UUID

@app.get("/users")
def get_users(api_key: str = Depends(api_key_header)):
    return db

@app.get("/users/{user_id}")
def get_user(user_id: UUID, api_key: str = Depends(api_key_header)):
    for user in db:
        if user['id'] == user_id:
            return user
    return {"message": "User not found"}

@app.post("/users")
def create_user(user: UserCreate, api_key: str = Depends(api_key_header)):
    user_id = uuid4()
    user_data = User(id=user_id, **user.dict())
    db.append(user_data.dict())
    return {"id": str(user_id), "message": "User created successfully"}

@app.put("/users/{user_id}")
def update_user(user_id: UUID, user: UserCreate, api_key: str = Depends(api_key_header)):
    for i, db_user in enumerate(db):
        if db_user['id'] == user_id:
            user_data = user.dict()
            user_data['id'] = user_id
            db[i] = user_data
            return {"message": "User updated successfully"}
    return {"message": "User not found"}

@app.delete("/users/{user_id}")
def delete_user(user_id: UUID, api_key: str = Depends(api_key_header)):
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
        servers=[{"url": "http://127.0.0.1:8000"}],
    )

    # Add security requirement to the OpenAPI schema
    security_scheme = {
        "X-API-Key": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header"
        }
    }
    security_requirements = [{"X-API-Key": []}]
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    openapi_schema["components"]["securitySchemes"] = {"X-API-Key": security_scheme}
    openapi_schema["security"] = security_requirements

    file_path = os.path.join(os.getcwd(), "openapi.json")
    with open(file_path, "w") as file:
        file.write(json.dumps(openapi_schema, indent=2))

    app.openapi_schema = openapi_schema
    return app.openapi_schema

custom_openapi()
app.openapi = custom_openapi
