# SuperElonAI/core/gemini_engine.py
import os
import json
import uuid
import google.generativeai as genai
from dotenv import load_dotenv
import networkx as nx

# Load environment variables from .env file
load_dotenv()

# Configure the Google Generative AI client
try:
    # Get the API key from environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY environment variable not set")
        client = None
    else:
        # Configure the client with the API key
        genai.configure(api_key=api_key)
        client = True  # Just a flag to indicate API key is set
except Exception as e:
    print(f"Lỗi không mong muốn khi khởi tạo Google Gemini client: {e}")
    client = None

def check_api_key_active():
    """Check if the Google API key is active and working."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return False, "Google API key not found in environment variables"
    
    try:
        # Configure the client with the API key
        genai.configure(api_key=api_key)
        # Make a minimal API call to test the key
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                return True, "Google API key is active and working"
        return False, "No suitable models found for text generation"
    except Exception as e:
        return False, f"Error checking Google API key: {str(e)}"

def generate_clarification_questions(scenario: str, existing_context: dict) -> list[str]:
    """Generate clarification questions using Google Gemini."""
    if not client:
        return ["Lỗi: Google Gemini client chưa được khởi tạo. Vui lòng kiểm tra API key."]
    
    if not scenario.strip():
        return ["To begin, please describe the core problem or scenario you'd like to analyze."]
    
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
        # Use Gemini Pro model
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        content = response.text.strip()
        if "No further clarification questions" in content:
            return ["No further clarification questions at this time. Ready to proceed?"]
        
        questions = [q.strip() for q in content.split('\n') if q.strip() and q[0].isdigit()]
        cleaned_questions = [q.split('.', 1)[1].strip() if '.' in q else q for q in questions]
        return cleaned_questions if cleaned_questions else ["Could not generate specific questions. Is the scenario clear?"]
    except Exception as e:
        print(f"Google Gemini API Error: {e}")
        return [f"Lỗi API Google Gemini khi tạo câu hỏi: {str(e)[:100]}..."]
    
    # Fallback if no questions were generated
    if not existing_context:
        return ["What is the primary goal?", "Any key constraints (budget, time)?"]
    return ["AI has no further questions now. Ready to proceed?"]

def simulate_outcomes(scenario: str, context: dict) -> nx.DiGraph:
    """
    Generates a decision tree (as a NetworkX DiGraph) for the given scenario and context,
    using Google Gemini.
    """
    if not client or not os.getenv("GOOGLE_API_KEY"):
        print("Google Gemini client hoặc API key không khả dụng. Không thể tạo cây.")
        graph_err = nx.DiGraph()
        graph_err.add_node("error_no_api", label="Lỗi: API Key Google không được cấu hình hoặc client lỗi.", 
                          type="error", full_label="Lỗi: API Key Google không được cấu hình hoặc client lỗi.")
        return graph_err

    print("Bắt đầu quá trình tạo cây quyết định bằng Google Gemini...")
    
    context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
    prompt = f"""
    You are an AI assistant, "Super ElonMusk AI Decision Matrix", generating a decision tree in valid JSON.
    The output MUST be a valid JSON object.
    Schema per node: {{"id": "unique_string_id", "label": "Descriptive Name", "type": "root|action|decision|event_chance|outcome", "edge_label": "Optional Label for edge", "details": {{}}, "children": []}}
    
    Scenario:
    "{scenario}"

    Provided Context:
    {context_str if context_str else "No specific context provided."}

    Based on the scenario and context, generate a comprehensive decision tree.
    - The root node should represent the overall scenario.
    - Identify 3-5 plausible high-level "action" nodes branching from the root.
    - For each action, consider potential subsequent "event_chance" nodes (with estimated probabilities if sensible, e.g., {{"probability": 0.6}}) or further "decision" nodes.
    - Each path should eventually lead to one or more "outcome" nodes.
    - Make labels descriptive and clear. Use unique IDs for all nodes.
    - Ensure the JSON is well-formed. Do not include any text outside the JSON object.

    Example of a small valid JSON output:
    {{"id":"root-node-123","label":"Product Launch Decision","type":"root","children":[{{"id":"action-launch-now-456","label":"Launch Product Immediately","type":"action","edge_label":"Decision: Launch Now","children":[{{"id":"event-market-good-789","label":"Market Reception Positive (P=0.7)","type":"event_chance","details":{{"probability":0.7}},"edge_label":"If market is good","children":[{{"id":"outcome-high-success-101","label":"Outcome: High Success & Profit","type":"outcome"}}]}}]}}]}}

    Now, generate the JSON for the given scenario:
    """
    
    llm_output_content = "No output received."
    try:
        print(f"Gửi yêu cầu tạo cây đến Google Gemini cho kịch bản: {scenario[:50]}...")
        
        # Use Gemini Pro model
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        llm_output_content = response.text.strip()
        
        print("Google Gemini response received, attempting to parse JSON...")
        # Extract JSON if there are markdown code blocks
        if "```json" in llm_output_content:
            llm_output_content = llm_output_content.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_output_content:
            llm_output_content = llm_output_content.split("```")[1].split("```")[0].strip()
            
        tree_data = json.loads(llm_output_content)
        
        # Validate basic structure
        if "id" not in tree_data or "label" not in tree_data or "type" not in tree_data:
            raise ValueError("Generated JSON is missing root level required fields (id, label, type).")
        
        print("JSON parsed successfully.")
        
        # Create the graph
        graph = nx.DiGraph()
        
        # Add the root node
        root_id = tree_data.get("id")
        if not root_id:
            print("Cảnh báo - Google Gemini không cung cấp 'id' cho root node. Tạo ID ngẫu nhiên.")
            root_id = str(uuid.uuid4())
            
        root_label = tree_data.get("label", "Scenario Root")
        root_type = tree_data.get("type", "root")
        root_details = tree_data.get("details", {})
        graph.add_node(root_id, label=str(root_label), full_label=str(root_label), 
                      type=root_type, details=root_details, id=root_id)
        
        # Add children nodes
        if "children" in tree_data and isinstance(tree_data.get("children"), list):
            _add_nodes_edges_from_dict(graph, root_id, tree_data["children"])
            
        if not graph.nodes:
            print("Cảnh báo - Không có node nào được thêm vào đồ thị dù raw_tree_data có vẻ hợp lệ.")
            graph.add_node("fallback_empty_graph", label="Không thể tạo cây (đồ thị trống).", 
                          type="error", full_label="Không thể tạo cây (đồ thị trống).")
            
        print(f"Tạo cây hoàn tất. Số node: {graph.number_of_nodes()}, Số cạnh: {graph.number_of_edges()}")
        return graph
        
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from Google Gemini: {e}")
        print(f"Output that caused error:\n{llm_output_content}")
        graph_err = nx.DiGraph()
        graph_err.add_node(str(uuid.uuid4()), 
                          label=f"Lỗi: Google Gemini không trả về JSON hợp lệ. Chi tiết: {str(e)[:100]}...", 
                          type="error", 
                          full_label=f"Lỗi: Google Gemini không trả về JSON hợp lệ. Chi tiết: {str(e)}")
        return graph_err
    except ValueError as e:
        print(f"Generated JSON has invalid structure: {e}")
        print(f"Output that caused error:\n{llm_output_content}")
        graph_err = nx.DiGraph()
        graph_err.add_node(str(uuid.uuid4()), 
                          label=f"Lỗi: JSON có cấu trúc không hợp lệ. {str(e)[:100]}...", 
                          type="error", 
                          full_label=f"Lỗi: JSON có cấu trúc không hợp lệ. {str(e)}")
        return graph_err
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        graph_err = nx.DiGraph()
        graph_err.add_node(str(uuid.uuid4()), 
                          label=f"Lỗi không mong muốn khi tạo cây: {str(e)[:100]}...", 
                          type="error", 
                          full_label=f"Lỗi không mong muốn khi tạo cây: {str(e)}")
        return graph_err

def _add_nodes_edges_from_dict(graph: nx.DiGraph, parent_node_id: str, children_list: list):
    """Helper function to recursively add nodes and edges to the graph."""
    for child_dict in children_list:
        child_id = child_dict.get("id", str(uuid.uuid4()))
        child_label = child_dict.get("label", "N/A")
        child_type = child_dict.get("type", "unknown")
        child_details = child_dict.get("details", {})
        
        display_label = str(child_label)
        
        graph.add_node(child_id, label=display_label, full_label=str(child_label), 
                      type=child_type, details=child_details, id=child_id)
        
        edge_label = child_dict.get("edge_label", child_type)
        
        if parent_node_id:
            graph.add_edge(parent_node_id, child_id, label=str(edge_label)[:30])
        
        if "children" in child_dict and isinstance(child_dict.get("children"), list):
            _add_nodes_edges_from_dict(graph, child_id, child_dict["children"])

if __name__ == '__main__':
    # Test the Google Gemini API
    is_active, message = check_api_key_active()
    print(f"Google API Key Status: {message}")
    
    if is_active:
        test_scenario = "We are considering a new product launch for a sustainable energy solution."
        test_context = {"Budget": "1M USD", "Target Market": "Urban homeowners"}
        print(f"Scenario: {test_scenario}\nContext: {test_context}")
        
        print("Generated Questions (from Google Gemini):")
        for q in generate_clarification_questions(test_scenario, test_context):
            print(f"- {q}")
    else:
        print("Google Gemini client không được khởi tạo hoặc API key không hoạt động.")