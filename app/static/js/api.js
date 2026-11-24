
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
};