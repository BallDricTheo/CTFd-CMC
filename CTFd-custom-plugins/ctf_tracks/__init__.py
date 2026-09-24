import os

from flask import render_template, request, redirect, url_for, abort, flash
from sqlalchemy import UniqueConstraint
from jinja2 import ChoiceLoader, FileSystemLoader

from CTFd.models import db, Solves, Challenges
from CTFd.utils.user import get_current_user, get_current_team
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_plugin_assets_directory


class Track(db.Model):
    __tablename__ = "ctf_tracks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(32), default="Medium")
    icon = db.Column(db.String(64), default="🎯")
    kind = db.Column(db.String(32), default="skill")
    sort_order = db.Column(db.Integer, default=0)
    published = db.Column(db.Boolean, default=True)

    levels = db.relationship(
        "TrackLevel",
        backref="track",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="TrackLevel.level_number",
    )


class TrackLevel(db.Model):
    __tablename__ = "ctf_track_levels"

    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(
        db.Integer,
        db.ForeignKey("ctf_tracks.id", ondelete="CASCADE"),
        nullable=False,
    )
    level_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    labs = db.relationship(
        "TrackLab",
        backref="level",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="TrackLab.sort_order",
    )

    __table_args__ = (
        UniqueConstraint(
            "track_id",
            "level_number",
            name="uq_track_level",
        ),
    )


class TrackLab(db.Model):
    __tablename__ = "ctf_track_labs"

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(
        db.Integer,
        db.ForeignKey("ctf_track_levels.id", ondelete="CASCADE"),
        nullable=False,
    )
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
    )
    title_override = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    required = db.Column(db.Boolean, default=True)

    challenge = db.relationship("Challenges", lazy=True)

    __table_args__ = (
        UniqueConstraint(
            "level_id",
            "challenge_id",
            name="uq_level_challenge",
        ),
    )


# =========================================================
# USER PROGRESS
# =========================================================

def _solved_challenge_ids(challenge_ids):
    user = get_current_user()
    team = get_current_team()

    if not user or not challenge_ids:
        return set()

    query = Solves.query.filter(
        Solves.challenge_id.in_(challenge_ids)
    )

    if team:
        query = query.filter(Solves.team_id == team.id)
    else:
        query = query.filter(Solves.user_id == user.id)

    return {row.challenge_id for row in query.all()}


def _track_data(track):
    labs = []
    challenge_ids = []
    level_data = []

    for level in track.levels:
        level_labs = []

        for lab in level.labs:
            if lab.challenge is None:
                continue

            challenge_ids.append(lab.challenge_id)
            level_labs.append(lab)
            labs.append(lab)

        level_data.append({
            "level": level,
            "labs": level_labs,
        })

    solved_ids = _solved_challenge_ids(challenge_ids)

    for lab in labs:
        lab.solved = lab.challenge_id in solved_ids

    for item in level_data:
        item["has_labs"] = len(item["labs"]) > 0

        item["completed"] = (
            item["has_labs"]
            and all(
                lab.solved
                for lab in item["labs"]
            )
        )

    required_labs = [
        lab for lab in labs
        if lab.required
    ]

    completed = sum(
        1
        for lab in required_labs
        if lab.solved
    )

    total = len(required_labs)

    progress = (
        round((completed / total) * 100)
        if total
        else 0
    )

    return {
        "track": track,
        "levels": level_data,
        "labs": labs,
        "completed": completed,
        "total": total,
        "progress": progress,
    }

# =========================================================
# ADMIN HELPERS
# =========================================================

def _admin_redirect():
    return redirect(url_for("tracks_admin"))


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# =========================================================
# PLUGIN LOAD
# =========================================================

def load(app):

    template_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "templates",
    )

    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(template_dir),
        app.jinja_loader,
    ])

    app.db.create_all()

    register_plugin_assets_directory(
        app,
        base_path="/plugins/ctf_tracks/assets/",
    )


    # =====================================================
    # PUBLIC
    # =====================================================

    @app.route("/tracks")
    def tracks_index():

        tracks = (
            Track.query
            .filter_by(published=True)
            .order_by(
                Track.sort_order.asc(),
                Track.name.asc(),
            )
            .all()
        )

        cards = [
            _track_data(track)
            for track in tracks
        ]

        return render_template(
            "tracks.html",
            cards=cards,
        )


    @app.route("/tracks/<slug>")
    def track_detail(slug):

        track = (
            Track.query
            .filter_by(
                slug=slug,
                published=True,
            )
            .first_or_404()
        )

        data = _track_data(track)

        return render_template(
            "track.html",
            **data,
        )


    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    @app.route("/admin/tracks", methods=["GET"])
    @admins_only
    def tracks_admin():

        tracks = (
            Track.query
            .order_by(
                Track.sort_order.asc(),
                Track.name.asc(),
            )
            .all()
        )

        challenges = (
            Challenges.query
            .order_by(
                Challenges.name.asc()
            )
            .all()
        )

        # Prepare statistics for admin UI
        for track in tracks:

            track._level_count = len(track.levels)

            track._lab_count = sum(
                len(level.labs)
                for level in track.levels
            )

        return render_template(
            "admin_tracks.html",
            tracks=tracks,
            challenges=challenges,
        )


    # =====================================================
    # TRACK CREATE
    # =====================================================

    @app.route(
        "/admin/tracks/create",
        methods=["POST"],
    )
    @admins_only
    def tracks_create():

        name = (
            request.form.get("name") or ""
        ).strip()

        slug = (
            request.form.get("slug") or ""
        ).strip().lower()

        difficulty = (
            request.form.get("difficulty")
            or "Medium"
        ).strip()

        icon = (
            request.form.get("icon")
            or "🎯"
        ).strip()

        description = (
            request.form.get("description")
            or ""
        ).strip()

        kind = (
            request.form.get("kind")
            or "skill"
        ).strip()

        sort_order = _safe_int(
            request.form.get("sort_order"),
            0,
        )

        published = (
            request.form.get("published")
            == "1"
        )

        if not name or not slug:
            flash(
                "Name và slug là bắt buộc.",
                "danger",
            )
            return _admin_redirect()

        if Track.query.filter_by(
            slug=slug
        ).first():

            flash(
                "Slug đã tồn tại.",
                "danger",
            )
            return _admin_redirect()

        track = Track(
            name=name,
            slug=slug,
            difficulty=difficulty,
            icon=icon,
            description=description,
            kind=kind,
            sort_order=sort_order,
            published=published,
        )

        db.session.add(track)
        db.session.commit()

        flash(
            "Đã tạo Track.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # TRACK UPDATE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/edit",
        methods=["POST"],
    )
    @admins_only
    def tracks_edit(track_id):

        track = Track.query.get_or_404(
            track_id
        )

        name = (
            request.form.get("name") or ""
        ).strip()

        slug = (
            request.form.get("slug") or ""
        ).strip().lower()

        if not name or not slug:
            flash(
                "Name và slug là bắt buộc.",
                "danger",
            )
            return _admin_redirect()

        duplicate = (
            Track.query
            .filter(
                Track.slug == slug,
                Track.id != track.id,
            )
            .first()
        )

        if duplicate:
            flash(
                "Slug đã được sử dụng bởi Track khác.",
                "danger",
            )
            return _admin_redirect()

        track.name = name
        track.slug = slug

        track.difficulty = (
            request.form.get("difficulty")
            or "Medium"
        ).strip()

        track.icon = (
            request.form.get("icon")
            or "🎯"
        ).strip()

        track.kind = (
            request.form.get("kind")
            or "skill"
        ).strip()

        track.description = (
            request.form.get("description")
            or ""
        ).strip()

        track.sort_order = _safe_int(
            request.form.get("sort_order"),
            0,
        )

        track.published = (
            request.form.get("published")
            == "1"
        )

        db.session.commit()

        flash(
            "Đã cập nhật Track.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # TRACK TOGGLE PUBLISH
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/toggle",
        methods=["POST"],
    )
    @admins_only
    def tracks_toggle(track_id):

        track = Track.query.get_or_404(
            track_id
        )

        track.published = not track.published

        db.session.commit()

        status = (
            "Published"
            if track.published
            else "Unpublished"
        )

        flash(
            f"Track {status}.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # TRACK DELETE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/delete",
        methods=["POST"],
    )
    @admins_only
    def tracks_delete(track_id):

        track = Track.query.get_or_404(
            track_id
        )

        name = track.name

        db.session.delete(track)
        db.session.commit()

        flash(
            f'Đã xóa Track "{name}".',
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # LEVEL CREATE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/level",
        methods=["POST"],
    )
    @admins_only
    def tracks_level_create(track_id):

        track = Track.query.get_or_404(
            track_id
        )

        number = _safe_int(
            request.form.get("level_number"),
            1,
        )

        if number < 1:
            flash(
                "Level number phải >= 1.",
                "danger",
            )
            return _admin_redirect()

        name = (
            request.form.get("name")
            or f"Level {number}"
        ).strip()

        description = (
            request.form.get("description")
            or ""
        ).strip()

        existing = (
            TrackLevel.query
            .filter_by(
                track_id=track.id,
                level_number=number,
            )
            .first()
        )

        if existing:
            flash(
                "Level này đã tồn tại.",
                "danger",
            )
            return _admin_redirect()

        level = TrackLevel(
            track_id=track.id,
            level_number=number,
            name=name,
            description=description,
        )

        db.session.add(level)
        db.session.commit()

        flash(
            "Đã tạo Level.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # LEVEL UPDATE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/level/<int:level_id>/edit",
        methods=["POST"],
    )
    @admins_only
    def tracks_level_edit(
        track_id,
        level_id,
    ):

        level = (
            TrackLevel.query
            .filter_by(
                id=level_id,
                track_id=track_id,
            )
            .first_or_404()
        )

        number = _safe_int(
            request.form.get("level_number"),
            level.level_number,
        )

        name = (
            request.form.get("name")
            or level.name
        ).strip()

        description = (
            request.form.get("description")
            or ""
        ).strip()

        duplicate = (
            TrackLevel.query
            .filter(
                TrackLevel.track_id == track_id,
                TrackLevel.level_number == number,
                TrackLevel.id != level.id,
            )
            .first()
        )

        if duplicate:
            flash(
                "Level number đã tồn tại.",
                "danger",
            )
            return _admin_redirect()

        level.level_number = number
        level.name = name
        level.description = description

        db.session.commit()

        flash(
            "Đã cập nhật Level.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # LEVEL DELETE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/level/<int:level_id>/delete",
        methods=["POST"],
    )
    @admins_only
    def tracks_level_delete(
        track_id,
        level_id,
    ):

        level = (
            TrackLevel.query
            .filter_by(
                id=level_id,
                track_id=track_id,
            )
            .first_or_404()
        )

        db.session.delete(level)
        db.session.commit()

        flash(
            "Đã xóa Level và các Lab mapping trong Level.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # LAB CREATE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/lab",
        methods=["POST"],
    )
    @admins_only
    def tracks_lab_create(track_id):

        track = Track.query.get_or_404(
            track_id
        )

        level_id = _safe_int(
            request.form.get("level_id"),
            0,
        )

        challenge_id = _safe_int(
            request.form.get("challenge_id"),
            0,
        )

        level = (
            TrackLevel.query
            .filter_by(
                id=level_id,
                track_id=track.id,
            )
            .first_or_404()
        )

        challenge = (
            Challenges.query
            .get_or_404(challenge_id)
        )

        title_override = (
            request.form.get("title_override")
            or ""
        ).strip() or None

        description = (
            request.form.get("description")
            or ""
        ).strip() or None

        sort_order = _safe_int(
            request.form.get("sort_order"),
            0,
        )

        required = (
            request.form.get("required")
            == "1"
        )

        existing = (
            TrackLab.query
            .filter_by(
                level_id=level.id,
                challenge_id=challenge.id,
            )
            .first()
        )

        if existing:
            flash(
                "Challenge đã nằm trong Level này.",
                "danger",
            )
            return _admin_redirect()

        lab = TrackLab(
            level_id=level.id,
            challenge_id=challenge.id,
            title_override=title_override,
            description=description,
            sort_order=sort_order,
            required=required,
        )

        db.session.add(lab)
        db.session.commit()

        flash(
            "Đã thêm Lab vào Track.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # LAB UPDATE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/lab/<int:lab_id>/edit",
        methods=["POST"],
    )
    @admins_only
    def tracks_lab_edit(
        track_id,
        lab_id,
    ):

        lab = (
            TrackLab.query
            .join(TrackLevel)
            .filter(
                TrackLevel.track_id == track_id,
                TrackLab.id == lab_id,
            )
            .first_or_404()
        )

        lab.title_override = (
            request.form.get("title_override")
            or ""
        ).strip() or None

        lab.description = (
            request.form.get("description")
            or ""
        ).strip() or None

        lab.sort_order = _safe_int(
            request.form.get("sort_order"),
            0,
        )

        lab.required = (
            request.form.get("required")
            == "1"
        )

        db.session.commit()

        flash(
            "Đã cập nhật Lab.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # LAB MOVE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/lab/<int:lab_id>/move",
        methods=["POST"],
    )
    @admins_only
    def tracks_lab_move(
        track_id,
        lab_id,
    ):

        lab = (
            TrackLab.query
            .join(TrackLevel)
            .filter(
                TrackLevel.track_id == track_id,
                TrackLab.id == lab_id,
            )
            .first_or_404()
        )

        new_level_id = _safe_int(
            request.form.get("level_id"),
            0,
        )

        new_level = (
            TrackLevel.query
            .filter_by(
                id=new_level_id,
                track_id=track_id,
            )
            .first_or_404()
        )

        duplicate = (
            TrackLab.query
            .filter(
                TrackLab.level_id == new_level.id,
                TrackLab.challenge_id == lab.challenge_id,
                TrackLab.id != lab.id,
            )
            .first()
        )

        if duplicate:
            flash(
                "Challenge đã tồn tại trong Level đích.",
                "danger",
            )
            return _admin_redirect()

        lab.level_id = new_level.id

        db.session.commit()

        flash(
            "Đã chuyển Lab sang Level mới.",
            "success",
        )

        return _admin_redirect()


    # =====================================================
    # LAB DELETE
    # =====================================================

    @app.route(
        "/admin/tracks/<int:track_id>/lab/<int:lab_id>/delete",
        methods=["POST"],
    )
    @admins_only
    def tracks_lab_delete(
        track_id,
        lab_id,
    ):

        lab = (
            TrackLab.query
            .join(TrackLevel)
            .filter(
                TrackLevel.track_id == track_id,
                TrackLab.id == lab_id,
            )
            .first_or_404()
        )

        db.session.delete(lab)
        db.session.commit()

        flash(
            "Đã remove Lab khỏi Track.",
            "success",
        )

        return _admin_redirect()
