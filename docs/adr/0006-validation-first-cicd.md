# 6. Validation-First CI/CD

Date: 2026-06-23

## Status
Accepted

## Context
A portfolio project needs to demonstrate CI/CD capabilities, but actual deployments require Azure subscriptions, credentials, and incurred costs which are difficult to distribute safely.

## Decision
The Azure DevOps pipeline is configured as "validation-first." It runs real build, test, linting, and Bicep validation steps to prove the code is sound. However, the deployment stages (pushing to ACR, applying Bicep, updating Container Apps) are implemented as explicit templates/placeholders using `echo` commands.

## Consequences
- **Positive:** Reviewers can clearly see a realistic pipeline structure without the author needing to embed real secrets or pay for continuous cloud deployments.
- **Negative:** The deployment steps cannot be tested end-to-end without a user providing their own Azure environment and configuring the placeholders.
