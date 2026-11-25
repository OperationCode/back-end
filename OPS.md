# Back-end Operations Runbook

How the back-end is built, deployed, rolled back, and debugged. Each step has a command you can copy. Run all commands from any directory.

Set this once per shell. Every later command uses it:

```bash
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
C=operationcode-ecs-us-east-2
```

## 1. Overview

```
 PR  ---> CI: build only (no push)
 merge to main ---> CI: build + push ECR back-end:prod   (environment ecr-main)
                              |
                              |  nothing deploys by itself
                              v
 you: retag :prod -> :staging, force new deployment  --> python_backend_staging
 you: check staging, then force new deployment       --> python_backend_prod
```

| Service | Image tag | Hostname | Health URL |
|---|---|---|---|
| `python_backend_staging` | `back-end:staging` | `api.staging.operationcode.org` | https://api.staging.operationcode.org/healthz |
| `python_backend_prod` | `back-end:prod` | `api.operationcode.org` | https://api.operationcode.org/healthz |

- Cluster: `operationcode-ecs-us-east-2`. Region: `us-east-2`. Each service runs one task.
- The task definition pins a tag, not a digest. ECS resolves the tag to a digest when a task starts.
- The services are defined in [operationcode_infra](https://github.com/OperationCode/operationcode_infra) (`terraform/apps.tf`). Change settings there, not by hand.

## 2. How images are built

- A pull request builds the image. It pushes nothing.
- A merge to `main` pushes `back-end:prod`. The job runs in the `ecr-main` environment and does not wait.
- A manual run (Actions > CI > "Run workflow") or a re-run of a push needs `ecr-approval`: a maintainer must approve it. A run on a branch other than `main` pushes `:staging`.
- Nothing deploys to ECS automatically. CI never calls ECS.
- Security setup (environments, IAM role, trust policy): [`.github/SETUP.md`](.github/SETUP.md).

## 3. Deploy (staging first, then prod)

Deploys cause a short outage: `deployment_minimum_healthy_percent` is 0 and there is no circuit breaker. ECS stops the old task before it starts the new one. If the new task fails, nothing rolls back: you must do section 4.

1. Wait for the CI run on `main` to finish and succeed:
   ```bash
   gh run list -R OperationCode/back-end --workflow ci.yml --branch main --limit 3
   ```
2. Save the running digest of each service. You need it for a rollback:
   ```bash
   for S in python_backend_staging python_backend_prod; do
     T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
     echo "$S $(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].containers[0].imageDigest' --output text)"
   done
   ```
3. Staging: give `:staging` the manifest of `:prod`, then deploy:
   ```bash
   M=$(aws ecr batch-get-image --repository-name back-end --image-ids imageTag=prod --query 'images[0].imageManifest' --output text)
   aws ecr put-image --repository-name back-end --image-tag staging --image-manifest "$M"
   aws ecs update-service --cluster $C --service python_backend_staging --force-new-deployment
   aws ecs wait services-stable --cluster $C --services python_backend_staging
   ```
4. Check staging. All three must pass:
   ```bash
   S=python_backend_staging
   T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
   # a) HEALTHY, and the digest is the digest of :prod
   aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].[healthStatus,containers[0].imageDigest]' --output text
   aws ecr describe-images --repository-name back-end --image-ids imageTag=prod --query 'imageDetails[0].imageDigest' --output text
   # b) HTTP 200
   curl -fsS -o /dev/null -w '%{http_code}\n' https://api.staging.operationcode.org/healthz
   # c) no errors in the last 15 minutes (no output is good)
   aws logs filter-log-events --log-group-name ecs-20221213004720404200000001 \
     --log-stream-name-prefix python_backend_staging --start-time $(( ($(date +%s) - 900) * 1000 )) \
     --filter-pattern '?Traceback ?ERROR' --query 'events[].message' --output text
   ```
5. Prod: `:prod` is already the image, so do not retag. Deploy:
   ```bash
   aws ecs update-service --cluster $C --service python_backend_prod --force-new-deployment
   aws ecs wait services-stable --cluster $C --services python_backend_prod
   ```
6. Check prod: repeat step 4 with `S=python_backend_prod`, the prefix `python_backend_prod`, and https://api.operationcode.org/healthz.

If a check fails, go to section 4.

## 4. Roll back

Use the digest you saved in deploy step 2. For prod:

```bash
DIGEST=sha256:<saved digest>
M=$(aws ecr batch-get-image --repository-name back-end --image-ids imageDigest=$DIGEST --query 'images[0].imageManifest' --output text)
aws ecr put-image --repository-name back-end --image-tag prod --image-manifest "$M"
aws ecs update-service --cluster $C --service python_backend_prod --force-new-deployment
aws ecs wait services-stable --cluster $C --services python_backend_prod
```

Then do the checks of deploy step 4 for prod. For staging, use `--image-tag staging` and `python_backend_staging`.

- ECR does not keep tag history. If you did not save the digest, you cannot find the old one by tag.
- The ECR lifecycle policy archives untagged images 7 days after the last pull. An archived image can need a restore before it can be pulled.
- `:prod` is the tag the next restart pulls. After a rollback, a new merge to `main` moves `:prod` again.

## 5. Run a management command (ECS Exec)

ECS Exec is enabled on both services. You need the `session-manager-plugin` (`brew install --cask session-manager-plugin`).

```bash
S=python_backend_prod   # or python_backend_staging
T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py shell"
```

The working directory is `/app/src`. For other commands, replace `python manage.py shell`, for example `python manage.py showmigrations`.

**Warning:** this is a shell inside the live container with database access. Use staging first. Prefer read-only commands. Do not change data unless you have a reviewed plan.

## 6. Dependency updates

Policy:

- Dependabot opens one grouped minor/patch pull request per ecosystem (Python, GitHub Actions) each week, on Monday. Docker base-image updates are patch only.
- Dependabot ignores major versions. A security fix that needs a major shows only as a Dependabot alert. Apply it by hand.
- The Dependabot cooldown is 3 days. It matches the 72-hour supply-chain rule of the org PR reviewer: do not take a release that is less than 72 hours old.
- Never apply a major version, unless a security fix requires it.

To update by hand:

1. Update within the constraints of `pyproject.toml`:
   ```bash
   poetry update
   ```
2. Check the release date of each changed package. Put back any version that is less than 72 hours old (`poetry add "<package>@<previous version>"`, or edit `poetry.lock` back with `git checkout -p poetry.lock`).
3. Run the same checks as CI (the Makefile has them):
   ```bash
   make ci      # ruff check, ruff format --check, pytest with coverage, bandit
   ```
4. Open one pull request with the `pyproject.toml` and `poetry.lock` changes. After the merge, deploy as in section 3.

## 7. Logs and troubleshooting

All containers write to one CloudWatch log group, `ecs-20221213004720404200000001`. The stream prefix is `python_backend_prod` or `python_backend_staging`.

```bash
# Follow the logs
aws logs tail ecs-20221213004720404200000001 --log-stream-name-prefix python_backend_prod --follow
# Check that the group name is still correct
aws logs describe-log-groups --log-group-name-prefix ecs-
```

Service state and deployments. `rolloutState` must be `COMPLETED`, and `runningCount` must equal `desiredCount`:

```bash
aws ecs describe-services --cluster $C --services python_backend_prod \
  --query 'services[0].[runningCount,desiredCount,deployments[].[status,rolloutState,taskDefinition],events[:5].message]'
aws ecs list-tasks --cluster $C --service-name python_backend_prod --desired-status STOPPED
```

If a new task keeps stopping, read the stop reason: `aws ecs describe-tasks --cluster $C --tasks <task ARN> --query 'tasks[0].[stoppedReason,containers[0].reason]'`.

Target group health (one target per group, health path `/healthz`):

```bash
aws elbv2 describe-target-groups --query 'TargetGroups[?contains(TargetGroupName,`python-backend`)].[TargetGroupName,TargetGroupArn]' --output text
aws elbv2 describe-target-health --target-group-arn <TargetGroupArn>
```

Errors and traces are in Sentry. Configure it with `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`, and `SENTRY_PROFILES_SAMPLE_RATE` (see `example.env`).
