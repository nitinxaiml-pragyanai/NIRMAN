import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# 1. CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="NIRMAN OMNIVERSE LAB",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. CSS (IMMERSIVE LAB)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

/* DEEP LAB ENVIRONMENT */
[data-testid="stAppViewContainer"] {
    background-color: #050505;
    background-image: 
        linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    color: #00ffff;
    font-family: 'Share Tech Mono', monospace;
    overflow: hidden;
}

/* HUD PANELS */
.hud-panel {
    position: absolute; pointer-events: none;
    background: rgba(0, 10, 20, 0.85);
    border: 1px solid #005555;
    padding: 15px; border-radius: 4px;
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.1);
    z-index: 10;
}

.hud-top-left { top: 20px; left: 20px; width: 300px; }
.hud-top-right { top: 20px; right: 20px; text-align: right; }
.hud-bottom { bottom: 20px; left: 50%; transform: translateX(-50%); width: 600px; text-align: center; }

/* DIAGNOSTIC BARS */
.bar-container { width: 100%; background: #111; height: 10px; margin-top: 5px; }
.bar-fill { height: 100%; background: #00ffff; width: 0%; transition: width 0.5s; }

/* HIDE JUNK */
::-webkit-scrollbar { display: none; }
#MainMenu, footer, header { display: none !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. HUD OVERLAY
# =========================================================
st.markdown("""
<div class="hud-panel hud-top-left">
    <h3 style="margin:0; border-bottom:1px solid #00ffff;">NIRMAN LAB v5</h3>
    <div style="font-size:12px; color:#aaa; margin-top:5px;">OMNIVERSE PHYSICS ENGINE</div>
    <br>
    <div>ACTIVE PROJECT: <span id="project-name" style="color:#ffcc00">NONE</span></div>
    <div>PART COUNT: <span id="part-count">0</span></div>
</div>

<div class="hud-panel hud-top-right">
    <div>SIMULATION STATUS</div>
    <div id="sim-status" style="font-size:24px; color:#00ff00; font-weight:bold;">STANDBY</div>
</div>

<div class="hud-panel hud-bottom">
    <div id="ai-log" style="font-size:18px; color:#00ffff; text-shadow: 0 0 5px #00ffff;">
        JARVIS: "Lab Initialized. Requesting Camera Access..."
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 4. THE OMNIVERSE ENGINE (HTML/JS)
# =========================================================
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/control_utils/control_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js"></script>
    
    <style>
        body { margin: 0; background: transparent; overflow: hidden; }
        #canvas-container { width: 100vw; height: 100vh; position: relative; }
        
        /* MINI CAMERA FEED (Picture-in-Picture) */
        #cam-canvas {
            position: absolute; bottom: 20px; right: 20px;
            width: 240px; height: 180px;
            border: 2px solid #00ffff; border-radius: 10px;
            opacity: 0.7; transform: scaleX(-1);
            z-index: 5; box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
            background: #000;
        }

        #mic-btn {
            position: absolute; bottom: 220px; right: 30px;
            width: 60px; height: 60px; border-radius: 50%;
            background: rgba(0,20,40,0.9); border: 2px solid #00ffff;
            color: #00ffff; font-size: 24px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 20px rgba(0,255,255,0.3); z-index: 100;
        }
        .mic-active { background: #ff0055 !important; border-color: white !important; }
    </style>
</head>
<body>
    <div id="canvas-container">
        <canvas id="cam-canvas"></canvas> 
    </div>
    
    <div id="mic-btn" onclick="toggleVoice()">🎙️</div>

    <video id="input_video" style="display:none;" autoplay playsinline></video>

    <script>
        // --- GLOBAL VARIABLES ---
        let scene, camera, renderer, activeGroup;
        let parts = {}; 
        let isSimulating = false;

        // --- 1. INITIALIZE THREE.JS ---
        function initThree() {
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(5, 5, 10);
            camera.lookAt(0, 0, 0);

            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.domElement.style.position = 'absolute';
            renderer.domElement.style.top = '0';
            renderer.domElement.style.left = '0';
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // Lights
            const ambLight = new THREE.AmbientLight(0x404040, 2);
            scene.add(ambLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 2);
            dirLight.position.set(5, 10, 7);
            scene.add(dirLight);

            // Grid
            const grid = new THREE.GridHelper(50, 50, 0x004444, 0x001111);
            scene.add(grid);

            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            TWEEN.update();
            if (activeGroup && !isSimulating) activeGroup.rotation.y += 0.002;
            renderer.render(scene, camera);
        }

        // --- 2. CAMERA & HAND TRACKING ---
        const videoElement = document.getElementById('input_video');
        const canvasElement = document.getElementById('cam-canvas');
        const canvasCtx = canvasElement.getContext('2d');

        function onResults(results) {
            // Draw video to the mini canvas
            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
            
            if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                // Draw skeleton on mini canvas
                drawConnectors(canvasCtx, results.multiHandLandmarks[0], HAND_CONNECTIONS, {color: '#00ffff', lineWidth: 2});
                drawLandmarks(canvasCtx, results.multiHandLandmarks[0], {color: '#ff0055', lineWidth: 1});
            }
            canvasCtx.restore();
        }

        const hands = new Hands({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`});
        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });
        hands.onResults(onResults);

        // START CAMERA
        const cameraFeed = new Camera(videoElement, {
            onFrame: async () => {
                await hands.send({image: videoElement});
            },
            width: 640,
            height: 480
        });
        cameraFeed.start();

        // --- 3. FABRICATION LOGIC (Time Band Example) ---
        function spawnTimeBand() {
            if (activeGroup) scene.remove(activeGroup);
            parts = {};
            activeGroup = new THREE.Group();
            
            // Chassis
            const ring = new THREE.Mesh(
                new THREE.TorusGeometry(1.5, 0.4, 16, 50),
                new THREE.MeshStandardMaterial({ color: 0xaaaaaa, metalness: 1.0, roughness: 0.2 })
            );
            ring.rotation.x = Math.PI / 2;
            activeGroup.add(ring);

            // Core
            const core = new THREE.Mesh(
                new THREE.CylinderGeometry(0.8, 0.8, 0.5, 32),
                new THREE.MeshStandardMaterial({ color: 0x111111 })
            );
            core.rotation.x = Math.PI / 2;
            activeGroup.add(core);
            parts['core'] = core;

            scene.add(activeGroup);
            speak("Time Band Prototype Assembled.");
            updateHUD("TIME BAND", "STABLE");
        }

        // --- 4. VOICE AI ---
        function speak(text) {
            document.getElementById('ai-log').innerText = 'JARVIS: "' + text + '"';
            const u = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.speak(u);
        }

        function updateHUD(name, status) {
            document.getElementById('project-name').innerText = name;
            document.getElementById('sim-status').innerText = status;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.lang = 'en-US';
            
            recognition.onresult = (event) => {
                const cmd = event.results[event.results.length - 1][0].transcript.toLowerCase();
                if (cmd.includes('time') || cmd.includes('band')) spawnTimeBand();
                if (cmd.includes('clear')) { if(activeGroup) scene.remove(activeGroup); speak("Cleared."); }
            };
        }

        function toggleVoice() {
            const btn = document.getElementById('mic-btn');
            if (btn.classList.contains('mic-active')) {
                recognition.stop(); btn.classList.remove('mic-active');
            } else {
                recognition.start(); btn.classList.add('mic-active'); speak("Online.");
            }
        }

        // Init Everything
        initThree();
        setTimeout(() => speak("Visual systems online. Camera active."), 1500);

    </script>
</body>
</html>
"""

# IMPORTANT: Height must be high enough to see everything
components.html(html_code, height=900)
