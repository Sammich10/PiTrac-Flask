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
    // img1.style.display = 'none';
    img2.src = '';
    // img2.style.display = 'none';
    
    // Clear metadata
    document.getElementById('frame_counter_0').innerText = '-';
    document.getElementById('fps_0').innerText = '-';
    document.getElementById('frame_counter_1').innerText = '-';
    document.getElementById('fps_1').innerText = '-';
    
    streamActive = false;
}

function captureCalibrationFrame(camera) {
    const command = "CaptureFrame";
    sendCalibrationCommand(command, camera, (data) => {
        // document.getElementById('commandResult').innerText = data.message;
    });
}

function acceptCalibrationFrame(camera) {
    const command = "AcceptFrame";
    sendCalibrationCommand(command, camera, (data) => {
        // document.getElementById('commandResult').innerText = data.message;
    });
}

function rejectCalibrationFrame(camera) {
    const command = "RejectFrame";
    sendCalibrationCommand(command, camera, (data) => {
        // document.getElementById('commandResult').innerText = data.message;
    });
}

function runDistortionCalibration(camera) {
    const command = "PerformDistortionCalibration";
    sendCalibrationCommand(command, camera, (data) => {
        // document.getElementById('commandResult').innerText = data.message;
    });
}

function saveCalibration(camera) {
    const command = "SaveDistortionCalibration";
    sendCalibrationCommand(command, camera, (data) => {
        // document.getElementById('commandResult').innerText = data.message;
    });
}

function sendCalibrationCommand(action, camera, responseHandler) {
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "commandID": "Calibrate", "action": action, "camera": camera})
    })
        .then(response => response.json())
        .then(data => {
            if (responseHandler) {
                responseHandler(data);
            }
        });
}
