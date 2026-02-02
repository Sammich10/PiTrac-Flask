let streamActive = false;
let panelExpanded = false;
let sseCamera0 = null;
let sseCamera1 = null;

function toggleViewfinderPanel() {
    const panel = document.getElementById('viewfinder-panel');
    const arrow = panel.querySelector('.expand-arrow');
    
    if (panelExpanded) {
        // Collapse panel and stop stream
        panel.classList.remove('expanded');
        panel.classList.add('collapsed');
        arrow.style.transform = 'rotate(0deg)';
        panelExpanded = false;
        
        // Stop stream when collapsing
        if (streamActive) {
            stopStream();
        }
    } else {
        // Expand panel and start stream
        panel.classList.remove('collapsed');
        panel.classList.add('expanded');
        arrow.style.transform = 'rotate(180deg)';
        panelExpanded = true;
        
        // Start stream when expanding (if connected)
        if (!streamActive) {
            startStream();
        }
    }
}

function startStream() {
    const img1 = document.getElementById('display_1');
    const img2 = document.getElementById('display_2');
    const status = document.getElementById('streamStatus');
    
    console.log('Starting SSE dual camera streams...');
    
    // Start SSE for Camera 0
    sseCamera0 = new EventSource('/stream/sse/camera0');
    sseCamera0.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.image) {
                img1.src = data.image;
                img1.style.display = 'block';
                
                // Update metadata
                if (data.metadata) {
                    document.getElementById('frame_counter_0').innerText = data.metadata.frame_number || '-';
                    document.getElementById('fps_0').innerText = (data.metadata.fps || 0).toFixed(1);
                }
            }
        } catch (e) {
            console.error('Error parsing SSE data for Camera 0:', e);
        }
    };
    
    sseCamera0.onerror = function(event) {
        console.error('Camera 0 SSE connection error');
        status.innerText = 'Camera 0 connection failed';
    };
    
    // Start SSE for Camera 1
    sseCamera1 = new EventSource('/stream/sse/camera1');
    sseCamera1.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.image) {
                img2.src = data.image;
                img2.style.display = 'block';
                
                // Update metadata
                if (data.metadata) {
                    document.getElementById('frame_counter_1').innerText = data.metadata.frame_number || '-';
                    document.getElementById('fps_1').innerText = (data.metadata.fps || 0).toFixed(1);
                }
            }
        } catch (e) {
            console.error('Error parsing SSE data for Camera 1:', e);
        }
    };
    
    sseCamera1.onerror = function(event) {
        console.error('Camera 1 SSE connection error');
        status.innerText = 'Camera 1 connection failed';
    };
    
    status.innerText = 'SSE streams connected';
    streamActive = true;
}

function stopStream() {
    const img1 = document.getElementById('display_1');
    const img2 = document.getElementById('display_2');
    const status = document.getElementById('streamStatus');
    
    console.log('Stopping SSE dual camera streams...');
    
    // Close SSE connections
    if (sseCamera0) {
        sseCamera0.close();
        sseCamera0 = null;
    }
    if (sseCamera1) {
        sseCamera1.close();
        sseCamera1 = null;
    }
    
    // Clear displays
    img1.src = '';
    img1.style.display = 'none';
    img2.src = '';
    img2.style.display = 'none';
    
    // Clear metadata
    document.getElementById('frame_counter_0').innerText = '-';
    document.getElementById('fps_0').innerText = '-';
    document.getElementById('frame_counter_1').innerText = '-';
    document.getElementById('fps_1').innerText = '-';
    
    status.innerText = 'Streams disconnected';
    streamActive = false;
}

function changeMode() {
    const selectedMode = document.getElementById("modeSelect").value;
    fetch('/api/change_mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mode: selectedMode })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').innerText = data.message;
        });
}

function sendCommand() {
    const command_id = "calibrate";
    const camera_id = document.getElementById("cameraSelect").value;
    const command = document.getElementById("commandSelect").value;
    
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ camera_id: camera_id, command_id: command_id, command: command})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('commandResult').innerText = data.message;
        });
}

function connectPiTrac() {
    fetch('/api/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('connectResult').innerText = data.message;
            if (data.success) {
                // Connection successful - no need to enable button since panel controls stream
                console.log('PiTrac connected successfully');
            }
        })
        .catch(error => {
            document.getElementById('connectResult').innerText = 'Connection failed: ' + error;
        });
}

function getStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('statusResult').innerText = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            document.getElementById('statusResult').innerText = 'Error: ' + error;
        });
}

function toggleViewfinderPanel() {
    const panel = document.getElementById('viewfinder-panel');
    const arrow = panel.querySelector('.expand-arrow');
    
    if (panelExpanded) {
        // Collapse panel and stop stream
        panel.classList.remove('expanded');
        panel.classList.add('collapsed');
        arrow.style.transform = 'rotate(0deg)';
        panelExpanded = false;
        
        // Stop stream when collapsing
        if (streamActive) {
            stopStream();
        }
    } else {
        // Expand panel and start stream
        panel.classList.remove('collapsed');
        panel.classList.add('expanded');
        arrow.style.transform = 'rotate(180deg)';
        panelExpanded = true;
        
        // Start stream when expanding (if connected)
        if (!streamActive) {
            startStream();
        }
    }
}

function getLaunchData() {
    // Placeholder for launch data functionality
    document.getElementById('launchDataResult').innerText = 'Launch data functionality not yet implemented';
}

// Initialize page
window.onload = function() {
    // Initialize panel as collapsed
    const panel = document.getElementById('viewfinder-panel');
    panel.classList.add('collapsed');
    
    // Hide video displays initially
    document.getElementById('display_1').style.display = 'none';
    document.getElementById('display_2').style.display = 'none';
};