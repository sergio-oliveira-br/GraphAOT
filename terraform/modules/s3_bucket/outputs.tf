# terraform/modules/s3_bucket/outputs.tf

# Expose ARN, bucket name, useful URIs
output "bucket_arn" {
  value = aws_s3_bucket.this.arn
}

output "bucket_name" {
  value = aws_s3_bucket.this.bucket
}
