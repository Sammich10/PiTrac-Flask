/**
 * @brief Functions to control the PiTrac system from the control panel interface.
 * Includes connecting to PiTrac, getting status, and changing operational mode.
 */

// Globals
let CONNECTED = false;

/**
 * @brief Sends a request to the backend to connect to the PiTrac system.
 */
function connectPiTrac() {
    // Disable the connect button to prevent multiple connection attempts
    button = document.getElementById('connect-button');
    button.disabled = true;
    button.innerText = 'Connecting...';
    fetch('/api/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                button.innerText = 'Connected';
                button.disabled = false;
                button.style.backgroundColor = 'green';
                CONNECTED = true;
                console.log('PiTrac connected successfully');
            } else {
                // Re-enable the connect button if connection failed
                CONNECTED = false;
                button.disabled = false;
                button.innerText = 'Connect to PiTrac';
                button.style.backgroundColor = '';
                console.log('Failed to connect to PiTrac');
            }
        })
        .catch(error => {
            // Connection failed due to an error
            CONNECTED = false;
            button.disabled = false;
            button.innerText = 'Connect to PiTrac';
            button.style.backgroundColor = '';
            console.log('Error connecting to PiTrac: ' + error);
        });
}

/**
 * @brief Sends a request to the backend to get the current status of the PiTrac system.
 */
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

/**
 * @brief Sends a command to the backend to change the operational mode of the PiTrac system.
 */
function changeMode() {
    const selected_mode = document.getElementById("mode-select").value;
    button = document.getElementById('connect-button');
    button.disabled = true;
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "commandID" : "SetMode", "action": selected_mode })
    })
        .then(response => response.json())
        .then(data => {
            // document.getElementById('result').innerText = data.message;
            button.disabled = false;
        })
        .catch(error => {
            // document.getElementById('result').innerText = 'Error: ' + error;
            button.disabled = false;
        });
}

// TODO: On load, current status of connection should be checked in the backend and the panel should
// be loaded accordingly. Currently no implementation of persistent backend status exists.
window.addEventListener('load', () => {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            if (data.connected) {
                CONNECTED = true;
                const button = document.getElementById('connect-button');
                button.innerText = 'Connected';
                button.disabled = false;
                button.style.backgroundColor = 'green';
            } else {
                CONNECTED = false;
                const button = document.getElementById('connect-button');
                button.innerText = 'Connect to PiTrac';
                button.disabled = false;
                button.style.backgroundColor = '';
            }
        });
});
