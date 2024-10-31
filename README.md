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
The following items are pending development or review:

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

Pending Items:
- [ ] Fix CSS scaling for student view
- [ ] Repurpose the "Notes" section
- [ ] Start using token-based endpoint instead of cookies
- [ ] Automate database updates
- [ ] Edit video URLs in UI
- [ ] Polish the UI with new elements
- [ ] Develop the "Third page" UI component
- [ ] Add a manual refresh button to the frontend for the database
- [ ] Clean up or repopulate the database before handover
- [ ] Runtime optimization on database/endpoints
- [ ] Endpoint debugging
- [ ] Code reformatting and cleanup
- [ ] Host the project on sponsor's server
- [ ] Optimize the decision to store 1 video per question vs. arrays
- [ ] Watchlist frontend and backend development
- [ ] Transition Flask-based code to Quart
- [ ] Finalize the documentation for project handover
