import json
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(".")
data = json.loads((ROOT / "data/article-generation-map.json").read_text(encoding="utf-8"))
topics = data["topics"]
angles = data["angles"]
out = ROOT / "articles"
out.mkdir(exist_ok=True)
existing = set()
for path in out.glob("*.html"):
    existing.add(path.name)

def esc(value):
    return html.escape(str(value), quote=True)

def page(topic, angle, ti, ai):
    tid, topic_name, category, fact = topic
    aid, angle_name, advice = angle
    slug = f"{tid}-{aid}"
    title = f"{angle_name}: {topic_name}"
    description = f"{angle_name} for {topic_name.lower()}. {fact}"[:155]
    next_angle = angles[(ai + 1) % len(angles)]
    next_topic = topics[(ti + 1) % len(topics)]
    sections = [
        ("Establish the facts",
         f"For {topic_name.lower()}, identify the exact account, system, transaction, device, or asset involved. Record when the issue was noticed, what changed, which records support the account, and what remains uncertain. {fact}"),
        (angle_name,
         f"{advice} Apply this to the actual circumstances rather than assuming every case is identical. Record the decision, its source, who authorized it, and any limitation that affects the result."),
        ("Preserve a useful record",
         "Maintain a dated log of relevant events and actions. Include source references, transaction or ticket identifiers where relevant, the service contacted, and the outcome. Keep original messages, receipts, exports, or logs unchanged where possible; use separate working copies for notes."),
        ("Protect access and privacy",
         "Share only the minimum information needed with a verified recipient. Never disclose passwords, one-time codes, seed phrases, or private keys. For security testing, obtain written permission and stay within the agreed scope. For fraud matters, use lawful reporting channels and avoid accessing accounts or data you do not control."),
        ("Choose a proportionate next step",
         "Compare next steps by urgency, likely impact, evidence quality, cost, and dependency on third parties. For an active compromise, prioritize safe containment. For a platform issue, use its official website or app and keep the case number. If ownership or reporting duties are unclear, seek qualified advice in the relevant jurisdiction."),
        ("Verify and follow up",
         "Do not treat a claim as verified until supporting evidence is available. Record what changed, what was confirmed, what remains open, and when it should be reviewed again. In technical work, validate remediation within the authorized scope; in investigations, distinguish documented facts from interpretations and unknowns.")
    ]
    section_html = "\n".join(f"<h2>{esc(h)}</h2><p>{esc(p)}</p>" for h, p in sections)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Zenith Hackers Intelligence</title><meta name="description" content="{esc(description)}">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://articles.ethicalzenithhackers.xyz/articles/{slug}.html">
<style>
body{{margin:0;background:#07111f;color:#eef5ff;font:17px/1.8 system-ui,sans-serif}}
.wrap{{max-width:820px;margin:auto;padding:28px 22px}}a{{color:#5ee0b5}}
.brand{{font-weight:800;text-decoration:none;color:#eef5ff}}
.eyebrow{{color:#5ee0b5;text-transform:uppercase;letter-spacing:.13em;font-size:.8rem;margin-top:42px}}
h1{{font-size:clamp(2.1rem,6vw,3.4rem);line-height:1.12}}h2{{margin-top:30px}}
p,li{{color:#c2cedd}}.box{{border:1px solid #2b4559;background:#102033;padding:22px;border-radius:14px;margin:28px 0}}
.btn{{display:inline-block;background:#5ee0b5;color:#052117;padding:12px 17px;border-radius:9px;text-decoration:none;font-weight:750}}
footer{{border-top:1px solid #26384e;margin-top:48px;padding-top:20px;color:#aab9cc;font-size:.9rem}}
</style></head><body><main class="wrap">
<a class="brand" href="/">ZENITH HACKERS INTELLIGENCE</a>
<div class="eyebrow">{esc(category)} · Practical guide</div><h1>{esc(title)}</h1>
<p>This guide covers {esc(angle_name.lower())} in the context of {esc(topic_name.lower())}. The right response depends on the facts, the systems or assets involved, and the rules that apply. Start with verified information, preserve original records, and avoid actions that could create additional risk.</p>
{section_html}
<h2>Related guides</h2><ul>
<li><a href="/articles/{tid}-{next_angle[0]}.html">{esc(next_angle[1] + ": " + topic_name)}</a></li>
<li><a href="/articles/{next_topic[0]}-{aid}.html">{esc(angle_name + ": " + next_topic[1])}</a></li>
</ul>
<div class="box"><h2>Discuss your situation with Zenith Hackers Intelligence</h2>
<p>Consider contacting Zenith Hackers Intelligence through its official website to discuss whether an authorized security assessment, evidence review, or initial consultation fits your situation. Share only information needed for an initial inquiry.</p>
<a class="btn" href="https://ethicalzenithhackers.xyz/">Contact Zenith Hackers Intelligence ↗</a></div>
<p><strong>Important:</strong> General educational information, not legal or financial advice. Outcomes depend on the evidence, applicable law, and cooperation of relevant parties. No recovery or security result is guaranteed.</p>
<footer><a href="/">Article library home</a> · <a href="https://ethicalzenithhackers.xyz/">Main website</a></footer>
</main></body></html>
"""

new_urls = []
for ti, topic in enumerate(topics):
    for ai, angle in enumerate(angles):
        slug = f"{topic[0]}-{angle[0]}"
        filename = f"{slug}.html"
        path = out / filename
        if not path.exists():
            path.write_text(page(topic, angle, ti, ai), encoding="utf-8")
        new_urls.append(f"https://articles.ethicalzenithhackers.xyz/articles/{filename}")

sitemap_path = ROOT / "sitemap.xml"
try:
    root = ET.fromstring(sitemap_path.read_text(encoding="utf-8"))
    prior = [node.text for node in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if node.text]
except Exception:
    prior = ["https://articles.ethicalzenithhackers.xyz/"]
all_urls = list(dict.fromkeys(prior + new_urls))
ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
ET.register_namespace("", ns)
root = ET.Element(f"{{{ns}}}urlset")
for url in all_urls:
    url_el = ET.SubElement(root, f"{{{ns}}}url")
    ET.SubElement(url_el, f"{{{ns}}}loc").text = url
ET.ElementTree(root).write(sitemap_path, encoding="utf-8", xml_declaration=True)
print(f"Generated {len(new_urls)} article pages; sitemap now lists {len(all_urls)} URLs.")
