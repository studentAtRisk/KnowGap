from quart import Quart
from quart_cors import cors
from routes.base_routes import init_base_routes
from routes.video_routes import init_video_routes
from routes.support_routes import init_support_routes
from routes.course_routes import init_course_routes

app = Quart(__name__)
cors(app)

init_base_routes(app)
init_course_routes(app)
init_video_routes(app)
init_support_routes(app)