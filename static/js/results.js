let hist_data = null;

fetch('/hist')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        hist_data = data.hist;
        createHist();

    });

function createHist() {
    let total = hist_data['total']

    let ctx = document.getElementById('histogram').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['M', 'E', 'S', 'C'], // The labels for your values
            datasets: [{
                label: 'Positive',
                data: [hist_data['M'], hist_data['E'], hist_data['S'], hist_data['C']], // Example positive data for M, E, S, C
                backgroundColor: 'rgb(20, 184, 166, .9)',
            }, {
                label: 'Negative',
                data: [total - hist_data['M'], total - hist_data['E'], total - hist_data['S'], total - hist_data['C']], // Example positive data for M, E, S, C
                backgroundColor: 'rgba(4, 47, 46, .9)',
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true // Ensures that the y-axis starts at 0
                }
            }
        }
    });
}