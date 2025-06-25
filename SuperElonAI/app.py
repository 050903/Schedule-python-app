# SuperElonAI/app.py
import streamlit as st
import networkx as nx
import json
from fpdf import FPDF # Đảm bảo bạn đã import
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Core logic imports
from core.questions import generate_clarification_questions
from core.ai_engine import simulate_outcomes # simulate_outcomes giờ sẽ luôn dùng LLM nếu có thể
from core.visualizer import render_decision_tree
from core.analyzer import rank_actions_and_recommend, FILTER_CRITERIA

st.set_page_config(page_title="Super ElonMusk AI", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# Session State Init
default_session_state = {
    'scenario': "", 'context_answers': {}, 'questions_to_ask': [],
    'decision_tree_graph': None, 'recommendations': [], 'current_stage': "scenario_input",
    'q_idx': 0, 'asked_questions_history': [], 'form_temp_custom_key': "",
    'form_temp_custom_value': "", 'tree_image_path': None
    # 'use_real_llm_tree' đã bị loại bỏ
}
for key, value in default_session_state.items():
    if key not in st.session_state: st.session_state[key] = value

# --- Helper Functions for Export (Giữ nguyên, chỉ rút gọn ở đây) ---
def get_export_filename(base_name, extension):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"

def export_to_json(data, filename_base="decision_matrix_export"):
    os.makedirs("outputs/export_results", exist_ok=True)
    filepath = os.path.join("outputs/export_results", get_export_filename(filename_base, "json"))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath

def export_to_markdown(data, filename_base="decision_matrix_export"):
    os.makedirs("outputs/export_results", exist_ok=True)
    filepath = os.path.join("outputs/export_results", get_export_filename(filename_base, "md"))
    md_content = f"# Decision Matrix Analysis: {data.get('scenario', 'N/A')}\n\n"
    md_content += f"## Context Provided:\n"
    if data.get('context'):
        for q, a in data.get('context', {}).items():
            md_content += f"- **{q}**: {a}\n"
    else:
        md_content += "No context provided.\n"
    md_content += "\n## Top Recommendations:\n"
    if data.get('recommendations'):
        for i, rec in enumerate(data.get('recommendations', [])):
            md_content += f"### {i+1}. {rec.get('path_description', 'N/A')} (Score: {rec.get('overall_score', 0)})\n"
            md_content += f"   - **Outcome:** {rec.get('outcome', 'N/A')}\n"
            md_content += f"   - **Reasoning:** {rec.get('reasoning', 'N/A')}\n"
            md_content += f"   - **Scores:**\n"
            if rec.get('scores'):
                for crit, score in rec.get('scores', {}).items():
                    md_content += f"     - {crit.replace('_',' ').title()}: {score}\n"
            md_content += "\n"
    else:
        md_content += "No recommendations generated.\n"
    
    if data.get('decision_tree_text'):
        md_content += "## Decision Tree (Textual Representation):\n"
        md_content += "```\n"
        for line in data.get('decision_tree_text'):
            md_content += line + "\n"
        md_content += "```\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    return filepath

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Super ElonMusk AI Decision Matrix Report', 0, 1, 'C')
        self.ln(5)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12); self.multi_cell(0, 10, title, 0, 'L'); self.ln(2)
    def chapter_body(self, body):
        self.set_font('Arial', '', 10); self.multi_cell(0, 5, body); self.ln()
    def add_recommendation(self, index, rec):
        self.set_font('Arial', 'B', 10)
        self.multi_cell(0, 5, f"{index}. {rec.get('path_description', 'N/A')} (Score: {rec.get('overall_score', 0)})")
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, f"   Outcome: {rec.get('outcome', 'N/A')}")
        self.multi_cell(0, 5, f"   Reasoning: {rec.get('reasoning', 'N/A')}")
        self.multi_cell(0, 5, "   Scores:")
        if rec.get('scores'):
            for crit, score in rec.get('scores', {}).items():
                self.multi_cell(0, 5, f"     - {crit.replace('_',' ').title()}: {score}")
        self.ln(3)

def export_to_pdf(data, tree_image_path=None, filename_base="decision_matrix_export"):
    os.makedirs("outputs/export_results", exist_ok=True)
    filepath = os.path.join("outputs/export_results", get_export_filename(filename_base, "pdf"))
    pdf = PDF(); pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page()
    pdf.chapter_title(f"Scenario: {data.get('scenario', 'N/A')}")
    pdf.chapter_title("Context Provided:")
    context_str = "\n".join([f"- {q}: {a}" for q, a in data.get('context', {}).items()]) if data.get('context') else "No specific context."
    pdf.chapter_body(context_str)
    pdf.chapter_title("Top Recommendations:")
    if data.get('recommendations'):
        for i, rec in enumerate(data.get('recommendations', [])):
            pdf.add_recommendation(i + 1, rec)
            if pdf.get_y() > 240: pdf.add_page(); pdf.chapter_title("Recommendations (Cont.):")
    if tree_image_path and os.path.exists(tree_image_path):
        pdf.add_page(orientation='L'); pdf.chapter_title("Decision Tree Visualization:")
        try: pdf.image(tree_image_path, x=10, y=pdf.get_y() + 5, w=277 * 0.95)
        except Exception as e: pdf.add_page(orientation='P'); pdf.chapter_body(f"Error embedding tree: {e}")
    elif data.get('decision_tree_text'):
        if pdf.get_y() > 200 or (pdf.page_no() > 0 and pdf.cur_orientation == 'L'): pdf.add_page(orientation='P')
        pdf.chapter_title("Decision Tree (Textual):"); pdf.chapter_body("\n".join(data.get('decision_tree_text')))
    pdf.output(filepath, 'F'); return filepath

def get_text_representation_of_tree(graph):
    if not graph or not graph.nodes(): return ["Tree is empty."]
    root_nodes = [n for n,d in graph.nodes(data=True) if d.get('type') == 'root' or graph.in_degree(n) == 0]
    if not root_nodes: return ["Cannot determine root."]
    root = [n for n in root_nodes if graph.nodes[n].get('type') == 'root']
    root = root[0] if root else root_nodes[0]
    lines = []; visited = set()
    def _dfs(node_id, G, prefix=""):
        if node_id in visited: lines.append(f"{prefix}- ... (cycle to: {G.nodes[node_id].get('label')})"); return
        visited.add(node_id)
        node_data = G.nodes[node_id]
        lines.append(f"{prefix}- {node_data.get('label','N/A')} (Type: {node_data.get('type','N/A')})")
        successors = list(G.successors(node_id))
        for i, child_id in enumerate(successors):
            edge_data = G.get_edge_data(node_id, child_id); edge_label = edge_data.get('label','') if edge_data else ''
            connector = "└──" if i == len(successors) - 1 else "├──"
            child_prefix = prefix + ("    " if i == len(successors) - 1 else "│   ")
            lines.append(f"{prefix}{connector} ({edge_label})" if edge_label else f"{prefix}{connector}")
            _dfs(child_id, G, child_prefix + ("  " if edge_label else ""))
    _dfs(root, graph); return lines
# --- UI ---
st.title("🚀 Super ElonMusk AI Decision Matrix")
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Reset Full Session"):
        for key in list(st.session_state.keys()): del st.session_state[key] # Clear all
        st.session_state.update(default_session_state) # Re-init with defaults
        st.rerun()
    # Toggle for LLM tree generation is removed
    st.info("1. Describe Scenario\n2. Answer AI Questions\n3. Analyze & Get Recommendations")
    
    # Display API key status
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API key is configured")
    else:
        st.error("❌ OpenAI API key is not configured")
    
    st.caption("AI will always be used for tree generation if API key is available.")

# Stage 1: Scenario Input
if st.session_state.current_stage == "scenario_input":
    st.header("1. Describe Your Scenario")
    scenario_text = st.text_area("Enter scenario here:", value=st.session_state.scenario, height=150, placeholder="e.g., 'Deciding on a new job offer with multiple factors...'")
    if st.button("Understand Scenario & Ask Questions", type="primary"):
        if scenario_text.strip():
            st.session_state.scenario = scenario_text; st.session_state.context_answers = {}
            st.session_state.asked_questions_history = []; st.session_state.q_idx = 0
            st.session_state.form_temp_custom_key = ""; st.session_state.form_temp_custom_value = "" # Reset custom fields
            st.session_state.questions_to_ask = generate_clarification_questions(st.session_state.scenario, {})
            st.session_state.asked_questions_history.extend(st.session_state.questions_to_ask)
            st.session_state.current_stage = "qa"; st.rerun()
        else: st.error("Scenario cannot be empty.")

# Stage 2: Dynamic Q&A
elif st.session_state.current_stage == "qa":
    st.header("2. Clarify Context: Answer These Key Questions")
    st.markdown(f"**Original Scenario:** *{st.session_state.scenario}*")
    if not st.session_state.questions_to_ask:
        st.info("No specific questions from the AI at this moment. You can add custom context or proceed directly to analysis.")
    
    with st.form(key=f"qa_form_{st.session_state.q_idx}"):
        st.markdown("The AI needs more information. Your answers are crucial.")
        for i, q_text in enumerate(st.session_state.questions_to_ask):
            st.text_input(label=f"**{q_text}**", key=f"ans_q_{st.session_state.q_idx}_{i}", value=st.session_state.context_answers.get(q_text, ""))
        
        st.session_state.form_temp_custom_key = st.text_input("Add custom context field (optional):", value=st.session_state.form_temp_custom_key, key=f"custom_q_input_{st.session_state.q_idx}")
        st.session_state.form_temp_custom_value = st.text_area("Custom context value:", value=st.session_state.form_temp_custom_value, key=f"custom_a_input_{st.session_state.q_idx}", height=70)
        
        form_cols = st.columns(2)
        submitted_qa = form_cols[0].form_submit_button("Submit Answers & Ask More (if any)")
        proceed_to_analysis_button = form_cols[1].form_submit_button("✅ All Context Provided, Proceed to Analysis")

    if submitted_qa or proceed_to_analysis_button:
        for i, q_text in enumerate(st.session_state.questions_to_ask):
            answer_value = st.session_state[f"ans_q_{st.session_state.q_idx}_{i}"]
            if answer_value.strip(): st.session_state.context_answers[q_text] = answer_value.strip()
            elif q_text in st.session_state.context_answers: del st.session_state.context_answers[q_text]
        
        custom_key_val = st.session_state[f"custom_q_input_{st.session_state.q_idx}"].strip()
        custom_value_val = st.session_state[f"custom_a_input_{st.session_state.q_idx}"].strip()
        if custom_key_val and custom_value_val:
            st.session_state.context_answers[custom_key_val] = custom_value_val
            st.session_state.form_temp_custom_key = ""; st.session_state.form_temp_custom_value = ""
        else:
            st.session_state.form_temp_custom_key = custom_key_val; st.session_state.form_temp_custom_value = custom_value_val
        
        if submitted_qa:
            cleaned_context = {k: v for k, v in st.session_state.context_answers.items() if v.strip()}
            new_questions = generate_clarification_questions(st.session_state.scenario, cleaned_context)
            st.session_state.questions_to_ask = [q for q in new_questions if q not in st.session_state.asked_questions_history and q not in cleaned_context]
            if not st.session_state.questions_to_ask: st.info("No further unique clarification questions from the AI.")
            st.session_state.asked_questions_history.extend(st.session_state.questions_to_ask); st.session_state.q_idx += 1; st.rerun()
        elif proceed_to_analysis_button:
            st.session_state.context_answers = {k: v for k, v in st.session_state.context_answers.items() if v.strip()}
            if not st.session_state.scenario.strip(): st.error("Scenario is empty!"); st.session_state.current_stage = "scenario_input"
            else: st.session_state.current_stage = "analysis"
            st.rerun()
            
    if st.session_state.context_answers:
        with st.expander("Current Context Summary:", expanded=False):
            for q, a in st.session_state.context_answers.items(): st.markdown(f"- **{q.strip()}**: {a.strip()}")

# Stage 3: Analysis and Recommendations
elif st.session_state.current_stage == "analysis":
    st.header("3. AI Decision Matrix & Recommendations")
    st.markdown(f"**Scenario Under Analysis:** *{st.session_state.scenario}*")
    if not st.session_state.scenario.strip():
        st.error("No scenario defined. Please go back and describe your scenario.")
        if st.button("⬅️ Describe Scenario"): st.session_state.current_stage = "scenario_input"; st.rerun()
        st.stop()

    if st.session_state.context_answers:
        with st.expander("View Provided Context", expanded=False):
            for q, a in st.session_state.context_answers.items(): st.markdown(f"- **{q}**: {a}")
    else: st.info("No specific context was provided beyond the initial scenario.")

    if st.session_state.decision_tree_graph is None or not st.session_state.recommendations:
        with st.spinner("AI is thinking... Simulating outcomes and analyzing options... This may take a moment."):
            # simulate_outcomes now always tries to use LLM if available
            st.session_state.decision_tree_graph = simulate_outcomes(st.session_state.scenario, st.session_state.context_answers)
            
            # Check if tree generation resulted in an error node
            tree_is_valid = False
            if st.session_state.decision_tree_graph and st.session_state.decision_tree_graph.nodes():
                first_node_type = st.session_state.decision_tree_graph.nodes[list(st.session_state.decision_tree_graph.nodes)[0]].get("type")
                if first_node_type != "error":
                    tree_is_valid = True
            
            if tree_is_valid:
                st.session_state.recommendations = rank_actions_and_recommend(st.session_state.decision_tree_graph, st.session_state.scenario, st.session_state.context_answers)
            else:
                 st.session_state.recommendations = [] # Ensure it's an empty list
                 # Error message will be shown by visualizer if tree is error type
    
    st.subheader("🌳 Visualized Decision Tree")
    # Visualizer will show error message if graph is error type
    tree_fig = render_decision_tree(st.session_state.decision_tree_graph, use_graphviz_layout=st.checkbox("Use advanced hierarchical layout (PyGraphviz)", value=True, key="use_graphviz_cb"))
    st.pyplot(tree_fig)
    if st.session_state.decision_tree_graph and st.session_state.decision_tree_graph.nodes() and st.session_state.decision_tree_graph.nodes[list(st.session_state.decision_tree_graph.nodes)[0]].get("type") != "error":
        st.session_state.tree_image_path = os.path.join("outputs", "temp_tree_image.png"); os.makedirs("outputs", exist_ok=True)
        try: tree_fig.savefig(st.session_state.tree_image_path, dpi=150, bbox_inches='tight')
        except Exception as e_save: st.warning(f"Could not save tree image for export: {e_save}")
    else:
        st.session_state.tree_image_path = None


    st.subheader("🏆 Ranked Strategic Options")
    if st.session_state.recommendations and st.session_state.recommendations[0].get("id") not in ["err_tree", "err_struct", "err_norank"]:
        for i, rec in enumerate(st.session_state.recommendations):
            with st.expander(f"{i+1}. {rec.get('path_description', 'N/A')} (Overall Score: {rec.get('overall_score', 0)})", expanded=(i < 1)): # Expand top 1
                st.markdown(f"**Outcome:** {rec.get('outcome', 'N/A')}")
                st.markdown(f"**Reasoning (AI Assessment):** {rec.get('reasoning', 'N/A')}")
                st.markdown("**Detailed Scores:**")
                score_cols = st.columns(len(FILTER_CRITERIA))
                for idx, crit in enumerate(FILTER_CRITERIA):
                    score_cols[idx].metric(label=crit.replace("_"," ").title(), value=rec.get('scores', {}).get(crit, "N/A"))
    elif st.session_state.recommendations and st.session_state.recommendations[0].get("id","").startswith("err_"):
         st.warning(f"Could not generate recommendations: {st.session_state.recommendations[0].get('reasoning', 'Tree or analysis error.')}")
    elif not st.session_state.decision_tree_graph or not st.session_state.decision_tree_graph.nodes() or st.session_state.decision_tree_graph.nodes[list(st.session_state.decision_tree_graph.nodes)[0]].get("type") == "error":
        st.warning("Recommendations cannot be generated as the decision tree is invalid or empty.")
    else:
        st.info("No specific recommendations could be generated based on the current analysis.")

    st.subheader("💾 Export Results")
    export_data = {
        "scenario": st.session_state.scenario, "context": st.session_state.context_answers,
        "recommendations": st.session_state.recommendations,
        "decision_tree_text": get_text_representation_of_tree(st.session_state.decision_tree_graph) if st.session_state.decision_tree_graph else None,
        "analysis_timestamp": datetime.datetime.now().isoformat()
    }
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    try:
        json_path = export_to_json(export_data)
        with open(json_path, "rb") as fp: col_exp1.download_button("📥 JSON", fp, os.path.basename(json_path), "application/json")
        md_path = export_to_markdown(export_data)
        with open(md_path, "r", encoding="utf-8") as fp: col_exp2.download_button("📝 Markdown", fp.read(), os.path.basename(md_path), "text/markdown")
        pdf_path = export_to_pdf(export_data, st.session_state.tree_image_path)
        with open(pdf_path, "rb") as fp: col_exp3.download_button("📄 PDF", fp, os.path.basename(pdf_path), "application/pdf")
        st.caption(f"Exports saved to: `outputs/export_results/`")
    except Exception as e_export: st.error(f"Error during export: {e_export}")

    if st.button("↩️ Analyze Another Scenario or Refine Context"):
        # Reset analysis specific states, keep scenario and context for refinement if desired
        st.session_state.decision_tree_graph = None; st.session_state.recommendations = []
        st.session_state.questions_to_ask = [] # Reset questions to allow re-generation
        st.session_state.q_idx = 0; st.session_state.asked_questions_history = [] # Full Q&A reset
        st.session_state.current_stage = "scenario_input" # Go back to start for new scenario or full Q&A re-run
        st.rerun()

st.markdown("---")
st.markdown("Super ElonMusk AI Decision Matrix v0.3.0 - *Always uses Real AI if API Key is set.*")
st.caption("Remember, even the most advanced AI is a tool. The final decision is yours. Think critically.")