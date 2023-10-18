from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gotham_app import crud
from gotham_app.exceptions import HTTPException

from robyn import Robyn, jsonify
import json
from gotham_app.models import db_session_maker




app = Robyn(__file__)


from robyn.robyn import Request


@app.post("/crimes")
async def add_crime(request):
    with db_session_maker() as db:
        crime = request.json()
        insertion = crud.create_crime(db, crime)

    if insertion is None:
        raise HTTPException(status_code=400, detail="Invalid crime data")

    return {
        "body": "Crime added successfully",
        "status_code": 200,
    }


@app.get("/crimes")
async def get_crimes(request):
    with db_session_maker() as db:
        skip = request.queries.get("skip", 0)
        limit = request.queries.get("limit", 100)
        crimes = crud.get_crimes(db, skip=skip, limit=limit)

    return jsonify(
        {
            "body": crimes,
            "status_code": 200,
        }
    )


@app.get("/crimes/:crime_id", auth_required=True)
async def get_crime(request):
    crime_id = int(request.path_params.get("crime_id"))
    with db_session_maker() as db:
        crime = crud.get_crime(db, crime_id=crime_id)

    if crime is None:
        raise HTTPException(status_code=404, detail="Crime not found")

    return crime


@app.put("/crimes/:crime_id")
async def update_crime(request):
    crime = request.json()
    crime_id = int(request.path_params.get("crime_id"))
    with db_session_maker() as db:
        updated_crime = crud.update_crime(db, crime_id=crime_id, crime=crime)
    if updated_crime is None:
        raise HTTPException(status_code=404, detail="Crime not found")
    return updated_crime


@app.delete("/crimes/{crime_id}")
async def delete_crime(request):
    crime_id = request.json()
    with db_session_maker() as db:
        success = crud.delete_crime(db, crime_id=crime_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crime not found")
    return {"message": "Crime deleted successfully"}


@app.post("/users/register")
async def register_user(request):
    print(request.body)
    user = request.json()
    with db_session_maker() as db:
        created_user = crud.create_user(db, user)
    return {
        "body": str(created_user),
        "status_code": 200,
    }


@app.post("/users/login")
async def login(request):
    data = request.json()
    username = data.get("username")
    password = data.get("password")

    with db_session_maker() as db:
        user = crud.authenticate_user(db, username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid username or password")

        access_token = crud.create_access_token(data={"sub": username})
        print(access_token)
        return {"access_token": access_token}


from robyn.authentication import AuthenticationHandler, BearerGetter, Identity


class BasicAuthHandler(AuthenticationHandler):
    def authenticate(self, request: Request):
        token = self.token_getter.get_token(request)

        try:
            payload = crud.decode_access_token(token)
            username = payload["sub"]
        except Exception:
            return

        with db_session_maker() as db:
            user = crud.get_user_by_username(db, username=username)

        return Identity(claims={"user": f"{ user }"})


app.configure_authentication(BasicAuthHandler(token_getter=BearerGetter()))


def is_superuser(user):
    return user.is_superuser


@app.get("/users/me", auth_required=True)
async def get_current_user(request):
    user = request.identity.claims["user"]
    return user


from gotham_app.frontend_router import frontend


app.include_router(frontend)


from robyn import WebSocket , WebSocketConnector
websocket = WebSocket(app, "/web_socket")

@websocket.on("message")
async def message(ws: WebSocketConnector, msg: str) -> str:
    global websocket_state
    websocket_id = ws.id
    resp = "Whaaat??"
    await ws.async_broadcast("This is a broadcast message")
    ws.sync_send_to(websocket_id, "This is a message to self")

    return resp


@websocket.on("close")
def close():
    return "GoodBye world, from ws"

@websocket.on("connect")
def connect():
    return "Hello world, from ws"


if __name__ == "__main__":
    app.start()
