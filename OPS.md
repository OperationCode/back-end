# Deploying a new backend version

The backend is deployed to AWS ECS (Elastic Container Service) with separate staging and production environments.

## Building and Pushing Docker Images

Use the `docker-build.sh` script to build multi-architecture images and push to AWS ECR:

```bash
# Build and push staging images
./docker-build.sh staging

# Build and push production images
./docker-build.sh prod
```

This creates:
- `back-end:staging-amd64` and `back-end:staging-arm64` images
- A multi-arch manifest at `back-end:staging`

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

