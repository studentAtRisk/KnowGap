import React, { useState, useEffect } from 'react';
import './Popup.css';
import youtube from '../Popup/imgs/youtube.png';
import StudentView from './Studentview';
import InstructorView from './InstructorView';

const Popup = () => {
  const [userRole, setUserRole] = useState('');
  const [apiToken, setApiToken] = useState('');
  const [assignments, setAssignments] = useState([]);
  const [students, setStudents] = useState([]);

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

  useEffect(() => {
    const fetchUserRole = async () => {
      const baseUrl = getCanvasBaseUrl();
      const courseId = fetchCurrentCourseId();
      const storedToken = localStorage.getItem('apiToken');

      if (!baseUrl || !courseId || !storedToken) {
        console.error('Missing base URL, course ID, or API token');
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
          `${baseUrl}/api/v1/courses/${courseId}/enrollments?user_id=self`,
          requestOptions
        );
        const enrollmentData = await response.json();
        const role = enrollmentData[0].type;
        console.log('User role:', role);
        setUserRole(role);

        if (role === 'StudentEnrollment') {
          fetchAssignments(baseUrl, courseId, storedToken);
        } else if (role === 'TeacherEnrollment') {
          fetchStudents(baseUrl, courseId, storedToken);
        }
      } catch (error) {
        console.error('Error fetching user role:', error);
      }
    };

    if (localStorage.getItem('apiToken')) {
      fetchUserRole();
    }
  }, []);

  const fetchAssignments = async (baseUrl, courseId, token) => {
    // Implement assignment fetching logic here
  };

  const fetchStudents = async (baseUrl, courseId, token) => {
    // Implement student fetching logic here
  };

  const removeToken = () => {
    localStorage.removeItem('apiToken');
    setApiToken('');
    setUserRole('');
    setAssignments([]);
    setStudents([]);
  };

  return (
    <div className="container">
      {localStorage.getItem('apiToken') ? (
        <div className="api-token-input">
          <p>API Token is set</p>
          <button onClick={removeToken}>Remove Token</button>
        </div>
      ) : (
        <div className="api-token-input">
          <input
            type="password"
            placeholder="Enter your API token"
            value={apiToken}
            onChange={(e) => setApiToken(e.target.value)}
          />
          <button
            onClick={() => {
              localStorage.setItem('apiToken', apiToken);
              window.location.reload();
            }}
          >
            Save Token
          </button>
        </div>
      )}
      {userRole === 'TeacherEnrollment' ? (
        <InstructorView students={students} />
      ) : userRole === 'StudentEnrollment' ? (
        <StudentView assignments={assignments} />
      ) : (
        <p>Please enter your API token to view your data.</p>
      )}
    </div>
  );
};

export default Popup;
