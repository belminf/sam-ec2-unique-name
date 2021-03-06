# sam-ec2-unique-name

AWS SAM package for an AWS Config rule to evaluate uniqueness of EC2 "Name" tag.

### Installing

To install using [`awscli`](http://docs.aws.amazon.com/cli/latest/userguide/installing.html):

```bash
# Variables
S3_BUCKET=foobar                      # S3 bucket for Lambda code
S3_REGION=us-east-1                   # S3 region for above bucket
CFN_TEMPLATE=serverless-output.yaml   # CloudFormation template generated
CFN_STACK=foobar                      # CloudFormation stack name
FAIL_EMPTY=1                          # Whether to fail for empty tags (0=False, 1=True)

# Create S3 bucket for Lambda code
$ aws s3 mb s3://${S3_BUCKET} --region ${S3_REGION}

# Package Lambda code and create CloudFormation template
$ aws cloudformation package --template-file template.yaml --output-template-file ${CFN_TEMPLATE} --s3-bucket ${S3_BUCKET}

# Deploy CloudFormation stack
$ aws cloudformation deploy --template-file ${CFN_TEMPLATE} --stack-name ${S3_BUCKET} --capabilities CAPABILITY_IAM --parameter-overrides FailEmpty=${FAIL_EMPTY}

```

## License

This project is licensed under the MIT License. See [LICENSE.txt](LICENSE.txt) for details.
