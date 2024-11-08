from quart import jsonify, request, Response

def init_base_routes(app):
    @app.route('/')
    async def hello_world():
        return jsonify('Welcome to the KnowGap Backend API!')

    @app.before_request
    async def handle_options_request():
        if request.method == 'OPTIONS':
            response = Response()
            response.headers.add('Access-Control-Allow-Origin', 'https://canvas.instructure.com')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            return response
