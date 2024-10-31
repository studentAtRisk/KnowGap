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

        # Log incoming request data for debugging
        print(f"Received data for course context update: {data}")

        # Input validation with debug logging
        if not course_id:
            print("Error: Missing course_id")
            return jsonify({'error': 'Missing course_id'}), 400
        if not course_context:
            print("Error: Missing course_context")
            return jsonify({'error': 'Missing course_context'}), 400

        # Update the course context and capture debug information
        try:
            context_result = await update_context(course_id, course_context)
            print(f"Context update result: {context_result}")
        except Exception as e:
            print(f"Exception during context update: {e}")
            return jsonify({
                'status': 'Error',
                'message': 'Failed to update course context',
                'error': str(e)
            }), 500

        # Check if context update was successful
        if context_result.get('success'):
            # Attempt to trigger video updates if context update succeeded
            try:
                videos_result = await update_course_videos(course_id)
                print(f"Videos update result: {videos_result}")
            except Exception as e:
                print(f"Exception during videos update: {e}")
                return jsonify({
                    'context_update': {
                        'status': 'Success',
                        'modified_count': context_result['modified_count'],
                        'upserted_id': context_result['upserted_id']
                    },
                    'videos_update': {
                        'status': 'Error',
                        'message': 'Failed to update videos for course',
                        'error': str(e)
                    }
                }), 500

            # Return success response if both updates succeeded
            return jsonify({
                'context_update': {
                    'status': 'Success',
                    'modified_count': context_result['modified_count'],
                    'upserted_id': context_result['upserted_id']
                },
                'videos_update': videos_result
            }), 200

        else:
            # Log error details for failed context update
            print(f"Context update failed with error: {context_result.get('error')}")
            # Handle error response if context update failed
            return jsonify({
                'status': 'Error',
                'message': 'Failed to update course context',
                'error': context_result.get('error')
            }), 500