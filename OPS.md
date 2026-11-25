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

Each block with checks runs in a subshell `( set -euo pipefail ... )`. It halts at the first failed command or check and prints `STOP: <reason>`. If a block ends with an error, STOP.

Nothing runs database migrations when a task starts. A release that has a new migration needs step 5 (staging) and step 9 (prod). Step 2b checks whether the new code needs the migration *before* it can start. If it does, step 3b runs it before the rollout.

1. Wait for the CI run on `main` to finish and succeed:
   ```bash
   gh run list -R OperationCode/back-end --workflow ci.yml --branch main --limit 3
   ```
2. Save the running digest of each service in a file, and print it. You need it for a rollback. A new terminal loses shell variables, the file does not. Run this step one time per deploy, before step 3. It refuses to overwrite a saved digest, so a failed deploy cannot replace the good digest with a bad one. Step 10 (deploy) and the end of section 4 (rollback) delete the file:
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2
     D=$HOME/back-end-deploy.env
     if [ -s $D ]; then echo "STOP: $D exists: a previous deploy or rollback was not finished. If it was finished, run: rm $D"; exit 1; fi
     W=$(mktemp $D.XXXXXX)   # temp file in the same directory: mv is atomic
     trap 'rm -f $W' EXIT    # a STOP leaves no partial file; after the mv, W is gone
     for S in python_backend_staging python_backend_prod; do
       T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
       G=$(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].containers[0].imageDigest' --output text)
       if [ -z "$G" ] || [ "$G" = None ]; then echo "STOP: no digest for $S"; exit 1; fi
       echo "$(echo ${S#python_backend_} | tr a-z A-Z)_DIGEST=$G" >> $W
     done
     mv $W $D
     cat $D   # copy these two lines to your notes
   )
   ```
2b. Check for a migration that must run before the rollout. List the migration files that are new since the last deploy (`<last deployed commit>` is the `main` commit of the previous deploy):
   ```bash
   git fetch origin && git diff --name-only <last deployed commit> origin/main -- 'src/**/migrations/*.py'
   ```
   Read the files, then choose one path:
   - No files, or the new code can start on the old schema: the **normal path**. Steps 5 and 9 apply the migrations after the rollout.
   - The new code needs the schema change to start (the new task would fail its health check), and the migration is backward-compatible with the old code that still runs (it only adds: new tables, or new columns that are null or have a default): the **migrate-first path**. Do step 3b on staging, and again on prod in step 7.
   - Any other case: STOP and ask a maintainer.

   The task definition pins a tag, not an image. So a one-off task started before the retag of step 3 runs the old image, and the old image does not have the new migration files. A running old task cannot run them for the same reason. That is why step 3b comes after the retag and before the rollout. If the staging task fails its health check with `ProgrammingError` or `no such column` in the logs, a migration that had to run first did not run.
3. Staging: give `:staging` the manifest of `:prod`, and check it:
   ```bash
   (
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     set -euo pipefail
     M=$(aws ecr batch-get-image --repository-name back-end --image-ids imageTag=prod --query 'images[0].imageManifest' --output text)
     if [ -z "$M" ] || [ "$M" = None ]; then echo "STOP: no :prod manifest"; exit 1; fi
     aws ecr put-image --repository-name back-end --image-tag staging --image-manifest "$M"
     P=$(aws ecr describe-images --repository-name back-end --image-ids imageTag=prod --query 'imageDetails[0].imageDigest' --output text)
     Q=$(aws ecr describe-images --repository-name back-end --image-ids imageTag=staging --query 'imageDetails[0].imageDigest' --output text)
     echo ":prod $P, :staging $Q"
     if [ "$P" != "$Q" ]; then echo "STOP: :staging is not :prod"; exit 1; fi
   )
   ```
3b. Migrate-first path only (step 2b). Run `migrate` in a one-off task of the service. The task uses the current task definition of the service, so it pulls the image that the tag has now: the new image. The command override replaces the gunicorn `CMD` of the image (the working directory is `/app/src`):
   ```bash
   export AWS_PROFILE=operationcode AWS_REGION=us-east-2
   C=operationcode-ecs-us-east-2 S=python_backend_staging   # prod (step 7): S=python_backend_prod
   (
     set -euo pipefail
     TD=$(aws ecs describe-services --cluster $C --services $S --query 'services[0].taskDefinition' --output text)
     R=$(aws ecs run-task --cluster $C --task-definition "$TD" --started-by ops-migrate \
       --capacity-provider-strategy capacityProvider=spot_instances,weight=1 \
       --overrides "{\"containerOverrides\":[{\"name\":\"$S\",\"command\":[\"python\",\"manage.py\",\"migrate\",\"--noinput\"]}]}")
     T=$(echo "$R" | jq -r '.tasks[0].taskArn // empty')
     if [ -z "$T" ]; then echo "$R" | jq '.failures'; echo "STOP: no task started"; exit 1; fi
     echo "task: $T"
     aws ecs wait tasks-stopped --cluster $C --tasks "$T"   # about 10 minutes, then exit code 255
     aws logs get-log-events --log-group-name ecs-20221213004720404200000001 --start-from-head \
       --log-stream-name "$S/$S/${T##*/}" --query 'events[].message' --output text || echo "(no log stream)"
     K=$(aws ecs describe-tasks --cluster $C --tasks "$T" --output json)
     X=$(echo "$K" | jq -r '.tasks[0].containers[0].exitCode')
     G=$(echo "$K" | jq -r '.tasks[0].containers[0].imageDigest')
     W=$(aws ecr describe-images --repository-name back-end --image-ids imageTag=${S#python_backend_} --query 'imageDetails[0].imageDigest' --output text)
     echo "exit code $X, task digest $G, tag digest $W, reason: $(echo "$K" | jq -r '.tasks[0].stoppedReason')"
     if [ "$X" != 0 ]; then echo "STOP: migrate failed"; exit 1; fi
     if [ "$G" != "$W" ]; then echo "STOP: the task did not run the new image"; exit 1; fi
     echo "migrate OK"
   )
   ```
   It must print `migrate OK`. Otherwise STOP: do not deploy. Read the log lines that the block prints. If the wait timed out, the task can still be running: check it with `aws ecs describe-tasks` and do not start a second one.
3c. Deploy staging:
   ```bash
   export AWS_PROFILE=operationcode AWS_REGION=us-east-2
   C=operationcode-ecs-us-east-2
   (
     set -euo pipefail
     aws ecs update-service --cluster $C --service python_backend_staging --force-new-deployment
     aws ecs wait services-stable --cluster $C --services python_backend_staging
   )
   ```
4. Check staging. All three must pass:
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2
     S=python_backend_staging U=https://api.staging.operationcode.org/healthz   # prod (step 8): S=python_backend_prod U=https://api.operationcode.org/healthz
     T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
     # a) HEALTHY, and the digest is the digest of :prod
     H=$(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].healthStatus' --output text)
     G=$(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].containers[0].imageDigest' --output text)
     P=$(aws ecr describe-images --repository-name back-end --image-ids imageTag=prod --query 'imageDetails[0].imageDigest' --output text)
     echo "health $H, task $G, :prod $P"
     if [ "$H" != HEALTHY ] || [ "$G" != "$P" ]; then echo "STOP: 4a failed"; exit 1; fi
     # b) HTTP 200
     if ! curl -fsS -o /dev/null -w '%{http_code}\n' "$U"; then echo "STOP: 4b failed"; exit 1; fi
     # c) no errors since the new task started (errors of the old task do not count)
     A=$(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].startedAt' --output text)
     B=$(python3 -c 'import sys,datetime as d; print(int(d.datetime.fromisoformat(sys.argv[1]).timestamp()*1000))' "$A")   # ISO time to epoch ms, same on macOS and Linux
     E=$(aws logs filter-log-events --log-group-name ecs-20221213004720404200000001 \
       --log-stream-name-prefix $S --start-time $B \
       --filter-pattern '?Traceback ?ERROR' --query 'events[].message' --output text)
     if [ -n "$E" ]; then echo "$E"; echo "STOP: 4c found errors"; exit 1; fi
     echo "step 4 OK"
   )
   ```
5. Migrations on staging (the new image has the migration files, so run this after the rollout). First list the pending ones with ECS Exec:
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2 S=python_backend_staging
     T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
     aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate --plan"
   )
   ```
   `No planned migration operations.` means you are done. Otherwise read the plan. Stop if it contains a destructive operation (`RemoveField`, `DeleteModel`, `RunSQL`) that you did not expect. Then apply and check:
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2 S=python_backend_staging
     T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
     aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate"
     aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate --plan"   # must say: No planned migration operations.
   )
   ```
   ECS Exec can return 0 even when the command in the container fails, so read the output. If `migrate` fails, STOP. Do not go to prod. A code rollback does not undo applied migrations.
6. Check staging again after the migration: run the step 4 block again.
7. Prod: `:prod` is already the image, so do not retag. On the migrate-first path, first run the step 3b block with `S=python_backend_prod`. Then deploy:
   ```bash
   export AWS_PROFILE=operationcode AWS_REGION=us-east-2
   C=operationcode-ecs-us-east-2
   (
     set -euo pipefail
     aws ecs update-service --cluster $C --service python_backend_prod --force-new-deployment
     aws ecs wait services-stable --cluster $C --services python_backend_prod
   )
   ```
8. Check prod: run the step 4 block with the prod values of `S` and `U` (in its comment).
9. Migrations on prod. Between step 7 and this step the new code runs on the old schema. Keep this time short, and do not skip the step when staging needed it. List the pending migrations:
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2 S=python_backend_prod
     T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
     aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate --plan"
   )
   ```
   If the plan is not empty, read it (same destructive-operation rule as step 5), then apply and check:
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2 S=python_backend_prod
     T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
     aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate"
     aws ecs execute-command --cluster $C --task "$T" --container $S --interactive --command "python manage.py migrate --plan"   # must say: No planned migration operations.
   )
   ```
10. Finish. When step 8 and step 9 passed, delete the saved digests. A later step 2 refuses to run while the file exists:
   ```bash
   rm $HOME/back-end-deploy.env
   ```

## 4. Roll back

Use the digest saved in deploy step 2 (`cat $HOME/back-end-deploy.env`). Set `ENV` to the environment that failed (`prod` or `staging`), then run the block. If `:TAG` already points at the saved digest, the block skips `put-image` and only redeploys:

```bash
ENV=prod   # or: ENV=staging
(
  set -euo pipefail
  export AWS_PROFILE=operationcode AWS_REGION=us-east-2
  C=operationcode-ecs-us-east-2
  . $HOME/back-end-deploy.env
  S=python_backend_$ENV TAG=$ENV
  case $ENV in prod) DIGEST=$PROD_DIGEST;; staging) DIGEST=$STAGING_DIGEST;; *) echo "STOP: ENV must be prod or staging"; exit 1;; esac
  if [ -z "$DIGEST" ] || [ "$DIGEST" = None ]; then echo "STOP: no saved digest"; exit 1; fi
  CUR=$(aws ecr describe-images --repository-name back-end --image-ids imageTag=$TAG --query 'imageDetails[0].imageDigest' --output text 2>/dev/null || echo none)
  if [ "$CUR" = "$DIGEST" ]; then
    echo "put-image skipped: :$TAG already points at $DIGEST"
  else
    M=$(aws ecr batch-get-image --repository-name back-end --image-ids imageDigest=$DIGEST --query 'images[0].imageManifest' --output text)
    if [ -z "$M" ] || [ "$M" = None ]; then echo "STOP: no manifest for $DIGEST"; exit 1; fi
    aws ecr put-image --repository-name back-end --image-tag $TAG --image-manifest "$M"
  fi
  aws ecs update-service --cluster $C --service $S --force-new-deployment
  aws ecs wait services-stable --cluster $C --services $S
)
```

Verify. Use the same `ENV`. The task digest must equal the saved digest (not `:prod`), the task must be HEALTHY, and the health URL must return 200:

```bash
ENV=prod   # or: ENV=staging
(
  set -euo pipefail
  export AWS_PROFILE=operationcode AWS_REGION=us-east-2
  C=operationcode-ecs-us-east-2
  . $HOME/back-end-deploy.env
  S=python_backend_$ENV
  case $ENV in
    prod) DIGEST=$PROD_DIGEST U=https://api.operationcode.org/healthz;;
    staging) DIGEST=$STAGING_DIGEST U=https://api.staging.operationcode.org/healthz;;
    *) echo "STOP: ENV must be prod or staging"; exit 1;;
  esac
  T=$(aws ecs list-tasks --cluster $C --service-name $S --query 'taskArns[0]' --output text)
  H=$(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].healthStatus' --output text)
  G=$(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].containers[0].imageDigest' --output text)
  echo "health $H, task $G, saved $DIGEST"
  if [ "$H" != HEALTHY ] || [ "$G" != "$DIGEST" ]; then echo "STOP: rollback check failed"; exit 1; fi
  if ! curl -fsS -o /dev/null -w '%{http_code}\n' "$U"; then echo "STOP: health URL failed"; exit 1; fi
  echo "rollback OK"
)
```

Finish. When the block prints `rollback OK`, delete the saved digests. A later step 2 refuses to run while the file exists:

```bash
rm $HOME/back-end-deploy.env
```

- ECR does not keep tag history. If you did not save the digest, you cannot find the old one by tag.
- The ECR lifecycle policy archives untagged images 7 days after the last pull. An archived image can need a restore before it can be pulled.
- A rollback does not undo migrations. If a migration broke the old code, ask a maintainer before you do anything else.
- `:prod` is the tag the next restart pulls. After a prod rollback, a new merge to `main` moves `:prod` again.

## 5. Run a management command (ECS Exec)

ECS Exec is enabled on both services. You need the `session-manager-plugin` (`brew install --cask session-manager-plugin`).

```bash
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
C=operationcode-ecs-us-east-2
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
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
# Follow the logs
aws logs tail ecs-20221213004720404200000001 --log-stream-name-prefix python_backend_prod --follow
# Check that the group name is still correct
aws logs describe-log-groups --log-group-name-prefix ecs-
```

Service state and deployments. `rolloutState` must be `COMPLETED`, and `runningCount` must equal `desiredCount`:

```bash
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
C=operationcode-ecs-us-east-2
aws ecs describe-services --cluster $C --services python_backend_prod \
  --query 'services[0].[runningCount,desiredCount,deployments[].[status,rolloutState,taskDefinition],events[:5].message]'
aws ecs list-tasks --cluster $C --service-name python_backend_prod --desired-status STOPPED
```

If a new task keeps stopping, read the stop reason: `aws ecs describe-tasks --cluster $C --tasks <task ARN> --query 'tasks[0].[stoppedReason,containers[0].reason]'`.

Target group health (one target per group, health path `/healthz`):

```bash
ENV=prod   # or: ENV=staging
(
  set -euo pipefail
  export AWS_PROFILE=operationcode AWS_REGION=us-east-2
  TG=$(aws elbv2 describe-target-groups --names ecs-python-backend-$ENV --query 'TargetGroups[0].TargetGroupArn' --output text)
  aws elbv2 describe-target-health --target-group-arn "$TG"
)
```

The target groups are `ecs-python-backend-prod` and `ecs-python-backend-staging`.

Errors and traces are in Sentry. Configure it with `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`, and `SENTRY_PROFILES_SAMPLE_RATE` (see `example.env`).

## 8. Rotate JWT_SECRET_KEY

`JWT_SECRET_KEY` signs the login tokens (HS256). It is a secret in Secrets Manager, in the JSON secret `prod/python_backend` (key `jwt_secret_key`) for prod and `staging/python_backend` for staging. The task definition reads it at task start. Terraform owns the task definition, so do not edit it by hand.

If the variable is missing from the task definition, the app uses an insecure default from the code. After any task definition change, check that it is still listed (this prints names, not values):

```bash
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
aws ecs describe-task-definition --task-definition python_backend_prod --query 'taskDefinition.containerDefinitions[0].secrets[?name==`JWT_SECRET_KEY`].name' --output text
```

To rotate, do staging first (`SECRET=staging/python_backend`), then prod (`SECRET=prod/python_backend`). Never print the value. This changes one key and keeps the others:

```bash
SECRET=staging/python_backend SVC=python_backend_staging   # prod: prod/python_backend, python_backend_prod
(
  set -euo pipefail
  export AWS_PROFILE=operationcode AWS_REGION=us-east-2
  C=operationcode-ecs-us-east-2
  umask 077; F=$(mktemp); K=$(mktemp); trap 'rm -f "$F" "$K"' EXIT
  openssl rand -base64 64 | tr -d '\n' > $K   # the new key goes through a file, not argv, so ps cannot show it
  aws secretsmanager get-secret-value --secret-id $SECRET --query SecretString --output text \
    | jq --rawfile k $K '.jwt_secret_key=$k' > $F
  if ! test -s $F || ! jq -e 'has("jwt_secret_key")' $F >/dev/null; then echo "STOP: bad secret JSON"; exit 1; fi
  jq 'keys' $F                      # check that all the keys are still there
  aws secretsmanager put-secret-value --secret-id $SECRET --secret-string file://$F
  aws ecs update-service --cluster $C --service $SVC --force-new-deployment
  aws ecs wait services-stable --cluster $C --services $SVC
)
```

Then do the checks of deploy step 4 for that service. The rotation logs out all users (access token 1 hour, refresh token 1 day). To undo it, put the old value back: Secrets Manager keeps the previous version under the label `AWSPREVIOUS`.
