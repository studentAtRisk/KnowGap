import React, { useState, useEffect } from 'react';
import './Popup.css';
import youtube from '../Popup/imgs/youtube.png';

const InstructorView = () => {
  const [activeTab, setActiveTab] = useState('assignments');
  const [students, setStudents] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [courseQuestions, setCourseQuestions] = useState([]);
  const [newVideo, setNewVideo] = useState({
    title: '',
    url: '',
    questionId: '',
  });
  const [courseContext, setCourseContext] = useState('');
  const [editingVideo, setEditingVideo] = useState(null);

  const imgs = { youtube: '/path/to/youtube/icon.png' };

  const getCanvasBaseUrl = () => {
    const url = window.location.href;
    const match = url.match(/(https?:\/\/[^\/]+)/);
    return match ? match[1] : null;
  };

  const fetchCurrentCourseId = () => {
    const url = window.location.href;
    const match = url.match(/\/courses\/(\d+)/);
    return match && match[1] ? match[1] : null;
  };

  const fetchEnrollments = async (courseId) => {
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
        `${baseUrl}/api/v1/courses/${courseId}/enrollments`,
        requestOptions
      );
      const enrollmentData = await response.json();
      return enrollmentData.filter(
        (enrollment) => enrollment.type === 'StudentEnrollment'
      );
    } catch (error) {
      console.error('Error fetching enrollment data:', error);
      return [];
    }
  };

  const fetchAssignments = async (courseId, userId) => {
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
      const assignmentsResponse = await fetch(
        `${baseUrl}/api/v1/courses/${courseId}/assignments`,
        requestOptions
      );
      const assignmentsResult = await assignmentsResponse.json();

      const studentAssignments = await Promise.all(
        assignmentsResult.map(async (assignment) => {
          const submissionResponse = await fetch(
            `${baseUrl}/api/v1/courses/${courseId}/assignments/${assignment.id}/submissions/${userId}`,
            requestOptions
          );
          const submissionResult = await submissionResponse.json();

          return {
            name: assignment.name,
            score: submissionResult.score || 'N/A',
            pointsPossible: assignment.points_possible,
          };
        })
      );

      return studentAssignments;
    } catch (error) {
      console.error('Error fetching assignments:', error);
      return [];
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      const courseId = fetchCurrentCourseId();
      if (courseId) {
        const enrollments = await fetchEnrollments(courseId);
        const studentData = await Promise.all(
          enrollments.map(async (enrollment) => {
            const assignments = await fetchAssignments(
              courseId,
              enrollment.user_id
            );
            return {
              id: enrollment.user_id,
              name: enrollment.user.name,
              scores: assignments.map((a) =>
                a.score !== 'N/A' ? parseFloat(a.score) : 0
              ),
              assignments: assignments,
            };
          })
        );
        setStudents(studentData);
        fetchCourseVideos(courseId);
      }
    };

    fetchData();
  }, []);

  const calculateAverageScore = (scores) => {
    const validScores = scores.filter((score) => score !== 'N/A');
    return validScores.length > 0
      ? validScores.reduce((acc, score) => acc + score, 0) / validScores.length
      : 0;
  };

  const calculateRiskFactor = (averageScore) => {
    return averageScore < 50 ? 1 : averageScore < 70 ? 0.5 : 0;
  };

  const getRiskMeterColor = (riskFactor) => {
    return riskFactor === 1
      ? 'bg-red-600'
      : riskFactor === 0.5
      ? 'bg-yellow-500'
      : 'bg-green-500';
  };

  const getClassPerformanceOverview = () => {
    let highRiskCount = 0;
    let mediumRiskCount = 0;
    let lowRiskCount = 0;
    let totalScore = 0;

    students.forEach((student) => {
      const averageScore = calculateAverageScore(student.scores);
      const riskFactor = calculateRiskFactor(averageScore);

      if (riskFactor === 1) {
        highRiskCount++;
      } else if (riskFactor === 0.5) {
        mediumRiskCount++;
      } else {
        lowRiskCount++;
      }

      totalScore += averageScore;
    });

    const classSize = students.length;
    const averageScore = totalScore / classSize;

    return {
      highRiskCount,
      mediumRiskCount,
      lowRiskCount,
      averageScore,
    };
  };

  const sendNotification = (message) => {
    setNotifications([...notifications, message]);
  };

  const fetchCourseVideos = async (courseId) => {
    const baseUrl =
      'https://slimy-betsy-student-risk-ucf-cdl-test-1cfbb0a5.koyeb.app';
    try {
      const response = await fetch(`${baseUrl}/get-course-videos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          course_id: courseId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received data:', data);
      setCourseQuestions(data.course_videos || []);
    } catch (error) {
      console.error('Error fetching course videos:', error);
    }
  };

  const addVideoToQuestion = (questionId, video) => {
    setCourseQuestions((prevQuestions) =>
      prevQuestions.map((question) =>
        question.questionid === questionId
          ? { ...question, video_data: [...question.video_data, video] }
          : question
      )
    );
  };
  const removeVideoFromQuestion = (questionId, videoIndex) => {
    setCourseQuestions((prevQuestions) =>
      prevQuestions.map((question) =>
        question.questionid === questionId
          ? {
              ...question,
              // Keep the existing video_data structure including thumbnails
              video_data: {
                ...question.video_data,
                isRemoved: true, // Add a flag instead of nullifying
              },
            }
          : question
      )
    );
  };

  const handleAddVideo = () => {
    if (!newVideo.questionId || !newVideo.title || !newVideo.url) {
      alert('Please fill in all fields');
      return;
    }

    const videoToAdd = {
      title: newVideo.title,
      link: newVideo.url,
      thumbnail: '',
      channel: 'Custom Added',
    };

    addVideoToQuestion(newVideo.questionId, videoToAdd);
    setNewVideo({ title: '', url: '', questionId: '' });
  };

  const updateCourseContext = async () => {
    const courseId = fetchCurrentCourseId();
    if (!courseId) return;

    const baseUrl =
      'https://slimy-betsy-student-risk-ucf-cdl-test-1cfbb0a5.koyeb.app';
    try {
      const response = await fetch(`${baseUrl}/update-course-context`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          courseid: courseId,
          course_context: courseContext,
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      console.log('Course context updated successfully');
    } catch (error) {
      console.error('Error updating course context:', error);
    }
  };

  const handleEditVideo = (questionId, videoIndex, currentLink) => {
    setEditingVideo({ questionId, videoIndex, currentLink });
  };

  const handleSaveEdit = async () => {
    if (!editingVideo) return;

    const question = courseQuestions.find(
      (q) => q.questionid === editingVideo.questionId
    );
    const video = question.video_data[editingVideo.videoIndex];

    const baseUrl =
      'https://slimy-betsy-student-risk-ucf-cdl-test-1cfbb0a5.koyeb.app';
    try {
      const response = await fetch(`${baseUrl}/update_video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quizid: fetchCurrentCourseId(),
          questionid: editingVideo.questionId,
          old_link: editingVideo.currentLink,
          new_link: editingVideo.newLink,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Update the local state
      setCourseQuestions((prevQuestions) =>
        prevQuestions.map((q) =>
          q.questionid === editingVideo.questionId
            ? {
                ...q,
                video_data: q.video_data.map((v, index) =>
                  index === editingVideo.videoIndex
                    ? { ...v, link: editingVideo.newLink }
                    : v
                ),
              }
            : q
        )
      );

      setEditingVideo(null);
      sendNotification(result.message);
    } catch (error) {
      console.error('Error updating video:', error);
      sendNotification('Failed to update video');
    }
  };

  const styles = {
    body: {
      backgroundColor: '#f7fafc',
      fontFamily: 'Arial, sans-serif',
    },
    container: {
      maxWidth: '40rem',
      margin: '1rem auto',
      padding: '1rem',
      backgroundColor: '#fff',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      borderRadius: '0.375rem',
    },
    title: {
      fontSize: '1.125rem',
      fontWeight: '600',
      marginBottom: '0.5rem',
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: '1rem',
    },
    item: {
      textAlign: 'center',
    },
    itemTitle: {
      fontSize: '0.875rem',
      fontWeight: '500',
      marginBottom: '0.25rem',
    },
    highRisk: {
      fontSize: '2rem',
      fontWeight: '700',
      color: '#e53e3e',
    },
    mediumRisk: {
      fontSize: '2rem',
      fontWeight: '700',
      color: '#ecc94b',
    },
    lowRisk: {
      fontSize: '2rem',
      fontWeight: '700',
      color: '#48bb78',
    },
    averageScore: {
      fontSize: '0.875rem',
      fontWeight: '500',
      marginTop: '1rem',
    },
    studentList: {
      listStyleType: 'none',
      padding: '0',
      margin: '0',
    },
    studentItem: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.75rem 1rem',
      backgroundColor: '#fff',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      borderLeft: '4px solid transparent',
      borderRadius: '0.375rem',
      transition: 'background-color 0.15s ease-in-out',
      cursor: 'pointer',
    },
    studentItemHover: {
      backgroundColor: '#bee3f8',
    },
    studentName: {
      fontSize: '1rem',
      fontWeight: '500',
      color: '#4a5568',
    },
    studentDetail: {
      fontSize: '0.875rem',
      color: '#a0aec0',
    },
    riskTag: {
      padding: '0.25rem 0.5rem',
      borderRadius: '0.375rem',
      fontSize: '0.75rem',
      fontWeight: '500',
      color: '#fff',
    },
    highRiskTag: {
      backgroundColor: '#e53e3e',
    },
    mediumRiskTag: {
      backgroundColor: '#ecc94b',
    },
    lowRiskTag: {
      backgroundColor: '#48bb78',
    },
    button: {
      backgroundColor: '#e53e3e',
      color: '#fff',
      padding: '0.5rem 0.75rem',
      borderRadius: '0.375rem',
      cursor: 'pointer',
      transition: 'background-color 0.15s ease-in-out',
    },
    buttonHover: {
      backgroundColor: '#c53030',
    },
    textArea: {
      width: '100%',
      border: '1px solid #cbd5e0',
      borderRadius: '0.375rem',
      padding: '0.5rem',
      marginBottom: '0.5rem',
    },
    messageButton: {
      backgroundColor: '#3182ce',
      color: '#fff',
      padding: '0.5rem 0.75rem',
      borderRadius: '0.375rem',
      cursor: 'pointer',
      transition: 'background-color 0.15s ease-in-out',
    },
    messageButtonHover: {
      backgroundColor: '#2b6cb0',
    },
    notificationList: {
      listStyleType: 'none',
      padding: '0',
      margin: '0',
      marginTop: '1rem',
    },
    notificationItem: {
      padding: '0.75rem 1rem',
      backgroundColor: '#fff',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      borderLeft: '4px solid #3182ce',
      borderRadius: '0.375rem',
    },
    videoCard: {
      border: '1px solid #e2e8f0',
      borderRadius: '0.375rem',
      padding: '1rem',
      marginBottom: '1rem',
      boxShadow:
        '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    },
    videoThumbnail: {
      width: '100%',
      height: 'auto',
      borderRadius: '0.25rem',
      marginBottom: '0.5rem',
    },
    videoTitle: {
      fontSize: '1rem',
      fontWeight: '600',
      marginBottom: '0.25rem',
    },
    videoChannel: {
      fontSize: '0.875rem',
      color: '#718096',
      marginBottom: '0.5rem',
    },
    questionText: {
      fontSize: '0.875rem',
      color: '#4a5568',
      marginTop: '0.5rem',
    },
    removeButton: {
      backgroundColor: '#e53e3e',
      color: '#fff',
      border: 'none',
      padding: '0.5rem',
      borderRadius: '0.25rem',
      cursor: 'pointer',
      marginTop: '0.5rem',
    },
    editButton: {
      backgroundColor: '#4299e1',
      color: '#fff',
      border: 'none',
      padding: '0.5rem',
      borderRadius: '0.25rem',
      cursor: 'pointer',
      marginTop: '0.5rem',
      marginLeft: '0.5rem',
    },
    editModal: {
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      backgroundColor: '#fff',
      padding: '2rem',
      borderRadius: '0.5rem',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      zIndex: 1000,
    },
    input: {
      width: '100%',
      padding: '0.5rem',
      marginBottom: '1rem',
      borderRadius: '0.25rem',
      border: '1px solid #e2e8f0',
    },
    saveButton: {
      backgroundColor: '#48bb78',
      color: '#fff',
      border: 'none',
      padding: '0.5rem 1rem',
      borderRadius: '0.25rem',
      cursor: 'pointer',
      marginRight: '0.5rem',
    },
    cancelButton: {
      backgroundColor: '#e53e3e',
      color: '#fff',
      border: 'none',
      padding: '0.5rem 1rem',
      borderRadius: '0.25rem',
      cursor: 'pointer',
    },
  };

  return (
    <body style={styles.body}>
      <div style={styles.container}>
        <div>
          <h2 style={styles.title}>Class Performance Overview</h2>
          <div style={styles.grid}>
            <div style={styles.item}>
              <h3 style={styles.itemTitle}>High Risk</h3>
              <p style={styles.highRisk}>
                {getClassPerformanceOverview().highRiskCount}
              </p>
            </div>
            <div style={styles.item}>
              <h3 style={styles.itemTitle}>Medium Risk</h3>
              <p style={styles.mediumRisk}>
                {getClassPerformanceOverview().mediumRiskCount}
              </p>
            </div>
            <div style={styles.item}>
              <h3 style={styles.itemTitle}>Low Risk</h3>
              <p style={styles.lowRisk}>
                {getClassPerformanceOverview().lowRiskCount}
              </p>
            </div>
          </div>
          <p style={styles.averageScore}>
            Average Score:{' '}
            {getClassPerformanceOverview().averageScore.toFixed(2)}%
          </p>
        </div>
      </div>

      <div
        style={{ ...styles.container, maxHeight: '400px', overflowY: 'auto' }}
      >
        <div>
          <h2 style={styles.title}>Student Risk Dashboard</h2>
          <ul style={styles.studentList}>
            {students.map((student) => (
              <li
                key={student.id}
                style={{
                  ...styles.studentItem,
                  ':hover': styles.studentItemHover,
                }}
              >
                <div>
                  <h3 style={styles.studentName}>{student.name}</h3>
                  <p style={styles.studentDetail}>
                    Average Score:{' '}
                    {calculateAverageScore(student.scores).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <span
                    style={{
                      ...styles.riskTag,
                      ...(calculateRiskFactor(
                        calculateAverageScore(student.scores)
                      ) === 1
                        ? styles.highRiskTag
                        : calculateRiskFactor(
                            calculateAverageScore(student.scores)
                          ) === 0.5
                        ? styles.mediumRiskTag
                        : styles.lowRiskTag),
                    }}
                  >
                    {calculateRiskFactor(
                      calculateAverageScore(student.scores)
                    ) === 1
                      ? 'High Risk'
                      : calculateRiskFactor(
                          calculateAverageScore(student.scores)
                        ) === 0.5
                      ? 'Medium Risk'
                      : 'Low Risk'}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div style={styles.container}>
        <div>
          <h2 style={styles.title}>Manage Course Videos</h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
              gap: '1rem',
            }}
          >
            {courseQuestions.map((question, index) => (
              <div key={index} style={styles.videoCard}>
                <img
                  src={question.video_data?.thumbnail}
                  alt={question.video_data?.title}
                  style={styles.videoThumbnail}
                />
                <h3 style={styles.videoTitle}>{question.video_data?.title}</h3>
                <p style={styles.videoChannel}>
                  {question.video_data?.channel}
                </p>
                <a
                  href={question.video_data?.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ display: 'block', marginBottom: '0.5rem' }}
                >
                  Watch Video
                </a>
                <p style={styles.questionText}>
                  <strong>Question:</strong> {question.question_text}
                </p>
                <p style={styles.questionText}>
                  <strong>Core Topic:</strong> {question.core_topic}
                </p>
                <button
                  onClick={() =>
                    removeVideoFromQuestion(question.questionid, 0)
                  }
                  style={styles.removeButton}
                >
                  Remove Video
                </button>
                <button
                  onClick={() =>
                    handleEditVideo(
                      question.questionid,
                      0,
                      question.video_data?.link
                    )
                  }
                  style={styles.editButton}
                >
                  Edit Video
                </button>
              </div>
            ))}
          </div>

          {editingVideo && (
            <div style={styles.editModal}>
              <h3>Edit Video Link</h3>
              <input
                type="text"
                value={editingVideo.newLink}
                onChange={(e) =>
                  setEditingVideo({ ...editingVideo, newLink: e.target.value })
                }
                style={styles.input}
              />
              <button onClick={handleSaveEdit} style={styles.saveButton}>
                Save
              </button>
              <button
                onClick={() => setEditingVideo(null)}
                style={styles.cancelButton}
              >
                Cancel
              </button>
            </div>
          )}

          <h4>Add New Video</h4>
          <select
            value={newVideo.questionId}
            onChange={(e) =>
              setNewVideo({ ...newVideo, questionId: e.target.value })
            }
          >
            <option value="">Select a question</option>
            {courseQuestions.map((question) => (
              <option key={question.questionid} value={question.questionid}>
                {question.question_text.substring(0, 50)}...
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Video Title"
            value={newVideo.title}
            onChange={(e) =>
              setNewVideo({ ...newVideo, title: e.target.value })
            }
          />
          <input
            type="text"
            placeholder="Video URL"
            value={newVideo.url}
            onChange={(e) => setNewVideo({ ...newVideo, url: e.target.value })}
          />
          <button onClick={handleAddVideo}>Add Video</button>
        </div>
      </div>

      <div style={styles.container}>
        <div>
          <h2 style={styles.title}>Course Context</h2>
          <textarea
            style={styles.textArea}
            value={courseContext}
            onChange={(e) => setCourseContext(e.target.value)}
            placeholder="Enter course context..."
          ></textarea>
          <button
            style={{
              ...styles.messageButton,
              ':hover': styles.messageButtonHover,
            }}
            onClick={updateCourseContext}
          >
            Update Course Context
          </button>
        </div>
      </div>
    </body>
  );
};

export default InstructorView;
