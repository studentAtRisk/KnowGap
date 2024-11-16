# KnowGap - Course Video Recommendations & Student Risk Prediction

## Overview

**KnowGap** is an intelligent platform designed to enhance student learning and course management. It combines student performance prediction with personalized video recommendations to improve understanding of incorrectly answered quiz questions. The platform integrates with learning management systems like Canvas to monitor student progress and provide instructors with critical insights, while helping students close knowledge gaps through targeted video recommendations.

## Features

1. **Student Risk Prediction**
   - Identifies students at risk of underperforming or failing based on quiz performance and other course metrics.
   - Offers insights to instructors, enabling timely intervention to help students succeed.

2. **Curated Video Recommendations**
   - Automatically generates personalized video recommendations for quiz questions that students answer incorrectly.
   - Leverages predefined or dynamically generated core topics for each question.
   - Stores new video data in the system, ensuring future reuse without redundant lookups.

3. **Integration with Canvas**
   - Uses course and quiz data from Canvas to monitor student performance.
   - Tracks quiz results and triggers video recommendations based on incorrect answers.

4. **Caching and Storing Results**
   - Caches dynamically generated core topics and videos, reducing the need for repeated API calls or queries.

Current Student View          |  Current Instructor View
:-------------------------:|:-------------------------:
![](https://i.ibb.co/592pv8d/image-2024-10-26-204812751.png)| ![](https://i.ibb.co/hRjdT0R/demo.png)

## TODOs & Milestones

### Achieved Milestones
- [x] Integration with Canvas for Quiz and Course Data
- [x] Student Risk Prediction Algorithm
- [x] Curated Video Recommendation System
- [x] Storing Video Data for Reuse
- [x] End-to-End Flow for Fetching and Displaying Videos
- [x] Automated Database Updates
- [x] Token-Based Authentication & Encryption
- [x] Endpoint to Store and Retrieve Videos by Course
- [x] Polished UI for Video Recommendations
- [x] Core Topic Generation for Recommending Videos
- [x] Regular sponsor meetings for dual perspective feedback (student and instructor)
- [x] Implemented unit testing for core features
- [x] Two-week sprint-based development cycle
- [x] Automated "Refresh DB" feature for real-time Canvas updates

### Pending Items / Future Features

- [ ] **Frontend Enhancements**
  - Fix CSS scaling for student view
  - Repurpose the "Notes" section
  - Start using token-based endpoint instead of cookies
  - Add a manual refresh button to the frontend for the database
  - Polish the UI with new elements (including a watchlist feature)
  - Watchlist frontend and backend development
  - Transition Flask-based code to Quart

- [ ] **Backend Improvements**
  - Automate deletion of old assessment data to handle larger datasets
  - Edit video URLs in UI
  - Runtime optimization on database/endpoints
  - Endpoint debugging
  - Code reformatting and cleanup
  - Optimize the decision to store 1 video per question vs. arrays
  - Ingest question formats rather than multiple instances of similar questions
  - Explore AWS/Cloud deployments for scalability

- [ ] **Testing and Deployment**
  - Clean up or repopulate the database before handover
  - Host the project on sponsor's server
  - Finalize the documentation for project handover

- [ ] **Integration and Scalability**
  - Implement OAuth2 for secure authentication
  - Add Single Sign-On (SSO) integration with UCF systems
  - Multi-LMS compatibility for Blackboard, Moodle, etc.
  - Cross-platform data sync with tools like Google Classroom or Khan Academy
  - Open API for third-party tool integration

- [ ] **User Experience and Analytics**
  - Provide detailed insights on risk level calculations
  - Allow users to give feedback on academic and mental health videos
  - Add detailed dashboards summarizing trends across courses
  - Predictive analytics for course outcomes

- [ ] **AI and Automation**
  - Integrate AI chatbot for 24/7 academic and mental health support
  - Implement automated intervention suggestions for instructors
  - Utilize NLP for feedback analysis from students and instructors

- [ ] **Security and Compliance**
  - Transition to OAuth2 and a fully fleshed-out token database
  - Ensure FERPA and GDPR compliance tools are implemented
  - Role-based access control for granular data permissions
  - End-to-end encryption for data security

- [ ] **Gamification and Engagement**
  - Gamified feedback mechanisms (badges, leaderboards)
  - Interactive tutorials for platform usage
  - Peer support features for students at similar risk levels

---
This README reflects the latest achieved milestones and upcoming features, providing a clear roadmap for both completed and planned work. Let me know if you need any further edits or additional features to be added.
