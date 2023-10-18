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
