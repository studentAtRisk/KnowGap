import React, { useState, useEffect } from 'react';
import './Studentview.css';
import youtube from './imgs/youtube.png';

const calculateSlope = (assignments) => {
  const lastFiveAssignments = assignments
    .filter(
      (assignment) => assignment.score !== 'N/A' && assignment.score !== 'Error'
    )
    .slice(-5);

  if (lastFiveAssignments.length < 2) {
    return 0;
  }

  const x = Array.from({ length: lastFiveAssignments.length }, (_, i) => i + 1);
  const y = lastFiveAssignments.map(
    (assignment) => (Number(assignment.score) / assignment.pointsPossible) * 100
  );

  const n = x.length;
  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.reduce((a, b, i) => a + b * y[i], 0);
  const sumXSquared = x.reduce((a, b) => a + b * b, 0);

  const slope = (n * sumXY - sumX * sumY) / (n * sumXSquared - sumX * sumX);
  return slope;
};

const normalizeGts = (slope, minSlope = -10, maxSlope = 10) => {
  return ((slope - minSlope) / (maxSlope - minSlope)) * 100;
};

const calculateRiskIndex = (rps, cgs, gts, currentScore) => {
  if (currentScore <= 69) {
    return { riskLevel: 'High Risk' };
  }

  const weights = {
    rps: 0.3,
    cgs: 0.55,
    gts: 0.15,
  };

  const riskIndex = weights.rps * rps + weights.cgs * cgs + weights.gts * gts;

  let riskLevel;
  if (riskIndex > 70) {
    riskLevel = 'Low Risk';
  } else if (riskIndex > 40 && riskIndex <= 70) {
    riskLevel = 'Medium Risk';
  } else {
    riskLevel = 'High Risk';
  }

  return { riskLevel };
};

const normalizeRiskLevel = (riskLevel) => {
  const level = riskLevel.replace(' Risk', '').toLowerCase();
  return level; // Returns "low", "medium", or "high"
};

const StudentView = () => {
  const [activeTab, setActiveTab] = useState('assignments');
  const [assignments, setAssignments] = useState([]);
  const [recommendedVideos, setRecommendedVideos] = useState([]);
  const [supportVideo, setSupportVideo] = useState(null);
  const [courseId, setCourseId] = useState('');
  const [apiToken, setApiToken] = useState('');
  const [classGrade, setClassGrade] = useState('N/A');
  const [studentName, setStudentName] = useState('');
  const [tokenStatus, setTokenStatus] = useState('');

  const imgs = { youtube };

  const getCanvasBaseUrl = () => {
    const url = window.location.href;
    const match = url.match(/(https?:\/\/[^\/]+)/);
    return match ? match[1] : null;
  };

  const fetchCurrentCourseId = () => {
    const url = window.location.href;
    const match = url.match(/\/courses\/(\d+)/);
    if (match && match[1]) {
      return match[1];
    }
    return null;
  };

  const fetchSupportVideos = async (riskLevel) => {
    try {
      const response = await fetch(
        'https://slimy-betsy-student-risk-ucf-cdl-test-1cfbb0a5.koyeb.app/get-support-video',
        {
          method: 'POST',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            risk: riskLevel,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching support video:', error);
      return null;
    }
  };

  const fetchAssignments = async (courseId) => {
    const baseUrl = getCanvasBaseUrl();
    if (!baseUrl) {
      console.error('Unable to determine Canvas base URL');
      return;
    }

    const storedToken = localStorage.getItem('apiToken');
    if (!storedToken) {
      console.error('No API token found');
      return;
    }

    const myHeaders = new Headers();
    myHeaders.append('Authorization', `Bearer ${storedToken}`);

    const requestOptions = {
      method: 'GET',
      headers: myHeaders,
      redirect: 'follow',
    };

    try {
      const assignmentsResponse = await fetch(
        `${baseUrl}/api/v1/courses/${courseId}/assignments`,
        requestOptions
      );
      const assignmentsResult = await assignmentsResponse.json();

      const formattedAssignments = await Promise.all(
        assignmentsResult.map(async (assignment) => {
          try {
            const submissionResponse = await fetch(
              `${baseUrl}/api/v1/courses/${courseId}/assignments/${assignment.id}/submissions/self`,
              requestOptions
            );
            if (!submissionResponse.ok) {
              throw new Error(
                `HTTP error! status: ${submissionResponse.status}`
              );
            }
            const submissionResult = await submissionResponse.json();

            return {
              name: assignment.name,
              score: submissionResult.score || 'N/A',
              pointsPossible: assignment.points_possible,
            };
          } catch (error) {
            console.error(
              `Error fetching submission for assignment ${assignment.id}:`,
              error
            );
            return {
              name: assignment.name,
              score: 'Error',
              pointsPossible: assignment.points_possible,
            };
          }
        })
      );

      setAssignments(formattedAssignments);
    } catch (error) {
      console.error('Error fetching assignments:', error);
    }
  };

  const fetchEnrollment = async (courseId) => {
    const baseUrl = getCanvasBaseUrl();
    const storedToken = localStorage.getItem('apiToken');

    if (!baseUrl || !storedToken) {
      console.error('Missing base URL or API token');
      return null;
    }

    const myHeaders = new Headers();
    myHeaders.append('Authorization', `Bearer ${storedToken}`);

    const requestOptions = {
      method: 'GET',
      headers: myHeaders,
      redirect: 'follow',
    };

    try {
      const response = await fetch(
        `${baseUrl}/api/v1/courses/${courseId}/enrollments?user_id=self`,
        requestOptions
      );
      const enrollmentData = await response.json();
      return enrollmentData[0].grades.current_score;
    } catch (error) {
      console.error('Error fetching enrollment data:', error);
      return null;
    }
  };

  const fetchUserProfile = async () => {
    const baseUrl = getCanvasBaseUrl();
    const storedToken = localStorage.getItem('apiToken');

    if (!baseUrl || !storedToken) {
      console.error('Missing base URL or API token');
      return;
    }

    const myHeaders = new Headers();
    myHeaders.append('Authorization', `Bearer ${storedToken}`);

    const requestOptions = {
      method: 'GET',
      headers: myHeaders,
      redirect: 'follow',
    };

    try {
      const response = await fetch(
        `${baseUrl}/api/v1/users/self`,
        requestOptions
      );
      const profileData = await response.json();
      setStudentName(profileData.name);
      return profileData.id;
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const fetchVideoRecommendations = async (userId, courseId) => {
    const baseUrl =
      'https://slimy-betsy-student-risk-ucf-cdl-test-1cfbb0a5.koyeb.app';

    try {
      const response = await fetch(`${baseUrl}/get-video-rec`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          userid: userId.toString(),
          courseid: courseId.toString(),
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching video recommendations:', error);
      return null;
    }
  };

  const formatVideoRecommendations = (data) => {
    const formattedVideos = [];
    if (data && typeof data === 'object') {
      for (const quizName in data) {
        const quizData = data[quizName] || {};
        Object.values(quizData).forEach((topicData) => {
          if (topicData && Array.isArray(topicData.videos)) {
            formattedVideos.push(
              ...topicData.videos.map((video) => ({
                ...video,
                reason: `Learn about ${topicData.topic || 'this topic'}`,
                id: video?.link?.split('v=')[1] || '',
                url: video?.link || '',
                viewCount: 'N/A',
                duration: 'N/A',
              }))
            );
          }
        });
      }
    }
    return formattedVideos;
  };

  useEffect(() => {
    const updateCourseAndData = async () => {
      const currentCourseId = fetchCurrentCourseId();
      if (currentCourseId && currentCourseId !== courseId) {
        setCourseId(currentCourseId);
        fetchAssignments(currentCourseId);
        const overallGrade = await fetchEnrollment(currentCourseId);
        setClassGrade(overallGrade);
        const userId = await fetchUserProfile();

        const stringUserId = userId.toString();
        const stringCurrentCourseId = currentCourseId.toString();

        const videoRecommendations = await fetchVideoRecommendations(
          stringUserId,
          stringCurrentCourseId
        );
        if (videoRecommendations) {
          const formattedVideos =
            formatVideoRecommendations(videoRecommendations);
          setRecommendedVideos(formattedVideos);
        }

        // Fetch support video based on risk level
        const { riskLevel } = calculateRisk();
        const supportVideoData = await fetchSupportVideos(
          normalizeRiskLevel(riskLevel)
        );
        setSupportVideo(supportVideoData);
      }
    };

    updateCourseAndData();
    const intervalId = setInterval(updateCourseAndData, 5000);
    return () => clearInterval(intervalId);
  }, [courseId]);

  const calculateRisk = () => {
    const slope = calculateSlope(assignments);
    const gts = normalizeGts(slope);

    const currentGrade = parseFloat(classGrade);
    if (isNaN(currentGrade)) {
      return { riskLevel: 'Medium Risk' };
    }

    const rps = currentGrade;
    const cgs = currentGrade;

    return calculateRiskIndex(rps, cgs, gts, currentGrade);
  };

  const getRiskLevelClass = (riskLevel) => {
    switch (riskLevel) {
      case 'High Risk':
        return 'risk-high';
      case 'Medium Risk':
        return 'risk-medium';
      case 'Low Risk':
        return 'risk-low';
      default:
        return '';
    }
  };

  const removeToken = () => {
    localStorage.removeItem('apiToken');
    setApiToken('');
    setAssignments([]);
    setClassGrade('N/A');
    setSupportVideo(null);
    setTokenStatus('');
  };

  const fetchTeacherCourses = async () => {
    const baseUrl = getCanvasBaseUrl();
    const storedToken = localStorage.getItem('apiToken');

    if (!baseUrl || !storedToken) {
      console.error('Missing base URL or API token');
      return [];
    }

    const myHeaders = new Headers();
    myHeaders.append('Authorization', `Bearer ${storedToken}`);

    const requestOptions = {
      method: 'GET',
      headers: myHeaders,
      redirect: 'follow',
    };

    try {
      const response = await fetch(
        `${baseUrl}/api/v1/courses?enrollment_type=teacher&per_page=100`,
        requestOptions
      );
      const coursesData = await response.json();
      return coursesData.map((course) => course.id);
    } catch (error) {
      console.error('Error fetching teacher courses:', error);
      return [];
    }
  };

  const sendTokenToServer = async (token) => {
    setTokenStatus('Sending token...');
    const baseUrl =
      'https://slimy-betsy-student-risk-ucf-cdl-test-1cfbb0a5.koyeb.app';
    const userId = await fetchUserProfile();
    const teacherCourses = await fetchTeacherCourses();

    const data = {
      userid: userId.toString(),
      access_token: token.toString(),
      courseids: teacherCourses.length > 0 ? teacherCourses : [],
      link: getCanvasBaseUrl(),
    };

    try {
      const response = await fetch(`${baseUrl}/add-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setTokenStatus('Token set successfully!');
      localStorage.setItem('apiToken', token);
    } catch (error) {
      console.error('Error sending token:', error);
      setTokenStatus('Error setting token. Please try again.');
    }
  };

  const testSendToken = async () => {
    const storedToken = localStorage.getItem('apiToken');
    if (storedToken) {
      await sendTokenToServer(storedToken);
    } else {
      setTokenStatus('No token stored. Please save a token first.');
    }
  };

  const { riskLevel } = calculateRisk();

  return (
    <body className="student-view">
      <div className="container">
        {localStorage.getItem('apiToken') ? (
          <div className="api-token-input">
            <p>API Token is set</p>
            <button onClick={removeToken}>Remove Token</button>
            <button onClick={testSendToken}>Refresh Status</button>
          </div>
        ) : (
          <div className="api-token-input">
            <input
              type="password"
              placeholder="Enter your API token"
              value={apiToken}
              onChange={(e) => setApiToken(e.target.value)}
            />
            <button onClick={() => sendTokenToServer(apiToken)}>
              Save Token
            </button>
            <button onClick={testSendToken}>Test Send Token</button>
            {tokenStatus && <p>{tokenStatus}</p>}
          </div>
        )}
        <div className="performance-overview fade-in">
          <h2 className="overview-title">Your Performance Overview</h2>
          <h3>{studentName}</h3>
          <div className="overview-grid">
            <div>
              <h3 className="risk-level">Risk Level</h3>
              <p className={`risk-value ${getRiskLevelClass(riskLevel)}`}>
                {riskLevel}
              </p>
            </div>
            <div>
              <h3 className="risk-level">Class Grade</h3>
              <p className="risk-value average-score">
                {classGrade === null ? 'N/A' : `${classGrade}%`}
              </p>
            </div>
            <div>
              <h3 className="risk-level">Recommended Videos</h3>
              <p className="risk-value recommended-videos">
                {recommendedVideos.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="tab-container">
        <button
          className={`tab-button ${
            activeTab === 'assignments' ? 'active' : ''
          }`}
          onClick={() => setActiveTab('assignments')}
        >
          Assignments
        </button>
        <button
          className={`tab-button ${activeTab === 'videos' ? 'active' : ''}`}
          onClick={() => setActiveTab('videos')}
        >
          Recommended Videos
        </button>
        <button
          className={`tab-button ${activeTab === 'support' ? 'active' : ''}`}
          onClick={() => setActiveTab('support')}
        >
          Support
        </button>
      </div>

      {activeTab === 'assignments' && (
        <div className="content-container slide-in">
          <h2 className="content-title">Your Assignments</h2>
          <div className="assignments-list">
            <ul>
              {assignments.map((assignment, index) => (
                <li
                  key={assignment.name}
                  className="list-item slide-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div>
                    <h3 className="item-title">{assignment.name}</h3>
                    <p
                      className={`item-score ${
                        assignment.score === 'N/A' ||
                        assignment.score === 'Error'
                          ? ''
                          : Number(assignment.score) <
                            assignment.pointsPossible * 0.7
                          ? 'score-bad'
                          : 'score-good'
                      }`}
                    >
                      {assignment.score === 'N/A' ||
                      assignment.score === 'Error'
                        ? assignment.score
                        : `${assignment.score}/${assignment.pointsPossible}`}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'videos' && (
        <div className="content-container slide-in">
          <h2 className="content-title">Recommended Videos</h2>
          <ul>
            {recommendedVideos.map((video, index) => (
              <li
                key={video.id}
                className="list-item slide-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="video-card">
                  <div className="video-info">
                    <h3 className="item-title">{video.title}</h3>
                    <p className="video-channel">{video.channel}</p>
                    <p className="video-stats">
                      {video.viewCount} • {video.duration}
                    </p>
                    <p className="video-reason">{video.reason}</p>
                  </div>
                </div>
                <a
                  href={video.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="youtube-link"
                >
                  <img src={video.thumbnail} alt="youtube-logo" />
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {activeTab === 'support' && (
        <div className="content-container slide-in">
          <h2 className="content-title">Support Resources</h2>
          {supportVideo && (
            <div className="support-video-container">
              <div className="support-video-card">
                <div className="support-video-info">
                  <h3 className="support-video-title">{supportVideo.title}</h3>
                  <p className="support-video-channel">
                    {supportVideo.channelTitle}
                  </p>
                </div>
                <a
                  href={supportVideo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="youtube-link"
                >
                  <img
                    className="support-video-thumbnail"
                    src={`https://img.youtube.com/vi/${supportVideo.videoId}/mqdefault.jpg`}
                    alt="Video thumbnail"
                  />
                </a>
              </div>
            </div>
          )}
        </div>
      )}
    </body>
  );
};

export default StudentView;
