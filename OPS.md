# Deploying a new backend version

The backend is deployed to AWS ECS (Elastic Container Service) with separate staging and production environments.

## Building and Pushing Docker Images

### Automated Builds (Recommended)

Docker images are automatically built and pushed to AWS ECR via GitHub Actions:

- **Pull requests**: build only, no push
- **Manual dispatch** on any branch: pushes to `:staging` (`:prod` on `main`) after a maintainer approves the `ecr-approval` environment. See [`.github/SETUP.md`](.github/SETUP.md)
- **main branch**: Automatically builds and pushes to `:prod` tag after CI checks pass

The automated builds use AWS OIDC for secure authentication (no long-lived credentials).

### Manual Builds (Legacy)

For manual builds, use the `docker-build.sh` script:

```bash
# Build and push staging images
./docker-build.sh staging

# Build and push production images
./docker-build.sh prod
```

This creates ARM64 images tagged as `back-end:staging` or `back-end:prod`.

## Deploying to ECS

After images are pushed to ECR, deploy by updating the ECS service:

1. **Update task definition** with new image tag
2. **Deploy to staging first** - Update ECS service to use new task definition
3. **Monitor logs** in CloudWatch or Sentry
4. **Validate staging** (see below)
5. **Deploy to production** - Repeat for production ECS service

## Important: JWT Secret Key Migration

**Before deploying these performance changes**, you must update the production `JWT_SECRET_KEY` environment variable:

1. Generate a new secret: `openssl rand -base64 64 | tr -d '\n'`
2. Set `JWT_SECRET_KEY` env var in ECS task definition to the generated string
3. Remove `JWT_PUBLIC_KEY` env var (no longer needed with HS256)

⚠️ **This will log out all users** (one-time migration from RS256 to HS256)

# Validating the staging environment

This requires a working node or docker environment.  I found docker to be easier and more reliable but that was me :shrug:

When you run the front-end repo in localdev mode, it automatically connects to the staging environment.
1. install dependencies:  `docker run -it -v ${PWD}:/src -w /src node:lts yarn`
2. run the dev server:  `docker run -it -v ${PWD}:/src -w /src -p 127.0.0.1:3000:3000/tcp node:lts yarn dev --hostname 0.0.0.0`
3. Connect to the dev server: `open http://localhost:3000`

# Monitoring

## Sentry Performance Monitoring

The application is instrumented with Sentry for error tracking and performance monitoring:
- Error tracking with breadcrumbs and context
- Transaction tracing for HTTP requests
- Database query performance tracking
- Python profiling for CPU-intensive operations

Configure via environment variables (see `example.env`):
- `SENTRY_DSN` - Sentry project DSN
- `SENTRY_TRACES_SAMPLE_RATE` - Percentage of requests to trace (0.0-1.0)
- `SENTRY_PROFILES_SAMPLE_RATE` - Percentage of transactions to profile (0.0-1.0)

## CloudWatch Logs

Application logs are sent to CloudWatch Logs. Access via AWS Console or CLI:

```bash
# View recent logs for staging
aws logs tail /ecs/back-end-staging --follow

# View recent logs for production
aws logs tail /ecs/back-end-production --follow
```

# GitHub Actions AWS OIDC Setup

The CI/CD pipeline uses AWS OIDC (OpenID Connect) for secure authentication to AWS without storing long-lived credentials. This follows AWS security best practices.

## Prerequisites

- AWS account with ECR repository: `633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end`
- GitHub repository: `operationcode/back-end`
- AWS IAM permissions to create IAM roles and policies

## Setup Instructions

### 1. Create IAM OIDC Identity Provider

If not already configured, create an OIDC identity provider for GitHub:

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### 2. Create IAM Role for GitHub Actions

Back-end has its own role, `GitHubActions-ECR-Push-back-end`. Do not share it with another repository. The old role `GitHubActions-ECR-Push` is shared with `operationcode-pybot` and is deleted after both repositories move to their own roles. For the change procedure and the open gap until then, see [`.github/SETUP.md`](.github/SETUP.md#the-old-shared-role).

The role is defined in [operationcode_infra](https://github.com/OperationCode/operationcode_infra), file `terraform/github_actions_ecr.tf`. Apply it with Terraform. Do not create the role by hand, and do not edit it by hand. The Terraform file is the source of truth. The JSON below is a reference only.

The trust policy accepts only the `ecr-main` and `ecr-approval` environments of `OperationCode/back-end`, with `StringEquals`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::633607774026:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": [
            "repo:OperationCode@10479364/back-end@182584277:environment:ecr-main",
            "repo:OperationCode@10479364/back-end@182584277:environment:ecr-approval"
          ]
        }
      }
    }
  ]
}
```

### 3. Add the ECR Permissions Policy

An inline policy allows push to the `back-end` ECR repository only. `ecr:GetAuthorizationToken` cannot be limited to a repository, so it is on `*`. Terraform also manages this policy. Reference:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "arn:aws:ecr:us-east-2:633607774026:repository/back-end"
    },
    {
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    }
  ]
}
```

### 4. Configure GitHub Secret

Add the IAM role ARN as a repository secret:

```bash
gh secret set AWS_ROLE_ARN --repo OperationCode/back-end --body "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push-back-end"
```

### 5. Verify Setup

After setup, the GitHub Actions workflow will automatically:
- Authenticate to AWS using OIDC
- Build Docker images for ARM64 platform
- Push images to ECR with appropriate tags (`:prod` from `main`, `:staging` from an approved dispatch)

You can verify by:
1. Running the workflow with a dispatch on a non-main branch and approving `ecr-approval` (should push `:staging`)
2. Merging to main (should push `:prod` after tests pass)
3. Checking ECR repository for new images

## Security Best Practices

✅ **OIDC Authentication**: No long-lived AWS credentials stored in GitHub  
✅ **Least Privilege**: IAM role only has permissions needed for ECR push operations, on the `back-end` repository only  
✅ **Repository Scoping**: Trust policy of the back-end role accepts only the `ecr-main` and `ecr-approval` environments of `OperationCode/back-end` (the old shared role stays open until it is deleted)  
✅ **Conditional Access**: Production builds only run after CI checks pass  
✅ **Build Caching**: Uses GitHub Actions cache to speed up builds

