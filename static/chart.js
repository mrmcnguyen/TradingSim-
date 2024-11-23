// static/path/to/your_chart_script.js
document.addEventListener('DOMContentLoaded', function () {
    // Fetch your data or define it here
    const labels = ["January", "Feburary", "March", "April", "May", "June", "July"];
    var data = {
        labels: labels,
        datasets: [{
            fill: true,
            label: "Portfolio value",
            data: [65, 59, 80, 81, 56, 55, 40],
            borderColor: '#0070f3',
            borderWidth: 2,
            tension: 0.1,
        }]
     };


    // Chart configuration
    var ctx = document.getElementById('myChart').getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgb(58, 144, 243, 1)'); // Starting color: #0070f3
    gradient.addColorStop(1, 'rgb(162, 199, 241, 0)'); // Ending color: transparent


    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                backgroundColor: gradient,
                fill: true,
                label: "Portfolio value",
                data: [65, 59, 80, 81, 56, 55, 40],
                borderColor: '#0070f3',
                borderWidth: 2,
                tension: 0.1,
            }]
          },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});



