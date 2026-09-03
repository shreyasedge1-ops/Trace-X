# graph_engine.py
import networkx as nx
from config import KNOWN_VASP_TAGS
from fetcher import fetch_wallet_transactions

def build_transaction_graph(transactions: list) -> nx.DiGraph:
    """
    Constructs a directed graph (DiGraph) from raw transaction records.
    Nodes represent wallet addresses; edges represent ETH transfers.
    """
    G = nx.DiGraph()

    for tx in transactions:
        u = tx["from"]
        v = tx["to"]
        weight = tx["value_eth"]
        tx_hash = tx["hash"]

        # Add nodes with initial attributes
        if not G.has_node(u):
            G.add_node(u, label=u[:8], vasp_info=KNOWN_VASP_TAGS.get(u, None))
        if not G.has_node(v):
            G.add_node(v, label=v[:8], vasp_info=KNOWN_VASP_TAGS.get(v, None))

        # Add directed edge representing transaction flow
        G.add_edge(u, v, weight=weight, hash=tx_hash)

    return G

def analyze_vasp_proximity(G: nx.DiGraph, target_address: str):
    """
    Analyzes the graph to trace paths from the target wallet to known VASPs.
    Returns detected VASP attribution targets, shortest path length, and graph features.
    """
    target = target_address.lower()
    attributions = []

    if not G.has_node(target):
        return {"target": target, "status": "Target not present in graph", "attributions": []}

    # Extract structural graph metrics for feature engineering
    in_degree = G.in_degree(target)
    out_degree = G.out_degree(target)
    degree_centrality = nx.degree_centrality(G).get(target, 0.0)

    # Search for paths to known VASP nodes
    for node in G.nodes():
        vasp_meta = KNOWN_VASP_TAGS.get(node)
        if vasp_meta and node != target:
            if nx.has_path(G, target, node):
                path = nx.shortest_path(G, target, node)
                attributions.append({
                    "vasp_entity": vasp_meta["entity"],
                    "vasp_type": vasp_meta["type"],
                    "vasp_address": node,
                    "hops": len(path) - 1,
                    "path": path
                })

    return {
        "target_wallet": target,
        "metrics": {
            "in_degree": in_degree,
            "out_degree": out_degree,
            "degree_centrality": round(degree_centrality, 4),
            "total_nodes_in_subgraph": G.number_of_nodes(),
            "total_edges_in_subgraph": G.number_of_edges()
        },
        "attributions": attributions
    }

if __name__ == "__main__":
    test_address = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
    print(f"Testing graph engine on address: {test_address}...\n")

    txs = fetch_wallet_transactions(test_address)
    graph = build_transaction_graph(txs)
    results = analyze_vasp_proximity(graph, test_address)

    print("=== GRAPH ANALYSIS RESULTS ===")
    print(f"Target Wallet: {results['target_wallet']}")
    print(f"Metrics: {results['metrics']}")
    print(f"\nDiscovered VASP Attributions ({len(results['attributions'])}):")
    for attr in results['attributions']:
        print(f"  - Entity: {attr['vasp_entity']} ({attr['vasp_type']})")
        print(f"    Hops: {attr['hops']}")
        print(f"    Flow Path: {' -> '.join([p[:8] for p in attr['path']])}")