PY_VERSION ?= 3.12
USE_DOCKER ?= 1
LAMBDA_ARCH ?= x86_64
FUNCTION_NAME ?= reddit-to-supabase-pipeline
AWS_REGION ?= us-east-2

.PHONY: build build-arm deploy

build:
	PY_VERSION=$(PY_VERSION) USE_DOCKER=$(USE_DOCKER) LAMBDA_ARCH=$(LAMBDA_ARCH) bash deploy/scripts/build_and_zip.sh

build-arm:
	PY_VERSION=$(PY_VERSION) USE_DOCKER=$(USE_DOCKER) LAMBDA_ARCH=arm64 bash deploy/scripts/build_and_zip.sh

deploy: build
	aws lambda update-function-code --function-name $(FUNCTION_NAME) --zip-file fileb://build/package.zip --region $(AWS_REGION)


