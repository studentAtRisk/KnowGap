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
