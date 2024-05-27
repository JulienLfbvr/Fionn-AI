const socket = io(); //socketio connection to server//

const loadingBarContainer = document.getElementById('loadingBarContainer');
const loadingBar = document.getElementById('loadingBar');
const analyze_btn = document.getElementById('analyze-btn');

let form = document.getElementById('dropzone-form');

let M_filter = document.getElementById('M');
let E_filter = document.getElementById('E');
let S_filter = document.getElementById('S');
let C_filter = document.getElementById('C');

form.addEventListener('submit', function(event) {
    event.preventDefault();

    // Set the cursor to loading
    document.body.style.cursor = 'wait';

    let formData = new FormData();
    let fileField = document.querySelector('input[type="file"]');

    let filterData = {
        "M_filter" : M_filter.checked,
        "E_filter" : E_filter.checked,
        "S_filter" : S_filter.checked,
        "C_filter" : C_filter.checked
    }

    formData.append('file', fileField.files[0]);
    formData.append('filter', JSON.stringify(filterData))

    

    loadingBarContainer.classList.remove('hidden'); // Show loading bar container
    loadingBar.style.transition = 'width 0.2s'; // Add transition effect
    analyze_btn.classList.add('hidden'); // Hide analyze button
    loadingBar.style.width = '0%'; // Reset width

    let progress = 0;
    const interval = setInterval(() => {
        progress += 1; // Increment progress more slowly
        loadingBar.style.width = `${progress}%`;

        if (progress >= 85) {
            clearInterval(interval);
        }
    }, 150); // Adjust speed for a more gradual progress

    fetch('/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        clearInterval(interval);
        loadingBar.style.width = '100%';
        // Redirect to /waiting after 3 seconds
        setTimeout(() => {
            window.location.href = '/waiting';
        }, 3000);

    })
    .catch(error => console.error('Error:', error));
});