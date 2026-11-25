
const actionLabels = JSON.parse(
    document.getElementById("action-labels").textContent
);

const actionValues = JSON.parse(
    document.getElementById("action-values").textContent
);

const statusLabels = JSON.parse(
    document.getElementById("status-labels").textContent
);

const statusValues = JSON.parse(
    document.getElementById("status-values").textContent
);


// 동작별 인식 건수 막대그래프
new Chart(document.getElementById("action-chart"), {
    type: "bar",

    data: {
        labels: actionLabels,

        datasets: [{
            label: "인식 건수",
            data: actionValues,
            backgroundColor: "#3563ad"
        }]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        scales: {
            y: {
                beginAtZero: true,

                ticks: {
                    precision: 0
                }
            }
        }
    }
});


// 분석 상태별 도넛그래프
new Chart(document.getElementById("status-chart"), {
    type: "doughnut",

    data: {
        labels: statusLabels,

        datasets: [{
            data: statusValues,

            backgroundColor: [
                "#94a3b8",
                "#3b82f6",
                "#16a34a",
                "#dc2626"
            ]
        }]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        plugins: {
            legend: {
                position: "bottom"
            }
        }
    }
});
