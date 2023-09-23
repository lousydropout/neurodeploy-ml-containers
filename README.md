# Containers

There is 1 image that is built and deployed in this repo:

1. containerized -- the actual image used by the execution lambda

## Deployment overview

Steps:

1. run `./deploy/west` or `./dev/east` and wait until code build has finished, and then
2. (for the `containerized` image) redeploy `neurodeploy-infra` so that the execution lambda will pull the latest image

## Prerequisites

- ECR account
- S3 bucket

## Steps for creating a Codebuild project

1. Click on create new project
2. For source provider, choose s3 and provide it with the bucket & directory of your choice
3. For environment, choose "Managed Image," "Ubuntu," "Standard," "6.0"
4. Also in environment, check the checkbox under "Privileged"
5. For Buildspec, choose "Insert build commands," click "Switch to editor," and enter the YAML Buildspec commands below with the appropriate `AWS_ACCOUNT_ID` and `REGION`.
6. Go to IAM Policies, find the `CodeBuildS3ReadOnlyPolicy-<project-name>-<region-name>` policy and add permission for it to interacte with ECR:

```json
{
  "Effect": "Allow",
  "Resource": "*",
  "Action": "ecr:*"
}
```

### Buildspec commands

Note: be sure to update the parameters `AWS_ACCOUNT_ID` and `REGION`.

```yaml
version: 0.2

env:
  variables:
    AWS_DEFAULT_REGION: "<REGION>"
    AWS_ACCOUNT_ID: "<AWS_ACCOUNT_ID>"
    CONTAINER_REPOSITORY_URL: <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/<ecr-repo>
    TAG_NAME: latest

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com

  build:
    commands:
      # - cd ./al2/x86_64/standard/1.0
      - docker build --tag $CONTAINER_REPOSITORY_URL:$TAG_NAME .

  post_build:
    commands:
      - docker push $CONTAINER_REPOSITORY_URL
```

### Add the following to the IAM roles created by CodeBuild

```json
{
  "Effect": "Allow",
  "Resource": "*",
  "Action": "ecr:*"
}
```

I was unable to login to ECR without the above.
