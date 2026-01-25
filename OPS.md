# Deploying a new backend version

The backend is deployed to AWS ECS (Elastic Container Service) with separate staging and production environments.

## Building and Pushing Docker Images

### Automated Builds (Recommended)

Docker images are automatically built and pushed to AWS ECR via GitHub Actions:

- **PR branches** (any branch except `main`): Automatically builds and pushes to `:staging` tag
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

Create an IAM role that GitHub Actions can assume:

```bash
# Create trust policy file
cat > github-actions-trust-policy.json <<EOF
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
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:operationcode/back-end:*"
        }
      }
    }
  ]
}
EOF

# Create the role
aws iam create-role \
  --role-name GitHubActions-ECR-Push \
  --assume-role-policy-document file://github-actions-trust-policy.json \
  --description "Allows GitHub Actions to push Docker images to ECR"
```

### 3. Attach ECR Permissions Policy

Create and attach a policy that allows pushing to ECR:

```bash
# Create policy file
cat > ecr-push-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
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
EOF

# Create the policy
aws iam create-policy \
  --policy-name GitHubActions-ECR-Push-Policy \
  --policy-document file://ecr-push-policy.json

# Attach policy to role
aws iam attach-role-policy \
  --role-name GitHubActions-ECR-Push \
  --policy-arn arn:aws:iam::633607774026:policy/GitHubActions-ECR-Push-Policy
```

### 4. Configure GitHub Secret

Add the IAM role ARN as a GitHub repository secret using the GitHub CLI:

```bash
# Ensure you're authenticated with GitHub CLI
# If not already authenticated, run: gh auth login

# Set the secret (replace with your actual role ARN if different)
gh secret set AWS_ROLE_ARN --body "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push"
```

**Note**: Make sure you're in the repository directory or specify the repo with `--repo operationcode/back-end`.

### 5. Verify Setup

After setup, the GitHub Actions workflow will automatically:
- Authenticate to AWS using OIDC
- Build Docker images for ARM64 platform
- Push images to ECR with appropriate tags (`:staging` or `:prod`)

You can verify by:
1. Pushing a commit to a non-main branch (should push `:staging`)
2. Merging to main (should push `:prod` after tests pass)
3. Checking ECR repository for new images

## Security Best Practices

✅ **OIDC Authentication**: No long-lived AWS credentials stored in GitHub  
✅ **Least Privilege**: IAM role only has permissions needed for ECR push operations  
✅ **Repository Scoping**: Trust policy restricts access to `operationcode/back-end` repository  
✅ **Conditional Access**: Production builds only run after CI checks pass  
✅ **Build Caching**: Uses GitHub Actions cache to speed up builds

