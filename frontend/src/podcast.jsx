import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Podcast.css';

function Podcast() {
  const [userId, setUserId] = useState('');
  const [promptUrl, setPromptUrl] = useState('');
  const [audioSrc, setAudioSrc] = useState(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);

  const audioRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const barsRef = useRef([]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handlePlay = () => {
      setIsPlaying(true);
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const src = ctx.createMediaElementSource(audio);
      const analyser = ctx.createAnalyser();

      analyser.fftSize = 32;
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      src.connect(analyser);
      analyser.connect(ctx.destination);
      analyserRef.current = analyser;

      const draw = () => {
        analyser.getByteFrequencyData(dataArray);
        for (let i = 0; i < 4; i++) {
          const barHeight = Math.max(dataArray[i] / 2.5, 20);
          if (barsRef.current[i]) {
            barsRef.current[i].style.height = `${barHeight}px`;
          }
        }
        animationRef.current = requestAnimationFrame(draw);
      };

      draw();
    };

    const handlePauseOrEnd = () => {
      setIsPlaying(false);
      cancelAnimationFrame(animationRef.current);
      if (barsRef.current) {
        barsRef.current.forEach(bar => {
          if (bar) bar.style.height = '20px';
        });
      }
    };

    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePauseOrEnd);
    audio.addEventListener('ended', handlePauseOrEnd);

    return () => {
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePauseOrEnd);
      audio.removeEventListener('ended', handlePauseOrEnd);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAudioSrc(null);

    try {
      const { data: scriptData } = await axios.post("http://127.0.0.1:8000/getscript", {
        user_id: "1",
        prompt: promptUrl,
      });

      const scriptText = scriptData?.script || scriptData?.data?.script;
      if (!scriptText) throw new Error("Script not received");

      const audioResponse = await axios.post(
        "http://127.0.0.1:8000/url",
        { user_id: "1", prompt: scriptText },
        { responseType: 'blob' }
      );

      const audioBlob = new Blob([audioResponse.data], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudioSrc(audioUrl);
    } catch (err) {
      console.error("Error:", err);
    }

    setLoading(false);
  };

  const handleAsk = async () => {
    if (!question || !audioRef.current) return;
    audioRef.current.pause();
    setLoading(true);

    try {
      const { data } = await axios.post("http://127.0.0.1:8000/askquestion", {
        user_id: "1",
        question,
        script: "",
      });

      const answerAudio = await axios.post(
        "http://127.0.0.1:8000/url",
        { user_id: "1", prompt: data.ans },
        { responseType: 'blob' }
      );

      const answerBlob = new Blob([answerAudio.data], { type: 'audio/mpeg' });
      const answerUrl = URL.createObjectURL(answerBlob);

      const answerAudioPlayer = new Audio(answerUrl);
      answerAudioPlayer.play();

      answerAudioPlayer.onended = () => {
        audioRef.current.play();
      };
    } catch (err) {
      console.error("Error asking question:", err);
    }

    setLoading(false);
  };

  return (
    <div className="podcast-container">
      <div className="title">
        <span className="red">Stream</span>2<span className="blue">Pod</span>
      </div>

      <form className="form" onSubmit={handleSubmit}>
        <label>YouTube Video URL</label>
        <input
          type="text"
          value={promptUrl}
          onChange={(e) => setPromptUrl(e.target.value)}
          placeholder="Paste your YouTube URL"
        />
        <button type="submit">Generate Podcast</button>
      </form>

      {loading && <div className="loader"></div>}

      {audioSrc && (
        <div className="player-container">
          <h5>Your Podcast</h5>
          <audio controls ref={audioRef} src={audioSrc} />
          <div className="waveform">
            {[0, 1, 2, 3].map((_, i) => (
              <div
                key={i}
                className="bar"
                ref={(el) => (barsRef.current[i] = el)}
              ></div>
            ))}
          </div>
        </div>
      )}

      <div className="ask-section">
        <label>Ask a Question</label>
        <div className="ask-group">
          <input
            type="text"
            placeholder="Ask about the podcast..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button onClick={handleAsk}>Ask</button>
        </div>
      </div>
    </div>
  );
}

export default Podcast;
