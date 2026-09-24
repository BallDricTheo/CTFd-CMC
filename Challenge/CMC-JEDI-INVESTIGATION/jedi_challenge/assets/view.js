(function () {

    function setStageState(stage, state) {

        const box = document.querySelector(
            '.jedi-stage[data-stage="' + stage + '"]'
        );

        const status = document.getElementById(
            'jedi-status-' + stage
        );

        const input = document.getElementById(
            'jedi-input-' + stage
        );

        const button = document.getElementById(
            'jedi-submit-' + stage
        );

        if (!box || !status) {
            return;
        }

        box.classList.remove(
            'jedi-locked',
            'jedi-active',
            'jedi-completed'
        );

        if (state === 'locked') {

            box.classList.add('jedi-locked');

            status.textContent = 'LOCKED';

            if (input) {
                input.disabled = true;
                input.placeholder =
                    'Hoàn thành Q' + (stage - 1) + ' trước';
            }

            if (button) {
                button.disabled = true;
            }

        } else if (state === 'active') {

            box.classList.add('jedi-active');

            status.textContent = 'READY';

            if (input) {
                input.disabled = false;
                input.placeholder =
                    'Nhập flag Q' + stage;
            }

            if (button) {
                button.disabled = false;
            }

        } else if (state === 'completed') {

            box.classList.add('jedi-completed');

            status.textContent = 'COMPLETED';

            if (input) {
                input.disabled = true;
            }

            if (button) {
                button.disabled = true;
            }
        }
    }


    function updateProgress(progress) {

        for (let stage = 1; stage <= 3; stage++) {

            if (stage <= progress) {

                setStageState(stage, 'completed');

            } else if (stage === progress + 1) {

                setStageState(stage, 'active');

            } else {

                setStageState(stage, 'locked');
            }
        }
    }


    function showMessage(stage, message, success) {

        const element = document.getElementById(
            'jedi-message-' + stage
        );

        if (!element) {
            return;
        }

        element.textContent = message;

        element.classList.remove(
            'jedi-success',
            'jedi-error'
        );

        element.classList.add(
            success ? 'jedi-success' : 'jedi-error'
        );
    }


    async function submitStage(stage) {

        const input = document.getElementById(
            'jedi-input-' + stage
        );

        const button = document.getElementById(
            'jedi-submit-' + stage
        );

        const challengeId = parseInt(
            document.getElementById('challenge-id').value
        );

        if (!input || !button) {
            return;
        }

        const flag = input.value.trim();

        if (!flag) {
            showMessage(
                stage,
                'Vui lòng nhập flag.',
                false
            );
            return;
        }

        button.disabled = true;

        /*
         * Stage được gửi cùng submission.
         *
         * Server sẽ kiểm tra:
         *
         * Q1 -> Q2 -> Q3
         *
         * Không tin tưởng localStorage hay JS.
         */
        const submission =
            'Q' + stage + '|' + flag;

        try {

            const response =
                await CTFd.api.post_challenge_attempt(
                    {},
                    {
                        challenge_id: challengeId,
                        submission: submission
                    }
                );

            const data = response.data || {};

            if (data.status === 'partial') {

                showMessage(
                    stage,
                    data.message,
                    true
                );

                updateProgress(stage);

                if (stage === 3) {
                    updateProgress(3);
                }

            } else if (data.status === 'correct') {

                showMessage(
                    stage,
                    data.message,
                    true
                );

                updateProgress(3);

            } else {

                showMessage(
                    stage,
                    data.message || 'Flag không chính xác.',
                    false
                );

                button.disabled = false;
            }

        } catch (error) {

            console.error(error);

            showMessage(
                stage,
                'Có lỗi khi gửi submission.',
                false
            );

            button.disabled = false;
        }
    }


    function initialize() {

        /*
         * Ban đầu chỉ Q1 được mở.
         *
         * Server mới là nơi quyết định thực tế.
         * Đây chỉ là UI state.
         */
        updateProgress(0);

        document
            .querySelectorAll('.jedi-submit')
            .forEach(function (button) {

                button.addEventListener(
                    'click',
                    function () {

                        const stage =
                            parseInt(
                                this.dataset.stage
                            );

                        submitStage(stage);
                    }
                );
            });


        document
            .querySelectorAll('.jedi-input')
            .forEach(function (input) {

                input.addEventListener(
                    'keydown',
                    function (event) {

                        if (event.key !== 'Enter') {
                            return;
                        }

                        const stage =
                            parseInt(
                                this.id.split('-').pop()
                            );

                        submitStage(stage);
                    }
                );
            });
    }


    /*
     * CTFd gọi script này khi render challenge.
     */
    CTFd._internal.challenge.data = undefined;

    CTFd._internal.challenge.renderer = null;

    CTFd._internal.challenge.preRender =
        function () {};

    CTFd._internal.challenge.postRender =
        function () {

            initialize();

        };

})();
