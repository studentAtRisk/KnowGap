# routes/user_token_management.py

from quart import request, jsonify
from services.user_service import add_user, get_user

def init_user_routes(app):
    
    @app.route('/add-token', methods=['POST'])
    async def add_token_route():
        data = await request.get_json()
        user_id = data.get('user_id')
        access_token = data.get('access_token')
        course_ids = data.get('course_ids')
        link = data.get('link')

        if not user_id or not access_token or not course_ids or not link:
            return jsonify({'error': 'Missing required fields'}), 400

        # Await the asynchronous service function
        updated_user = await add_user(user_id, access_token, course_ids, link)
        if updated_user:
            return jsonify({'status': 'Complete'}), 200
        else:
            return jsonify({'status': 'Error', 'message': 'Failed to update user'}), 500

    @app.route('/get-user', methods=['POST'])
    async def get_user_route():
        data = await request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'Missing User ID'}), 400

        # Await the asynchronous service function
        user_data = await get_user(user_id)
        if user_data:
            return jsonify({'status': 'Success', 'user_details': user_data}), 200
        else:
            return jsonify({'status': 'Error', 'message': 'User not found'}), 404
