# terraform/providers.tf

# Configure the provider (AWS)
provider "aws" {
  region = var.aws_region
}
