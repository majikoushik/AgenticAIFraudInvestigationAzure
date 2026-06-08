# Retention Scan Failure

Check backend logs, verify JSON store paths exist, confirm records are valid JSON, rerun with `dry_run=true`, and inspect `/api/v1/retention/scans/{scan_id}` for category errors.
