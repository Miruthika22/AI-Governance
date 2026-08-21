"""
Recommendation Agent Service
Generates personalized product/content recommendations using OpenAI,
grounded in a retrieval step against a knowledge base.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

MODEL_NAME = os.environ.get(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)


def retrieve_user_context(user_id: str) -> str:
    """
    Placeholder retrieval step against the recommendation knowledge base.
    """
    return (
        f"User {user_id} recently viewed: "
        "wireless headphones, running shoes, yoga mats."
    )


def generate_recommendations(user_id: str) -> str:
    """
    Generates personalized recommendations using OpenAI
    based on retrieved user context.
    """

    context = retrieve_user_context(user_id)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=500,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a product recommendation assistant. "
                    "Recommend relevant products based on the user's "
                    "activity. Be concise and helpful."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Based on this user's activity, recommend "
                    "3 relevant products:\n\n"
                    f"{context}"
                ),
            },
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    print(
        generate_recommendations("user_12345")
    )