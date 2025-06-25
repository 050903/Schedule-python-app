# SuperElonAI/core/analyzer.py
import networkx as nx
import os
import openai
import json

# --- Cấu hình OpenAI Client ---
try:
    client = openai.OpenAI()
except openai.OpenAIError as e:
    print(f"Lỗi khởi tạo OpenAI client trong analyzer.py: {e}. Hãy đảm bảo OPENAI_API_KEY đã được đặt.")
    client = None
except Exception as e:
    print(f"Lỗi không mong muốn khi khởi tạo OpenAI client trong analyzer.py: {e}")
    client = None

FILTER_CRITERIA = ["feasibility", "impact", "cost_effectiveness", "time_to_implement", "safety_risk", "innovation_level"]

def _query_llm_for_path_evaluation(path_description: str, outcome_description: str, scenario: str, context: dict) -> dict:
    default_error_eval = {"scores": {c: 0 for c in FILTER_CRITERIA}, "reasoning": "Evaluation error."}
    if not client:
        return {**default_error_eval, "reasoning": "Lỗi: OpenAI client (analyzer.py) chưa được khởi tạo."}

    context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
    prompt = f"""
    You are an AI decision analysis assistant. Evaluate the following decision path and its outcome.
    Scenario: "{scenario}"
    Context: {context_str if context_str else "None."}
    Path Taken: "{path_description}"
    Resulting Outcome: "{outcome_description}"

    Evaluate against: {', '.join(FILTER_CRITERIA)}.
    Scores: 1 (very poor) to 10 (excellent).
    Return JSON: {{"scores": {{crit1: score1, ...}}, "reasoning": "Brief overall reasoning."}}
    Example: {{"scores":{{"feasibility":7,"impact":9,...}},"reasoning":"Good path."}}
    Output ONLY the JSON object.
    """ # (Đây là prompt rút gọn, bạn nên dùng prompt chi tiết hơn đã thảo luận)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Output JSON path evaluation."}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}, max_tokens=500, temperature=0.4
        )
        content = response.choices[0].message.content.strip()
        eval_data = json.loads(content)
        if "scores" not in eval_data or "reasoning" not in eval_data: raise ValueError("Missing keys in LLM JSON.")
        # Ensure all criteria have scores
        for crit in FILTER_CRITERIA:
            if crit not in eval_data["scores"]: eval_data["scores"][crit] = 0 # Default if missing
        return eval_data
    except (openai.APIError, json.JSONDecodeError, ValueError) as e:
        print(f"Error from LLM/JSON (analyzer.py): {e}\nLLM Output: {content if 'content' in locals() else 'N/A'}")
        return {**default_error_eval, "reasoning": f"Lỗi LLM/JSON: {str(e)[:100]}..."}
    except Exception as e:
        print(f"Unexpected error in _query_llm_for_path_evaluation: {e}")
        return {**default_error_eval, "reasoning": f"Lỗi không mong muốn: {str(e)[:100]}..."}


def _calculate_overall_score(scores: dict, weights: dict = None) -> float:
    if weights is None: weights = {criterion: 1 for criterion in FILTER_CRITERIA}
    total_score, total_weight, valid_scores_count = 0, 0, 0
    for crit, score_val in scores.items():
        if crit in weights:
            try:
                score = float(score_val)
                total_score += score * weights[crit]; total_weight += weights[crit]; valid_scores_count +=1
            except (ValueError, TypeError): continue
    return total_score / total_weight if total_weight > 0 and valid_scores_count > 0 else 0

def rank_actions_and_recommend(graph: nx.DiGraph, scenario: str, context: dict) -> list:
    if not graph or not graph.nodes() or graph.nodes[list(graph.nodes)[0]].get("type") == "error": # Check for error node from ai_engine
        return [{"id": "err_tree", "path_description": "No valid tree.", "reasoning": "Decision tree is empty or invalid.", "scores": {}, "overall_score": 0}]

    recommendations = []; root_nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == 'root']
    if not root_nodes: root_nodes = [n for n, deg in graph.in_degree() if deg == 0]
    if not root_nodes and graph.nodes(): root_nodes = [list(graph.nodes())[0]]
    
    outcome_nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == 'outcome']
    if not root_nodes or not outcome_nodes: return [{"id": "err_struct", "path_description": "Incomplete tree.", "reasoning": "No root/outcome.", "scores": {}, "overall_score": 0}]

    path_id_counter = 1; processed_paths = set()
    for root_node in root_nodes:
        initial_choices = [c for c in graph.successors(root_node) if graph.nodes[c].get('type') in ['action', 'decision']]
        if not initial_choices and graph.nodes[root_node].get('type') in ['action', 'decision']: initial_choices = [root_node]
        if not initial_choices: continue

        for start_node in initial_choices:
            for outcome_node in outcome_nodes:
                if nx.has_path(graph, start_node, outcome_node):
                    for path_nodes in nx.all_simple_paths(graph, source=start_node, target=outcome_node):
                        if not path_nodes or tuple(path_nodes) in processed_paths: continue
                        processed_paths.add(tuple(path_nodes))
                        
                        desc_parts = [f"Start: {graph.nodes[path_nodes[0]].get('full_label', 'N/A')}"]
                        for i in range(len(path_nodes) - 1):
                            u, v = path_nodes[i], path_nodes[i+1]
                            edge_lbl = graph.get_edge_data(u,v).get('label','to')
                            node_lbl_v = graph.nodes[v].get('full_label','N/A')
                            desc_parts.append(f"->({edge_lbl}) {node_lbl_v}")
                        
                        path_desc = " ".join(desc_parts)
                        outcome_lbl = graph.nodes[outcome_node].get('full_label', 'N/A')
                        evaluation = _query_llm_for_path_evaluation(path_desc, outcome_lbl, scenario, context)
                        overall = _calculate_overall_score(evaluation["scores"])
                        recommendations.append({"id": f"p_{path_id_counter}", "path_description": path_desc, "outcome": outcome_lbl, **evaluation, "overall_score": round(overall, 2)})
                        path_id_counter += 1
    
    ranked = sorted(recommendations, key=lambda x: x["overall_score"], reverse=True)
    return ranked if ranked else [{"id": "err_norank", "path_description": "No paths evaluated.", "reasoning": "No actionable paths found or LLM eval failed.", "scores": {}, "overall_score": 0}]

if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("Vui lòng đặt OPENAI_API_KEY để test analyzer.py với LLM.")
    else:
        if client:
            G_test = nx.DiGraph(); G_test.add_node("root", type="root", full_label="Test Root")
            G_test.add_node("act1", type="action", full_label="Action X"); G_test.add_node("out1", type="outcome", full_label="Success X")
            G_test.add_edge("root", "act1", label="Do X"); G_test.add_edge("act1", "out1", label="Leads to")
            print("Testing analyzer with LLM...")
            recs = rank_actions_and_recommend(G_test, "Test Scenario", {"Budget": "High"})
            for r in recs: print(f"\nPath: {r['path_description']}\nOutcome: {r['outcome']}\nScore: {r['overall_score']}\nReason: {r['reasoning']}\nScores: {r['scores']}")
        else: print("OpenAI client (analyzer.py) không được khởi tạo.")