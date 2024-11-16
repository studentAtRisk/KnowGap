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
- [x] Third Page: Mental Health Support Videos by Risk Level
- [x] Implemented unit testing for core features
- [x] Two-week sprint-based development cycle
- [x] Automated "Refresh DB" feature for real-time Canvas updates

### Pending Items / Future Features

- [ ] **Enhancing User Experience**
  - Provide detailed breakdowns of how the risk score is calculated.
  - Clarify what each score means in the context of passing/failing a class (to users, both students and instructors)
  - Allow users to give feedback on academic and mental health videos.
  - Use feedback to improve recommendations and ensure content relevance.
  - Enable students to save academic or mental health videos to a personal watchlist for later viewing, or remove ones they have already watched or no longer need.
  - Allow professors to curate playlists of recommended content for their classes.
  - Enable students to opt in to test the application further with real-life instructor data and grow user base.
  - Collect feedback to refine features and ensure practical utility.
  - Provide instructors with a detailed dashboard summarizing trends across multiple courses and highlighting areas of concern.

- [ ] **Frontend Enhancements**
  - Use cookies to store support content for determined period of time (i.e. 48-72 hours)
  - Implement OAuth2 for secure and seamless authentication.
  - Transition from cookies to a fully fleshed-out token database for better security and scalability. (Endpoint exists, need to test and call in frontend)
  - Fix CSS scaling for student view
  - Instead of having all course questions, have an additional drop down for course quizzes, and pull up questions to add videos based on selected course assessment
  - Start using token-based endpoint instead of cookies
  - Add a manual refresh button to the frontend for the database
  - Polish the UI with new elements (including a watchlist feature)
  - Watchlist frontend and backend development

- [ ] **Backend Improvements**
  - Automate deletion of old assessment data to handle larger datasets efficiently.
  - Ingest and structure data to accommodate GraphQL compatibility.
  - Explore AWS or other cloud-based deployments to scale the platform for institutional or global use.
  - Ingest unique question formats and structures rather than processing multiple instances of similar questions with different values.
  - Edit video URLs in UI
  - Runtime optimization on database/endpoints
  - Endpoint debugging
  - Code reformatting and cleanup
  - Optimize the decision to store 1 video per question vs. arrays

- [ ] **Testing and Deployment**
  - Implement a robust unit testing framework to ensure reliability and maintainability as the application evolves.
  - Clean up or repopulate the database before handover
  - Host the project on sponsor's server
  - Finalize the documentation for project handover

- [ ] **Integration and Scalability**
  - Add Single Sign-On (SSO) integration with UCF systems
  - Multi-LMS compatibility for Blackboard, Moodle, etc.
  - Cross-platform data sync with tools like Google Classroom or Khan Academy
  - Open API for third-party tool integration

- [ ] **Security and Compliance**
  - Transition to OAuth2 and a fully fleshed-out token database
  - Ensure FERPA and GDPR compliance tools are implemented
  - Role-based access control for granular data permissions
  - End-to-end encryption for data security

- [ ] **Gamification and Engagement**
  - Use badges or leaderboards to encourage student engagement with recommended videos or mental health resources.
  - Develop guided tutorials for students to learn how to use the platform effectively.
  - Facilitate anonymous peer mentoring for students at similar risk levels

---
This README reflects the latest achieved milestones and upcoming features, providing a clear roadmap for both completed and planned work. Let me know if you need any further edits or additional features to be added.
