# routes/support_routes.py

from quart import request, jsonify
from services.support_service import get_videos_for_risk_level, get_random_video

def init_support_routes(app):
    @app.route('/get-support-video', methods=['POST'])
    async def get_support_video():
        data = await request.get_json()
        risk_level = data.get('risk')

        if not risk_level or risk_level not in ["low", "medium", "high"]:
            return jsonify({"error": "Invalid risk level"}), 400
        
        # Fetch videos for the specified risk level
        videos = await get_videos_for_risk_level(risk_level)
        random_video = get_random_video(videos)

        if random_video:
            return jsonify(random_video), 200
        else:
            return jsonify({"message": "No videos found for this risk level"}), 404
