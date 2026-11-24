# GitHub Actions Docker Push Setup

This guide gives the setup that CI must have to push Docker images to ECR. It also gives the security rules for that setup. For the AWS OIDC provider, see [`OPS.md`](../OPS.md#github-actions-aws-oidc-setup).

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
- The gate is not complete until the old shared role is deleted. See [The Old Shared Role](#the-old-shared-role).

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

## The Old Shared Role

Before this change, back-end used `arn:aws:iam::633607774026:role/GitHubActions-ECR-Push`. Back-end and `OperationCode/operationcode-pybot` both use it today:
- Its trust uses `StringLike` with `repo:...:*` subjects for back-end and pybot. Any branch or pull request of either repository can assume it.
- Its policy allows push to `repository/back-end` and to `repository/pybot`. Thus a session of either repository can overwrite the images of the other.

Each repository moves to its own role on its own: back-end with [Safe Change to the New Role](#safe-change-to-the-new-role) below, pybot with its own `.github/SETUP.md`.

**During either move, nobody changes the old role.** No trust edits, no permission edits, and no "Revoke active sessions".

**The old role is not gated.** It stays open to branch workflows of both repositories until it is deleted. A writer of either repository can edit a workflow on a branch, put the old role ARN in it, and get credentials without an approval. These credentials can push `back-end` and `pybot` images, `:prod` included. The environments do not stop this. The gap closes only when the old role is deleted. The old role is deleted once, after both repositories have completed step 6 of their move (see [Delete the Old Role](#delete-the-old-role)). Until then, a push through this gap is detected, not prevented.

## Safe Change to the New Role

Use this procedure to move back-end from the old shared role to its own role. Do not change the old role (see [The Old Shared Role](#the-old-shared-role)).

If back-end is the first of the two repositories to start its move, write down the time of step 1 (S). The CloudTrail check in [Delete the Old Role](#delete-the-old-role) starts at S - 12 h. If pybot started first, use the time of its step 1.

1. Create the two environments, as given in [Required Environments](#required-environments).
2. Create the new role, as given in [Create the role](#create-the-role). Get the pull request that adds the environments to `ci.yml` approved and green. Do not merge it yet.
3. Set the secret to the new role ARN, as given in [Required Secret](#required-secret). Write down the time of this change (T). After T, each new back-end job uses the new role.
   - Between step 3 and step 5, every push run of the old workflow fails at "Configure AWS credentials", because the new role does not trust its subject. Nobody must push to `main` during this time.
4. Cancel every back-end CI run that is in progress or queued. These runs can hold the old ARN or credentials of the old role.
   ```bash
   # List the runs, then cancel each one.
   for s in in_progress queued; do
     gh run list --repo OperationCode/back-end --status $s --limit 100 --json databaseId --jq '.[].databaseId'
   done | xargs -n 1 gh run cancel --repo OperationCode/back-end
   ```
   To cancel one run: `gh run cancel <id> --repo OperationCode/back-end`. Run the list again until it is empty.
5. Immediately merge the pull request. The push to `main` that the merge causes uses `ecr-main` and the new role, and pushes `:prod`.
   - If the first push fails, correct the new role (see the rules above). Then re-run the job. The re-run uses `ecr-approval`, so a maintainer must approve it.
   - When the push run is complete, write down the image digest of `:prod`. You compare with it in the CloudTrail check:
     `aws ecr describe-images --region us-east-2 --repository-name back-end --image-ids imageTag=prod --query 'imageDetails[0].imageDigest' --output text`
6. Confirm one successful push to `main` through the new role. Use the CloudTrail `AssumeRoleWithWebIdentity` event for the new role ARN:
   ```bash
   aws cloudtrail lookup-events --region us-east-2 \
     --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRoleWithWebIdentity \
     --start-time <T> --output json |
     jq -r '.Events[] | (.CloudTrailEvent | fromjson) as $c
       | select($c.requestParameters.roleArn == "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push-back-end")
       | [.EventTime, $c.requestParameters.roleArn, ($c.userIdentity.userName // "-"),
          ($c.sourceIPAddress // "-"), ($c.errorCode // "ok")] | @tsv'
   ```
   Expect a line with `ok` at the time of the push run, with the subject `repo:OperationCode@10479364/back-end@182584277:environment:ecr-main`. Or use the run log: the `main` push run is green, its job ran in `ecr-main`, and "Build and push Docker image" pushed `back-end:prod`. The back-end move is complete after this step.

## Delete the Old Role

Delete the old role once, after both repositories have completed step 6 of their move: back-end above, and pybot in its own `.github/SETUP.md`. This section is the only deletion procedure. The pybot guide points to it.

1. Delete every inline policy:
   ```bash
   OLD=GitHubActions-ECR-Push
   aws iam list-role-policies --role-name $OLD
   for p in $(aws iam list-role-policies --role-name $OLD --query 'PolicyNames[]' --output text); do
     aws iam delete-role-policy --role-name $OLD --policy-name "$p"
   done
   ```
2. Detach every managed policy:
   ```bash
   OLD=GitHubActions-ECR-Push
   aws iam list-attached-role-policies --role-name $OLD
   for a in $(aws iam list-attached-role-policies --role-name $OLD --query 'AttachedPolicies[].PolicyArn' --output text); do
     aws iam detach-role-policy --role-name $OLD --policy-arn "$a"
   done
   ```
3. Remove the role from each instance profile, if there are any:
   ```bash
   OLD=GitHubActions-ECR-Push
   aws iam list-instance-profiles-for-role --role-name $OLD
   for ip in $(aws iam list-instance-profiles-for-role --role-name $OLD --query 'InstanceProfiles[].InstanceProfileName' --output text); do
     aws iam remove-role-from-instance-profile --instance-profile-name "$ip" --role-name $OLD
   done
   ```
4. Delete the role:
   ```bash
   OLD=GitHubActions-ECR-Push
   aws iam delete-role --role-name $OLD
   ```
5. Confirm. This command must fail with `NoSuchEntity`. Write down the time of this confirmation (D).
   ```bash
   OLD=GitHubActions-ECR-Push
   aws iam get-role --role-name $OLD
   date -u +%Y-%m-%dT%H:%M:%SZ   # D
   ```
6. Delete the old managed policy only if nothing else uses it. The policy has non-default versions (for example `v1`), and `delete-policy` fails with `DeleteConflict` until they are deleted. The block stops if the attachment count is not `0`:
   ```bash
   POLICY=arn:aws:iam::633607774026:policy/GitHubActions-ECR-Push-Policy
   COUNT=$(aws iam get-policy --policy-arn $POLICY --query Policy.AttachmentCount --output text)
   if [ "$COUNT" = "0" ]; then
     aws iam list-policy-versions --policy-arn $POLICY
     for v in $(aws iam list-policy-versions --policy-arn $POLICY \
         --query 'Versions[?IsDefaultVersion==`false`].VersionId' --output text); do
       aws iam delete-policy-version --policy-arn $POLICY --version-id "$v"
     done
     aws iam delete-policy --policy-arn $POLICY
   else
     echo "AttachmentCount is $COUNT: something else uses the policy. Do not delete it."
   fi
   ```

### CloudTrail check of the old role

An IAM change can take time to propagate, so the old role can still issue a session for up to approximately 1 h after D. An ECR login token from such a session stays valid for 12 hours. Thus a token of the old role can push until D + 13 h. An unapproved push in this window is detected, not prevented. When you follow these steps, you accept this risk.

- At D + 13 h plus approximately 30 minutes (CloudTrail can deliver events late), list every ECR write event of the old role, on both ECR repositories, from S - 12 h to D + 13 h:
  ```bash
  for e in InitiateLayerUpload PutImage BatchDeleteImage; do
    aws cloudtrail lookup-events --region us-east-2 \
      --lookup-attributes AttributeKey=EventName,AttributeValue=$e \
      --start-time <S-12h> --end-time <D+13h> --output json |
      jq -r '.Events[] | (.CloudTrailEvent | fromjson) as $c
        | ($c.userIdentity.sessionContext.sessionIssuer.arn // "-") as $role
        | select($role == "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push")
        | [.EventTime, .EventName, .Username, $role,
           ($c.requestParameters.repositoryName // "-"),
           ($c.sourceIPAddress // "-")] | @tsv'
  done
  ```
  The columns are: time, event, `Username`, session issuer ARN, ECR repository, source IP address. The command selects the old role by the session issuer ARN. Do not use `Username` for this: for a role session it is the session name, and the caller chooses it.
- Each event must match a CI run that you know about (time and run) of the repository in the event: `back-end` or `pybot`. After step 4 of a repository's move, no run of that repository uses the old role. Thus an event of the old role on that repository after that time is unexpected.
- `lookup-events` returns only the last 90 days. If D + 13 h is more than 80 days after S, also run this check every 80 days, so that no part of the window is lost.
- The `PutImage` events are the real control. The tag check below shows only the current state of each tag.
- At the same time, make sure that each tag digest is a digest that a known CI run pushed. For back-end `:prod`, this is the digest from step 5, unless a later known run pushed `:prod`. Query each tag on its own:
  ```bash
  for t in prod staging; do
    aws ecr describe-images --region us-east-2 --repository-name back-end \
      --image-ids imageTag=$t --query 'imageDetails[].[imageTags,imageDigest,imagePushedAt]'
  done
  for t in prod latest staging; do
    aws ecr describe-images --region us-east-2 --repository-name pybot \
      --image-ids imageTag=$t --query 'imageDetails[].[imageTags,imageDigest,imagePushedAt]'
  done
  ```
  An `ImageNotFoundException` for a tag means that the tag does not exist. This is not a failure of the check.
- If an event or a digest does not match, push a known-good image again (re-run the default-branch build of that repository with an `ecr-approval` approval) and investigate.

## Deploy to Staging and Prod (maintainers)

Pull requests do not push images. CI never deploys to ECS. The task definitions pin `back-end:prod` and `back-end:staging`, so a deploy is a manual force-new-deployment.

Merging to `main` builds the `runtime` target and pushes `back-end:prod`. Staging gets the same image, so it tests exactly what prod will run.

1. Save the running digest for a rollback, for each service:
   ```bash
   export AWS_PROFILE=operationcode AWS_REGION=us-east-2
   C=operationcode-ecs-us-east-2
   T=$(aws ecs list-tasks --cluster $C --service-name python_backend_prod --query 'taskArns[0]' --output text)
   aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].containers[0].imageDigest' --output text
   ```
2. Staging first. Give `:staging` to the image that the main build pushed:
   ```bash
   M=$(aws ecr batch-get-image --repository-name back-end --image-ids imageTag=prod --query 'images[0].imageManifest' --output text)
   aws ecr put-image --repository-name back-end --image-tag staging --image-manifest "$M"
   aws ecs update-service --cluster $C --service python_backend_staging --force-new-deployment
   aws ecs wait services-stable --cluster $C --services python_backend_staging
   curl -fsS https://api.staging.operationcode.org/healthz
   ```
3. Then prod. Run the same `update-service` and `wait` for `python_backend_prod`, then `curl -fsS https://api.operationcode.org/healthz`.

To roll back: `batch-get-image` with `imageDigest=<saved digest>`, `put-image` that manifest to the tag, then force a new deployment.

Caveat: `deployment_minimum_healthy_percent` is 0 and there is no circuit breaker. Each deploy has a short outage, and there is no automatic rollback.

The `ecr-approval` dispatch (Actions > CI > "Run workflow") still exists for a manual rebuild. It is not the staging path. Read the branch's `.github/workflows/ci.yml` before you approve, because the approved job runs with that file and its credentials can also write `:prod`.

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

- [Full AWS OIDC setup](../OPS.md#github-actions-aws-oidc-setup)
- [GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc)
- [AWS OIDC with GitHub](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
