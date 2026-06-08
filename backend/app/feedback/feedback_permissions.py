from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, has_permission


def can_view_feedback(user: AuthenticatedUser, feedback: dict) -> bool:
    return (
        user.is_admin()
        or has_permission(user, Permission.MANAGE_AI_FEEDBACK)
        or feedback.get("submitted_by") == user.user_id
    )
