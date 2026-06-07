from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: str
    display_name: str | None = None
    email: str | None = None
    roles: list[str]
    primary_role: str
    auth_mode: str
    tenant_id: str | None = None
    token_subject: str | None = None

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, roles: list[str]) -> bool:
        return any(role in self.roles for role in roles)

    def is_admin(self) -> bool:
        return self.has_role("ADMIN")


def mask_email(email: str | None) -> str | None:
    if not email or "@" not in email:
        return email
    name, domain = email.split("@", 1)
    if len(name) <= 2:
        return f"{name[:1]}***@{domain}"
    return f"{name[:2]}***@{domain}"
