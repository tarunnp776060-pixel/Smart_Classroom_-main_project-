// Analytics Chart.js Script

document.addEventListener('DOMContentLoaded', () => {
    const pieCtx = document.getElementById('attentionPieChart');
    const lineCtx = document.getElementById('attentionLineChart');
    const barCtx = document.getElementById('studentBarChart');

    let pieChart = null;
    let lineChart = null;
    let barChart = null;

    function renderCharts(data) {
        // 1. Doughnut Chart: Attentiveness Category Breakdown
        if (pieCtx) {
            if (pieChart) pieChart.destroy();
            pieChart = new Chart(pieCtx, {
                type: 'doughnut',
                data: {
                    labels: data.category_distribution.labels,
                    datasets: [{
                        data: data.category_distribution.data,
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderWidth: 2,
                        borderColor: '#111827'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#9ca3af', font: { family: 'Inter' } } }
                    }
                }
            });
        }

        // 2. Line Chart: Attention Timeline Trend
        if (lineCtx) {
            if (lineChart) lineChart.destroy();
            lineChart = new Chart(lineCtx, {
                type: 'line',
                data: {
                    labels: data.timeline_trend.timestamps,
                    datasets: [{
                        label: 'Average Attention Score (%)',
                        data: data.timeline_trend.scores,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.15)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { min: 0, max: 100, grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af' } },
                        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af' } }
                    },
                    plugins: {
                        legend: { labels: { color: '#9ca3af' } }
                    }
                }
            });
        }

        // 3. Bar Chart: Student-wise Comparison
        if (barCtx) {
            if (barChart) barChart.destroy();
            barChart = new Chart(barCtx, {
                type: 'bar',
                data: {
                    labels: data.student_comparison.names,
                    datasets: [{
                        label: 'Attention Score (%)',
                        data: data.student_comparison.scores,
                        backgroundColor: 'rgba(139, 92, 246, 0.7)',
                        borderColor: '#8b5cf6',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { min: 0, max: 100, grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af' } },
                        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af' } }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    }

    function fetchAnalyticsData() {
        const sessionFilter = document.getElementById('filterSession')?.value || '';
        const studentFilter = document.getElementById('filterStudent')?.value || '';

        fetch(`/api/analytics/charts_data?session_id=${sessionFilter}&student_id=${studentFilter}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    renderCharts(data);
                }
            })
            .catch(err => console.error("Analytics fetch error:", err));
    }

    // Initial load
    fetchAnalyticsData();

    // Filter event listeners
    const sessionFilter = document.getElementById('filterSession');
    const studentFilter = document.getElementById('filterStudent');
    if (sessionFilter) sessionFilter.addEventListener('change', fetchAnalyticsData);
    if (studentFilter) studentFilter.addEventListener('change', fetchAnalyticsData);
});
