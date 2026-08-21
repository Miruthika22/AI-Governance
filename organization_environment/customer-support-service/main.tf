# Infrastructure for the Customer Support Agent.
# The agent is deployed as an AWS Bedrock-based conversational agent,
# fronting the GPT-4 integration defined in app.py.

resource "aws_bedrock_agent" "customer_support_agent" {
  agent_name              = "customer-support-agent"
  description              = "Handles customer support responses and ticket summarization"
  idle_session_ttl_seconds = 600
}

resource "aws_iam_role" "support_agent_role" {
  name = "customer-support-agent-role"

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