import React, { useState, useEffect, useRef } from 'react';
import './index.css';

const BACKEND = 'https://age-gender-backend.onrender.com';
const PREDICT_URL = `${BACKEND}/predict`;



/* helper to pick the mode of an array */
const mostCommon = (arr) =>
  arr
    .sort((a, b) =>
      arr.filter(v => v === a).length - arr.filter(v => v === b).length
    )
    .pop();

function App() {
  /* ---------- original dark‑mode logic ---------- */
  const [darkMode, setDarkMode] = useState(false);
  useEffect(() => {
    document.body.style.backgroundColor = darkMode ? '#121212' : '#f4f4f4';
    document.body.classList.toggle('light-mode', !darkMode);
  }, [darkMode]);
  const toggleTheme = () => setDarkMode(!darkMode);

  /* ---------- refs & state ---------- */
  const videoRef   = useRef(null);
  const canvasRef  = useRef(null);
  const [resultText, setResultText] = useState('');

  /* ✨ new: keep last 5 ages for smoothing */
  const ageHistory = useRef([]);

  /* ---------- request webcam once ---------- */
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => (videoRef.current.srcObject = stream))
      .catch(err   => setResultText('Camera blocked or in use.'));
  }, []);

  /* ---------- draw video & overlay predictions every frame ---------- */
  const predictionsRef = useRef([]);
  useEffect(() => {
    let raf;
    const draw = () => {
      const v = videoRef.current;
      const c = canvasRef.current;
      if (v && c && v.readyState === 4) {
        const w = v.videoWidth, h = v.videoHeight;
        if (w && h) {
          c.width = w; c.height = h;
          const ctx = c.getContext('2d');
          ctx.drawImage(v, 0, 0, w, h);             // live frame
          ctx.strokeStyle = '#00ff88';
          ctx.lineWidth   = 2;
          ctx.font        = '16px monospace';
          ctx.fillStyle   = '#00ff88';
          predictionsRef.current.forEach(p => {
            const [x1, y1, x2, y2] = p.box;
            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
            ctx.fillText(`${p.gender}, ${p.age}`, x1, y1 - 6);
          });
        }
      }
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, []);

  /* ---------- capture & send one frame every 500 ms ---------- */
  useEffect(() => {
    const id = setInterval(() => {
      const v = videoRef.current;
      const c = canvasRef.current;
      if (!v || !c || !v.videoWidth) return;    // camera not ready
      const ctx = c.getContext('2d');
      c.width = v.videoWidth; c.height = v.videoHeight;
      ctx.drawImage(v, 0, 0, c.width, c.height);   // ensure current frame drawn

      // Create a small offscreen canvas for faster upload
const smallCanvas = document.createElement('canvas');
const smallCtx = smallCanvas.getContext('2d');

smallCanvas.width = 160;
smallCanvas.height = 120;

// Downscale the video into smaller canvas
smallCtx.drawImage(video, 0, 0, 160, 120);

// Encode as lower-quality JPEG
const dataURL = smallCanvas.toDataURL('image/jpeg', 0.4);

      fetch(PREDICT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataURL }),
      })
        .then(res => res.json())
        .then(json => {
          if (json.predictions && json.predictions.length) {
            /* ✨ temporal smoothing on the first face */
            const first = json.predictions[0];
            ageHistory.current.push(first.age);
            if (ageHistory.current.length > 5) ageHistory.current.shift();
            const stableAge = mostCommon(ageHistory.current);
            first.age = stableAge;                 // overwrite for display

            predictionsRef.current = json.predictions;
            setResultText(`${first.gender}, ${stableAge}`);
          } else {
            predictionsRef.current = [];
            setResultText('No face detected');
            ageHistory.current = [];
          }
        })
        .catch(() => setResultText('Error predicting'));
    }, 200);
    return () => clearInterval(id);
  }, []);

  /* ---------- UI (unchanged) ---------- */
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

      {/* hidden video for capture */}
      <video ref={videoRef} autoPlay playsInline muted width="1" height="1"
             style={{ position: 'absolute', opacity: 0 }} />
      {/* visible canvas */}
      <canvas ref={canvasRef} style={styles.video} />

      {/* label */}
      <p style={{ marginTop: 10, fontWeight: 'bold' }}>{resultText}</p>

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

/* ---------- your original inline styles ---------- */
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
  darkGradient:  'linear-gradient(90deg, #00ffcc, #00aaff)',
  video: {
    width: '520px',
    height: '400px',
    borderRadius: '10px',
    border: '3px solid #00ffcc',
    boxShadow: '0 0 10px rgba(0, 255, 204, 0.5)',
    marginTop: '0.5rem',
  },
  controls: { marginTop: '1rem' },
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
