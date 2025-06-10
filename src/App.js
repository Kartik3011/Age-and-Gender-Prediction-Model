import React, { useState, useEffect } from 'react';
import './index.css';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
  if (darkMode) {
    document.body.classList.remove('light-mode');  // dark mode = remove light-mode class
    document.body.style.backgroundColor = '#121212'; // optional, can be handled by CSS
  } else {
    document.body.classList.add('light-mode');     // light mode = add light-mode class
    document.body.style.backgroundColor = '#f4f4f4';
  }
}, [darkMode]);


  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div style={{ ...styles.container, color: darkMode ? '#f1f1f1' : '#111' }}>
      <h1
        style={{
          ...styles.heading,
          backgroundImage: darkMode ? styles.darkGradient : styles.lightGradient,
        }}
        className="animate-heading"
      >
        Real-Time Age & Gender Detection
      </h1>
      <p style={styles.subtext}>Detect faces live from your webcam stream</p>

      <img
        src="http://localhost:5000/video_feed"
        alt="Live Stream"
        style={styles.video}
      />

      <div style={styles.controls}>
        <button
          style={{
            ...styles.button,
            backgroundColor: darkMode ? '#00ccff' : '#00ffcc',
            color: '#000',
          }}
          onClick={toggleTheme}
        >
          Toggle {darkMode ? 'Light' : 'Dark'} Mode
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    padding: '1rem 1rem 2rem',
    textAlign: 'center',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    transition: 'all 0.3s ease',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'flex-start',
    alignItems: 'center',
  },
  heading: {
    fontSize: '2.5rem',
    margin: '1.5rem 0 0.2rem',
    backgroundClip: 'text',
    WebkitBackgroundClip: 'text',
    color: 'transparent',
    fontWeight: '800',
    transition: 'transform 0.3s ease',
  },
  subtext: {
    fontSize: '1rem',
    marginBottom: '1rem',
    opacity: 0.75,
    fontStyle: 'italic',
  },
  lightGradient: 'linear-gradient(90deg, #007bff, #00ffcc)',
  darkGradient: 'linear-gradient(90deg, #00ffcc, #00aaff)',
  video: {
    width: '520px',
    height: '400px',
    borderRadius: '10px',
    border: '3px solid #00ffcc',
    boxShadow: '0 0 10px rgba(0, 255, 204, 0.5)',
    marginTop: '0.5rem',
  },
  controls: {
    marginTop: '1rem',
  },
  button: {
    border: 'none',
    padding: '10px 20px',
    fontSize: '1rem',
    fontWeight: '600',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
};

export default App;
