# SuperElonAI/core/ai_engine.py
import networkx as nx
import uuid
import os
from openai import OpenAI # Luôn cần thiết
import json   # Luôn cần thiết
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    print(f"Lỗi không mong muốn khi khởi tạo OpenAI client trong ai_engine.py: {e}")
    client = None

def _query_llm_for_tree_structure(scenario: str, context: dict) -> dict: # Đổi lại tên gốc
    """
    AI Integration Point: Interacts with OpenAI to generate a decision tree.
    """
    if not client:
        print("Lỗi nghiêm trọng: OpenAI client (ai_engine.py) chưa được khởi tạo. Không thể tạo cây từ LLM.")
        return {"id": str(uuid.uuid4()), "label": "Lỗi: OpenAI client không hoạt động. Kiểm tra API Key và kết nối.", "type": "error", "children": []}

    context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
    
    # SỬ DỤNG PROMPT CHI TIẾT VÀ TỐT NHẤT CỦA BẠN Ở ĐÂY
    # Đây là ví dụ rút gọn, hãy thay thế bằng prompt đầy đủ bạn đã tinh chỉnh
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
    
    llm_output_content = "No LLM output received." # Khởi tạo để tránh lỗi nếu API call thất bại sớm
    try:
        print(f"AI_ENGINE: Gửi yêu cầu tạo cây đến LLM cho kịch bản: {scenario[:50]}...")
        # Use the new API format
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI that generates decision tree structures in valid JSON format, adhering strictly to the provided schema."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.2,
            response_format={"type": "json_object"}  # Ensure JSON response
        )
        llm_output_content = response.choices[0].message.content.strip()
        
        print(f"AI_ENGINE: LLM response received, attempting to parse JSON...")
        tree_data = json.loads(llm_output_content)
        
        # Validate basic structure
        if "id" not in tree_data or "label" not in tree_data or "type" not in tree_data:
            raise ValueError("Generated JSON is missing root level required fields (id, label, type).")
        print("AI_ENGINE: JSON parsed successfully.")
        return tree_data

    except Exception as e:
        print(f"AI_ENGINE: OpenAI API returned an Error: {e}")
        return {"id": str(uuid.uuid4()), "label": f"Lỗi API OpenAI khi tạo cây: {str(e)[:100]}...", "type": "error", "children": []}
    except json.JSONDecodeError as e:
        print(f"AI_ENGINE: Failed to decode JSON from LLM: {e}")
        print(f"AI_ENGINE: LLM Output that caused error:\n{llm_output_content}")
        return {"id": str(uuid.uuid4()), "label": f"Lỗi: LLM không trả về JSON hợp lệ. Chi tiết: {str(e)[:100]}...", "type": "error", "children": []}
    except ValueError as e: # Bắt lỗi validate cấu trúc JSON
        print(f"AI_ENGINE: Generated JSON has invalid structure: {e}")
        print(f"AI_ENGINE: LLM Output that caused error:\n{llm_output_content}")
        return {"id": str(uuid.uuid4()), "label": f"Lỗi: LLM JSON có cấu trúc không hợp lệ. {str(e)[:100]}...", "type": "error", "children": []}
    except Exception as e:
        print(f"AI_ENGINE: An unexpected error occurred in _query_llm_for_tree_structure: {e}")
        return {"id": str(uuid.uuid4()), "label": f"Lỗi không mong muốn khi tạo cây: {str(e)[:100]}...", "type": "error", "children": []}


def _add_nodes_edges_from_dict(graph: nx.DiGraph, parent_node_id: str, children_list: list):
    # Hàm này giữ nguyên
    for child_dict in children_list:
        child_id = child_dict.get("id", str(uuid.uuid4()))
        child_label = child_dict.get("label", "N/A")
        child_type = child_dict.get("type", "unknown")
        child_details = child_dict.get("details", {})
        
        display_label = str(child_label)
        # Không cắt ngắn label ở đây nữa, để visualizer tự xử lý nếu cần
        # if len(display_label) > 50: display_label = display_label[:47] + "..."

        graph.add_node(child_id, label=display_label, full_label=str(child_label), type=child_type, details=child_details, id=child_id)
        
        edge_label = child_dict.get("edge_label", child_type) # Ưu tiên edge_label từ LLM
        
        if parent_node_id:
            graph.add_edge(parent_node_id, child_id, label=str(edge_label)[:30]) # Vẫn có thể cắt ngắn edge label
        
        if "children" in child_dict and isinstance(child_dict.get("children"), list):
            _add_nodes_edges_from_dict(graph, child_id, child_dict["children"])


def simulate_outcomes(scenario: str, context: dict) -> nx.DiGraph: # Bỏ tham số use_real_llm
    """
    Generates a decision tree (as a NetworkX DiGraph) for the given scenario and context,
    ALWAYS attempting to use the real LLM.
    """
    if not client or not os.getenv("OPENAI_API_KEY"):
        print("AI_ENGINE: OpenAI client hoặc API key không khả dụng. Không thể tạo cây.")
        graph_err = nx.DiGraph()
        graph_err.add_node("error_no_api", label="Lỗi: API Key OpenAI không được cấu hình hoặc client lỗi.", type="error", full_label="Lỗi: API Key OpenAI không được cấu hình hoặc client lỗi.")
        return graph_err

    print("AI_ENGINE: Bắt đầu quá trình tạo cây quyết định bằng LLM...")
    raw_tree_data = _query_llm_for_tree_structure(scenario, context) # Luôn gọi hàm LLM
    
    graph = nx.DiGraph()
    
    # Kiểm tra xem raw_tree_data có phải là lỗi không
    if raw_tree_data.get("type") == "error":
        error_label_from_llm = raw_tree_data.get("label", "Lỗi không xác định từ LLM khi tạo cây.")
        print(f"AI_ENGINE: Đã xảy ra lỗi khi LLM tạo cây: {error_label_from_llm}")
        graph.add_node(raw_tree_data.get("id", "error_node_llm"), 
                       label=error_label_from_llm[:50], # Cắt ngắn nếu quá dài
                       full_label=error_label_from_llm, 
                       type="error")
        return graph

    root_id = raw_tree_data.get("id") # LLM PHẢI cung cấp ID
    if not root_id: # Fallback nếu LLM không cung cấp ID cho root, mặc dù không nên xảy ra
        print("AI_ENGINE: Cảnh báo - LLM không cung cấp 'id' cho root node. Tạo ID ngẫu nhiên.")
        root_id = str(uuid.uuid4())

    root_label = raw_tree_data.get("label", "Scenario Root (Từ LLM)")
    root_type = raw_tree_data.get("type", "root") # LLM nên đặt là "root"
    root_details = raw_tree_data.get("details", {})
    graph.add_node(root_id, label=str(root_label), full_label=str(root_label), type=root_type, details=root_details, id=root_id)
    
    if "children" in raw_tree_data and isinstance(raw_tree_data.get("children"), list):
        _add_nodes_edges_from_dict(graph, root_id, raw_tree_data["children"])
        
    if not graph.nodes: # Trường hợp rất hiếm nếu raw_tree_data hợp lệ nhưng không có node nào được thêm
        print("AI_ENGINE: Cảnh báo - Không có node nào được thêm vào đồ thị dù raw_tree_data có vẻ hợp lệ.")
        graph.add_node("fallback_empty_graph", label="Không thể tạo cây (đồ thị trống).", type="error", full_label="Không thể tạo cây (đồ thị trống).")

    print(f"AI_ENGINE: Tạo cây hoàn tất. Số node: {graph.number_of_nodes()}, Số cạnh: {graph.number_of_edges()}")
    return graph


if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("Vui lòng đặt biến môi trường OPENAI_API_KEY để chạy thử nghiệm ai_engine.py với LLM.")
    else:
        if client:
            print("\n--- Testing ai_engine.py with REAL LLM (OpenAI) for Tree Structure ---")
            # test_scenario_llm = "Deciding whether to invest $100,000 in a new AI startup focused on renewable energy."
            test_scenario_llm = "I have a job offer from Company A and Company B. Company A offers higher salary but less work-life balance. Company B offers lower salary but better culture and remote work. I need to decide which offer to accept, or if I should negotiate further with either."
            test_context_llm = {
                "My current role satisfaction": "Medium",
                "My financial needs": "High, saving for a house",
                "Importance of work-life balance": "Very high",
                "Career growth opportunities at Company A": "Perceived as good",
                "Career growth opportunities at Company B": "Uncertain, but seems flexible"
            }
            
            print(f"AI_ENGINE TEST: Gửi kịch bản: '{test_scenario_llm}'")
            llm_decision_tree = simulate_outcomes(test_scenario_llm, test_context_llm)
            
            print(f"\nGenerated Decision Tree (from LLM) for: {test_scenario_llm}")
            print(f"Number of nodes: {llm_decision_tree.number_of_nodes()}")
            print(f"Number of edges: {llm_decision_tree.number_of_edges()}")
            
            if llm_decision_tree.nodes():
                is_error_tree = llm_decision_tree.nodes[list(llm_decision_tree.nodes)[0]].get("type") == "error"
                if is_error_tree:
                    print(f"  ERROR NODE DETECTED: {llm_decision_tree.nodes[list(llm_decision_tree.nodes)[0]].get('full_label')}")
                else:
                    for node_id, data_node in llm_decision_tree.nodes(data=True):
                        print(f"  Node {data_node.get('id')} ({data_node.get('label')}) - Type: {data_node.get('type')}, Details: {data_node.get('details')}")
                    
                    print("\n  Edges (from LLM tree):")
                    for u, v, data_edge in llm_decision_tree.edges(data=True):
                        label_u = llm_decision_tree.nodes[u].get('label', 'Unknown Node U')
                        label_v = llm_decision_tree.nodes[v].get('label', 'Unknown Node V')
                        print(f"    Edge from '{label_u}' (ID: {u}) to '{label_v}' (ID: {v}): Label={data_edge.get('label')}")
            else:
                print("  Không có node nào được tạo từ LLM.")
        else:
            print("\nOpenAI client (ai_engine.py) không được khởi tạo, không thể chạy test LLM.")