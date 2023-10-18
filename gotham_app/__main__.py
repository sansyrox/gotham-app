from robyn import Robyn, jsonify
from gotham_app.models import db_session_maker
from gotham_app import crud
from robyn.robyn import Request


app = Robyn(__file__)


@app.get("/crimes")
async def get_crimes(request):
    ...


if __name__ == "__main__":
    app.start()
