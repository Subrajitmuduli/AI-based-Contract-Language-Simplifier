# Enhanced admin.py with colorful HTML and basic charts using Chart.js
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json, os

LOG_PATH = "logs/simplification_requests.json"
GLOSSARY_PATH = "glossary.json"

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Admin - Simplification Monitor</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  body { font-family: Arial, sans-serif; background:#f4f6f9; padding:20px; }
  h1 { color:#333; }
  table { background:white; border-collapse: collapse; width:100%; margin-top:20px; }
  th, td { border:1px solid #ccc; padding:10px; text-align:left; }
  th { background:#4CAF50; color:white; }
  tr:nth-child(even) { background:#f2f2f2; }
  .chart-container { width: 45%; display:inline-block; margin:20px; }
</style>
</head>
<body>
<h1>Admin Dashboard</h1>



<h2>Recent Simplification Requests</h2>
{% if entries %}
  <table>
    <tr><th>Timestamp</th><th>User</th><th>Level</th><th>Model</th><th>Input</th><th>Output</th></tr>
    {% for e in entries[::-1] %}
      <tr>
        <td>{{ e.timestamp }}</td>
        <td>{{ e.user }}</td>
        <td>{{ e.level }}</td>
        <td>{{ e.model_used }}</td>
        <td style="max-width:250px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{{ e.input_snippet }}</td>
        <td style="max-width:250px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{{ e.output_snippet }}</td>
      </tr>
    {% endfor %}
  </table>
{% else %}
  <p>No entries yet.</p>
{% endif %}

<h2>Manage Glossary</h2>
<form method="POST" action="/glossary">
  <textarea name="glossary" rows="10" cols="80">{{ glossary }}</textarea><br>
  <button type="submit">Save Glossary</button>
</form>

<h2>Activity Charts</h2>
<div class="charts-wrapper" style="display:flex; justify-content:center; gap:40px; margin-top:30px;">

  <div class="chart-container" style="width:350px; height:350px;">
    <canvas id="userChart"></canvas>
  </div>

  <div class="chart-container" style="width:350px; height:350px;">
    <canvas id="uploadChart"></canvas>
  </div>

</div>


<script>
  const userLabels = {{ user_labels|safe }};
  const userCounts = {{ user_counts|safe }};
  const uploadLabels = ["Uploads"];
  const uploadCounts = [{{ total_uploads }}];

  new Chart(document.getElementById('userChart'), {
      type: 'bar',
      data: { labels: userLabels, datasets: [{ label: 'Requests per User (All Users)', data: userCounts }] }
  });

  new Chart(document.getElementById('uploadChart'), {
      type: 'pie',
      data: { labels: uploadLabels, datasets: [{ label: 'Total Uploads (All Users)', data: uploadCounts }] }
  });
</script>

</body>
</html>
"""

def read_json(path):
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def read_glossary():
    if not os.path.exists(GLOSSARY_PATH): return {}
    with open(GLOSSARY_PATH, "r", encoding="utf-8") as f: return json.load(f)

@app.route("/")
def index():
    entries = read_json(LOG_PATH)
    glossary = json.dumps(read_glossary(), indent=2)

    # Chart Data
    user_count_map = {}
    for e in entries:
        user_count_map[e.get("user", "Unknown")] = user_count_map.get(e.get("user", "Unknown"), 0) + 1

    user_labels = list(user_count_map.keys())
    user_counts = list(user_count_map.values())
    total_uploads = len(entries)

    return render_template_string(
        TEMPLATE,
        entries=entries,
        glossary=glossary,
        user_labels=user_labels,
        user_counts=user_counts,
        total_uploads=total_uploads,
    )

@app.route("/glossary", methods=["POST"])
def update_glossary():
    text = request.form.get("glossary", "{}")
    try:
        parsed = json.loads(text)
        with open(GLOSSARY_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
    except Exception as e:
        return f"Invalid JSON: {e}", 400
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8502)