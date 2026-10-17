#!/usr/bin/env python3
"""Generate one bilingual Persian/English article and update the static site."""
from __future__ import annotations
import base64, datetime as dt, html, json, os, re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BLOG = ROOT / "blog"
TEMPLATE = Path(__file__).with_name("article-template.html")
SITE = "https://mohammadmahdinaeiji.ir"
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
TEXT_MODEL = os.environ.get("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
IMAGE_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")

class PublishError(RuntimeError):
    pass

def api_post(path: str, payload: dict, timeout: int = 240) -> dict:
    if not API_KEY:
        raise PublishError("OPENAI_API_KEY is missing")
    req = urllib.request.Request(
        "https://api.openai.com/v1/" + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:1500]
        raise PublishError(f"OpenAI API error {e.code}: {detail}") from e
    except Exception as e:
        raise PublishError(f"OpenAI API request failed: {e}") from e

def request_article(existing_slugs: list[str]) -> dict:
    prompt = f"""Create one original, genuinely useful bilingual Persian/English blog article for a graphic designer's portfolio blog. The writer is Mohammadmahdi Naeiji. Topics may include graphic design, visual identity, typography, illustration, creative process, AI and design, portfolio practice, or visual culture. Choose a specific angle, not generic SEO filler. Avoid duplicating these existing article slugs: {existing_slugs}.
Return ONLY valid JSON with this exact shape:
{{"slug":"short-english-kebab-case-slug","title_fa":"...","title_en":"...","description_fa":"...","description_en":"...","intro_fa":"...","intro_en":"...","category_fa":"طراحی","category_en":"Design","alt_fa":"...","alt_en":"...","image_prompt":"Detailed art-direction prompt for a sophisticated editorial cover image, no text/letters/logos/watermarks","sections":[{{"heading_fa":"...","heading_en":"...","paragraphs_fa":["...","..."],"paragraphs_en":["...","..."]}}]}}
Requirements:
- Persian must be natural contemporary Persian, not a literal translation; English must read naturally.
- 5 to 7 sections. Each section has 2-3 substantive paragraphs in BOTH languages, corresponding in meaning.
- Article should be specific, practical, original, non-repetitive, with examples and a clear conclusion. No unsupported claims or fabricated sources/statistics.
- Both intros are about 40-70 words; descriptions around 120-160 characters.
- Slug must be English lowercase kebab-case, 3-7 words, ASCII letters/digits/hyphens only.
- image_prompt must describe one cohesive editorial image appropriate to the topic, with no text, typography, logos, or watermarks.
- Output valid JSON only. No markdown fences."""
    result = api_post("chat/completions", {
        "model": TEXT_MODEL,
        "temperature": 0.8,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "You are an experienced bilingual editor and design writer. Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
    })
    try:
        article = json.loads(result["choices"][0]["message"]["content"])
    except Exception as e:
        raise PublishError(f"Could not parse article JSON: {e}") from e
    validate_article(article)
    return article

def validate_article(a: dict) -> None:
    required = ["slug", "title_fa", "title_en", "description_fa", "description_en", "intro_fa", "intro_en", "category_fa", "category_en", "alt_fa", "alt_en", "image_prompt", "sections"]
    missing = [k for k in required if not a.get(k)]
    if missing:
        raise PublishError("Article missing fields: " + ", ".join(missing))
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+){2,6}", str(a["slug"])):
        raise PublishError("Unsafe/invalid slug: " + repr(a["slug"]))
    if not isinstance(a["sections"], list) or not 5 <= len(a["sections"]) <= 7:
        raise PublishError("Article must contain 5-7 sections")
    for i, sec in enumerate(a["sections"], 1):
        for key in ("heading_fa", "heading_en", "paragraphs_fa", "paragraphs_en"):
            if not sec.get(key):
                raise PublishError(f"Section {i} missing {key}")
        if not isinstance(sec["paragraphs_fa"], list) or not isinstance(sec["paragraphs_en"], list):
            raise PublishError(f"Section {i} paragraphs must be arrays")
        if len(sec["paragraphs_fa"]) < 2 or len(sec["paragraphs_en"]) < 2:
            raise PublishError(f"Section {i} needs at least two paragraphs per language")
        if len(sec["paragraphs_fa"]) != len(sec["paragraphs_en"]):
            raise PublishError(f"Section {i} Persian/English paragraph counts differ")
    total_fa = sum(len(p) for s in a["sections"] for p in s["paragraphs_fa"])
    total_en = sum(len(p) for s in a["sections"] for p in s["paragraphs_en"])
    if total_fa < 1800 or total_en < 1800:
        raise PublishError(f"Article too short (fa={total_fa}, en={total_en} characters)")

def generate_image(prompt: str) -> bytes:
    result = api_post("images/generations", {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "size": "1024x1024",
        "n": 1,
        "output_format": "png",
    }, timeout=360)
    try:
        return base64.b64decode(result["data"][0]["b64_json"])
    except Exception as e:
        raise PublishError(f"Image generation returned no base64 image: {e}") from e

def esc(v: str) -> str:
    return html.escape(str(v), quote=True)

def text(v: str) -> str:
    return html.escape(str(v), quote=False)

def render_body(a: dict) -> str:
    out = []
    for sec in a["sections"]:
        out.append(f'<h2 data-fa="{esc(sec["heading_fa"])}" data-en="{esc(sec["heading_en"])}">{text(sec["heading_fa"])}</h2>')
        for fa, en in zip(sec["paragraphs_fa"], sec["paragraphs_en"]):
            out.append(f'<p data-fa="{esc(fa)}" data-en="{esc(en)}">{text(fa)}</p>')
    return "\n\n      ".join(out)

def card_home(a: dict) -> str:
    url = f'{SITE}/blog/{a["slug"]}/'
    img = f'{SITE}/blog/{a["slug"]}/images/cover.png'
    return f"""<a class="blog-card-template blog-card-link" href="{url}" aria-label="{esc(a['title_fa'])}">
                    <img src="{img}" alt="{esc(a['alt_fa'])}" loading="lazy" decoding="async">
                    <div class="blog-card-copy">
                        <h3 data-fa="{esc(a['title_fa'])}" data-en="{esc(a['title_en'])}">{text(a['title_fa'])}</h3>
                        <p data-fa="{esc(a['description_fa'])}" data-en="{esc(a['description_en'])}">{text(a['description_fa'])}</p>
                    </div>
                </a>"""

def card_blog(a: dict, date_label: str) -> str:
    url = f'{SITE}/blog/{a["slug"]}/'
    img = f'/blog/{a["slug"]}/images/cover.png'
    return f"""<a class="blog-card" href="{url}">
      <div class="blog-cover">
        <img src="{img}" alt="{esc(a['alt_fa'])}" loading="lazy" decoding="async">
      </div>
      <div class="blog-card-body">
        <div class="blog-meta"><span data-fa="{esc(a['category_fa'])}" data-en="{esc(a['category_en'])}">{text(a['category_fa'])}</span><span>{date_label}</span></div>
        <h2 class="blog-title-card" data-fa="{esc(a['title_fa'])}" data-en="{esc(a['title_en'])}">{text(a['title_fa'])}</h2>
        <p class="blog-excerpt" data-fa="{esc(a['description_fa'])}" data-en="{esc(a['description_en'])}">{text(a['description_fa'])}</p>
      </div>
    </a>"""

def insert_after_marker(path: Path, card: str) -> None:
    content = path.read_text(encoding="utf-8")
    marker = "<!-- AUTO BLOG CARDS START -->"
    if marker not in content or "<!-- AUTO BLOG CARDS END -->" not in content:
        raise PublishError(f"Missing card markers in {path.relative_to(ROOT)}")
    content = content.replace(marker, marker + "\n" + card + "\n", 1)
    path.write_text(content, encoding="utf-8")

def update_sitemap(slug: str, date: str) -> None:
    path = ROOT / "sitemap.xml"
    if not path.exists():
        return
    s = path.read_text(encoding="utf-8")
    url = f"{SITE}/blog/{slug}/"
    if url in s:
        raise PublishError("Article URL already exists in sitemap")
    entry = f"\n  <url>\n    <loc>{url}</loc>\n    <lastmod>{date}</lastmod>\n    <priority>0.70</priority>\n  </url>\n"
    s = s.replace("</urlset>", entry + "</urlset>")
    path.write_text(s, encoding="utf-8")

def render_page(a: dict) -> str:
    t = TEMPLATE.read_text(encoding="utf-8")
    values = {
        "__TITLE_FA__": esc(a["title_fa"]), "__TITLE_EN__": esc(a["title_en"]),
        "__DESCRIPTION_FA__": esc(a["description_fa"]),
        "__KEYWORDS__": esc(", ".join([a["category_fa"], a["category_en"], "طراحی گرافیک", "Graphic Design", "محمدمهدی نائیجی"])),
        "__SLUG__": a["slug"], "__INTRO_FA__": esc(a["intro_fa"]), "__INTRO_EN__": esc(a["intro_en"]),
        "__ALT_FA__": esc(a["alt_fa"]), "__ALT_EN__": esc(a["alt_en"]), "__ARTICLE_BODY__": render_body(a),
    }
    for k, v in values.items():
        t = t.replace(k, v)
    if re.search(r"__[A-Z_]+__", t):
        raise PublishError("Unresolved placeholder remains in article template")
    canonical = f'<link rel="canonical" href="{SITE}/blog/{a["slug"]}/">'
    if 'rel="canonical"' not in t:
        t = t.replace("</head>", canonical + "\n</head>", 1)
    return t

def validate_publish(slug: str, page: str, home_card_html: str, blog_card_html: str) -> None:
    if not re.search(r"<h1\b", page, re.I) or "</html>" not in page.lower():
        raise PublishError("Generated article HTML is incomplete")
    if "data-fa=" not in page or "data-en=" not in page:
        raise PublishError("Generated page is not bilingual")
    if re.search(r"__[A-Z_]+__", page):
        raise PublishError("Generated page contains placeholder tokens")
    if f"/blog/{slug}/images/cover.png" not in page:
        raise PublishError("Article cover path missing")
    if "blog-card-link" not in home_card_html or "blog-title-card" not in blog_card_html:
        raise PublishError("Card structure validation failed")

def main() -> None:
    if not (ROOT / "index.html").exists() or not (BLOG / "index.html").exists():
        raise PublishError("Expected static site files not found")
    existing = [p.name for p in BLOG.iterdir() if p.is_dir()]
    article = request_article(existing)
    slug = article["slug"]
    target = BLOG / slug
    if target.exists():
        raise PublishError(f"Slug already exists: {slug}")
    cover_prompt = article["image_prompt"] + "\nCreate a polished editorial cover image for a bilingual graphic-design blog. Strong composition, tasteful restrained palette, high craft, no text, no letters, no logos, no watermark."
    inline_prompt = article["image_prompt"] + "\nCreate a second distinct supporting editorial illustration for the same article. Change composition and viewpoint while preserving the visual direction. No text, no letters, no logos, no watermark."
    cover = generate_image(cover_prompt)
    inline = generate_image(inline_prompt)
    body = render_body(article)
    inline_html = f'<figure class="article-image"><div class="article-image-frame"><img src="/blog/{slug}/images/visual-02.png" alt="{esc(article["alt_fa"])}" loading="lazy" decoding="async"></div></figure>'
    parts = body.split("\n\n      ")
    if len(parts) >= 4:
        parts.insert(4, inline_html)
    else:
        parts.append(inline_html)
    body_with_image = "\n\n      ".join(parts)
    page = render_page(article).replace(body, body_with_image)
    home_card_html = card_home(article)
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    blog_card_html = card_blog(article, today)
    validate_publish(slug, page, home_card_html, blog_card_html)
    # Nothing is committed unless all generation and validation steps succeed.
    target_images = target / "images"
    target_images.mkdir(parents=True, exist_ok=False)
    (target_images / "cover.png").write_bytes(cover)
    (target_images / "visual-02.png").write_bytes(inline)
    (target / "index.html").write_text(page, encoding="utf-8")
    insert_after_marker(ROOT / "index.html", home_card_html)
    insert_after_marker(BLOG / "index.html", blog_card_html)
    update_sitemap(slug, today)
    for rel in [f"blog/{slug}/index.html", f"blog/{slug}/images/cover.png", f"blog/{slug}/images/visual-02.png"]:
        if not (ROOT / rel).is_file():
            raise PublishError("Missing generated file: " + rel)
    for path in [ROOT / "index.html", BLOG / "index.html"]:
        if f"/blog/{slug}/" not in path.read_text(encoding="utf-8"):
            raise PublishError("New card missing from " + str(path))
    print(json.dumps({"status": "ok", "slug": slug, "title_fa": article["title_fa"], "title_en": article["title_en"], "article": f"blog/{slug}/index.html", "images": 2}, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except PublishError as e:
        print(f"PUBLISH VALIDATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
