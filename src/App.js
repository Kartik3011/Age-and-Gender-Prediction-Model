import React, { useState, useEffect, useRef } from "react";
import "./index.css";

const BACKEND = "https://age-gender-backend.onrender.com"; // IMP- Change this link to local port if running locally on computer terminal.
const PREDICT_URL = `${BACKEND}/predict`;

const mostCommon = (arr) =>
  arr
    .sort(
      (a, b) =>
        arr.filter((v) => v === a).length - arr.filter((v) => v === b).length
    )
    .pop();

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const toggleTheme = () => setDarkMode(!darkMode);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [resultText, setResultText] = useState("");
  const [loading, setLoading] = useState(true); // 👈 show startup message

  const ageHistory = useRef([]);
  const predictionsRef = useRef([]);

  useEffect(() => {
    document.body.style.backgroundColor = darkMode ? "#121212" : "#f4f4f4";
    document.body.classList.toggle("light-mode", !darkMode);
  }, [darkMode]);

  // Get webcam
  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => (videoRef.current.srcObject = stream))
      .catch(() => setResultText("Camera blocked or in use."));
  }, []);

  // Draw predictions
  useEffect(() => {
    let raf;
    const draw = () => {
      const v = videoRef.current;
      const c = canvasRef.current;
      if (v && c && v.readyState === 4) {
        const w = v.videoWidth,
          h = v.videoHeight;
        if (w && h) {
          c.width = w;
          c.height = h;
          const ctx = c.getContext("2d");
          ctx.drawImage(v, 0, 0, w, h);
          ctx.strokeStyle = "#00ff88";
          ctx.lineWidth = 2;
          ctx.font = "16px monospace";
          ctx.fillStyle = "#00ff88";
          predictionsRef.current.forEach((p) => {
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

  // Predict every 500ms
  useEffect(() => {
    const id = setInterval(() => {
      const v = videoRef.current;
      const c = canvasRef.current;
      if (!v || !c || !v.videoWidth) return;
      const ctx = c.getContext("2d");
      c.width = v.videoWidth;
      c.height = v.videoHeight;
      ctx.drawImage(v, 0, 0, c.width, c.height);

      const dataURL = c.toDataURL("image/jpeg", 0.7);
      fetch(PREDICT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataURL }),
      })
        .then((res) => res.json())
        .then((json) => {
          setLoading(false); // 👈 backend responded at least once
          if (json.predictions && json.predictions.length) {
            const first = json.predictions[0];
            ageHistory.current.push(first.age);
            if (ageHistory.current.length > 5) ageHistory.current.shift();
            const stableAge = mostCommon(ageHistory.current);
            first.age = stableAge;
            predictionsRef.current = json.predictions;
            setResultText(`${first.gender}, ${stableAge}`);
          } else {
            predictionsRef.current = [];
            setResultText("No face detected");
            ageHistory.current = [];
          }
        })
        .catch(() => {
          setResultText("Error predicting");
        });
    }, 500);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ ...styles.container, color: darkMode ? "#f1f1f1" : "#111" }}>
      <h1
        style={{
          ...styles.heading,
          backgroundImage: darkMode
            ? styles.darkGradient
            : styles.lightGradient,
        }}
        className="animate-heading"
      >
        Real-Time Age & Gender Detection
      </h1>
      <p style={styles.subtext}>Detect faces live from your webcam stream</p>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        width="1"
        height="1"
        style={{ position: "absolute", opacity: 0 }}
      />
      <canvas ref={canvasRef} style={styles.video} />

      <p style={{ marginTop: 10, fontWeight: "bold" }}>
        {loading
          ? "Backend is starting, please wait 30 seconds, Refresh if it is too laggy."
          : resultText}
      </p>

      <div style={styles.controls}>
        <button
          style={{
            ...styles.button,
            backgroundColor: darkMode ? "#00ccff" : "#00ffcc",
            color: "#000",
          }}
          onClick={toggleTheme}
        >
          Toggle {darkMode ? "Light" : "Dark"} Mode
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    padding: "1rem 1rem 2rem",
    textAlign: "center",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    transition: "all 0.3s ease",
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-start",
    alignItems: "center",
  },
  heading: {
    fontSize: "2.5rem",
    margin: "1.5rem 0 0.2rem",
    backgroundClip: "text",
    WebkitBackgroundClip: "text",
    color: "transparent",
    fontWeight: "800",
    transition: "transform 0.3s ease",
  },
  subtext: {
    fontSize: "1rem",
    marginBottom: "1rem",
    opacity: 0.75,
    fontStyle: "italic",
  },
  lightGradient: "linear-gradient(90deg, #007bff, #00ffcc)",
  darkGradient: "linear-gradient(90deg, #00ffcc, #00aaff)",
  video: {
    width: "520px",
    height: "400px",
    borderRadius: "10px",
    border: "3px solid #00ffcc",
    boxShadow: "0 0 10px rgba(0, 255, 204, 0.5)",
    marginTop: "0.5rem",
  },
  controls: { marginTop: "1rem" },
  button: {
    border: "none",
    padding: "10px 20px",
    fontSize: "1rem",
    fontWeight: "600",
    borderRadius: "6px",
    cursor: "pointer",
    transition: "all 0.3s ease",
  },
};

export default App;
