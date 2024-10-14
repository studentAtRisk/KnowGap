import React, { useState, useEffect } from 'react';
import './Popup.css';
import youtube from '../Popup/imgs/youtube.png';

const InstructorView = () => {
  const [activeTab, setActiveTab] = useState('assignments');
  const [students, setStudents] = useState([]);
  const [notifications, setNotifications] = useState([]);

  const imgs = { youtube };

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
          <h2 style={styles.title}>Early Intervention Alerts</h2>
          <ul style={styles.studentList}>
            {students
              .filter(
                (student) =>
                  calculateRiskFactor(calculateAverageScore(student.scores)) ===
                  1
              )
              .map((student) => (
                <li
                  key={student.id}
                  style={{
                    ...styles.studentItem,
                    borderLeft: '4px solid #e53e3e',
                  }}
                >
                  <div>
                    <h3 style={styles.studentName}>{student.name}</h3>
                    <p style={styles.studentDetail}>
                      Average Score:{' '}
                      {calculateAverageScore(student.scores).toFixed(2)}%
                    </p>
                  </div>
                  <button
                    style={{ ...styles.button, ':hover': styles.buttonHover }}
                    onClick={() =>
                      sendNotification(
                        `Sent intervention alert for ${student.name}`
                      )
                    }
                  >
                    Send Intervention Alert
                  </button>
                </li>
              ))}
          </ul>
        </div>
      </div>

      <div style={styles.container}>
        <div>
          <h2 style={styles.title}>Communication Tools</h2>
          <textarea
            style={styles.textArea}
            placeholder="Enter your message..."
          ></textarea>
          <button
            style={{
              ...styles.messageButton,
              ':hover': styles.messageButtonHover,
            }}
            onClick={() => sendNotification('Message sent to students')}
          >
            Send Message
          </button>
          <div style={{ marginTop: '1rem' }}>
            <h3 style={styles.itemTitle}>Notifications</h3>
            <ul style={styles.notificationList}>
              {notifications.map((notification, index) => (
                <li key={index} style={styles.notificationItem}>
                  <p style={styles.studentDetail}>{notification}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Existing Assignments and Videos */}
      {/* ... */}
    </body>
  );
};

export default InstructorView;
