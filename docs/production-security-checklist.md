# Production Security Checklist

- [ ] No secrets in repo
- [ ] No secrets in pipeline YAML
- [ ] Key Vault enabled
- [ ] Managed identity enabled
- [ ] Public network disabled where practical
- [ ] Private endpoints enabled for data and AI services
- [ ] Private DNS configured
- [ ] RBAC least privilege assigned
- [ ] Admin keys not used by runtime
- [ ] Diagnostic settings enabled
- [ ] Application Insights configured
- [ ] Audit logs enabled
- [ ] Security health endpoint protected
- [ ] Admin config does not expose secrets
- [ ] Frontend does not receive backend secrets
- [ ] Secret rotation process documented
- [ ] Incident response runbooks available
