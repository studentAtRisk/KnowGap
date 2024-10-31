# Services Directory

## Overview

The `services` directory is responsible for handling the core business logic and database interactions of the KnowGap Backend API. Each service file is organized around specific features or resources, separating core logic from routing. This modular approach enables easier maintenance, testing, and scalability.

## Service Files

### 1. `video_service.py`
- **Purpose**: Manages all operations related to videos, such as generating recommendations and updating video metadata.
- **Key Functions**:
  - **`get_assessment_videos(student_id, course_id)`**: Retrieves incorrect questions and associated video links based on assessments for a specific student and course.
  - **`get_course_videos(course_id)`**: Fetches video data for a specific course.
  - **`update_videos_for_filter(filter_criteria)`**: Updates video recommendations for questions that match a given filter.
  - **`update_course_videos(course_id)`**: Updates all video recommendations for questions within a specified course.

### 2. `course_service.py`
- **Purpose**: Handles operations related to course data, including updating the course context and managing specific course information.
- **Key Functions**:
  - **`update_context(course_id, course_context)`**: Updates or inserts context information for a specific course, aiding in more targeted video recommendations.
  - **Other Course Management Functions** (if applicable): Includes functions for adding, updating, and retrieving course data if extended in the future.

### 3. `user_service.py`
- **Purpose**: Manages user token operations, including token encryption, storage, and retrieval. This service ensures that user tokens are securely handled and stored.
- **Key Functions**:
  - **`add_or_update_user_token(user_id, access_token, course_ids, link)`**: Encrypts and stores or updates the user token, linking it to specified courses.
  - **`get_user_token(user_id)`**: Retrieves and decrypts the user token for a specific user, allowing for secure access to course data and recommendations.

## Async Flow and Database Interactions

All service functions utilize asynchronous programming with the `Motor` library for MongoDB interactions, which ensures non-blocking data access and efficient performance when working with the database.

- **MongoDB Collections**: Each service file interacts with specific MongoDB collections, such as `Students`, `Quiz Questions`, `Tokens`, and `Course Contexts`, based on its functionality.
- **Data Validation and Error Handling**: Each function performs data validation and error handling to ensure reliable database interactions and minimize the risk of runtime issues.

## How Services are Used in Routes

The service functions are called by route handlers in the `routes` directory. This approach:
1. Keeps routes clean and focused on request-response handling.
2. Allows services to manage complex business logic and database interactions.

Example usage in a route:
```python
# Example from video_routes.py
from services.video_service import get_course_videos

@app.route('/get-course-videos', methods=['GET'])
async def get_course_videos_route():
    course_id = request.args.get('course_id')
    course_videos = await get_course_videos(course_id)
    return jsonify(course_videos), 200
```

## Adding New Services

To add a new service:

1. **Create a new file** in the `services` directory with a descriptive name (e.g., `new_feature_service.py`).
2. **Define the necessary business logic and database functions** within this file.
3. **Import and call these functions** within the appropriate route file to make them accessible via the API.

## Benefits of Service Layer

- **Separation of Concerns**: By keeping business logic separate from route handlers, the codebase remains modular and easier to manage.
- **Reusability**: Service functions can be reused across different routes or even other services as needed.
- **Testability**: Each service function can be individually tested, making it easier to maintain and scale the application.

