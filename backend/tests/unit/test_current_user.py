from app.auth.current_user import AuthenticatedUser, mask_email


def test_authenticated_user_role_helpers() -> None:
    user = AuthenticatedUser(
        user_id="admin_01",
        roles=["ADMIN"],
        primary_role="ADMIN",
        auth_mode="local",
    )

    assert user.has_role("ADMIN")
    assert user.has_any_role(["AUDITOR", "ADMIN"])
    assert user.is_admin()


def test_mask_email() -> None:
    assert mask_email("fraud_analyst@example.com") == "fr***@example.com"
