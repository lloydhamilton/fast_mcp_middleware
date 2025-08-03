terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = ">=5.54.1"
    }
    random = {
      source = "hashicorp/random"
      version = "3.6.2"
    }
  }

  backend "s3" {}  # S3 configs will be injected

}

provider "aws" {
  alias = "iam_assume_role"
  assume_role {
    role_arn = var.terraform_assume_role_arn
    session_name = "terraform"
    external_id = "terraform"
  }
  region = "eu-west-2"
}
