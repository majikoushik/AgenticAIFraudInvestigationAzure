from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def present(path: str) -> str:
    return "present" if (ROOT / path).exists() else "missing"


def main() -> None:
    report = [
        "# Local Security Hardening Report",
        "",
        f"- Key Vault module: {present('infra/bicep/modules/key-vault.bicep')}",
        f"- Managed identity module: {present('infra/bicep/modules/managed-identity.bicep')}",
        f"- Role assignments module: {present('infra/bicep/modules/role-assignments.bicep')}",
        f"- Private endpoints module: {present('infra/bicep/modules/private-endpoints.bicep')}",
        f"- Private DNS module: {present('infra/bicep/modules/private-dns-zones.bicep')}",
        f"- Backend security package: {present('backend/app/security/secure_config_loader.py')}",
        "",
        "No Azure login is required for this static report.",
    ]
    output = ROOT / "security-report.md"
    output.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
