# GitHub Actions Docker Push Setup

This guide gives the setup that CI must have to push Docker images to ECR. It also gives the security rules for that setup.

## How pushes are gated

Only maintainers can cause CI to push an image. The workflow file does not enforce this, because a writer can change the file on a branch. GitHub Environments and the AWS trust policy enforce it.

```
pull_request (any author)    --> docker-build        build only, no AWS credentials
push to main, first attempt  --> docker-build-push   environment ecr-main      no wait
workflow_dispatch (any ref)  --> docker-build-push   environment ecr-approval  maintainer approves (manual rebuild)
re-run of any push run       --> docker-build-push   environment ecr-approval  maintainer approves
                                        |
                                        v
     role GitHubActions-ECR-Push-back-end trusts ONLY the ecr-main and ecr-approval subjects
```

- `ecr-main` can skip the wait because the org ruleset on `main` requires a pull request with code-owner review.
- Image tags: `:prod` when the ref is `main`, and `:staging` for all other refs. Both tags are in the same ECR repository.
- The old shared role was deleted. See [The Old Shared Role](#the-old-shared-role-deleted).

## Required Secret

- **`AWS_ROLE_ARN`** (repository secret): the ARN of the IAM role that the push job assumes.

```bash
gh secret set AWS_ROLE_ARN --repo OperationCode/back-end --body "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push-back-end"
```

## Required Environments

Create the two environments in Settings > Environments. Create them **before** a workflow uses them. If a workflow uses an environment that does not exist, GitHub creates it with no protection rules.

| Environment | Required reviewers | Deployment branches and tags |
|---|---|---|
| `ecr-main` | None | "Selected branches and tags", with one **branch** rule: `main`. Do not add a tag rule. Do not use "Protected branches only". |
| `ecr-approval` | The maintainers, at minimum the code owners `irvingpop` and `kylemh` | No restriction |

## AWS Role

The back-end repository has its own role, `GitHubActions-ECR-Push-back-end`. No other repository uses it.

### Trust policy

The repository uses immutable OIDC subjects. To get the prefix, run this command:

```bash
gh api repos/OperationCode/back-end/actions/oidc/customization/sub --jq .sub_claim_prefix
# repo:OperationCode@10479364/back-end@182584277
```

Save this as `be-trust.json`:

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

Rules:
- Use `StringEquals` and these two subjects only. Do not use `StringLike` or `*`.
- Do not add `:pull_request` or `:ref:refs/heads/...` subjects. A writer can get those subjects without approval.
- Do not add subjects of another repository. Each repository gets its own role.
- The role must have only this one `Allow` statement. Examine all statements with this command:
  `aws iam get-role --role-name GitHubActions-ECR-Push-back-end --query Role.AssumeRolePolicyDocument`
- If an assume-role step fails, read the `oidc.sub` line from the "Debug OIDC claims" step. Then correct the environment subject. Never add an old subject back.

### Permissions policy (inline)

Save this as `be-ecr-push.json`. The first statement has the ECR actions of the push job: `docker/build-push-action` checks, uploads, and tags the image. It applies to the `back-end` repository only. `ecr:GetAuthorizationToken` (used by `amazon-ecr-login`) cannot be limited to a repository, so it has its own statement on `*`.

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

### Create the role

The role is defined in [operationcode_infra](https://github.com/OperationCode/operationcode_infra), file `terraform/github_actions_ecr.tf`. Apply it with Terraform. Do not create the role by hand, and do not edit it by hand.

The trust policy and permissions policy above are a reference only. The Terraform file is the source of truth.

To examine the result after the apply:

```bash
aws iam get-role --role-name GitHubActions-ECR-Push-back-end \
  --query 'Role.[Arn,MaxSessionDuration,AssumeRolePolicyDocument]'
aws iam list-role-policies --role-name GitHubActions-ECR-Push-back-end           # only ecr-push-back-end
aws iam list-attached-role-policies --role-name GitHubActions-ECR-Push-back-end  # empty
```

## The Old Shared Role (deleted)

Before back-end had its own role, back-end and `OperationCode/operationcode-pybot` shared `GitHubActions-ECR-Push`. Its trust allowed any branch of either repository.

The role was deleted on 2026-11-23, after both repositories moved to their own roles. The CloudTrail check of its window came back clean. `aws iam get-role --role-name GitHubActions-ECR-Push` now returns `NoSuchEntity`. The gap is closed.

## Deploy to Staging and Prod (maintainers)

The deploy, check, and rollback steps are in [`OPS.md`](../OPS.md#3-deploy-staging-first-then-prod). Read the branch's `.github/workflows/ci.yml` before you approve an `ecr-approval` run, because the approved job runs with that file and its credentials can also write `:prod`.

## Troubleshooting

### Build fails with "Error assuming role"
- Verify the `AWS_ROLE_ARN` secret is set correctly
- Compare the `oidc.sub` line from "Debug OIDC claims" with the subjects in the trust policy
- Make sure the job ran in `ecr-main` or `ecr-approval`

### Build fails with "AccessDenied" to ECR
- Verify the IAM role has the inline policy `ecr-push-back-end`
- Check that the policy allows access to the correct ECR repository
- Ensure the repository path matches: `633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end`

### Production build runs even when tests fail
- This shouldn't happen - production builds depend on `ci-success` job
- Check that `ci-success` job is properly failing when tests fail

## Additional Resources

- [Deploy and rollback runbook](../OPS.md)
- [GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc)
- [AWS OIDC with GitHub](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
