# terraform/main.tf

# main resources
module "s3" {
  source      = "./modules/s3_bucket"
  bucket_name = var.bucket_name
  region      = var.aws_region
}
