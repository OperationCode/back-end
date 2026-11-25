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
- A manual run (Actions > CI > "Run workflow") or a re-run of a push needs `ecr-approval`: a maintainer must approve it. A run on a branch other than `main` pushes `:staging`. Do not use it to deploy staging: use section 3. The approved job runs the `ci.yml` of that branch, and its credentials can also write `:prod`, so read that file before you approve.
- Do not use `docker-build.sh` to deploy. It pushes from a laptop and skips the gates.
- Nothing deploys to ECS automatically. CI never calls ECS.
- Security setup (environments, IAM role, trust policy): [`.github/SETUP.md`](.github/SETUP.md).

## 3. Deploy (staging first, then prod)

Deploys cause a short outage: `deployment_minimum_healthy_percent` is 0 and there is no circuit breaker. ECS stops the old task before it starts the new one. If the new task fails, nothing rolls back: you must do section 4.

**Stop rule:** if any step or check below fails, STOP. Do not go on to prod. Go to section 4 and roll back the environment that failed. A `wait services-stable` that times out (about 10 minutes, exit code 255) is a failure.

Nothing runs database migrations when a task starts. A release that has a new migration needs step 5 (staging) and step 9 (prod). Step 2b checks whether the new code needs the migration *before* it can start.

1. Wait for the CI run on `main` to finish and succeed:
   ```bash
   gh run list -R OperationCode/back-end --workflow ci.yml --branch main --limit 3
   ```
2. Save the running digest of each service in a file, and print it. You need it for a rollback. A new terminal loses shell variables, the file does not:
   ```bash
   D=$HOME/back-end-deploy.env; : > $D
   for S in python_backend_staging python_backend_prod; do
     T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
     G=$(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].containers[0].imageDigest' --output text)
     echo "$(echo ${S#python_backend_} | tr a-z A-Z)_DIGEST=$G" >> $D
   done
   cat $D   # copy these two lines to your notes. Stop if a value is empty or None.
   ```
2b. Check for a migration that must run before the rollout. List the migration files that are new since the last deploy (`<last deployed commit>` is the `main` commit of the previous deploy):
   ```bash
   git fetch origin && git diff --name-only <last deployed commit> origin/main -- 'src/**/migrations/*.py'
   ```
   No output: go on to step 3. If there are files, read them. If the new code can start on the old schema, go on: step 5 and step 9 apply them after the rollout. If the new code needs the schema change to start (the new task would fail its health check), the order is migrate first. A running old task cannot do this: its image does not contain the new migration files. Run `python manage.py migrate` from the new image instead (a one-off task of the service task definition, with the command overridden), and only if the migration is backward-compatible with the old code (it only adds: new tables, or new columns that are null or have a default). Otherwise STOP and ask a maintainer. The one-off task is not tested here. Staging goes first, so a mistake costs only staging: if the staging task fails its health check with `ProgrammingError` or `no such column` in the logs, this is the cause.
3. Staging: give `:staging` the manifest of `:prod`, check it, then deploy:
   ```bash
   M=$(aws ecr batch-get-image --repository-name back-end --image-ids imageTag=prod --query 'images[0].imageManifest' --output text)
   test -n "$M" -a "$M" != None || { echo "no :prod manifest: STOP"; false; }
   aws ecr put-image --repository-name back-end --image-tag staging --image-manifest "$M"
   for t in prod staging; do aws ecr describe-images --repository-name back-end --image-ids imageTag=$t --query 'imageDetails[0].imageDigest' --output text; done   # the two digests must be equal
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
5. Migrations on staging (the new image has the migration files, so run this after the rollout). First list the pending ones (ECS Exec, see section 5 for `$T`):
   ```bash
   aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate --plan"
   ```
   `No planned migration operations.` means you are done. Otherwise read the plan. Stop if it contains a destructive operation (`RemoveField`, `DeleteModel`, `RunSQL`) that you did not expect. Then apply and check:
   ```bash
   aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate"
   aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate --plan"   # must say: No planned migration operations.
   ```
   If `migrate` fails, STOP. Do not go to prod. A code rollback does not undo applied migrations.
6. Check staging again (steps 4b and 4c) after the migration.
7. Prod: `:prod` is already the image, so do not retag. Deploy:
   ```bash
   aws ecs update-service --cluster $C --service python_backend_prod --force-new-deployment
   aws ecs wait services-stable --cluster $C --services python_backend_prod
   ```
8. Check prod: repeat step 4 with `S=python_backend_prod`, the prefix `python_backend_prod`, and https://api.operationcode.org/healthz.
9. Migrations on prod: repeat step 5 with the prod `$S` and `$T`. Between step 7 and step 9 the new code runs on the old schema. Keep this time short, and do not skip the step when staging needed it.

## 4. Roll back

Use the digest saved in deploy step 2 (`cat $HOME/back-end-deploy.env`). Set `S` and `TAG` for the environment that failed, then run the block:

```bash
. $HOME/back-end-deploy.env
S=python_backend_prod TAG=prod DIGEST=$PROD_DIGEST            # prod
# S=python_backend_staging TAG=staging DIGEST=$STAGING_DIGEST   # staging
test -n "$DIGEST" -a "$DIGEST" != None || { echo "no saved digest: STOP"; false; }
M=$(aws ecr batch-get-image --repository-name back-end --image-ids imageDigest=$DIGEST --query 'images[0].imageManifest' --output text)
aws ecr put-image --repository-name back-end --image-tag $TAG --image-manifest "$M"
aws ecs update-service --cluster $C --service $S --force-new-deployment
aws ecs wait services-stable --cluster $C --services $S
```

Verify. The task digest must equal `$DIGEST` (the saved digest, not `:prod`), the task must be HEALTHY, and the health URL must return 200:

```bash
T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].[healthStatus,containers[0].imageDigest]' --output text
echo "$DIGEST"
```

- ECR does not keep tag history. If you did not save the digest, you cannot find the old one by tag.
- The ECR lifecycle policy archives untagged images 7 days after the last pull. An archived image can need a restore before it can be pulled.
- A rollback does not undo migrations. If a migration broke the old code, ask a maintainer before you do anything else.
- `:prod` is the tag the next restart pulls. After a prod rollback, a new merge to `main` moves `:prod` again.

## 5. Run a management command (ECS Exec)

ECS Exec is enabled on both services. You need the `session-manager-plugin` (`brew install --cask session-manager-plugin`).

```bash
S=python_backend_prod   # or python_backend_staging
T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py shell"
```

The working directory is `/app/src`. For other commands, replace `python manage.py shell`, for example `python manage.py showmigrations`. Type `exit` to leave. The container runs as a non-root user.

**Warning:** this is a shell inside the live container with database access. Use staging first. Prefer read-only commands. Do not change data unless you have a reviewed plan. The session is recorded only in CloudTrail.

## 6. Dependency updates

Policy:

- Dependabot runs each Monday. Python and GitHub Actions: one grouped minor/patch pull request each. Docker: no group and no cooldown, and the `python` base image takes patch updates only.
- Dependabot ignores major versions. A security fix that needs a major shows only as a Dependabot alert. Apply it by hand.
- The cooldown for Python and GitHub Actions is 3 days. It matches the 72-hour supply-chain rule of the org PR reviewer: do not take a release that is less than 72 hours old.
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

## 8. Rotate JWT_SECRET_KEY

`JWT_SECRET_KEY` signs the login tokens (HS256). It is a secret in Secrets Manager, in the JSON secret `prod/python_backend` (key `jwt_secret_key`) for prod and `staging/python_backend` for staging. The task definition reads it at task start. Terraform owns the task definition, so do not edit it by hand.

If the variable is missing from the task definition, the app uses an insecure default from the code. After any task definition change, check that it is still listed (this prints names, not values):

```bash
aws ecs describe-task-definition --task-definition python_backend_prod --query 'taskDefinition.containerDefinitions[0].secrets[?name==`JWT_SECRET_KEY`].name' --output text
```

To rotate, do staging first (`SECRET=staging/python_backend`), then prod (`SECRET=prod/python_backend`). Never print the value. This changes one key and keeps the others:

```bash
SECRET=staging/python_backend SVC=python_backend_staging   # prod: prod/python_backend, python_backend_prod
(
  set -euo pipefail
  umask 077; F=$(mktemp); trap 'rm -f "$F"' EXIT
  aws secretsmanager get-secret-value --secret-id $SECRET --query SecretString --output text \
    | jq --arg k "$(openssl rand -base64 64 | tr -d '\n')" '.jwt_secret_key=$k' > $F
  test -s $F && jq -e 'has("jwt_secret_key")' $F >/dev/null   # not empty, key present
  jq 'keys' $F                      # check that all the keys are still there
  aws secretsmanager put-secret-value --secret-id $SECRET --secret-string file://$F
  aws ecs update-service --cluster $C --service $SVC --force-new-deployment
  aws ecs wait services-stable --cluster $C --services $SVC
)
```

Then do the checks of deploy step 4 for that service. The rotation logs out all users (access token 1 hour, refresh token 1 day). To undo it, put the old value back: Secrets Manager keeps the previous version under the label `AWSPREVIOUS`.
