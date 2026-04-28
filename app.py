from flask import Flask, render_template_string, request
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
app = Flask(__name__)
if not os.path.exists('static'):
    os.makedirs('static')
file_path = "tirunelveli_tourism_network.xlsx"
places_df = pd.read_excel(file_path, sheet_name="Places")
edges_df = pd.read_excel(file_path, sheet_name="Connections")
G = nx.Graph()
for place in places_df['Place']:
    G.add_node(place)

for i, row in edges_df.iterrows():
    G.add_edge(row['Source'], row['Target'])
def calculate_metrics():
    degree = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)

    df = pd.DataFrame({
        'Place': list(G.nodes()),
        'Degree': [round(degree[n], 3) for n in G.nodes()],
        'Betweenness': [round(betweenness[n], 3) for n in G.nodes()],
        'Closeness': [round(closeness[n], 3) for n in G.nodes()],
    })

    return df.sort_values(by="Degree", ascending=False)
def find_path(src, dst):
    try:
        path = nx.shortest_path(G, source=src, target=dst)
        return " → ".join(path)
    except:
        return "No path found"
def find_all_paths(src):
    results = {}
    for node in G.nodes():
        if node != src:
            try:
                path = nx.shortest_path(G, source=src, target=node)
                results[node] = " → ".join(path)
            except:
                results[node] = "No path"
    return results
def draw_graph():
    plt.figure(figsize=(12,10))

    pos = nx.spring_layout(G, k=0.8)

    nx.draw_networkx_nodes(
        G, pos,
        node_size=3000,
        node_color='skyblue'
    )

    nx.draw_networkx_edges(G, pos, width=1.5)

    nx.draw_networkx_labels(
        G, pos,
        font_size=8,
        font_weight='bold',
        bbox=dict(facecolor='white', alpha=0.7)
    )

    plt.title("Tirunelveli Tourism Network", fontsize=14)
    plt.axis('off')
    plt.savefig('static/graph.png', bbox_inches='tight')
    plt.close()
@app.route('/', methods=['GET', 'POST'])
def home():
    df = calculate_metrics()
    draw_graph()

    result = ""
    all_paths_result = {}

    if request.method == 'POST':


        if request.form.get('source') and request.form.get('destination'):
            src = request.form.get('source')
            dst = request.form.get('destination')
            result = find_path(src, dst)


        if request.form.get('source_all'):
            src_all = request.form.get('source_all')
            all_paths_result = find_all_paths(src_all)

    return render_template_string('''
    <html>
    <head>
        <title>Tirunelveli Tourism</title>
        <style>
            body { font-family: Arial; background: #f4f6f8; }
            .container { padding: 20px; }
            .card {
                background: white;
                padding: 15px;
                margin: 15px 0;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            input, button {
                padding: 8px;
                margin: 5px;
            }
            button {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
        </style>
    </head>

    <body>
    <div class="container">

        <h1>Tirunelveli Tourism Network</h1>

        <div class="card">
            <h2> Graph</h2>
            <img src="/static/graph.png" width="650">
        </div>

        <div class="card">
            <h2>Find Path (A → B)</h2>
            <form method="post">
                <input name="source" placeholder="Source">
                <input name="destination" placeholder="Destination">
                <button type="submit">Find</button>
            </form>
            <p><b>{{result}}</b></p>
        </div>

        <div class="card">
            <h2>Paths from One Place to ALL</h2>
            <form method="post">
                <input name="source_all" placeholder="Enter Source">
                <button type="submit">Find All</button>
            </form>

            <ul>
            {% for place, path in all_paths.items() %}
                <li><b>{{place}}</b>: {{path}}</li>
            {% endfor %}
            </ul>
        </div>

        <div class="card">
            <h2>Centrality Analysis</h2>
            {{table | safe}}
        </div>

    </div>
    </body>
    </html>
    ''', table=df.to_html(index=False), result=result, all_paths=all_paths_result)

if __name__ == '__main__':
    app.run(debug=True)