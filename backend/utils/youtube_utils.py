# utils/youtube_utils.py
from youtubesearchpython import VideosSearch

async def fetch_video_for_topic(topic):
    """
    Fetch a single video for a given topic from YouTube.
    
    Parameters:
    - topic (str): The topic to search for.

    Returns:
    - dict: A dictionary containing video metadata (title, link, channel, thumbnail),
            or an empty dictionary if no video is found.
    """
    try:
        # Search for a single video related to the topic
        search = VideosSearch(topic, limit=1)
        search_results = search.result().get('result', [])

        if search_results:
            # Retrieve the first video in the search results
            video = search_results[0]
            video_data = {
                'title': video['title'],
                'link': video['link'],
                'channel': video['channel']['name'],
                'thumbnail': video['thumbnails'][0]['url']
            }
            return video_data

        # Return an empty dictionary if no results are found
        return {}

    except Exception as e:
        print(f"Error fetching videos for topic '{topic}': {e}")
        return {}
