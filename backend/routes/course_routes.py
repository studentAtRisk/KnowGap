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

        if not course_id or not course_context:
            return jsonify({'error': 'Missing course_id or course_context'}), 400

        # Update the course context
        context_result = await update_context(course_id, course_context)

        # Check if context update was successful
        if context_result.get('success'):
            # Trigger video updates if context update is successful
            videos_result = await update_course_videos(course_id)
            return jsonify({
                'context_update': {
                    'status': 'Success',
                    'modified_count': context_result['modified_count'],
                    'upserted_id': context_result['upserted_id']
                },
                'videos_update': videos_result
            }), 200
        else:
            # Handle error response if context update failed
            return jsonify({
                'status': 'Error',
                'message': 'Failed to update course context',
                'error': context_result.get('error')
            }), 500