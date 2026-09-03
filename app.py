# app.py
from flask import Flask, request, jsonify
from fetcher import fetch_wallet_transactions
from graph_engine import build_transaction_graph, analyze_vasp_proximity
from classifier import calculate_wallet_risk

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "system": "TRACE-X Crypto Forensics Engine (SIH26182)",
        "status": "online",
        "endpoints": [
            "/api/v1/investigate?address=<ETH_WALLET_ADDRESS>"
        ]
    })

@app.route("/api/v1/investigate", methods=["GET"])
def investigate_wallet():
    wallet_address = request.args.get("address", "").strip()

    if not wallet_address or not wallet_address.startswith("0x"):
        return jsonify({
            "error": "Invalid or missing Ethereum wallet address. Parameter 'address' required."
        }), 400

    # 1. Fetch blockchain transactions
    txs = fetch_wallet_transactions(wallet_address, max_results=50)

    # 2. Build multi-hop graph & detect VASP proximity
    graph = build_transaction_graph(txs)
    graph_analysis = analyze_vasp_proximity(graph, wallet_address)

    # 3. Calculate AI risk score & XAI attribution
    risk_assessment = calculate_wallet_risk(graph_analysis)

    # 4. Format payload for React / Cytoscape frontend
    nodes = []
    edges = []

    for n, data in graph.nodes(data=True):
        nodes.append({
            "id": n,
            "label": data.get("label", n[:8]),
            "is_target": n.lower() == wallet_address.lower(),
            "vasp_info": data.get("vasp_info")
        })

    for u, v, data in graph.edges(data=True):
        edges.append({
            "source": u,
            "target": v,
            "value_eth": data.get("weight", 0.0),
            "tx_hash": data.get("hash", "")
        })

    return jsonify({
        "case_summary": risk_assessment,
        "graph_analysis": graph_analysis["metrics"],
        "graph_data": {
            "nodes": nodes,
            "edges": edges
        }
    }), 200

if __name__ == "__main__":
    print("Starting TRACE-X Forensics API Server...")
    app.run(host="0.0.0.0", port=8000, debug=True)