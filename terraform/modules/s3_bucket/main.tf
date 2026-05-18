# terraform/modules/s3_bucket/main.tf

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name

  tags = {
    Project = "MSc-Cloud-Computer-Research"
  }
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "ownership" {
  bucket = aws_s3_bucket.this.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lc" {
  bucket = aws_s3_bucket.this.id

  rule {
    id     = "audit-logs-to-glacier"
    status = "Enabled"

    filter {
      prefix = "audit-logs/"
    }

    transition {
      days          = 0
      storage_class = "GLACIER"
    }
  }

  depends_on = [aws_s3_bucket.this, aws_s3_bucket_ownership_controls.ownership]
}
