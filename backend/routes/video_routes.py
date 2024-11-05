# routes/video_routes.py

from quart import request, jsonify
from services.video_service import (
    get_assessment_videos, get_course_videos, update_course_videos,
    update_video_link, add_video, remove_video, update_videos_for_filter
)

def init_video_routes(app):
    @app.route('/get-assessment-videos', methods=['POST'])
    async def get_assessment_videos_route():
        data = await request.get_json()
        if not all(k in data for k in ("student_id", "course_id")):
            return jsonify({"error": "Missing student_id or course_id"}), 400

        assessment_videos = await get_assessment_videos(data['student_id'], data['course_id'])
        if assessment_videos:
            return jsonify({"assessment_videos": assessment_videos}), 200
        else:
            return jsonify({"message": "No assessment videos found"}), 404

    @app.route('/get-course-videos', methods=['GET'])
    async def get_course_videos_route():
        course_id = request.args.get('course_id')
        if not course_id:
            return jsonify({"error": "Missing course_id"}), 400
        
        course_videos = await get_course_videos(course_id)
        if course_videos:
            return jsonify({"course_videos": course_videos}), 200
        else:
            return jsonify({"message": "No videos found for this course"}), 404

    @app.route('/update-course-videos', methods=['POST'])
    async def update_course_videos_route():
        data = await request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'error': 'Missing Course ID'}), 400
        
        result = await update_course_videos(course_id)
        return jsonify(result), 200

    @app.route('/update-video-link', methods=['POST'])
    async def update_video_link_route():
        data = await request.get_json()
        if not all(k in data for k in ("quiz_id", "question_id", "old_link", "new_link")):
            return jsonify({"error": "Missing required parameters"}), 400

        result = await update_video_link(data['quiz_id'], data['question_id'], data['old_link'], data['new_link'])
        if result["success"]:
            return jsonify({"message": result["message"]}), 200
        else:
            return jsonify({"error": result["message"]}), 404

    @app.route('/add-video', methods=['POST'])
    async def add_video_route():
        data = await request.get_json()
        if not all(k in data for k in ("quiz_id", "question_id", "video_link")):
            return jsonify({"error": "Missing required parameters"}), 400

        result = await add_video(data['quiz_id'], data['question_id'], data['video_link'])
        if result["success"]:
            return jsonify({"message": result["message"]}), 200
        else:
            return jsonify({"error": result["message"]}), 409

    @app.route('/remove-video', methods=['POST'])
    async def remove_video_route():
        data = await request.get_json()
        if not all(k in data for k in ("quiz_id", "question_id", "video_link")):
            return jsonify({"error": "Missing required parameters"}), 400

        result = await remove_video(data['quiz_id'], data['question_id'], data['video_link'])
        if result["success"]:
            return jsonify({"message": result["message"]}), 200
        else:
            return jsonify({"error": result["message"]}), 404
        
    @app.route('/update-all-videos', methods=['POST'])
    async def update_all_videos_route():
        data = await request.get_json()
        result = await update_videos_for_filter()
        if result.get("message") == "success":
            return jsonify({"message": result["message"]}), 200
        else:
            return jsonify({"error": result["message"]}), 404