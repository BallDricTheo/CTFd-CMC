from CTFd.models import Challenges, Flags, Partials
from CTFd.plugins.challenges import (
    BaseChallenge,
    ChallengeResponse,
    CHALLENGE_CLASSES,
)
from CTFd.plugins import register_plugin_assets_directory
from CTFd.utils.user import get_current_user, get_current_team


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

    # Stage -> flag
    STAGES = {
        1: "flag{m47ry05hk4}",
        2: "flag{k3n081}",
        3: "flag{r5-d4_k-2so_bd-1}",
    }

    @classmethod
    def get_progress(cls, challenge):
        user = get_current_user()
        team = get_current_team()

        if not user:
            return 0

        partials = Partials.query.filter_by(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
        ).all()

        completed = set()

        for partial in partials:
            provided = (partial.provided or "").strip()

            for stage, flag in cls.STAGES.items():
                if provided == f"Q{stage}|{flag}":
                    completed.add(stage)

        # Final solve means everything is complete
        from CTFd.models import Solves

        solved = Solves.query.filter_by(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
        ).first()

        if solved:
            return 3

        # Only allow contiguous progression
        progress = 0

        for stage in range(1, 4):
            if stage in completed:
                progress = stage
            else:
                break

        return progress

    @classmethod
    def attempt(cls, challenge, request):
        data = request.form or request.get_json()

        submission = (data.get("submission") or "").strip()

        if "|" not in submission:
            return ChallengeResponse(
                status="incorrect",
                message="Định dạng submission không hợp lệ.",
            )

        stage_raw, flag = submission.split("|", 1)

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

        if stage not in cls.STAGES:
            return ChallengeResponse(
                status="incorrect",
                message="Stage không tồn tại.",
            )

        current_progress = cls.get_progress(challenge)

        # Enforce Q1 -> Q2 -> Q3 server-side
        if stage != current_progress + 1:
            if stage <= current_progress:
                return ChallengeResponse(
                    status="partial",
                    message=f"Q{stage} đã được hoàn thành.",
                )

            return ChallengeResponse(
                status="incorrect",
                message=f"Bạn phải hoàn thành Q{current_progress + 1} trước.",
            )

        expected = cls.STAGES[stage]

        if flag != expected:
            return ChallengeResponse(
                status="incorrect",
                message=f"Q{stage} chưa chính xác. Hãy tiếp tục phân tích artifact.",
            )

        # Q1 / Q2 = partial
        if stage < 3:
            return ChallengeResponse(
                status="partial",
                message=f"✓ Q{stage} chính xác. Q{stage + 1} đã được mở.",
            )

        # Q3 = correct -> CTFd creates final Solve
        return ChallengeResponse(
            status="correct",
            message="✓ JEDI INVESTIGATION hoàn tất. Bạn đã thu thập đủ 3 bằng chứng.",
        )


CHALLENGE_CLASSES["jedi"] = JediChallenge


def load(app):
    register_plugin_assets_directory(
        app,
        base_path="/plugins/jedi_challenge/assets/",
    )
