# SuperElonAI/core/visualizer.py
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def render_decision_tree(graph: nx.DiGraph, use_graphviz_layout: bool = True):
    if not graph or not graph.nodes() or graph.nodes[list(graph.nodes)[0]].get("type") == "error":
        fig, ax = plt.subplots(figsize=(10, 2))
        error_label = "No tree data."
        if graph and graph.nodes(): # If there's an error node from ai_engine
            error_node_data = graph.nodes[list(graph.nodes)[0]]
            if error_node_data.get("type") == "error":
                error_label = error_node_data.get("label", "Error generating tree.")
        ax.text(0.5, 0.5, error_label, ha='center', va='center', fontsize=12, color='red')
        ax.axis('off')
        return fig

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(20, 14))
    color_map = {"root": "#4A90E2", "decision": "#F5A623", "action": "#50E3C2", "event_chance": "#BD10E0", "outcome": "#D0021B", "error": "#333333", "unknown": "#9B9B9B"}
    node_colors = [color_map.get(graph.nodes[node].get('type', 'unknown'), color_map['unknown']) for node in graph.nodes()]
    node_labels = {node: data.get('label', 'N/A') for node, data in graph.nodes(data=True)} # 'label' is already truncated in ai_engine

    pos = None; layout_prog = "dot"
    if use_graphviz_layout:
        try:
            pos = nx.nx_agraph.graphviz_layout(graph, prog=layout_prog)
        except Exception: # Catch broad exception for pygraphviz issues
            print("PyGraphviz layout failed or not available. Falling back to spring_layout.")
            pos = nx.spring_layout(graph, k=0.9, iterations=60, seed=42, scale=2)
    else:
        pos = nx.spring_layout(graph, k=0.9, iterations=60, seed=42, scale=2)

    nx.draw_networkx_nodes(graph, pos, node_size=3000, node_color=node_colors, alpha=0.9, ax=ax, edgecolors='gray', linewidths=0.5)
    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), arrowstyle="-|>", arrowsize=18, edge_color="darkgray", width=1.2, alpha=0.8, ax=ax, node_size=3000)
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=7, font_weight="normal", ax=ax, font_family='sans-serif')
    edge_labels_dict = nx.get_edge_attributes(graph, 'label')
    if edge_labels_dict:
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels_dict, font_size=6, font_color='black', ax=ax, bbox=dict(facecolor='white', alpha=0.3, edgecolor='none', pad=0.3))

    legend_patches = [mpatches.Patch(color=color, label=label.capitalize()) for label, color in color_map.items() if label != "error" or any(d.get("type")=="error" for n,d in graph.nodes(data=True))]
    ax.legend(handles=legend_patches, loc='best', fontsize='x-small', title="Node Types")
    ax.set_title("Super ElonMusk AI Decision Matrix: Simulated Outcomes", fontsize=18, fontweight="bold")
    plt.axis('off'); plt.tight_layout(pad=1.0)
    return fig

if __name__ == '__main__':
    # Test visualizer with a sample graph
    G_test = nx.DiGraph(); G_test.add_node("r", label="Root", type="root"); G_test.add_node("a1", label="Action 1", type="action")
    G_test.add_node("o1", label="Outcome A (Success)", type="outcome"); G_test.add_edge("r", "a1", label="Do it")
    G_test.add_edge("a1", "o1", label="Leads to"); fig = render_decision_tree(G_test)
    # fig.savefig("test_visualizer_output.png") # Uncomment to save
    plt.show()