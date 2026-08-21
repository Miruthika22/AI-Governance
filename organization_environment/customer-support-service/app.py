"""
Customer Support Agent
Generates and summarizes customer-support responses using an OpenAI GPT-4 model.
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MODEL_NAME = "gpt-4-turbo"


def generate_support_response(customer_message: str, ticket_history: str = "") -> str:
    """
    Calls the OpenAI GPT-4 model to generate a customer-support reply,
    optionally grounded in prior ticket history.
    """
    system_prompt = (
        "You are a customer support assistant. Generate a helpful, "
        "concise response based on the customer's message and any "
        "relevant ticket history."
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Ticket history:\n{ticket_history}\n\nCustomer message:\n{customer_message}"},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def summarize_ticket(ticket_text: str) -> str:
    """Summarizes a long support ticket thread using the same GPT-4 model."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Summarize the following support ticket in 2-3 sentences."},
            {"role": "user", "content": ticket_text},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(generate_support_response("My order hasn't arrived yet."))