// Real-Time Classroom Monitoring Frontend Script

document.addEventListener('DOMContentLoaded', () => {
    const btnStart = document.getElementById('btnStartMonitoring');
    const btnStop = document.getElementById('btnStopMonitoring');
    const selectSource = document.getElementById('selectVideoSource');
    const imgStream = document.getElementById('liveVideoStream');

    const cardDetected = document.getElementById('statDetectedCount');
    const cardRecognized = document.getElementById('statRecognizedCount');
    const cardAttentive = document.getElementById('statAttentiveCount');
    const cardInattentive = document.getElementById('statInattentiveCount');
    const studentListContainer = document.getElementById('liveStudentsList');

    let isMonitoringActive = true;
    let pollInterval = null;

    function updateStats() {
        if (!isMonitoringActive) return;

        fetch('/api/monitoring_stats')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    const stats = data.stats;
                    
                    if (cardDetected) cardDetected.innerText = stats.total_detected;
                    if (cardRecognized) cardRecognized.innerText = stats.recognized_count;
                    if (cardAttentive) cardAttentive.innerText = stats.attentive_count;
                    if (cardInattentive) cardInattentive.innerText = stats.inattentive_count;

                    // Update live student cards feed
                    if (studentListContainer) {
                        if (stats.students_data.length === 0) {
                            studentListContainer.innerHTML = `
                                <div class="text-center py-4 text-muted">
                                    <i class="fas fa-eye-slash fa-2x mb-2 opacity-50"></i>
                                    <p class="mb-0">No faces detected in current frame.</p>
                                </div>`;
                        } else {
                            studentListContainer.innerHTML = stats.students_data.map(s => {
                                let badgeClass = s.category === 'Attentive' ? 'badge-attentive' :
                                                (s.category === 'Partially Attentive' ? 'badge-partially' : 'badge-inattentive');
                                return `
                                    <div class="d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-dark border border-secondary">
                                        <div class="d-flex align-items-center gap-2">
                                            <div class="avatar-placeholder">${s.name.charAt(0)}</div>
                                            <div>
                                                <div class="fw-bold text-white small">${s.name} (${s.student_id})</div>
                                                <div class="text-muted text-xs" style="font-size:0.75rem;">
                                                    Eye: ${s.eye_status} | Pose: ${s.head_pose}
                                                </div>
                                            </div>
                                        </div>
                                        <div class="text-end">
                                            <span class="badge ${badgeClass}">${s.attention_score}%</span>
                                            <div class="text-xs text-muted" style="font-size:0.7rem;">${s.category}</div>
                                        </div>
                                    </div>
                                `;
                            }).join('');
                        }
                    }
                }
            })
            .catch(err => console.error("Stats Polling Error:", err));
    }

    // Toggle Monitoring
    if (btnStart) {
        btnStart.addEventListener('click', () => {
            fetch('/api/monitoring/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'start' })
            }).then(() => {
                isMonitoringActive = true;
                if (imgStream) imgStream.src = '/video_feed?' + new Date().getTime();
                btnStart.classList.add('d-none');
                if (btnStop) btnStop.classList.remove('d-none');
            });
        });
    }

    if (btnStop) {
        btnStop.addEventListener('click', () => {
            fetch('/api/monitoring/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'stop' })
            }).then(() => {
                isMonitoringActive = false;
                if (imgStream) imgStream.src = '';
                btnStop.classList.add('d-none');
                if (btnStart) btnStart.classList.remove('d-none');
            });
        });
    }

    // Source Selector
    if (selectSource) {
        selectSource.addEventListener('change', (e) => {
            const source = e.target.value;
            fetch('/api/monitoring/set_source', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source: source })
            }).then(() => {
                if (imgStream) imgStream.src = '/video_feed?' + new Date().getTime();
            });
        });
    }

    // Start polling stats every 1 second
    pollInterval = setInterval(updateStats, 1000);
});
