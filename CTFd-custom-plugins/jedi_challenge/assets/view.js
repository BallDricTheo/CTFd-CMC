(function () {
    "use strict";

    /*
     * JEDI Investigation Challenge
     * Dynamic stages
     * CTFd 3.8.7
     */

    let jediStages = [];


    function getChallengeId() {
        if (
            typeof CTFd !== "undefined" &&
            CTFd._internal &&
            CTFd._internal.challenge &&
            CTFd._internal.challenge.data &&
            CTFd._internal.challenge.data.id
        ) {
            return parseInt(
                CTFd._internal.challenge.data.id,
                10
            );
        }

        const el = document.getElementById("challenge-id");

        if (el && el.value) {
            const id = parseInt(el.value, 10);

            if (!isNaN(id)) {
                return id;
            }
        }

        const challengeElement =
            document.querySelector("[data-challenge-id]");

        if (
            challengeElement &&
            challengeElement.dataset &&
            challengeElement.dataset.challengeId
        ) {
            const id = parseInt(
                challengeElement.dataset.challengeId,
                10
            );

            if (!isNaN(id)) {
                return id;
            }
        }

        return null;
    }


    function getCsrfToken() {
        if (
            typeof window !== "undefined" &&
            window.init &&
            window.init.csrfNonce
        ) {
            return window.init.csrfNonce;
        }

        return null;
    }


    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value || "";
        return div.innerHTML;
    }


    function getStageElements(stage) {
        return {
            box: document.getElementById(`jedi-q${stage}`),
            input: document.getElementById(`input-q${stage}`),
            button: document.getElementById(`button-q${stage}`),
            status: document.getElementById(`status-q${stage}`),
            message: document.getElementById(`message-q${stage}`)
        };
    }


    function renderMetadata(category, tactics, tools) {
        const container =
            document.getElementById("jedi-metadata");

        if (!container) {
            console.warn(
                "JEDI: metadata container not found"
            );
            return;
        }

        const safeCategory =
            escapeHtml(category || "");

        const safeTactics =
            Array.isArray(tactics)
                ? tactics.map(escapeHtml).filter(Boolean)
                : [];

        const safeTools =
            Array.isArray(tools)
                ? tools.map(escapeHtml).filter(Boolean)
                : [];

        let html = "";

        if (safeCategory) {
            html += `
                <div class="jedi-metadata-section">
                    <div class="jedi-metadata-label">
                        Category
                    </div>
                    <div class="jedi-metadata-tags">
                        <span class="jedi-metadata-tag">
                            ${safeCategory}
                        </span>
                    </div>
                </div>
            `;
        }

        if (safeTactics.length > 0) {
            html += `
                <div class="jedi-metadata-section">
                    <div class="jedi-metadata-label">
                        Tactics
                    </div>
                    <div class="jedi-metadata-tags">
                        ${safeTactics.map(function (item) {
                            return `
                                <span class="jedi-metadata-tag">
                                    ${item}
                                </span>
                            `;
                        }).join("")}
                    </div>
                </div>
            `;
        }

        if (safeTools.length > 0) {
            html += `
                <div class="jedi-metadata-section">
                    <div class="jedi-metadata-label">
                        Tools
                    </div>
                    <div class="jedi-metadata-tags">
                        ${safeTools.map(function (item) {
                            return `
                                <span class="jedi-metadata-tag">
                                    ${item}
                                </span>
                            `;
                        }).join("")}
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;
    }


    function renderStages(stages) {
        const container =
            document.getElementById("jedi-challenge");

        if (!container) {
            console.error(
                "JEDI: challenge container not found"
            );
            return;
        }

        container.innerHTML = "";

        jediStages = Array.isArray(stages)
            ? stages
            : [];

        if (jediStages.length === 0) {
            container.innerHTML =
                '<div class="alert alert-warning">Không có stage được cấu hình.</div>';

            return;
        }

        jediStages.forEach(function (stageConfig, index) {
            const stage = parseInt(
                stageConfig.stage,
                10
            );

            if (isNaN(stage)) {
                return;
            }

            const title =
                escapeHtml(stageConfig.title);

            const question =
                escapeHtml(stageConfig.question);

            const box =
                document.createElement("div");

            box.className =
                "jedi-stage mt-4 locked";

            if (index === 0) {
                box.className =
                    "jedi-stage";
            }

            box.id = `jedi-q${stage}`;

            box.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="mb-0">Q${stage} — ${title}</h4>
                    <span
                        id="status-q${stage}"
                        class="badge ${stage === 1 ? "bg-success" : "bg-secondary"}"
                    >
                        ${stage === 1 ? "OPEN" : "LOCKED"}
                    </span>
                </div>

                <p>${question}</p>

                <div class="row mt-3">
                    <div class="col-12 col-md-8">
                        <input
                            type="text"
                            id="input-q${stage}"
                            class="form-control"
                            placeholder="${
                                stage === 1
                                    ? `Nhập flag Q${stage}...`
                                    : `Hoàn thành Q${stage - 1} để mở...`
                            }"
                            autocomplete="off"
                            ${stage === 1 ? "" : "disabled"}
                        >
                    </div>

                    <div class="col-12 col-md-4 mt-2 mt-md-0">
                        <button
                            type="button"
                            id="button-q${stage}"
                            class="btn btn-outline-secondary w-100"
                            onclick="submitJediStage(${stage})"
                            ${stage === 1 ? "" : "disabled"}
                        >
                            Submit Q${stage}
                        </button>
                    </div>
                </div>

                <div
                    id="message-q${stage}"
                    class="jedi-message mt-3"
                ></div>
            `;

            container.appendChild(box);
        });
    }


    function setStageState(stage, state) {
        const elements =
            getStageElements(stage);

        const box = elements.box;
        const input = elements.input;
        const button = elements.button;
        const status = elements.status;

        if (!box || !status) {
            console.warn(
                `JEDI: Q${stage} DOM elements not found`
            );

            return;
        }

        if (state === "completed") {
            box.classList.remove("locked");

            status.innerText =
                "✓ COMPLETED";

            status.className =
                "badge bg-success";

            if (input) {
                input.disabled = true;
                input.placeholder =
                    "Đã hoàn thành";
            }

            if (button) {
                button.disabled = true;
            }

            return;
        }

        if (state === "open") {
            box.classList.remove("locked");

            status.innerText =
                "OPEN";

            status.className =
                "badge bg-success";

            if (input) {
                input.disabled = false;
                input.placeholder =
                    `Nhập flag Q${stage}...`;
            }

            if (button) {
                button.disabled = false;
            }

            return;
        }

        box.classList.add("locked");

        status.innerText =
            "LOCKED";

        status.className =
            "badge bg-secondary";

        if (input) {
            input.disabled = true;

            input.placeholder =
                stage > 1
                    ? `Hoàn thành Q${stage - 1} để mở...`
                    : "Chưa mở";
        }

        if (button) {
            button.disabled = true;
        }
    }


    function renderProgress(progress) {
        progress = parseInt(
            progress,
            10
        );

        if (isNaN(progress)) {
            progress = 0;
        }

        const total =
            jediStages.length;

        progress = Math.max(
            0,
            Math.min(progress, total)
        );

        console.log(
            "JEDI: rendering progress:",
            progress,
            "/",
            total
        );

        jediStages.forEach(function (stageConfig) {
            const stage =
                parseInt(
                    stageConfig.stage,
                    10
                );

            if (stage <= progress) {
                setStageState(
                    stage,
                    "completed"
                );
            } else if (
                stage === progress + 1
            ) {
                setStageState(
                    stage,
                    "open"
                );
            } else {
                setStageState(
                    stage,
                    "locked"
                );
            }
        });
    }


    async function loadProgress() {
        const challengeId =
            getChallengeId();

        console.log(
            "JEDI Challenge ID:",
            challengeId
        );

        if (!challengeId) {
            console.error(
                "JEDI: Challenge ID not found"
            );

            return;
        }

        try {
            const response =
                await fetch(
                    `/plugins/jedi_challenge/progress/${challengeId}`,
                    {
                        method: "GET",
                        credentials: "same-origin",
                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );

            console.log(
                "JEDI progress HTTP status:",
                response.status
            );

            if (!response.ok) {
                throw new Error(
                    `HTTP ${response.status}`
                );
            }

            const data =
                await response.json();

            console.log(
                "JEDI progress:",
                data
            );

            if (
                data &&
                data.success === true
            ) {
                renderMetadata(
                    data.category || "",
                    data.tactics || [],
                    data.tools || []
                );

                renderStages(
                    data.stages || []
                );

                renderProgress(
                    data.progress || 0
                );
            } else {
                console.warn(
                    "JEDI: progress API returned unsuccessful response"
                );

                renderStages([]);

            }

        } catch (error) {
            console.error(
                "JEDI progress error:",
                error
            );
        }
    }


    window.submitJediStage =
        async function (stage) {

            const input =
                document.getElementById(
                    `input-q${stage}`
                );

            const message =
                document.getElementById(
                    `message-q${stage}`
                );

            const button =
                document.getElementById(
                    `button-q${stage}`
                );

            if (!input || !message) {
                console.error(
                    `JEDI: Q${stage} input/message not found`
                );

                return;
            }

            const flag =
                input.value.trim();

            if (!flag) {
                message.innerText =
                    "Vui lòng nhập flag.";

                return;
            }

            const challengeId =
                getChallengeId();

            if (!challengeId) {
                message.innerText =
                    "Không xác định được Challenge ID.";

                return;
            }

            if (button) {
                button.disabled = true;
            }

            message.innerText =
                "Đang kiểm tra...";

            try {
                const csrfToken =
                    getCsrfToken();

                if (!csrfToken) {
                    throw new Error(
                        "Không tìm thấy CSRF token của CTFd."
                    );
                }

                const response =
                    await fetch(
                        "/api/v1/challenges/attempt",
                        {
                            method: "POST",

                            credentials:
                                "same-origin",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json",

                                "CSRF-Token":
                                    csrfToken
                            },

                            body:
                                JSON.stringify({
                                    challenge_id:
                                        challengeId,

                                    submission:
                                        `Q${stage}|${flag}`
                                })
                        }
                    );

                console.log(
                    "JEDI submission HTTP status:",
                    response.status
                );

                let data = null;

                try {
                    data =
                        await response.json();
                } catch (e) {
                    console.warn(
                        "JEDI: response is not JSON"
                    );
                }

                if (
                    response.status === 403
                ) {
                    message.innerText =
                        "⛔ CTFd từ chối request (403). Kiểm tra CSRF/session.";

                    if (button) {
                        button.disabled = false;
                    }

                    return;
                }

                if (!response.ok) {
                    message.innerText =
                        `Lỗi HTTP ${response.status}.`;

                    if (button) {
                        button.disabled = false;
                    }

                    return;
                }

                const result =
                    data && data.data
                        ? data.data
                        : data;

                const status =
                    result && result.status
                        ? result.status
                        : null;

                const serverMessage =
                    result && result.message
                        ? result.message
                        : "Không nhận được phản hồi hợp lệ từ CTFd.";

                message.innerText =
                    serverMessage;

                if (
                    status === "correct" ||
                    status === "partial"
                ) {
                    await loadProgress();
                    return;
                }

                if (button) {
                    button.disabled = false;
                }

            } catch (error) {
                console.error(
                    "JEDI submission error:",
                    error
                );

                message.innerText =
                    error.message ||
                    "Không thể gửi submission.";

                if (button) {
                    button.disabled = false;
                }
            }
        };


    CTFd._internal.challenge.preRender =
        function () {
            console.log(
                "JEDI: preRender"
            );
        };


    CTFd._internal.challenge.postRender =
        function () {
            console.log(
                "JEDI: postRender"
            );

            loadProgress();
        };

})();
