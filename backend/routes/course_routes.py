# routes/course_routes.py

from quart import request, jsonify
from services.course_service import update_context
from services.video_service import update_course_videos  # Assuming this is in video_service

def init_course_routes(app):
    @app.route('/update-course-context', methods=['POST'])
    async def update_course_context_route():
        """Route to update course context and trigger video updates."""
        data = await request.get_json()
        course_id = data.get('courseid')
        course_context = data.get('course_context')

        # Log the request data for debugging
        print(f"Received data for course context update: {data}")

        # Validate required fields
        if not course_id or not course_context:
            return jsonify({'error': 'Missing course_id or course_context'}), 400

        # Attempt to update the course context
        context_result = await update_context(course_id, course_context)
        print(f"Context update result: {context_result}")

        # Handle context update response based on the status
        if context_result['status'] == 'Updated' or context_result['status'] == 'Inserted':
            # Trigger video updates if context update is successful
            videos_result = await update_course_videos(course_id)
            return jsonify({
                'context_update': context_result,
                'videos_update': videos_result
            }), 200
        elif context_result['status'] == 'No changes made':
            # If no changes were made, return a relevant message
            return jsonify({
                'status': 'No changes made',
                'message': context_result['message']
            }), 200
        else:
            # Handle unexpected cases
            return jsonify({
                'status': 'Error',
                'message': 'Unexpected result from update operation',
                'error': context_result
            }), 500