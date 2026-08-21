# Infrastructure for the Recommendation Agent Service.
# A Bedrock knowledge base backs the retrieval step consumed by the
# Claude 3 recommendation logic in app.py.

resource "aws_bedrock_knowledge_base" "recommendation_kb" {
  name     = "recommendation-agent-kb"
  role_arn = aws_iam_role.recommendation_kb_role.arn
}

resource "aws_iam_role" "recommendation_kb_role" {
  name = "recommendation-agent-kb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "bedrock.amazonaws.com"
      }
    }]
  })
}