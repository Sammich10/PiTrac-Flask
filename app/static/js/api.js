let streamActive = false;
let panelExpanded = false;

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
    
    console.log('Starting dual camera streams...');
    const timestamp = new Date().getTime();
    
    // Camera 0 stream
    img1.src = '/stream/camera0?' + timestamp;
    img1.style.display = 'block';
    
    // Camera 1 stream  
    img2.src = '/stream/camera1?' + timestamp;
    img2.style.display = 'block';
    
    status.innerText = 'Connecting to streams...';
    
    // Track when both streams are loaded
    let loadedStreams = 0;
    const streamLoaded = () => {
        loadedStreams++;
        if (loadedStreams === 2) {
            console.log('Both streams loaded successfully');
            status.innerText = 'Dual streams connected';
            streamActive = true;
        }
    };
    
    img1.onload = streamLoaded;
    img2.onload = streamLoaded;
    
    img1.onerror = function() {
        console.error('Camera 0 stream connection failed');
        status.innerText = 'Camera 0 stream failed';
    };
    
    img2.onerror = function() {
        console.error('Camera 1 stream connection failed');
        status.innerText = 'Camera 1 stream failed';
    };
}

function stopStream() {
    const img1 = document.getElementById('display_1');
    const img2 = document.getElementById('display_2');
    const status = document.getElementById('streamStatus');
    
    console.log('Stopping dual camera streams...');
    img1.src = '';
    img1.style.display = 'none';
    img2.src = '';
    img2.style.display = 'none';
    
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