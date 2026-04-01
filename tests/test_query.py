#!/usr/bin/env python3

import sys
import time
import random

def simulate_query(question):
    """Simulate a query response for testing purposes"""

    # Simulate processing time
    time.sleep(2)

    # Sample responses based on question content
    responses = {
        "education policy": "Education policy refers to the collection of laws and rules that govern the operation of education systems. Education occurs in many forms for many purposes through many institutions. Examples include early childhood education, kindergarten through to 12th grade, two and four year colleges, graduate and professional education, adult education and job training.",
        "school vouchers": "School vouchers are government-funded scholarships that pay for students to attend private school rather than public school. Vouchers are funded by the government and are usually for a specific dollar amount. Proponents argue they increase school choice and competition, while critics worry they may drain resources from public schools.",
        "federal education funding": "Federal education funding in the United States comes primarily through programs like Title I for disadvantaged students, IDEA for special education, and Pell Grants for higher education. The federal government typically provides about 8-10% of total K-12 education funding, with states and localities providing the majority."
    }

    # Find the most relevant response
    question_lower = question.lower()
    response = "I can help you with education policy questions. Please ask me about topics like school funding, educational standards, school choice, or educational research."

    for key, value in responses.items():
        if key in question_lower:
            response = value
            break

    # Format the response like the real query.py would
    sources = [
        "education_policy_handbook.pdf",
        "federal_funding_guide.pdf",
        "school_choice_research.pdf"
    ]

    output = f"""--- Sources Used ---
{chr(10).join(sources)}
--------------------

Answer:
{response}

"""

    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_query.py 'your question here'")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = simulate_query(question)
    print(result)