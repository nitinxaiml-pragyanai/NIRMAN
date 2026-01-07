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
# 2. INDUSTRIAL STARK CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&display=swap');

/* GLOBAL RESET */
[data-testid="stAppViewContainer"] {
    background-color: #000;
    margin: 0; padding: 0;
    overflow: hidden;
    color: #00ffff;
    font-family: 'Chakra Petch', sans-serif;
}

/* HUD LAYOUT */
.hud-container {
    position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none; z-index: 10;
}

.hud-panel {
    background: rgba(0, 15, 30, 0.9);
    border: 1px solid #005555;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
    padding: 15px; border-radius: 4px; pointer-events: auto;
}

.top-left { position: absolute; top: 20px; left: 20px; width: 320px; }
.top-right { position: absolute; top: 20px; right: 20px; text-align: right; }
.bottom-center { 
    position: absolute; bottom: 30px; left: 50%; 
    transform: translateX(-50%); width: 600px; text-align: center;
    background: transparent; border: none; box-shadow: none;
}

/* TEXT STYLES */
h1 { font-size: 24px; margin: 0; color: #fff; text-transform: uppercase; letter-spacing: 2px; }
.sub { font-size: 12px; color: #0088ff; }
.val { color: #ffcc00; font-weight: bold; }

/* LOADING SCREEN */
#loader-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: #000; z-index: 9999;
    display: flex; align-items: center; justify-content: center;
    flex-direction: column;
}
.spinner {
    width: 50px; height: 50px;
    border: 3px solid rgba(0,255,255,0.3);
    border-radius: 50%; border-top-color: #00ffff;
    animation: spin 1s ease-in-out infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* HIDE STREAMLIT ELEMENTS */
#MainMenu, header, footer { display: none !important; }
::-webkit-scrollbar { display: none; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. STATIC HTML UI
# =========================================================
st.markdown("""
<div id="loader-overlay">
    <div class="spinner"></div>
    <br>
    <div style="color:#00ffff; letter-spacing:2px;">INITIALIZING OMNIVERSE PROTOCOLS...</div>
</div>

<div class="hud-container">
    <div class="hud-panel top-left">
        <h1>NIRMAN LAB <span style="font-size:12px; color:#00ffff;">v6.0</span></h1>
        <div class="sub">INDUSTRIAL PROTOTYPING ENGINE</div>
        <hr style="border-color:#005555; opacity:0.5;">
        <div>PROJECT: <span class="val" id="ui-project">STANDBY</span></div>
        <div>STATUS: <span class="val" id="ui-status" style="color:#00ff00">ONLINE</span></div>
        <div>INTEGRITY: <span class="val" id="ui-integrity">100%</span></div>
    </div>
    
    <div class="hud-panel top-right">
        <div>SIMULATION DIAGNOSTICS</div>
        <div id="ui-sim-state" style="font-size:28px; font-weight:bold; color:#333;">IDLE</div>
        <div style="font-size:10px; color:#666;">THERMAL LOAD</div>
        <div style="width:100%; height:5px; background:#111; margin-top:5px;">
            <div id="ui-thermal" style="width:0%; height:100%; background:#ff0055; transition: width 0.2s;"></div>
        </div>
    </div>
    
    <div class="hud-panel bottom-center">
        <div id="ui-log" style="font-size:20px; color:#00ffff; text-shadow: 0 0 10px #00ffff;">
            JARVIS: "Systems nominal. Awaiting input."
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 4. THE CORE ENGINE (JS)
# =========================================================
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/control_utils/control_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js"></script>

    <style>
        body { margin: 0; background: transparent; overflow: hidden; }
        #render-target { width: 100vw; height: 100vh; position: absolute; top:0; left:0; z-index:0; }
        
        #pip-cam {
            position: absolute; bottom: 20px; right: 20px;
            width: 200px; height: 150px;
            border: 2px solid #005555; background: #000;
            border-radius: 8px; z-index: 50;
            transform: scaleX(-1); /* Mirror effect */
            opacity: 0.8;
        }

        #mic-trigger {
            position: absolute; bottom: 180px; right: 85px;
            width: 60px; height: 60px; border-radius: 50%;
            background: rgba(0,20,40,0.9); border: 2px solid #00ffff;
            color: #00ffff; font-size: 24px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 15px rgba(0,255,255,0.2); z-index: 100;
            transition: 0.3s;
        }
        .mic-on { background: #ff0055 !important; border-color: #fff !important; box-shadow: 0 0 30px #ff0055 !important; }
        
        #error-msg {
            display: none; position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(50,0,0,0.9); color: white; padding: 20px;
            border: 2px solid red; z-index: 99999; text-align: center;
        }
    </style>
</head>
<body>

    <div id="render-target"></div>
    <canvas id="pip-cam"></canvas>
    <div id="mic-trigger" onclick="toggleMic()">🎙️</div>
    <div id="error-msg">
        <h3>CAMERA ACCESS DENIED</h3>
        <p>Please allow camera permissions in your browser settings and refresh.</p>
    </div>
    
    <video id="source-video" style="display:none;" autoplay playsinline></video>

    <script>
        // --- SYSTEM GLOBALS ---
        let scene, camera, renderer;
        let activePrototype = null;
        let partsRegistry = {};
        let isSimulationRunning = false;
        
        // --- 1. INITIALIZATION SEQUENCE ---
        async function bootSystem() {
            try {
                initThreeJS();
                await initMediaPipe();
                // Remove Loader from Parent
                window.parent.document.getElementById('loader-overlay').style.display = 'none';
                speak("System Online. Camera Active.");
            } catch (e) {
                console.error("Boot Failed", e);
                document.getElementById('error-msg').style.display = 'block';
            }
        }

        // --- 2. THREE.JS ENGINE ---
        function initThreeJS() {
            const container = document.getElementById('render-target');
            
            scene = new THREE.Scene();
            // Fog for depth
            scene.fog = new THREE.FogExp2(0x000000, 0.03);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 2, 8);
            
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            // Lighting Setup
            const amb = new THREE.AmbientLight(0x404040, 2);
            scene.add(amb);
            
            const key = new THREE.DirectionalLight(0x00ffff, 1);
            key.position.set(5, 10, 5);
            scene.add(key);

            const rim = new THREE.SpotLight(0xff0055, 2);
            rim.position.set(-5, 5, -5);
            scene.add(rim);

            // Floor Grid
            const grid = new THREE.GridHelper(50, 50, 0x003333, 0x001111);
            scene.add(grid);

            // Resize Handler
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });

            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            TWEEN.update();
            
            // Idle Rotation
            if (activePrototype && !isSimulationRunning) {
                activePrototype.rotation.y += 0.002;
            }
            
            renderer.render(scene, camera);
        }

        // --- 3. PROTOTYPE FABRICATION ---
        function spawnPrototype(type) {
            // Clean Workspace
            if (activePrototype) scene.remove(activePrototype);
            partsRegistry = {};
            activePrototype = new THREE.Group();

            if (type === 'time_band') {
                // Procedural Time Band
                const casing = new THREE.Mesh(
                    new THREE.TorusGeometry(1.2, 0.3, 16, 100),
                    new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.9, roughness: 0.1 })
                );
                casing.rotation.x = Math.PI/2;
                activePrototype.add(casing);

                const core = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.5, 0.5, 0.2, 32),
                    new THREE.MeshStandardMaterial({ color: 0x111111, emissive: 0x00ffff, emissiveIntensity: 0.2 })
                );
                core.rotation.x = Math.PI/2;
                activePrototype.add(core);
                partsRegistry['core'] = core;

                const holograph = new THREE.Mesh(
                    new THREE.RingGeometry(0.6, 1.4, 32),
                    new THREE.MeshBasicMaterial({ color: 0x00ffff, side: THREE.DoubleSide, transparent: true, opacity: 0.2 })
                );
                holograph.rotation.x = Math.PI/2;
                activePrototype.add(holograph);

                updateUI("TIME BAND PROTO", "STABLE");
                speak("Time Band schematic loaded.");

            } else if (type === 'helmet') {
                // Iron Man Helmet
                const dome = new THREE.Mesh(
                    new THREE.SphereGeometry(1.2, 32, 32),
                    new THREE.MeshStandardMaterial({ color: 0xaa0000, metalness: 0.7, roughness: 0.3 })
                );
                activePrototype.add(dome);

                const faceplate = new THREE.Mesh(
                    new THREE.BoxGeometry(1.4, 1.8, 0.5),
                    new THREE.MeshStandardMaterial({ color: 0xffcc00, metalness: 1.0, roughness: 0.1 })
                );
                faceplate.position.set(0, -0.2, 1.1);
                
                // Pivot Logic
                const pivot = new THREE.Group();
                pivot.add(faceplate);
                pivot.position.set(0, 1, 0); // Hinge point
                faceplate.position.y = -1.2; // Offset
                
                activePrototype.add(pivot);
                partsRegistry['faceplate'] = pivot;

                updateUI("MARK VII HELMET", "LOCKED");
                speak("Helmet fabrication complete.");
            }

            scene.add(activePrototype);
        }

        // --- 4. MECHANICS & SIMULATION ---
        function toggleMechanism(part, action) {
            const obj = partsRegistry[part];
            if (!obj) return;

            const targetRot = (action === 'open') ? -Math.PI/2.5 : 0;
            new TWEEN.Tween(obj.rotation)
                .to({ x: targetRot }, 800)
                .easing(TWEEN.Easing.Quadratic.Out)
                .start();
            
            speak(action === 'open' ? "Disengaging mechanism." : "Mechanism secured.");
        }

        function runSafetyCheck() {
            if (!activePrototype) return speak("No active build to test.");
            
            isSimulationRunning = true;
            updateUI(null, "TESTING...");
            speak("Running thermal stress test...");

            let stress = 0;
            const interval = setInterval(() => {
                stress += 2;
                updateThermal(stress);
                
                // Visual Warning
                activePrototype.traverse(c => {
                    if (c.isMesh && c.material.emissive) {
                        c.material.emissive.setHex(0xff0000);
                        c.material.emissiveIntensity = stress / 50;
                    }
                });

                if (stress >= 100) {
                    clearInterval(interval);
                    isSimulationRunning = false;
                    const passed = Math.random() > 0.2;
                    
                    if(passed) {
                        updateUI(null, "PASSED");
                        speak("Test Passed. Structural integrity at 100%.");
                        updateThermal(0);
                         activePrototype.traverse(c => { if(c.isMesh && c.material.emissive) c.material.emissive.setHex(0x00ffff); });
                    } else {
                        updateUI(null, "FAILURE");
                        speak("Critical failure detected in power coupling.");
                    }
                }
            }, 50);
        }

        // --- 5. UI BRIDGE ---
        function updateUI(proj, status) {
            if (proj) window.parent.document.getElementById('ui-project').innerText = proj;
            if (status) window.parent.document.getElementById('ui-status').innerText = status;
            if (status === 'FAILURE') window.parent.document.getElementById('ui-status').style.color = 'red';
            else window.parent.document.getElementById('ui-status').style.color = '#00ff00';
        }

        function updateThermal(val) {
            window.parent.document.getElementById('ui-thermal').style.width = val + "%";
            window.parent.document.getElementById('ui-sim-state').innerText = val + "% LOAD";
        }

        function updateLog(txt) {
            window.parent.document.getElementById('ui-log').innerText = 'JARVIS: "' + txt + '"';
        }

        function speak(text) {
            updateLog(text);
            const u = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.speak(u);
        }

        // --- 6. VISION & VOICE ---
        async function initMediaPipe() {
            const video = document.getElementById('source-video');
            const pipCanvas = document.getElementById('pip-cam');
            const ctx = pipCanvas.getContext('2d');

            const hands = new Hands({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`});
            hands.setOptions({
                maxNumHands: 1,
                modelComplexity: 0, // Fast
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            hands.onResults(results => {
                ctx.save();
                ctx.clearRect(0, 0, pipCanvas.width, pipCanvas.height);
                ctx.drawImage(results.image, 0, 0, pipCanvas.width, pipCanvas.height);
                if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                    drawConnectors(ctx, results.multiHandLandmarks[0], HAND_CONNECTIONS, {color: '#00ffff', lineWidth: 2});
                }
                ctx.restore();
            });

            const camera = new Camera(video, {
                onFrame: async () => { await hands.send({image: video}); },
                width: 320, height: 240
            });
            await camera.start();
        }

        // VOICE RECOGNITION
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.lang = 'en-US';
            
            recognition.onresult = (e) => {
                const cmd = e.results[e.results.length - 1][0].transcript.toLowerCase();
                
                if (cmd.includes('time') || cmd.includes('band')) spawnPrototype('time_band');
                if (cmd.includes('helmet') || cmd.includes('suit')) spawnPrototype('helmet');
                
                if (cmd.includes('open')) toggleMechanism('faceplate', 'open');
                if (cmd.includes('close')) toggleMechanism('faceplate', 'close');
                
                if (cmd.includes('test') || cmd.includes('diagnostic')) runSafetyCheck();
                
                if (cmd.includes('clear')) {
                     if(activePrototype) scene.remove(activePrototype);
                     speak("Workspace cleared.");
                }
            };
        }

        function toggleMic() {
            const btn = document.getElementById('mic-trigger');
            if (btn.classList.contains('mic-on')) {
                recognition.stop(); btn.classList.remove('mic-on');
            } else {
                recognition.start(); btn.classList.add('mic-on'); speak("Listening.");
            }
        }

        // START
        bootSystem();

    </script>
</body>
</html>
"""

components.html(html_code, height=900)
