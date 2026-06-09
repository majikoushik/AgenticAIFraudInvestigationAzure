# Readiness Assessment Script

This script runs a local production readiness assessment and exports a report.

## Usage

```bash
# Run from project root
cd c:\Koushik\AgenticAIFraudInvestigationAzure

# Full assessment for prod environment
python scripts/readiness/run-readiness-assessment.py --environment prod

# Assessment for specific categories only
python scripts/readiness/run-readiness-assessment.py --categories SECURITY,IDENTITY_AND_ACCESS

# Assessment without auto-creating risks
python scripts/readiness/run-readiness-assessment.py --no-risks

# Export as JSON
python scripts/readiness/run-readiness-assessment.py --format json
```

## Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | Assessment passed (READY or READY_WITH_RISKS) |
| 1 | NOT_READY — blockers found |
| 2 | Script execution error |

## Output

- Console summary with category scores and blocking issues
- Report exported to: `data/exports/readiness/{assessment_id}/production-readiness-report.md`
- Assessment stored in: `data/synthetic/readiness_assessments.json`

## Azure DevOps Integration

Add this step to your Azure DevOps pipeline:

```yaml
- script: |
    pip install -r backend/requirements.txt
    python scripts/readiness/run-readiness-assessment.py \
      --environment prod \
      --fail-on-not-ready
  displayName: 'Production Readiness Check'
  workingDirectory: $(Build.SourcesDirectory)

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: 'data/exports/readiness'
    artifactName: 'readiness-report'
  condition: always()
```
