# Routes Directory

## Overview

The `routes` directory contains all route definitions for the KnowGap Backend API. Each route file is organized by functionality to handle different aspects of the application, such as managing videos, courses, and user tokens. Each route file initializes its respective endpoints through a dedicated function (`init_<route_name>_routes`) that registers routes with the main application instance in `app.py`.

## Route Files

### 1. `base_routes.py`
- **Purpose**: Contains foundational routes, including the root (`/`) endpoint for a welcome or health check message.
- **Main Endpoint**:
  - `GET /` - Returns a welcome message to indicate that the API is active.

### 2. `video_routes.py`
- **Purpose**: Manages all endpoints related to video operations, such as retrieving and updating video recommendations.
- **Key Endpoints**:
  - `POST /update-all-videos` - Triggers an update of videos for all questions in the database.
  - `POST /update-course-videos` - Updates videos specifically for a single course.
  - `GET /get-course-videos` - Retrieves video recommendations for a specified course.
  - `POST /get-video-rec` - Fetches video recommendations based on a student's course performance.

### 3. `course_routes.py`
- **Purpose**: Handles endpoints for course-related operations, such as updating the course context and managing course data.
- **Key Endpoints**:
  - `POST /update-course-context` - Updates the context for a specific course and triggers video updates accordingly.
  - `GET /course/<course_id>` - Retrieves details of a specific course by `course_id`.
  - `POST /course` - Adds a new course to the database.
  - `PUT /course/<course_id>` - Updates details of an existing course.
  - `DELETE /course/<course_id>` - Deletes a specified course.

### 4. `user_token_management.py`
- **Purpose**: Handles operations related to user tokens, including adding, updating, and retrieving tokens for secure access.
- **Key Endpoints**:
  - `POST /add-token` - Adds or updates a user token for authentication.
  - `GET /get-user` - Retrieves token details for a specific user by `user_id`.

## Route Initialization

Each route file contains an initialization function that registers its routes with the main `app` instance in `app.py`. This approach keeps route definitions modular, making it easy to maintain and expand the API.

### Example Initialization in `app.py`

```python
from quart import Quart
from quart_cors import cors
from routes.base_routes import init_base_routes
from routes.video_routes import init_video_routes
from routes.course_routes import init_course_routes
from routes.user_token_management import init_user_token_management_routes

app = Quart(__name__)
cors(app)

# Registering Routes
init_base_routes(app)
init_video_routes(app)
init_course_routes(app)
init_user_token_management_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
```
## Route Conventions

### Error Handling
Each route validates request data and returns a JSON error response if required fields are missing.

### Response Structure
Standardized JSON responses with `status` and `message` fields are used to maintain consistency across endpoints.

## Extending Routes

To add new routes, create a new file in the `routes` directory and follow these steps:

1. **Define the required endpoints and their corresponding handler functions.**
2. **Create an initialization function (`init_<your_route_name>_routes`) to register the routes.**
3. **Import and call this initialization function in `app.py` to activate the new routes.**
