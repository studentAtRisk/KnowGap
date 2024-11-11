from pymongo import MongoClient

# MongoDB connection
client = MongoClient('mongodb+srv://Jason:uJ3gkMl0rmG75c55@studentsatrisk.ptqdmcu.mongodb.net/')
db = client['NoGap']
quizzes_collection = db['Quiz Questions']

def update_video_link(quiz_id, old_link, new_video):
    """
    Function to update a specific video in the video_data array.

    :param quiz_id: The quiz ID associated with the document.
    :param old_link: The link of the video to be replaced.
    :param new_video: A dictionary with the new video details (link, title, thumbnail, etc.).
    """
    # Step 1: Pull (remove) the video with the old link
    quizzes_collection.update_one(
            {"quizid": quiz_id},  # Find the document by quiz ID
            {"$pull": {"video_data": {"link": old_link}}}  # Remove the old video based on the link
            )

# Step 2: Push (add) the new video data
    quizzes_collection.update_one(
            {"quizid": quiz_id},  # Find the document by quiz ID
            {"$push": {"video_data": new_video}}  # Add the new video data
            )

    print(f"Video with link {old_link} updated to {new_video['link']}")

# Example usage:
quiz_id = 2372742  # The quiz ID to target
old_link = "https://www.youtube.com/watch?v=bBWha3RAo6E"  # The old video link to remove
new_video = {
        "link": "https://www.youtube.com/watch?v=newLink123",  # The new video link to add
        "title": "New Aerodynamics Simulation Video",
        "channel": "AeroTech",
        "thumbnail": "https://i.ytimg.com/vi/newLink123/hq720.jpg"
        }

# Call the function to update the video link
update_video_link(quiz_id, old_link, new_video)

