# GitHub Actions Environment Variables Setup

This is a quick reference guide. For complete setup instructions, see [`OPS.md`](../OPS.md#github-actions-aws-oidc-setup).

## Required Secret

The workflow requires one GitHub repository secret:

- **`AWS_ROLE_ARN`**: The ARN of the IAM role that GitHub Actions will assume to push Docker images to ECR

## Setup Steps

### 1. Create AWS IAM Role

**Follow the complete instructions in [`OPS.md`](../OPS.md#github-actions-aws-oidc-setup)** which includes:
- Creating the OIDC identity provider
- Creating the IAM role with trust policy  
- Attaching ECR permissions policy

After completing the AWS setup, you'll have an IAM role ARN (typically: `arn:aws:iam::633607774026:role/GitHubActions-ECR-Push`)

### 2. Add GitHub Secret

Add the IAM role ARN as a GitHub repository secret using the GitHub CLI:

```bash
# Ensure you're authenticated with GitHub CLI
# If not already authenticated, run: gh auth login

# Set the secret (replace with your actual role ARN if different)
gh secret set AWS_ROLE_ARN --body "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push"
```

**Note**: Make sure you're in the repository directory or specify the repo with `--repo operationcode/back-end`.

### 3. Verify Setup

After adding the secret, the workflow will automatically:
- Authenticate to AWS using OIDC (no credentials stored)
- Build Docker images for ARM64 platform
- Push to ECR with appropriate tags:
  - `:staging` for non-main branches
  - `:prod` for main branch (after CI passes)

## Testing

To test the setup:

1. **Test staging build**: Push to any branch except `main`
   - Should trigger Docker build and push to `:staging` tag
   - Check ECR repository to verify image was pushed

2. **Test production build**: Merge to `main` branch
   - Should run lint, test, security checks first
   - If all pass, should build and push to `:prod` tag
   - Check ECR repository to verify image was pushed

## Troubleshooting

### Build fails with "Error assuming role"
- Verify the `AWS_ROLE_ARN` secret is set correctly
- Check that the IAM role exists and has the correct trust policy
- Ensure the OIDC identity provider is configured

### Build fails with "AccessDenied" to ECR
- Verify the IAM role has the ECR push policy attached
- Check that the policy allows access to the correct ECR repository
- Ensure the repository path matches: `633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end`

### Production build runs even when tests fail
- This shouldn't happen - production builds depend on `ci-success` job
- Check that `ci-success` job is properly failing when tests fail
- Verify branch protection rules if using them

## Additional Resources

- Full AWS OIDC setup: See [`OPS.md`](../OPS.md#github-actions-aws-oidc-setup)
- GitHub Actions secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- AWS OIDC with GitHub: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
