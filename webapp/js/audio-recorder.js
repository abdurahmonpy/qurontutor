/**
 * Audio Recorder with Canvas Visualizer
 * Uses MediaRecorder Web API and Web Audio API
 */
class QuranAudioRecorder {
  constructor(options = {}) {
    this.canvas = options.canvas || null;
    this.onStateChange = options.onStateChange || (() => {});
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.audioStream = null;
    this.audioContext = null;
    this.analyser = null;
    this.animationId = null;
    this.startTime = null;
    this.timerInterval = null;
    this.durationSeconds = 0;
    this.isRecording = false;
  }

  async start() {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Brauzeringizda ovoz yozish (MediaDevices) qo'llab-quvvatlanmaydi.");
      }

      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      // Setup Web Audio Analyser
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.audioContext = new AudioCtx();
      const source = this.audioContext.createMediaStreamSource(this.audioStream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 64;
      source.connect(this.analyser);

      // Setup MediaRecorder
      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/ogg;codecs=opus';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = ''; // Let browser choose default
        }
      }

      this.mediaRecorder = mimeType ? new MediaRecorder(this.audioStream, { mimeType }) : new MediaRecorder(this.audioStream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          this.audioChunks.push(e.data);
        }
      };

      this.mediaRecorder.start(100);
      this.isRecording = true;
      this.startTime = Date.now();
      this.durationSeconds = 0;
      this.spokenTranscript = '';

      // Start Web SpeechRecognition (Arabic)
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        try {
          this.recognition = new SpeechRecognition();
          this.recognition.lang = 'ar-SA';
          this.recognition.continuous = true;
          this.recognition.interimResults = true;

          this.recognition.onresult = (e) => {
            let final = '';
            let interim = '';
            for (let i = 0; i < e.results.length; i++) {
              if (e.results[i].isFinal) {
                final += e.results[i][0].transcript + ' ';
              } else {
                interim += e.results[i][0].transcript;
              }
            }
            this.spokenTranscript = (final + interim).trim();
            if (this.onTranscript) {
              this.onTranscript(this.spokenTranscript);
            }
          };

          this.recognition.onerror = (err) => {
            console.warn("Browser SpeechRecognition notice:", err.error);
          };

          this.recognition.start();
        } catch (e) {
          console.warn("Could not start SpeechRecognition:", e);
        }
      }

      // Timer
      this.timerInterval = setInterval(() => {
        this.durationSeconds = Math.floor((Date.now() - this.startTime) / 1000);
        this.onStateChange({ status: 'recording', duration: this.durationSeconds });
      }, 1000);

      // Start Visualizer
      if (this.canvas) {
        this._startVisualizer();
      }

      this.onStateChange({ status: 'recording', duration: 0 });
      return true;
    } catch (err) {
      this.onStateChange({ status: 'error', error: err.message });
      throw err;
    }
  }

  stop() {
    return new Promise((resolve) => {
      if (this.recognition) {
        try {
          this.recognition.stop();
        } catch (e) {}
      }

      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        const text = this.spokenTranscript;
        this._cleanup();
        this.onStateChange({ status: 'idle', duration: 0 });
        resolve({ audioBlob: null, spokenText: text });
        return;
      }

      this.mediaRecorder.onstop = () => {
        const mimeType = this.mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        const text = this.spokenTranscript;
        this._cleanup();
        this.onStateChange({ status: 'idle', duration: 0 });
        resolve({ audioBlob, spokenText: text });
      };

      this.mediaRecorder.stop();
    });
  }

  cancel() {
    this._cleanup();
    this.onStateChange({ status: 'idle', duration: 0 });
  }

  _startVisualizer() {
    if (!this.canvas || !this.analyser) return;
    const ctx = this.canvas.getContext('2d');
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!this.isRecording) return;
      this.animationId = requestAnimationFrame(draw);

      this.analyser.getByteFrequencyData(dataArray);

      const width = this.canvas.width;
      const height = this.canvas.height;
      ctx.clearRect(0, 0, width, height);

      const barWidth = (width / bufferLength) * 2.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * height;

        // Gradient from emerald to gold
        const gradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
        gradient.addColorStop(0, '#f59e0b');
        gradient.addColorStop(1, '#10b981');

        ctx.fillStyle = gradient;
        ctx.fillRect(x, height - barHeight, barWidth - 2, barHeight);

        x += barWidth;
      }
    };

    draw();
  }

  _cleanup() {
    this.isRecording = false;
    if (this.timerInterval) clearInterval(this.timerInterval);
    if (this.animationId) cancelAnimationFrame(this.animationId);

    if (this.audioStream) {
      this.audioStream.getTracks().forEach((track) => track.stop());
      this.audioStream = null;
    }
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close().catch(() => {});
      this.audioContext = null;
    }
  }
}

window.QuranAudioRecorder = QuranAudioRecorder;
