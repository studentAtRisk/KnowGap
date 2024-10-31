from quart import jsonify

def init_base_routes(app):
    @app.route('/')
    async def hello_world():
        return jsonify('Welcome to the KnowGap Backend API!')
