# SuperElonAI/core/questions.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_api_key_active():
    """Check if the OpenAI API key is active and working."""
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False, "API key not found in environment variables"
    
    try:
        # Create a client instance with the API key
        client = OpenAI(api_key=api_key)
        # Make a minimal API call to test the key
        response = client.models.list(limit=1)
        return True, "API key is active and working"
    except Exception as e:
        return False, f"Error checking API key: {str(e)}"

# --- Cấu hình OpenAI Client ---
try:
    # Get the API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable not set")
        client = None
    else:
        # Create a client instance with the API key
        client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Lỗi không mong muốn khi khởi tạo OpenAI client trong questions.py: {e}")
    client = None


def _query_llm_for_questions(scenario: str, existing_context: dict) -> list[str]:
    if not client:
        return ["Lỗi: OpenAI client (questions.py) chưa được khởi tạo. Vui lòng kiểm tra API key."]

    context_str = "\n".join([f"- {k}: {v}" for k, v in existing_context.items()])
    prompt = f"""
    You are an AI assistant named "Super ElonMusk AI Decision Matrix", designed to help users make optimal decisions by thinking from first principles.
    A user has presented the following scenario:
    "{scenario}"

    They have already provided the following context:
    {context_str if context_str else "No context provided yet."}

    Based on the scenario and existing context, generate up to 3-4 insightful and concise follow-up questions to help clarify the situation further.
    These questions should aim to uncover:
    1. The core objectives and desired outcomes.
    2. Key constraints (time, budget, resources, ethical considerations).
    3. Major known and unknown risks.
    4. Key stakeholders and their perspectives.
    5. Assumptions being made.
    6. What "success" truly looks like.
    7. What has already been tried or considered.

    Do NOT ask questions if the information is already clearly available in the existing context.
    Focus on questions that will significantly improve the understanding needed to build a decision tree.
    Return the questions as a numbered list. Each question should be on a new line.
    Example:
    1. What is the primary metric for success in this project?
    2. Are there any hard deadlines or budget caps we must adhere to?
    
    If you think enough context is provided or the scenario is very simple, you can return "No further clarification questions at this time."
    """
    try:
        # Use the new API format
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a world-class decision-making assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5,
            n=1
        )
        content = response.choices[0].message.content.strip()
        if "No further clarification questions" in content:
            return ["No further clarification questions at this time. Ready to proceed?"]
        questions = [q.strip() for q in content.split('\n') if q.strip() and q[0].isdigit()]
        cleaned_questions = [q.split('.', 1)[1].strip() if '.' in q else q for q in questions]
        return cleaned_questions if cleaned_questions else ["Could not generate specific questions. Is the scenario clear?"]
    except Exception as e:
        print(f"OpenAI API Error (questions.py): {e}")
        return [f"Lỗi API OpenAI khi tạo câu hỏi: {str(e)[:100]}..."]

def generate_clarification_questions(scenario: str, existing_context: dict) -> list[str]:
    if not scenario.strip():
        return ["To begin, please describe the core problem or scenario you'd like to analyze."]
    questions = _query_llm_for_questions(scenario, existing_context)
    if not questions and scenario:
        if not existing_context:
             return ["What is the primary goal?", "Any key constraints (budget, time)?"] # Fallback
        return ["AI has no further questions now. Ready to proceed?"]
    return questions

if __name__ == '__main__':
    # Check if API key is active
    is_active, message = check_api_key_active()
    print(f"API Key Status: {message}")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Vui lòng đặt OPENAI_API_KEY để test questions.py với LLM.")
    else:
        if client and is_active:
            test_scenario = "We are considering a new product launch for a sustainable energy solution."
            test_context = {"Budget": "1M USD", "Target Market": "Urban homeowners"}
            print(f"Scenario: {test_scenario}\nContext: {test_context}")
            print("Generated Questions (from LLM):")
            for q in generate_clarification_questions(test_scenario, test_context):
                print(f"- {q}")
        else:
            print("OpenAI client (questions.py) không được khởi tạo hoặc API key không hoạt động.")