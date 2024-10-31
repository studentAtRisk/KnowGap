from quart import Quart
from quart_cors import cors
from routes.base_routes import init_base_routes
from routes.video_routes import init_video_routes
from routes.support_routes import init_support_routes
from routes.course_routes import init_course_routes

app = Quart(__name__)
cors(app, 
     allow_origin="canvas.instructure.com",
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
     allow_credentials=True)

init_base_routes(app)
init_course_routes(app)
init_video_routes(app)
init_support_routes(app)