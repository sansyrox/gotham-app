from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import crud
from .exceptions import HTTPException
from .models import Crime, User

from robyn import Robyn, jsonify
import json




DATABASE_URL = "sqlite:///./gotham_crime_data.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = Robyn(__file__)


from robyn.robyn import Request, Response
from sqlalchemy.orm import Session


@app.post("/crimes")
async def add_crime(request):
    with SessionLocal() as db:
        crime = json.loads(request.body)
        insertion = crud.create_crime(db, crime)

    if insertion is None:
        raise HTTPException(status_code=400, detail="Invalid crime data")

    return {
        "body": "Crime added successfully",
        "status_code": 200,
    }

@app.get("/crimes")
async def get_crimes(request):
    with SessionLocal() as db:
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
    with SessionLocal() as db:
        crime = crud.get_crime(db, crime_id=crime_id)

    if crime is None:
        raise HTTPException(status_code=404, detail="Crime not found")

    return crime

@app.put("/crimes/:crime_id")
async def update_crime(request):
    crime = json.loads(request.body)
    crime_id = int(request.path_params.get("crime_id"))
    with SessionLocal() as db:
        updated_crime = crud.update_crime(db, crime_id=crime_id, crime=crime)
    if updated_crime is None:
        raise HTTPException(status_code=404, detail="Crime not found")
    return updated_crime

@app.delete("/crimes/{crime_id}")
async def delete_crime(request):
    crime_id = int(request.path_params.get("crime_id"))
    with SessionLocal() as db:
        success = crud.delete_crime(db, crime_id=crime_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crime not found")
    return {"message": "Crime deleted successfully"}


@app.post("/users/register")
async def register_user(request):
    print(request.body)
    user = json.loads(request.body)
    with SessionLocal() as db:
        created_user = crud.create_user(db, user)
    return {
        "body": str( created_user ),
        "status_code": 200,
    }


@app.post("/users/login")
async def login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    with SessionLocal() as db:
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

        with SessionLocal() as db:
            user = crud.get_user_by_username(db, username=username)

        return Identity(claims={"user": f"{ user }"})


app.configure_authentication(BasicAuthHandler(token_getter=BearerGetter()))

def is_superuser(user):
    return user.is_superuser

@app.get("/users/me", auth_required=True)
async def get_current_user(request):
    user = request.identity.claims["user"]
    return user


from robyn.templating import JinjaTemplate
from robyn import SubRouter
import os
import pathlib


current_file_path = pathlib.Path(__file__).parent.resolve()
jinja_template = JinjaTemplate(os.path.join(current_file_path, "templates"))


frontend = SubRouter(__name__, prefix="/frontend")

@frontend.get("/")
async def get_frontend(request):
    context = {"framework": "Robyn", "templating_engine": "Jinja2"}
    return jinja_template.render_template("index.html", **context)

app.include_router(frontend)



if __name__ == "__main__":
    app.start()

