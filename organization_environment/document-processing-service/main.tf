# Infrastructure for the Document Processing Service.
# Embeddings are generated via a SageMaker-hosted model endpoint.

resource "aws_sagemaker_endpoint" "embedding_endpoint" {
  name                 = "document-embedding-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.embedding_config.name
}

resource "aws_sagemaker_endpoint_configuration" "embedding_config" {
  name = "document-embedding-endpoint-config"

  production_variants {
    variant_name           = "primary"
    model_name              = "all-mpnet-base-v2"
    initial_instance_count   = 1
    instance_type            = "ml.m5.large"
  }
}