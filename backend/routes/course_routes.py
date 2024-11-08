from quart import request, jsonify
from services.course_service import update_context, update_student_quiz_data, get_incorrect_question_data, get_questions_by_course, update_quiz_reccs, update_quiz_questions_per_course
from services.video_service import update_course_videos
from utils.course_utils import get_quizzes  # Assuming get_quizzes is in course_utils
from quart_cors import cors

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
        if context_result['status'] == 'Success':
            # Trigger video updates if context update is successful
            videos_result = await update_course_videos(course_id)
            return jsonify({
                'context_update': context_result,
                'videos_update': videos_result
            }), 200
        elif context_result['status'] == 'No changes made':
            return jsonify({
                'status': 'No changes made',
                'message': context_result['message']
            }), 200
        else:
            return jsonify({
                'status': 'Error',
                'message': 'Unexpected result from update operation',
                'error': context_result
            }), 500

    @app.route('/update-course-db', methods=['POST'])
    async def update_course_db_route():
        """Route to update database with course quiz information and student data."""
        data = await request.get_json()
        course_id = data.get('courseid')
        access_token = data.get('access_token')
        link = data.get('link')

        print(f"Received data for course DB update: {data}")

        # Validate required fields
        if not course_id or not access_token or not link:
            return jsonify({'error': 'Missing course_id, access_token, or link'}), 400

        # Attempt to update the course database
        db_result = await update_student_quiz_data(course_id, access_token, link)
        print(f"Database update result: {db_result}")

        if db_result['status'] != 'Success':
            return jsonify({'status': 'Error', 'message': db_result['error']}), 500


        db_result = await update_quiz_questions_per_course(course_id, access_token, link)
        print(f"Database update result: {db_result}")
        
        if db_result == 1:
            return jsonify({'status': 'Success', 'message': db_result['message']}), 200
        else:
            return jsonify({'status': 'Error', 'message': db_result['error']}), 500

    @app.route('/get-course-quizzes', methods=['POST'])
    async def get_course_quizzes_route():
        """Route to fetch quizzes for a course."""
        data = await request.get_json()
        course_id = data.get('courseid')
        link = data.get('link')
        access_token = data.get('access_token')

        # Log the request data for debugging
        print(f"Received data for fetching course quizzes: {data}")

        if not course_id or not link or not access_token:
            return jsonify({'error': 'Missing course_id or link'}), 400

        try:
            quiz_list, quiz_names = await get_quizzes(course_id, access_token, link)
            return jsonify({'status': 'Success', 'quizzes': quiz_names}), 200
        except Exception as e:
            print(f"Error fetching quizzes: {e}")
            return jsonify({'status': 'Error', 'message': str(e)}), 500

    @app.route('/get-incorrect-questions', methods=['POST'])
    async def get_incorrect_questions_route():
        """Route to fetch incorrect question data for a specific quiz."""
        data = await request.get_json()
        course_id = data.get('courseid')
        current_quiz = data.get('quizid')
        link = data.get('link')

        print(f"Received data for fetching incorrect questions: {data}")

        if not course_id or not current_quiz or not link:
            return jsonify({'error': 'Missing course_id, quiz_id, or link'}), 400

        try:
            question_data = await get_incorrect_question_data(course_id, current_quiz, link)
            return jsonify({'status': 'Success', 'data': question_data}), 200
        except Exception as e:
            print(f"Error fetching incorrect questions: {e}")
            return jsonify({'status': 'Error', 'message': str(e)}), 500


    @app.route('/get-questions-by-course/<course_id>', methods=['POST'])
    async def get_questions_by_course_route(course_id):
        """Route to fetch questions for a specific course."""
        try:
            question_data = await get_questions_by_course(course_id)
            
            if "error" in question_data:
                return jsonify(question_data), 404

            return jsonify({"status": "Success", "data": question_data}), 200
        except Exception as e:
            print(f"Error fetching questions for course {course_id}: {e}")
            return jsonify({"status": "Error", "message": str(e)}), 500
