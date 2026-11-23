# GitHub Actions Docker Push Setup

This guide gives the setup that CI must have to push Docker images to ECR. It also gives the security rules for that setup. For the AWS OIDC provider and the ECR policy, see [`OPS.md`](../OPS.md#github-actions-aws-oidc-setup).

## How pushes are gated

Only maintainers can cause CI to push an image. The workflow file does not enforce this, because a writer can change the file on a branch. GitHub Environments and the AWS trust policy enforce it.

```
pull_request (any author)    --> docker-build        build only, no AWS credentials
push to main, first attempt  --> docker-build-push   environment ecr-main      no wait
workflow_dispatch (any ref)  --> docker-build-push   environment ecr-approval  maintainer approves
re-run of any push run       --> docker-build-push   environment ecr-approval  maintainer approves
                                        |
                                        v
           AWS role trust accepts ONLY the ecr-main and ecr-approval subjects
```

- `ecr-main` can skip the wait because the org ruleset on `main` requires a pull request with code-owner review.
- Image tags: `:prod` when the ref is `main`, and `:staging` for all other refs. Both tags are in the same ECR repository.

## Required Secret

- **`AWS_ROLE_ARN`**: the ARN of the IAM role that the push job assumes, for example `arn:aws:iam::633607774026:role/GitHubActions-ECR-Push`.

```bash
gh secret set AWS_ROLE_ARN --repo OperationCode/back-end --body "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push"
```

## Required Environments

Create the two environments in Settings > Environments. Create them **before** a workflow uses them. If a workflow uses an environment that does not exist, GitHub creates it with no protection rules.

| Environment | Required reviewers | Deployment branches and tags |
|---|---|---|
| `ecr-main` | None | "Selected branches and tags", with one **branch** rule: `main`. Do not add a tag rule. Do not use "Protected branches only". |
| `ecr-approval` | The maintainers, at minimum the code owners `irvingpop` and `kylemh` | No restriction |

## AWS Trust Policy Subjects

The repository uses immutable OIDC subjects. To get the prefix, run this command:

```bash
gh api repos/OperationCode/back-end/actions/oidc/customization/sub --jq .sub_claim_prefix
# repo:OperationCode@10479364/back-end@182584277
```

The role trust must use `StringEquals` and these two subjects only:

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": [
      "repo:OperationCode@10479364/back-end@182584277:environment:ecr-main",
      "repo:OperationCode@10479364/back-end@182584277:environment:ecr-approval"
    ]
  }
}
```

Rules:
- Do not use `StringLike` or `*`.
- Do not add `:pull_request` or `:ref:refs/heads/...` subjects. A writer can get those subjects without approval.
- The role must have only this one `Allow` statement for the GitHub OIDC provider. Examine all statements with this command:
  `aws iam get-role --role-name GitHubActions-ECR-Push --query Role.AssumeRolePolicyDocument`
- If an assume-role step fails, read the `oidc.sub` line from the "Debug OIDC claims" step. Then correct the environment subject. Never add an old subject back.

## Safe Change of the Trust Policy

Use this procedure when you change from an older trust policy. It makes sure that no unapproved credential path stays open during the change.

1. Create the two environments, as given in [Required Environments](#required-environments).
2. Get the pull request that adds the environments to `ci.yml` approved and green. Do not merge it yet.
3. Make sure that no CI run is in progress or queued:
   `gh run list --repo OperationCode/back-end --status in_progress` and `--status queued`. Cancel any run that you find.
4. Replace the trust policy with the environment-only policy above, in one `aws iam update-assume-role-policy` call. Examine all statements again.
5. Revoke the sessions that the old trust issued: IAM > Roles > the role > "Revoke active sessions". Do this before the merge, so that the revocation does not stop the first `ecr-main` build. A trust change does not cancel credentials that were already issued:
   - An STS session stays valid for up to the role's maximum session duration. Get it with `aws iam get-role --role-name GitHubActions-ECR-Push --query Role.MaxSessionDuration`. The default is 3600 seconds, and `configure-aws-credentials` asks for 1 hour by default.
   - An ECR login token (`GetAuthorizationToken`) stays valid for 12 hours.
   - Look in CloudTrail for ECR pushes in the 12 hours before step 4 that did not come from CI runs you know about.
6. Immediately merge the pull request. The push to `main` that the merge causes uses `ecr-main` and pushes `:prod`.
   - Between step 4 and step 6, every push run of the old workflow fails at "Configure AWS credentials". Nobody must push to `main` during this time.
   - If the first push fails, correct the trust subject (see the rules above). Then re-run the job. The re-run uses `ecr-approval`, so a maintainer must approve it.

## Push a Staging Image (maintainers)

Pull requests do not push images. To push `:staging` from a branch:

1. Go to Actions > CI > "Run workflow". Select the branch. You can also run `gh workflow run ci.yml --repo OperationCode/back-end --ref <branch>`.
2. The `Build and Push Docker Image` job waits for the `ecr-approval` review.
3. Before you approve, read the commit **and** `.github/workflows/ci.yml` on that branch. The approved job runs with the branch's workflow file. Its credentials can also write `:prod`.
4. Approve the deployment. The job pushes `back-end:staging`.

A dispatch on `main` pushes `:prod`, and it also needs approval.

## Troubleshooting

### Build fails with "Error assuming role"
- Verify the `AWS_ROLE_ARN` secret is set correctly
- Compare the `oidc.sub` line from "Debug OIDC claims" with the subjects in the trust policy
- Make sure the job ran in `ecr-main` or `ecr-approval`

### Build fails with "AccessDenied" to ECR
- Verify the IAM role has the ECR push policy attached
- Check that the policy allows access to the correct ECR repository
- Ensure the repository path matches: `633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end`

### Production build runs even when tests fail
- This shouldn't happen - production builds depend on `ci-success` job
- Check that `ci-success` job is properly failing when tests fail

## Additional Resources

- [Full AWS OIDC setup](../OPS.md#github-actions-aws-oidc-setup)
- [GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc)
- [AWS OIDC with GitHub](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
