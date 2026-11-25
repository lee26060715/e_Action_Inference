
const API_URL = "/api/analyses/";

const form = document.getElementById("analysis-form");
const startButton = document.getElementById("start-button");
const jobId = document.getElementById("job-id");
const jobStatus = document.getElementById("job-status");
const errorMessage = document.getElementById("error-message");
const predictionBody = document.getElementById("prediction-body");
const historyBody = document.getElementById("history-body");

const csrfToken = form.querySelector(
    "[name=csrfmiddlewaretoken]"
).value;

const actionNames = {
    bend_return: "허리를 굽혔다 펴기",
    leg_raise_lower: "다리 올렸다 내리기",
    walk_turn_walk: "걷고 돌아서 걷기",
    drink_return: "마시고 원위치",
    sit_stand: "앉았다 일어나기",
    wave: "손 흔들기",
    UNKNOWN: "판단 불가 (UNKNOWN)"
};


// API 요청 공통 함수
async function requestAPI(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Accept": "application/json",
            "X-CSRFToken": csrfToken,
            ...options.headers
        }
    });

    if (response.status === 204) {
        return null;
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || JSON.stringify(data)
        );
    }

    return data;
}


// 테이블 행 추가
function addRow(tbody, values) {
    const row = document.createElement("tr");

    values.forEach(value => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
    });

    tbody.appendChild(row);
}


// 빈 테이블 안내 메시지
function showEmpty(tbody, columns, message) {
    tbody.replaceChildren();

    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = columns;
    cell.textContent = message;

    row.appendChild(cell);
    tbody.appendChild(row);
}


// 분석 결과 표시
function renderPredictions(
    predictions,
    tbody = predictionBody
) {
    tbody.replaceChildren();

    if (!predictions || predictions.length === 0) {
        showEmpty(
            tbody, 4,
            "표시할 분석 결과가 없습니다."
        );
        return;
    }

    predictions.forEach(prediction => {
        addRow(tbody, [
            prediction.track_id,
            actionNames[prediction.action_label]
                || prediction.action_label,
            (prediction.confidence * 100).toFixed(2) + "%",
            prediction.window_count
        ]);
    });
}


// 분석 기록 조회
async function loadHistory() {
    const data = await requestAPI(API_URL);

    const jobs = Array.isArray(data)
        ? data
        : data.results || [];

    historyBody.replaceChildren();

    if (jobs.length === 0) {
        showEmpty(historyBody, 6, "분석 기록이 없습니다.");
        return;
    }

    jobs.sort((a, b) => b.id - a.id);

    jobs.slice(0, 10).forEach(job => {
        addRow(historyBody, [
            job.id,
            job.title || "(제목 없음)",
            job.input_type,
            job.status,
            new Date(job.created_at).toLocaleString("ko-KR")
        ]);

        const row = historyBody.lastElementChild;
        const cell = document.createElement("td");
        const button = document.createElement("button");

        button.type = "button";
        button.textContent = "상세 보기";
        button.className = "history-detail-button";

        button.addEventListener("click", () => {
            loadDetail(job.id).catch(error => {
                errorMessage.textContent = error.message;
            });
        });

        cell.appendChild(button);
        row.appendChild(cell);
    });
}


// Polling: 1초마다 분석 상태 조회
async function pollStatus(id) {
    const maxAttempts = 300;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        const data = await requestAPI(
            `${API_URL}${id}/status/`
        );

        jobStatus.textContent = data.status;

        if (data.status === "SUCCESS") {
            renderPredictions(data.predictions);
            return;
        }

        if (data.status === "FAILURE") {
            throw new Error(
                data.error_message || "분석에 실패했습니다."
            );
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    throw new Error(
        "상태 조회 시간이 초과되었습니다. 서버에서 작업이 계속 진행 중일 수 있습니다."
    );
}


// 분석 시작 버튼
form.addEventListener("submit", async event => {
    event.preventDefault();

    startButton.disabled = true;
    startButton.textContent = "분석 중...";

    jobId.textContent = "-";
    jobStatus.textContent = "요청 중";
    errorMessage.textContent = "";

    showEmpty(predictionBody, 4, "분석 중입니다.");

    try {
        const formData = new FormData(form);

        const data = await requestAPI(API_URL, {
            method: "POST",
            body: formData
        });

        jobId.textContent = data.id;
        jobStatus.textContent = data.status;

        await pollStatus(data.id);

    } catch (error) {
        errorMessage.textContent = error.message;

        if (jobStatus.textContent === "요청 중") {
            jobStatus.textContent = "요청 오류";
        }

        showEmpty(predictionBody, 4, "표시할 결과가 없습니다.");

    } finally {
        startButton.disabled = false;
        startButton.textContent = "분석 시작";

        loadHistory().catch(error => {
            console.error(error);
        });
    }
});


// 페이지 초기화
startButton.disabled = false;

loadHistory().catch(error => {
    errorMessage.textContent = error.message;
});



// 분석 기록 상세 관리
const detailSection = document.getElementById("detail-section");
const detailForm = document.getElementById("detail-form");
const detailMessage = document.getElementById("detail-message");
const detailTitle = document.getElementById("detail-title");
const detailMemo = document.getElementById("detail-memo");
const deleteButton = document.getElementById("delete-button");
const closeDetailButton = document.getElementById("close-detail-button");

let selectedJobId = null;


// 상세 조회
async function loadDetail(id) {
    const data = await requestAPI(`${API_URL}${id}/`);

    selectedJobId = data.id;

    document.getElementById("detail-id").textContent = data.id;

    document.getElementById("detail-input-type").textContent =
        data.input_type;

    document.getElementById("detail-status").textContent =
        data.status;

    document.getElementById("detail-created-at").textContent =
        new Date(data.created_at).toLocaleString("ko-KR");

    detailTitle.value = data.title || "";
    detailMemo.value = data.memo || "";

    detailMessage.textContent = data.error_message || "";

    deleteButton.disabled =
        !["SUCCESS", "FAILURE"].includes(data.status);

    renderPredictions(
        data.predictions,
        document.getElementById("detail-prediction-body")
    );

    detailSection.hidden = false;

    detailSection.scrollIntoView({
        behavior: "smooth"
    });
}


// 제목 및 메모 수정
detailForm.addEventListener("submit", async event => {
    event.preventDefault();

    if (selectedJobId === null) {
        return;
    }

    const id = selectedJobId;

    try {
        await requestAPI(`${API_URL}${id}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: detailTitle.value,
                memo: detailMemo.value
            })
        });

        await loadHistory();
        await loadDetail(id);

        detailMessage.textContent = "수정되었습니다.";

    } catch (error) {
        detailMessage.textContent = error.message;
    }
});


// 분석 기록 삭제
deleteButton.addEventListener("click", async () => {
    if (selectedJobId === null) {
        return;
    }

    const confirmed = confirm(
        "이 분석 기록을 삭제하시겠습니까?"
    );

    if (!confirmed) {
        return;
    }

    const id = selectedJobId;

    deleteButton.disabled = true;

    try {
        await requestAPI(`${API_URL}${id}/`, {
            method: "DELETE"
        });

        selectedJobId = null;
        detailSection.hidden = true;

        if (jobId.textContent === String(id)) {
            jobId.textContent = "-";
            jobStatus.textContent = "대기 중";
            errorMessage.textContent = "";

            showEmpty(
                predictionBody, 4,
                "아직 분석 결과가 없습니다."
            );
        }

        await loadHistory();

    } catch (error) {
        detailMessage.textContent = error.message;
        deleteButton.disabled = false;
    }
});


// 상세 화면 닫기
closeDetailButton.addEventListener("click", () => {
    detailSection.hidden = true;
    selectedJobId = null;
});


// 입력 방식 선택
const inputTypeRadios = document.querySelectorAll(
    'input[name="input_type"]'
);

const uploadFields = document.getElementById("upload-fields");
const cameraFields = document.getElementById("camera-fields");

const videoInput = document.getElementById("video");
const cameraUrlInput = document.getElementById("camera-url");


// 입력 방식에 따른 화면 전환
function updateInputFields() {

    const inputType = document.querySelector(
        'input[name="input_type"]:checked'
    ).value;

    const isUpload = inputType === "UPLOAD";

    // 영상 업로드 입력란
    uploadFields.hidden = !isUpload;
    videoInput.disabled = !isUpload;
    videoInput.required = isUpload;

    // IP Webcam 입력란
    cameraFields.hidden = isUpload;
    cameraUrlInput.disabled = isUpload;
    cameraUrlInput.required = !isUpload;
}


// 입력 방식 변경 이벤트
inputTypeRadios.forEach(radio => {

    radio.addEventListener(
        "change",
        updateInputFields
    );

});


// 최초 화면 초기화
updateInputFields();
