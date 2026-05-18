# terraform/variables.tf

# Reusable variables declared (bucket name, region, lifecycle days)
variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "bucket_name" {
  type = string
}
