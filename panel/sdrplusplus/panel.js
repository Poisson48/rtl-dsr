/**
 * SDR++ Panel — Full-page sidebar panel for Home Assistant.
 *
 * This registers a custom panel in the HA sidebar (like AdGuard or
 * Studio Code Server). Clicking the sidebar entry opens the SDR++
 * interface as a full page.
 */

const PANEL_VERSION = "0.1.0";

class SdrPlusPlusPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = {};
    this._started = false;
    this._state = {
      bins: new Array(512).fill(-120),
      peakDb: -120,
      peakFreq: 0,
      noiseFloor: -120,
      centerFreq: 100.0,
      sampleRate: 2.048,
      mode: "spectrum",
      gain: "auto",
      rssi: -120,
      connected: false,
    };
    this._requestTimer = null;
    this._demoMode = false;
  }

  setConfig(config) {
    this._config = config || {};
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._started) {
      this._started = true;
      this._render();
      this._startPolling();
    }
  }

  disconnectedCallback() {
    if (this._requestTimer) clearInterval(this._requestTimer);
    this._started = false;
  }

  _startPolling() {
    const interval = this._config.poll_interval || 250;
    this._requestTimer = setInterval(() => this._pollFft(), interval);
  }

  async _pollFft() {
    if (!this._hass && !this._demoMode) return;

    try {
      let resp;
      if (this._demoMode || !this._hass) {
        resp = this._generateDemoData();
      } else {
        resp = await this._hass.callService(
          "rtl_dsr",
          "get_fft",
          { fft_size: this._config.fft_size || 512 },
          undefined,
          true
        );
      }

      const data = resp && resp.response;
      if (data && data.bins && data.bins.length) {
        this._state.bins = data.bins;
        this._state.peakDb = data.peak_db;
        this._state.peakFreq = data.peak_freq;
        this._state.noiseFloor = data.noise_floor;
        this._state.centerFreq = data.center_freq;
        this._state.sampleRate = data.sample_rate;
        this._state.mode = data.mode;
        this._state.gain = data.gain;
        this._state.rssi = data.rssi;
        this._state.connected = true;
        this._drawSpectrum();
        this._drawWaterfall();
        this._updateReadouts();
      } else {
        this._state.connected = false;
        this._updateReadouts();
      }
    } catch (err) {
      if (!this._demoMode) {
        console.warn("RTL-SDR: switching to demo mode -", err.message);
        this._demoMode = true;
      }
      this._state.connected = false;
      this._updateReadouts();
    }
  }

  _generateDemoData() {
    const bins = Array.from({ length: 512 }, (_, i) => {
      const base = -65 + 3 * Math.sin(i / 25);
      if (Math.abs(i - 170) < 3) base += 25;
      if (Math.abs(i - 340) < 2) base += 15;
      return base;
    });
    return {
      response: {
        bins: bins,
        bin_count: 512,
        center_freq: this._state.centerFreq,
        sample_rate: this._state.sampleRate,
        peak_freq: this._state.centerFreq,
        peak_db: -40.0,
        noise_floor: -65.0,
        rssi: -42.5,
        tuner_type: "R820T (demo)",
        mode: this._state.mode,
        gain: this._state.gain,
      },
    };
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
          background: #0a0e14;
          color: #d8dee9;
          height: 100vh;
          overflow: hidden;
        }
        .wrap {
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
          height: 100%;
          max-width: 1600px;
          margin: 0 auto;
        }
        .title-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          flex-wrap: wrap;
          padding-bottom: 12px;
          border-bottom: 1px solid #1a2230;
        }
        .title {
          font-weight: 700;
          font-size: 24px;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .badge {
          font-size: 12px;
          padding: 4px 12px;
          border-radius: 999px;
          background: #1c2530;
          border: 1px solid #2a3542;
          margin-left: 8px;
        }
        .badge.ok { background: #0d3b2a; border-color: #1f7a5a; color: #7ee2b8; }
        .badge.err { background: #3b0d0d; border-color: #7a1f1f; color: #ff8a80; }
        .panel {
          display: grid;
          grid-template-columns: 1fr;
          gap: 16px;
          flex: 1;
          min-height: 0;
        }
        @media (min-width: 1200px) {
          .panel { grid-template-columns: 1fr 320px; }
        }
        .scope {
          background: #05080d;
          border: 1px solid #1a2230;
          border-radius: 12px;
          position: relative;
          overflow: hidden;
        }
        canvas { display: block; width: 100%; }
        #spectrum { height: 200px; }
        #waterfall { height: 400px; image-rendering: pixelated; }
        .grid-overlay {
          position: absolute; inset: 0; pointer-events: none;
          background-image:
            linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px);
          background-size: 10% 25%;
        }
        .controls {
          display: flex;
          flex-direction: column;
          gap: 12px;
          background: #0d1218;
          border: 1px solid #1a2230;
          border-radius: 12px;
          padding: 16px;
          overflow-y: auto;
        }
        .controls h3 {
          margin: 0 0 8px 0;
          font-size: 13px;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: #7a8899;
          padding-bottom: 8px;
          border-bottom: 1px solid #1a2230;
        }
        .row {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .row label {
          flex: 1;
          font-size: 13px;
          color: #9aa7b8;
        }
        .row input, .row select {
          flex: 1.5;
          background: #05080d;
          color: #d8dee9;
          border: 1px solid #2a3542;
          border-radius: 8px;
          padding: 8px 12px;
          font-size: 14px;
          min-height: 40px;
        }
        .row input:focus, .row select:focus {
          outline: 2px solid #4fc3f7;
          border-color: transparent;
        }
        .btn-row {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          margin-top: 8px;
        }
        button {
          flex: 1 1 auto;
          min-width: 100px;
          background: #1c2530;
          color: #d8dee9;
          border: 1px solid #2a3542;
          border-radius: 8px;
          padding: 12px 16px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.15s;
          min-height: 44px;
        }
        button:hover {
          background: #2a3542;
          border-color: #4fc3f7;
          transform: translateY(-1px);
        }
        button.primary {
          background: #12324a;
          border-color: #1f5a85;
          color: #7ec8ff;
        }
        button.on {
          background: #0d3b2a;
          border-color: #1f7a5a;
          color: #7ee2b8;
        }
        .readouts {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 8px;
          font-family: 'Consolas', monospace;
          font-size: 13px;
        }
        @media (min-width: 480px) {
          .readouts { grid-template-columns: repeat(4, 1fr); }
        }
        .readout {
          background: #05080d;
          border: 1px solid #1a2230;
          border-radius: 8px;
          padding: 10px 12px;
        }
        .readout .lbl {
          color: #7a8899;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .readout .val {
          color: #4fc3f7;
          font-weight: 700;
          font-size: 18px;
          margin-top: 4px;
        }
        .s-meter {
          height: 16px;
          background: #05080d;
          border: 1px solid #2a3542;
          border-radius: 999px;
          overflow: hidden;
          position: relative;
          margin-top: 8px;
        }
        .s-meter .fill {
          height: 100%;
          background: linear-gradient(90deg, #4fc3f7, #7ee2b8, #ffd54f, #ff8a80);
          transition: width 0.15s ease-out;
        }
        .freq-display {
          font-family: 'Consolas', monospace;
          font-size: 48px;
          font-weight: 700;
          color: #4fc3f7;
          letter-spacing: 0.02em;
          text-align: center;
          padding: 16px;
          background: #05080d;
          border: 1px solid #1a2230;
          border-radius: 12px;
        }
        .freq-display span.unit {
          font-size: 20px;
          color: #7a8899;
          margin-left: 8px;
        }
        .waterfall-legend {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          color: #7a8899;
          padding: 4px 8px;
          font-family: 'Consolas', monospace;
        }
      </style>
      <div class="wrap">
        <div class="title-row">
          <div class="title">
            📻 SDR++ <span style="font-size:14px;color:#7a8899;">v${PANEL_VERSION}</span>
          </div>
          <div>
            <span id="connBadge" class="badge">● déconnexion</span>
            <span id="modeBadge" class="badge">—</span>
          </div>
        </div>

        <div class="freq-display" id="freqDisplay">100.000<span class="unit">MHz</span></div>

        <div class="panel">
          <div style="display:flex;flex-direction:column;gap:12px;min-height:0;">
            <div class="scope">
              <canvas id="spectrum" width="1600" height="400"></canvas>
              <div class="grid-overlay"></div>
            </div>
            <div class="waterfall-legend">
              <span id="spanLeft">98.976 MHz</span>
              <span>FFT Spectrum</span>
              <span id="spanRight">101.024 MHz</span>
            </div>
            <div class="scope" style="flex:1;">
              <canvas id="waterfall" width="512" height="400"></canvas>
            </div>
            <div class="s-meter">
              <div class="fill" id="sFill" style="width:0%"></div>
            </div>
          </div>

          <div class="controls">
            <h3>Contrôles</h3>
            <div class="row">
              <label>Fréquence</label>
              <input id="freqInput" type="number" step="0.001" value="100.0" />
              <span style="color:#7a8899;font-size:12px">MHz</span>
            </div>
            <div class="row">
              <label>Échantillonnage</label>
              <input id="rateInput" type="number" step="0.001" value="2.048" />
              <span style="color:#7a8899;font-size:12px">MS/s</span>
            </div>
            <div class="row">
              <label>Gain</label>
              <select id="gainSelect">
                <option value="auto">auto</option>
                <option value="0.0">0.0</option>
                <option value="14.4">14.4</option>
                <option value="28.0">28.0</option>
                <option value="40.2">40.2</option>
                <option value="49.6">49.6</option>
              </select>
            </div>
            <div class="row">
              <label>Mode</label>
              <select id="modeSelect">
                <option value="off">off</option>
                <option value="spectrum">spectrum</option>
                <option value="nfm">nfm</option>
                <option value="wfm">wfm</option>
                <option value="am">am</option>
                <option value="usb">usb</option>
                <option value="lsb">lsb</option>
                <option value="raw">raw</option>
              </select>
            </div>
            <div class="btn-row">
              <button id="btnApply" class="primary">Appliquer</button>
              <button id="btnPreamp">Préampli</button>
            </div>
            <div class="btn-row">
              <button data-freq="101.1">FM 101.1</button>
              <button data-freq="433.92">ISM 433</button>
              <button data-freq="868.3">ISM 868</button>
              <button data-freq="1090">ADS-B</button>
            </div>
            <div class="btn-row">
              <button id="btnReset">Reset</button>
            </div>

            <h3 style="margin-top:16px">Lecture</h3>
            <div class="readouts">
              <div class="readout">
                <div class="lbl">RSSI</div>
                <div class="val" id="rdRssi">-- dB</div>
              </div>
              <div class="readout">
                <div class="lbl">Pic</div>
                <div class="val" id="rdPeak">--</div>
              </div>
              <div class="readout">
                <div class="lbl">Fréq pic</div>
                <div class="val" id="rdPeakFreq">--</div>
              </div>
              <div class="readout">
                <div class="lbl">Bruit</div>
                <div class="val" id="rdNoise">-- dB</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.$ = (id) => this.shadowRoot.getElementById(id);

    this.$("btnApply").addEventListener("click", () => this._applySettings());
    this.$("btnPreamp").addEventListener("click", (e) => {
      const on = !e.target.classList.contains("on");
      this._callService("set_preamp", { preamp: on });
      e.target.classList.toggle("on", on);
    });
    this.$("btnReset").addEventListener("click", () => {
      this._callService("reset", {});
      this.$("freqInput").value = "100.0";
    });
    this.shadowRoot.querySelectorAll("button[data-freq]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const freq = parseFloat(btn.dataset.freq);
        this.$("freqInput").value = freq.toFixed(3);
        this._callService("set_frequency", { frequency: freq });
        this._callService("set_mode", { mode: "nfm" });
        this.$("modeSelect").value = "nfm";
      });
    });
  }

  _applySettings() {
    const freq = parseFloat(this.$("freqInput").value);
    const rate = parseFloat(this.$("rateInput").value);
    const gain = this.$("gainSelect").value;
    const mode = this.$("modeSelect").value;
    if (!isNaN(freq)) this._callService("set_frequency", { frequency: freq });
    if (!isNaN(rate)) this._callService("set_sample_rate", { sample_rate: rate });
    this._callService("set_gain", { gain });
    this._callService("set_mode", { mode });
  }

  _callService(service, data) {
    if (!this._hass) return;
    this._hass.callService("rtl_dsr", service, data);
  }

  _drawSpectrum() {
    const canvas = this.$("spectrum");
    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    ctx.strokeStyle = "rgba(255,255,255,0.05)";
    ctx.lineWidth = 1;
    for (let i = 1; i < 10; i++) {
      const x = (i / 10) * W;
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let i = 1; i < 4; i++) {
      const y = (i / 4) * H;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    const bins = this._state.bins;
    const minDb = -110;
    const maxDb = 0;
    const rangeDb = maxDb - minDb;

    ctx.beginPath();
    ctx.strokeStyle = "#4fc3f7";
    ctx.lineWidth = 2;
    for (let i = 0; i < bins.length; i++) {
      const x = (i / (bins.length - 1)) * W;
      const y = H - ((bins[i] - minDb) / rangeDb) * H;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();

    ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath();
    const grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, "rgba(79,195,247,0.35)");
    grad.addColorStop(1, "rgba(79,195,247,0)");
    ctx.fillStyle = grad;
    ctx.fill();

    if (this._state.peakFreq) {
      const span = this._state.sampleRate;
      const lo = this._state.centerFreq - span / 2;
      const hi = this._state.centerFreq + span / 2;
      const px = ((this._state.peakFreq - lo) / (hi - lo)) * W;
      ctx.strokeStyle = "#ff8a80";
      ctx.setLineDash([4, 4]);
      ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, H); ctx.stroke();
      ctx.setLineDash([]);
    }

    ctx.fillStyle = "#7a8899";
    ctx.font = "12px Consolas";
    ctx.fillText("0 dB", 8, 16);
    ctx.fillText("-55 dB", 8, H / 2);
    ctx.fillText("-110 dB", 8, H - 8);
  }

  _drawWaterfall() {
    const canvas = this.$("waterfall");
    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;

    const imageData = ctx.getImageData(0, 0, W, H - 1);
    ctx.putImageData(imageData, 0, 1);

    const bins = this._state.bins;
    const minDb = -110;
    const maxDb = 0;
    const rangeDb = maxDb - minDb;
    for (let x = 0; x < W; x++) {
      const binIdx = Math.floor((x / W) * bins.length);
      const v = (bins[binIdx] - minDb) / rangeDb;
      ctx.fillStyle = this._waterfallColor(v);
      ctx.fillRect(x, 0, 1, 1);
    }
  }

  _waterfallColor(v) {
    v = Math.max(0, Math.min(1, v));
    const r = Math.floor(255 * Math.max(0, 1.5 - Math.abs(v - 0.9) * 3));
    const g = Math.floor(255 * Math.max(0, 1.2 - Math.abs(v - 0.6) * 2.5));
    const b = Math.floor(255 * Math.max(0, 1.3 - Math.abs(v - 0.25) * 2.2));
    return `rgb(${r},${g},${b})`;
  }

  _updateReadouts() {
    const s = this._state;
    this.$("rdRssi").textContent = `${(s.rssi || -120).toFixed(1)} dB`;
    this.$("rdPeak").textContent = `${(s.peakDb || -120).toFixed(1)} dB`;
    this.$("rdPeakFreq").textContent = `${(s.peakFreq || 0).toFixed(3)} MHz`;
    this.$("rdNoise").textContent = `${(s.noiseFloor || -120).toFixed(1)} dB`;

    this.$("freqDisplay").innerHTML =
      `${(s.centerFreq || 0).toFixed(3)}<span class="unit">MHz</span>`;

    const span = s.sampleRate;
    this.$("spanLeft").textContent = `${(s.centerFreq - span / 2).toFixed(3)} MHz`;
    this.$("spanRight").textContent = `${(s.centerFreq + span / 2).toFixed(3)} MHz`;

    const sVal = ((s.rssi + 110) / 110) * 100;
    this.$("sFill").style.width = `${Math.max(0, Math.min(100, sVal))}%`;

    const badge = this.$("connBadge");
    badge.className = "badge " + (s.connected ? "ok" : "err");
    badge.textContent = s.connected ? "● connecté" : "● déconnexion";

    const mb = this.$("modeBadge");
    mb.textContent = `${s.mode} · ${s.gain}`;
  }
}

customElements.define("sdr-plus-plus-panel", SdrPlusPlusPanel);

export default SdrPlusPlusPanel;
