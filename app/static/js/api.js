let streamActive = false;
let panelExpanded = false;
let sseCamera0 = null;
let sseCamera1 = null;

function startStream() {
    const img1 = document.getElementById('display_1');
    const img2 = document.getElementById('display_2');
    const status1 = document.getElementById('camera0Title');
    const status2 = document.getElementById('camera1Title');
    
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
                    document.getElementById('exposure_0').innerText = `${parseFloat(data.metadata.exposure || 0).toFixed(4)} s`;
                    document.getElementById('fov_0').innerText = `${parseFloat(data.metadata.fov_scale || 0).toFixed(2)}°`;
                    document.getElementById('gain_0').innerText = `${parseFloat(data.metadata.gain || 0).toFixed(2)} dB`;
                }
            }
        } catch (e) {
            console.error('Error parsing SSE data for Camera 0:', e);
        }
    };
    
    sseCamera0.onerror = function(event) {
        console.error('Camera 0 SSE connection error');
        status1.innerText = 'Camera 0 connection failed';
    };
    status1.innerText = 'Camera 0 stream connected';
    
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
                    document.getElementById('exposure_1').innerText = `${parseFloat(data.metadata.exposure || 0).toFixed(4)} s`;
                    document.getElementById('fov_1').innerText = `${parseFloat(data.metadata.fov_scale || 0).toFixed(2)}°`;
                    document.getElementById('gain_1').innerText = `${parseFloat(data.metadata.gain || 0).toFixed(2)} dB`;
                }
            }
        } catch (e) {
            console.error('Error parsing SSE data for Camera 1:', e);
        }
    };
    
    sseCamera1.onerror = function(event) {
        console.error('Camera 1 SSE connection error');
        status2.innerText = 'Camera 1 connection failed';
    };
    
    status2.innerText = 'Camera 1 stream connected';

    streamActive = true;
}

function stopStream() {
    const img1 = document.getElementById('display_1');
    const img2 = document.getElementById('display_2');
    
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

function captureCalibrationFrame(camera) {
    const command_id = "calibrate";
    const command = "capture_image";
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ camera_id: camera, command_id: command_id, "action": command})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('commandResult').innerText = data.message;
        });
}

function acceptCalibrationFrame(camera) {
    const command_id = "calibrate";
    const command = "accept_image";
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ camera_id: camera, command_id: command_id, "action": command})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('commandResult').innerText = data.message;
        });
}

function rejectCalibrationFrame(camera) {
    const command_id = "calibrate";
    const command = "reject_image";
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ camera_id: camera, command_id: command_id, "action": command})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('commandResult').innerText = data.message;
        });
}

function runDistortionCalibration(camera) {
    const command_id = "calibrate";
    const command = "do_distortion_cal";
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ camera_id: camera, command_id: command_id, "action": command})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('commandResult').innerText = data.message;
        });
}

function saveCalibration(camera) {
    const command_id = "calibrate";
    const command = "save_calibration";
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ camera_id: camera, command_id: command_id, "action": command})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('commandResult').innerText = data.message;
        });
}

/**
 * @brief Sends a command to the backend to toggle distortion correction for the specified camera.
 * 
 * @param {string} camera The camera identifier ('0' or '1') for which to toggle distortion correction
 */
function toggleDistortionCorrection(camera) {
    const checkbox = (camera == '0') ? document.getElementById('distortionCheckbox0') : document.getElementById('distortionCheckbox1');
    const enabled = checkbox.checked;
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command_id: "configure", "apply_calibrations": enabled,  camera_id: camera})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('distortionResult').innerText = data.message;
        });
}

function toggleLiveDetection(camera) {
    const checkbox = (camera == '0') ? document.getElementById('liveDetectionCheckbox0') : document.getElementById('liveDetectionCheckbox1');
    const enabled = checkbox.checked;
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command_id: "configure", "enable_live_detection": enabled,  camera_id: camera})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('liveDetectionResult').innerText = data.message;
        });
}

function updateExposureValue(camera) {
    // Update the display text for the slider value
    const labelId = camera === '0' ? 'exposure_0' : 'exposure_1';
    const inputId = camera === '0' ? 'exposureSet0' : 'exposureSet1';
    const level = parseFloat(document.getElementById(inputId).value);
    const el = document.getElementById(labelId)
    // Update the text next to the slider to show the current value
    //el.innerText = `${level.toFixed(3)}s`;
}

function updateFOVValue(camera) {
    // Update the display text for the slider value
    const labelId = camera === '0' ? 'fov_0' : 'fov_1';
    const inputId = camera === '0' ? 'fovSet0' : 'fovSet1';
    const level = parseFloat(document.getElementById(inputId).value);
    const el = document.getElementById(labelId)
    // Update the text next to the slider to show the current value
    //el.innerText = `${level.toFixed(2)}°`;
}

function updateGainValue(camera) {
    // Update the display text for the slider value
    const labelId = camera === '0' ? 'gain_0' : 'gain_1';
    const inputId = camera === '0' ? 'gainSet0' : 'gainSet1';
    const level = parseFloat(document.getElementById(inputId).value);
    const el = document.getElementById(labelId)
    // Update the text next to the slider to show the current value
    //el.innerText = `${level.toFixed(2)}dB`;
}

function updateCameraControls(camera) {
    const e_sliderId = camera === '0' ? 'exposureSet0' : 'exposureSet1';
    const exposure = parseFloat(document.getElementById(e_sliderId).value);
    const f_sliderId = camera === '0' ? 'fovSet0' : 'fovSet1';
    const fov = parseFloat(document.getElementById(f_sliderId).value);
    const g_sliderId = camera === '0' ? 'gainSet0' : 'gainSet1';
    const gain = parseFloat(document.getElementById(g_sliderId).value);
    const s_sliderId = camera === '0' ? 'saveConfigCheckbox0' : 'saveConfigCheckbox1';
    const save_config = document.getElementById(s_sliderId).checked;
    
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command_id: "configure", "set_exposure": exposure, "set_fov_scale": fov, "set_gain": gain, camera_id: camera, "apply_configuration": save_config})
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('distortionResult').innerText = data.message;
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

function togglePanel(event) {
    // Get the panel-header that was clicked
    const panelHeader = event.currentTarget;
    // Get the parent panel (the expandable-panel div)
    const panel = panelHeader.parentElement;
    const arrow = panelHeader.querySelector('.expand-arrow');
    
    const isCollapsed = panel.classList.contains('collapsed');
    
    if (isCollapsed) {
        // Expand panel
        panel.classList.remove('collapsed');
        panel.classList.add('expanded');
        arrow.style.transformOrigin = 'center center';
        arrow.style.transform = 'rotate(180deg)';
        
        // Special handling for viewfinder panel - start stream
        if (panel.id === 'viewfinder-panel') {
            panelExpanded = true;
            if (!streamActive) {
                startStream();
            }
        }
    } else {
        // Collapse panel
        panel.classList.remove('expanded');
        panel.classList.add('collapsed');
        arrow.style.transformOrigin = 'center center';
        arrow.style.transform = 'rotate(0deg)';
        
        // Special handling for viewfinder panel - stop stream
        if (panel.id === 'viewfinder-panel') {
            panelExpanded = false;
            if (streamActive) {
                stopStream();
            }
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
    
    // Initialize camera settings panels as collapsed
    const camera0Settings = document.getElementById('camera0Settings');
    const camera1Settings = document.getElementById('camera1Settings');
    if (camera0Settings) camera0Settings.classList.add('collapsed');
    if (camera1Settings) camera1Settings.classList.add('collapsed');
    
    // Hide video displays initially
    document.getElementById('display_1').style.display = 'none';
    document.getElementById('display_2').style.display = 'none';
};