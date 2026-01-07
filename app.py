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
# 2. STARK LAB INTERFACE CSS
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
}

.hud-top-left { top: 20px; left: 20px; width: 300px; }
.hud-top-right { top: 20px; right: 20px; text-align: right; }
.hud-bottom { bottom: 20px; left: 50%; transform: translateX(-50%); width: 600px; text-align: center; }

/* DIAGNOSTIC BARS */
.bar-container { width: 100%; background: #111; height: 10px; margin-top: 5px; }
.bar-fill { height: 100%; background: #00ffff; width: 0%; transition: width 0.5s; }
.critical { background: #ff0055 !important; box-shadow: 0 0 10px #ff0000; }

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
    <div>INTEGRITY: <span id="integrity-val">100%</span></div>
    <div class="bar-container"><div id="integrity-bar" class="bar-fill" style="width:100%"></div></div>
</div>

<div class="hud-panel hud-top-right">
    <div>SIMULATION STATUS</div>
    <div id="sim-status" style="font-size:24px; color:#00ff00; font-weight:bold;">STANDBY</div>
    <br>
    <div style="font-size:12px;">THERMAL LOAD</div>
    <div class="bar-container"><div id="thermal-bar" class="bar-fill" style="width:0%; background:#ff5500;"></div></div>
</div>

<div class="hud-panel hud-bottom">
    <div id="ai-log" style="font-size:18px; color:#00ffff; text-shadow: 0 0 5px #00ffff;">
        JARVIS: "Lab Initialized. Ready for fabrication, Sir."
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 4. THE OMNIVERSE ENGINE
# =========================================================
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js"></script>
    
    <style>
        body { margin: 0; background: transparent; overflow: hidden; }
        #canvas-container { width: 100vw; height: 100vh; }
        
        #mic-btn {
            position: absolute; bottom: 100px; right: 30px;
            width: 70px; height: 70px; border-radius: 50%;
            background: rgba(0,20,40,0.9); border: 2px solid #00ffff;
            color: #00ffff; font-size: 30px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 20px rgba(0,255,255,0.3); z-index: 100;
        }
        .mic-active { background: #ff0055 !important; border-color: white !important; animation: pulse 1s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255,0,85,0.7); } 100% { box-shadow: 0 0 0 20px rgba(255,0,85,0); } }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="mic-btn" onclick="toggleVoice()">🎙️</div>

    <script>
        // --- GLOBAL VARIABLES ---
        let scene, camera, renderer, activeGroup;
        let parts = {}; // Store named parts for "Focus" mode
        let isSimulating = false;

        // --- 1. THREE.JS SETUP ---
        function init() {
            scene = new THREE.Scene();
            
            // Camera
            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(5, 5, 10);
            camera.lookAt(0, 0, 0);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // Lights
            const ambLight = new THREE.AmbientLight(0x404040, 2);
            scene.add(ambLight);
            
            const dirLight = new THREE.DirectionalLight(0xffffff, 2);
            dirLight.position.set(5, 10, 7);
            scene.add(dirLight);

            // Grid Floor
            const grid = new THREE.GridHelper(50, 50, 0x004444, 0x001111);
            scene.add(grid);

            animate();
        }

        // --- 2. COMPLEX FABRICATION ENGINE ---

        function createCircuitMaterial() {
            // Procedural tech texture placeholder
            return new THREE.MeshStandardMaterial({
                color: 0x003300, roughness: 0.3, metalness: 0.8,
                emissive: 0x00ff00, emissiveIntensity: 0.2
            });
        }

        function createWire(p1, p2, color) {
            const path = new THREE.CatmullRomCurve3([
                p1,
                new THREE.Vector3((p1.x+p2.x)/2, p1.y+2, (p1.z+p2.z)/2), // Curve up
                p2
            ]);
            const geo = new THREE.TubeGeometry(path, 20, 0.05, 8, false);
            const mat = new THREE.MeshStandardMaterial({ color: color });
            return new THREE.Mesh(geo, mat);
        }

        function spawnTimeBand() {
            clearScene();
            activeGroup = new THREE.Group();
            activeGroup.name = "TimeBand";
            
            // 1. The Main Chassis (Torus)
            const chassisGeo = new THREE.TorusGeometry(1.5, 0.4, 16, 100);
            const chassisMat = new THREE.MeshStandardMaterial({ color: 0xaaaaaa, metalness: 1.0, roughness: 0.2 });
            const chassis = new THREE.Mesh(chassisGeo, chassisMat);
            chassis.rotation.x = Math.PI / 2;
            activeGroup.add(chassis);
            parts['chassis'] = chassis;

            // 2. Quantum Core (The Center)
            const coreGeo = new THREE.CylinderGeometry(0.8, 0.8, 0.5, 32);
            const coreMat = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.8 });
            const core = new THREE.Mesh(coreGeo, coreMat);
            core.rotation.x = Math.PI / 2;
            activeGroup.add(core);
            parts['core'] = core;

            // 3. The Holographic Emitter (Glass)
            const lensGeo = new THREE.SphereGeometry(0.6, 32, 16, 0, Math.PI * 2, 0, Math.PI/2);
            const lensMat = new THREE.MeshPhysicalMaterial({ 
                color: 0x00ffff, transmission: 0.9, opacity: 1, transparent: true, roughness: 0 
            });
            const lens = new THREE.Mesh(lensGeo, lensMat);
            lens.rotation.x = -Math.PI / 2;
            lens.position.z = 0.25;
            activeGroup.add(lens);
            parts['lens'] = lens;

            // 4. Detailed Circuitry (Chips)
            for(let i=0; i<6; i++) {
                const chip = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.1, 0.4), createCircuitMaterial());
                const angle = (i / 6) * Math.PI * 2;
                chip.position.set(Math.cos(angle)*1.2, 0, Math.sin(angle)*1.2);
                chip.rotation.y = -angle;
                activeGroup.add(chip);
                
                // Add Wires connecting chips to core
                const wire = createWire(chip.position, new THREE.Vector3(0, 0.2, 0), 0xffcc00);
                activeGroup.add(wire);
            }

            scene.add(activeGroup);
            updateHUD("Time Band Prototype", 24, "STABLE");
        }

        function spawnHelmet() {
            clearScene();
            activeGroup = new THREE.Group();
            activeGroup.name = "Helmet";

            // 1. Main Dome
            const dome = new THREE.Mesh(
                new THREE.SphereGeometry(1.5, 32, 32),
                new THREE.MeshStandardMaterial({ color: 0xaa0000, metalness: 0.8, roughness: 0.2 })
            );
            activeGroup.add(dome);

            // 2. Faceplate (Moveable)
            const faceGeo = new THREE.BoxGeometry(1.6, 2, 0.5);
            const faceMat = new THREE.MeshStandardMaterial({ color: 0xffcc00, metalness: 1.0, roughness: 0.1 });
            const faceplate = new THREE.Mesh(faceGeo, faceMat);
            faceplate.position.set(0, -0.2, 1.3);
            
            // Create a Pivot Group for rotation
            const facePivot = new THREE.Group();
            facePivot.add(faceplate);
            facePivot.position.set(0, 1, 0); // Pivot at forehead
            faceplate.position.y = -1.2; // Offset back
            
            activeGroup.add(facePivot);
            parts['faceplate'] = facePivot; // Store pivot for animation

            // 3. Eyes (Glowing)
            const eyeGeo = new THREE.BoxGeometry(0.4, 0.1, 0.1);
            const eyeMat = new THREE.MeshBasicMaterial({ color: 0x00ffff });
            const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
            const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
            eyeL.position.set(-0.4, -0.2, 1.6);
            eyeR.position.set(0.4, -0.2, 1.6);
            activeGroup.add(eyeL);
            activeGroup.add(eyeR);

            scene.add(activeGroup);
            updateHUD("Mark 7 Helmet", 15, "SECURE");
        }

        // --- 3. ANIMATION & MECHANICS SYSTEM ---

        function openMechanism(partName) {
            if (partName === 'helmet' && parts['faceplate']) {
                // Tween animation for Faceplate
                new TWEEN.Tween(parts['faceplate].rotation)
                    .to({ x: -Math.PI / 2.5 }, 1000) // Rotate up
                    .easing(TWEEN.Easing.Quadratic.Out)
                    .start();
                speak("Faceplate disengaged.");
            }
        }

        function closeMechanism(partName) {
            if (partName === 'helmet' && parts['faceplate']) {
                new TWEEN.Tween(parts['faceplate].rotation)
                    .to({ x: 0 }, 1000) // Rotate down
                    .easing(TWEEN.Easing.Bounce.Out)
                    .start();
                speak("Faceplate secured. HUD Online.");
            }
        }

        function focusOn(partKey) {
            if (parts[partKey]) {
                const target = parts[partKey];
                
                // Tween Camera Position
                new TWEEN.Tween(camera.position)
                    .to({ x: target.position.x + 2, y: target.position.y + 2, z: target.position.z + 2 }, 1500)
                    .easing(TWEEN.Easing.Cubic.InOut)
                    .onUpdate(() => camera.lookAt(target.position))
                    .start();
                    
                speak("Isolating " + partKey + " for micro-work.");
            }
        }

        function resetView() {
            new TWEEN.Tween(camera.position)
                .to({ x: 5, y: 5, z: 10 }, 1500)
                .easing(TWEEN.Easing.Cubic.InOut)
                .onUpdate(() => camera.lookAt(0,0,0))
                .start();
        }

        // --- 4. SAFETY SIMULATION SYSTEM ---

        function runDiagnostics() {
            if (!activeGroup) return speak("No active prototype to test.");
            
            isSimulating = true;
            document.getElementById('sim-status').innerText = "RUNNING...";
            speak("Initiating structural integrity check...");
            
            // Simulate Load
            let load = 0;
            const interval = setInterval(() => {
                load += 5;
                document.getElementById('thermal-bar').style.width = load + "%";
                
                // Color change simulation on model
                if (activeGroup) {
                    activeGroup.traverse((c) => {
                        if (c.isMesh && c.material.emissive) {
                            c.material.emissive.setHex(0xff0000); // Turn red
                            c.material.emissiveIntensity = load / 50;
                        }
                    });
                }

                if (load >= 100) {
                    clearInterval(interval);
                    isSimulating = false;
                    
                    // Random Result
                    const success = Math.random() > 0.3;
                    if (success) {
                        document.getElementById('sim-status').innerText = "PASSED";
                        document.getElementById('sim-status').style.color = "#00ff00";
                        speak("Test Complete. All systems nominal. Prototype is safe for fabrication.");
                        // Reset color
                        activeGroup.traverse(c => { if(c.isMesh) c.material.emissive.setHex(0x000000); });
                    } else {
                        document.getElementById('sim-status').innerText = "CRITICAL FAILURE";
                        document.getElementById('sim-status').style.color = "#ff0000";
                        speak("Warning. Thermal runaway detected in core. Redesign recommended.");
                    }
                }
            }, 100);
        }


        // --- 5. UTILS ---
        function clearScene() {
            if (activeGroup) scene.remove(activeGroup);
            parts = {};
            activeGroup = null;
        }

        function updateHUD(proj, count, integrity) {
            document.getElementById('project-name').innerText = proj.toUpperCase();
            document.getElementById('part-count').innerText = count;
            document.getElementById('integrity-val').innerText = integrity;
        }

        function animate() {
            requestAnimationFrame(animate);
            TWEEN.update();
            if (activeGroup && !isSimulating) activeGroup.rotation.y += 0.002; // Idle spin
            renderer.render(scene, camera);
        }

        function speak(text) {
            window.parent.postMessage({type: 'log', message: 'JARVIS: ' + text}, '*');
            document.getElementById('ai-log').innerText = 'JARVIS: "' + text + '"';
            const u = new SpeechSynthesisUtterance(text);
            u.pitch = 0.9; u.rate = 1.1;
            window.speechSynthesis.speak(u);
        }

        // --- 6. VOICE CONTROL ---
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const cmd = event.results[event.results.length - 1][0].transcript.toLowerCase();
                
                // Creation
                if (cmd.includes('time') || cmd.includes('band')) spawnTimeBand();
                if (cmd.includes('helmet') || cmd.includes('mask')) spawnHelmet();
                
                // Mechanics
                if (cmd.includes('open') && cmd.includes('helmet')) openMechanism('helmet');
                if (cmd.includes('close') && cmd.includes('helmet')) closeMechanism('helmet');
                
                // Focus
                if (cmd.includes('focus') && cmd.includes('lens')) focusOn('lens');
                if (cmd.includes('focus') && cmd.includes('core')) focusOn('core');
                if (cmd.includes('reset view') || cmd.includes('zoom out')) resetView();
                
                // Simulation
                if (cmd.includes('test') || cmd.includes('diagnostic') || cmd.includes('safety')) runDiagnostics();
            };
        }

        function toggleVoice() {
            const btn = document.getElementById('mic-btn');
            if (btn.classList.contains('mic-active')) {
                recognition.stop(); btn.classList.remove('mic-active');
            } else {
                recognition.start(); btn.classList.add('mic-active');
                speak("Listening.");
            }
        }

        init();
        setTimeout(() => speak("Omniverse Lab loaded. Environment stable."), 1000);

    </script>
</body>
</html>
"""

components.html(html_code, height=900)
