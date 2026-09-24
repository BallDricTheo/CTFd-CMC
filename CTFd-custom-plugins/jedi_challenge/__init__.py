import json
import os

from flask import jsonify

from CTFd.models import Partials, Solves
from CTFd.plugins.challenges import (
    BaseChallenge,
    ChallengeResponse,
    CHALLENGE_CLASSES,
)
from CTFd.plugins import register_plugin_assets_directory
from CTFd.utils.user import get_current_user, get_current_team


CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "configs",
)


def load_config(challenge):
    path = os.path.join(
        CONFIG_DIR,
        f"{challenge.id}.json",
    )

    if not os.path.isfile(path):
        return {"stages": []}

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, ValueError):
        return {"stages": []}

    stages = config.get("stages", [])

    normalized = []

    for item in stages:
        try:
            stage = int(item["stage"])
        except (KeyError, TypeError, ValueError):
            continue

        answers = item.get("answers", [])

        if isinstance(answers, str):
            answers = [answers]

        normalized.append({
            "stage": stage,
            "title": item.get(
                "title",
                f"Q{stage}",
            ),
            "question": item.get(
                "question",
                "",
            ),
            "answers": [
                str(answer).strip()
                for answer in answers
                if str(answer).strip()
            ],
            "case_sensitive": bool(
                item.get(
                    "case_sensitive",
                    False,
                )
            ),
        })

    normalized.sort(
        key=lambda x: x["stage"]
    )

    return {
        "category": config.get("category", ""),
        "tactics": config.get("tactics", []),
        "tools": config.get("tools", []),
        "stages": normalized,
    }


class JediChallenge(BaseChallenge):
    id = "jedi"
    name = "JEDI Investigation"

    templates = {
        "create": "/plugins/challenges/assets/create.html",
        "update": "/plugins/challenges/assets/update.html",
        "view": "/plugins/jedi_challenge/templates/view.html",
    }

    scripts = {
        "create": "/plugins/challenges/assets/create.js",
        "update": "/plugins/challenges/assets/update.js",
        "view": "/plugins/jedi_challenge/assets/view.js",
    }

    route = "/plugins/jedi_challenge/assets/"
    blueprint = None

    # =========================================================
    # CONFIG
    # =========================================================

    @classmethod
    def get_stages(cls, challenge):
        return load_config(challenge).get(
            "stages",
            [],
        )

    @classmethod
    def get_stage(cls, challenge, stage):
        for item in cls.get_stages(challenge):
            if item["stage"] == stage:
                return item

        return None

    # =========================================================
    # ANSWER VALIDATION
    # =========================================================

    @classmethod
    def answer_matches(cls, stage_config, provided):
        provided = (provided or "").strip()

        for expected in stage_config.get(
            "answers",
            [],
        ):
            expected = str(expected).strip()

            if stage_config.get(
                "case_sensitive",
                False,
            ):
                if provided == expected:
                    return True
            else:
                if provided.lower() == expected.lower():
                    return True

        return False

    # =========================================================
    # PROGRESS
    # =========================================================

    @classmethod
    def get_progress(cls, challenge):
        user = get_current_user()
        team = get_current_team()

        if not user:
            return 0

        stages = cls.get_stages(challenge)

        if not stages:
            return 0

        team_id = team.id if team else None

        partials = Partials.query.filter_by(
            user_id=user.id,
            team_id=team_id,
            challenge_id=challenge.id,
        ).all()

        completed = set()

        for partial in partials:
            provided = (
                partial.provided or ""
            ).strip()

            if "|" not in provided:
                continue

            stage_raw, flag = provided.split(
                "|",
                1,
            )

            stage_raw = stage_raw.strip().upper()
            flag = flag.strip()

            if not stage_raw.startswith("Q"):
                continue

            try:
                stage = int(stage_raw[1:])
            except ValueError:
                continue

            stage_config = cls.get_stage(
                challenge,
                stage,
            )

            if stage_config is None:
                continue

            if cls.answer_matches(
                stage_config,
                flag,
            ):
                completed.add(stage)

        solved = Solves.query.filter_by(
            user_id=user.id,
            team_id=team_id,
            challenge_id=challenge.id,
        ).first()

        if solved:
            return len(stages)

        progress = 0

        for item in stages:
            stage = item["stage"]

            if stage in completed:
                progress = stage
            else:
                break

        return progress

    # =========================================================
    # ATTEMPT
    # =========================================================

    @classmethod
    def attempt(cls, challenge, request):
        data = request.form or request.get_json() or {}

        submission = (
            data.get("submission") or ""
        ).strip()

        if not submission:
            return ChallengeResponse(
                status="incorrect",
                message="Submission không được để trống.",
            )

        if "|" not in submission:
            return ChallengeResponse(
                status="incorrect",
                message="Định dạng submission không hợp lệ.",
            )

        stage_raw, flag = submission.split(
            "|",
            1,
        )

        stage_raw = stage_raw.strip().upper()
        flag = flag.strip()

        if not stage_raw.startswith("Q"):
            return ChallengeResponse(
                status="incorrect",
                message="Stage không hợp lệ.",
            )

        try:
            stage = int(stage_raw[1:])
        except ValueError:
            return ChallengeResponse(
                status="incorrect",
                message="Stage không hợp lệ.",
            )

        stage_config = cls.get_stage(
            challenge,
            stage,
        )

        if stage_config is None:
            return ChallengeResponse(
                status="incorrect",
                message="Stage không tồn tại.",
            )

        stages = cls.get_stages(challenge)

        current_progress = cls.get_progress(
            challenge
        )

        if stage <= current_progress:
            return ChallengeResponse(
                status="partial",
                message=f"✓ Q{stage} đã được hoàn thành.",
            )

        expected_next = current_progress + 1

        if stage != expected_next:
            return ChallengeResponse(
                status="incorrect",
                message=(
                    f"Bạn phải hoàn thành "
                    f"Q{expected_next} trước."
                ),
            )

        if not cls.answer_matches(
            stage_config,
            flag,
        ):
            return ChallengeResponse(
                status="incorrect",
                message=(
                    f"Q{stage} chưa chính xác. "
                    "Hãy tiếp tục phân tích artifact."
                ),
            )

        current_index = None

        for index, item in enumerate(stages):
            if item["stage"] == stage:
                current_index = index
                break

        is_final = (
            current_index is not None
            and current_index == len(stages) - 1
        )

        if not is_final:
            next_stage = stages[
                current_index + 1
            ]["stage"]

            return ChallengeResponse(
                status="partial",
                message=(
                    f"✓ Q{stage} chính xác. "
                    f"Q{next_stage} đã được mở."
                ),
            )

        return ChallengeResponse(
            status="correct",
            message=(
                "✓ JEDI INVESTIGATION hoàn tất. "
                f"Bạn đã hoàn thành đủ {len(stages)} câu hỏi."
            ),
        )


# =============================================================
# REGISTER CHALLENGE
# =============================================================

CHALLENGE_CLASSES["jedi"] = JediChallenge


# =============================================================
# PLUGIN LOAD
# =============================================================

def load(app):

    register_plugin_assets_directory(
        app,
        base_path="/plugins/jedi_challenge/assets/",
    )

    @app.route(
        "/plugins/jedi_challenge/progress/<int:challenge_id>",
        methods=["GET"],
    )
    def jedi_progress(challenge_id):

        from CTFd.models import Challenges

        challenge = Challenges.query.filter_by(
            id=challenge_id
        ).first()

        if challenge is None:
            return jsonify({
                "success": False,
                "progress": 0,
            }), 404

        config = load_config(challenge)
        stages = config.get("stages", [])

        progress = JediChallenge.get_progress(
            challenge
        )

        public_stages = []

        for item in stages:
            public_stages.append({
                "stage": item["stage"],
                "title": item.get(
                    "title",
                    f"Q{item['stage']}",
                ),
                "question": item.get(
                    "question",
                    "",
                ),
            })

        return jsonify({
            "success": True,
            "progress": progress,
            "total": len(stages),
            "category": config.get("category", ""),
            "tactics": config.get("tactics", []),
            "tools": config.get("tools", []),
            "stages": public_stages,
        })
