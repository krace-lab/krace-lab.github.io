import json
from pathlib import Path
from jinja2 import Template
from models import SessionReport

_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>パドック診断 - {{ r.venue }}{{ r.race_number }}R</title>
<style>
body{font-family:'Helvetica Neue',sans-serif;padding:20px;background:#f5f5f5}
h1{color:#333;border-bottom:2px solid #333;padding-bottom:10px}
.meta{color:#666;margin-bottom:20px}
table{width:100%;border-collapse:collapse;background:white;box-shadow:0 1px 3px rgba(0,0,0,.1)}
th{background:#2c3e50;color:white;padding:10px;text-align:center}
td{padding:8px 10px;border-bottom:1px solid #eee;text-align:center}
tr:hover{background:#f9f9f9}
.sabc-S{color:#e74c3c;font-weight:bold;font-size:1.2em}
.sabc-A{color:#e67e22;font-weight:bold}
.sabc-B{color:#3498db}
.sabc-C{color:#95a5a6}
.danger{color:#e74c3c;font-weight:bold}
.debuff-row{background:#fff9c4}
.warn{background:#ffebee;padding:15px;border-radius:5px;margin:20px 0}
.json-block{background:#263238;color:#aed6f1;padding:15px;border-radius:5px;font-family:monospace;font-size:.85em;overflow-x:auto;white-space:pre}
</style>
</head>
<body>
<h1>パドック診断データ - {{ r.venue }}{{ r.race_number }}R</h1>
<div class="meta">分析日: {{ r.date }} | フレーム数: {{ r.total_frames }}枚 | モデル: LLaVA 13B</div>
<table>
<tr><th>馬番</th><th>馬名</th><th>体重</th><th>騎手</th><th>SABC</th><th>前進気勢</th><th>発汗</th><th>歩様</th><th>引き手</th><th>コース適性</th><th>F数</th><th>特記</th></tr>
{% for h in r.horses %}
<tr{% if h.debuff_flag %} class="debuff-row"{% endif %}>
<td>{{ h.horse_number }}</td><td>{{ h.horse_name }}</td><td>{{ h.weight_change }}</td><td>{{ h.jockey }}</td>
<td class="sabc-{{ h.sabc }}">{{ h.sabc }}</td>
<td>{% if h.zenshin_kise_score >= 10 %}★{% endif %}{{ h.zenshin_kise_score }}</td>
<td{% if h.sweat == "危険" %} class="danger"{% endif %}>{% if h.sweat == "危険" %}⚠️危険{% else %}{{ h.sweat }}{% endif %}</td>
<td>{{ h.gait }}</td><td>{{ h.handlers }}人</td>
<td>{{ h.course_fit | join("・") }}</td><td>{{ h.frame_count }}</td><td>{{ h.notes }}</td>
</tr>
{% endfor %}
</table>
{% set warns = r.horses | selectattr("debuff_flag") | list %}
{% if warns %}
<div class="warn"><strong>⚠️ 注意馬:</strong><br>
{% for h in warns %}{{ h.horse_number }}番 {{ h.horse_name }}: {{ h.notes }}<br>{% endfor %}
</div>{% endif %}
<h3>OSバフ/デバフ連携データ（JSON）</h3>
<div class="json-block">{{ paddock_json }}</div>
</body></html>"""

def generate_html(report: SessionReport) -> str:
    paddock_json = json.dumps(
        {"paddock_agent": [
            {"horse_number": h.horse_number, "horse_name": h.horse_name,
             "sabc": h.sabc, "zenshin_kise": h.zenshin_kise_score,
             "debuff": h.debuff_flag, "course_fit": h.course_fit}
            for h in report.horses
        ]}, ensure_ascii=False, indent=2
    )
    return Template(_TEMPLATE).render(r=report, paddock_json=paddock_json)

def save_report(report: SessionReport, output_dir: str = "reports") -> str:
    Path(output_dir).mkdir(exist_ok=True)
    filename = f"パドック診断データ_{report.venue}{report.race_number}R_{report.date}.html"
    path = Path(output_dir) / filename
    path.write_text(generate_html(report), encoding="utf-8")
    return str(path)
