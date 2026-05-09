"""
Sustainability News Digest
Fetches this week's sustainability news, summarizes it with Claude,
and saves it as an HTML file you can open in any browser.
"""

import os
import anthropic
import json
from datetime import date

# ── Configuration ────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

FOCUS_AREAS = [
    "corporate sustainability and net zero commitments",
    "green technology startups and climate tech",
    "clean energy and renewables (solar, wind, storage)",
    "climate policy and regulation (EU taxonomy, SEC rules, carbon markets)",
]

TODAY = date.today().strftime("%B %d, %Y")
FILENAME = f"digest-{date.today().strftime('%Y-%m-%d')}.html"

# ── Step 1: Search for this week's news with Claude's web search tool ─────────
def fetch_news() -> str:
    """Uses Claude with web_search to find this week's sustainability news."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    search_prompt = f"""Today is {TODAY}. Search the web for the most important sustainability and climate news published in the last 7 days.

Focus specifically on:
{chr(10).join(f"- {area}" for area in FOCUS_AREAS)}

Search for at least 8-10 different articles across these topics. For each article you find, note:
- The headline
- The source/outlet
- The FULL URL of the article (this is critical — include the complete https:// link)
- A 2-3 sentence summary of the key facts
- Why it matters for sustainability professionals

Return your findings as a structured list of articles, always including the full URL for each one."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": search_prompt}],
    )

    raw_news = ""
    for block in response.content:
        if block.type == "text":
            raw_news += block.text

    return raw_news


# ── Step 2: Turn raw research into a polished digest ─────────────────────────
def summarize_into_digest(raw_news: str) -> dict:
    """Takes raw news findings and produces a clean, structured digest."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are a sustainability intelligence analyst. Based on the following news research for {TODAY}, create a professional weekly digest.

RAW RESEARCH:
{raw_news}

Format your response as a JSON object with this exact structure:
{{
  "title": "a compelling title for the weekly digest including today's date",
  "intro": "2-3 sentence executive summary of the most important themes this week",
  "sections": [
    {{
      "theme": "Section title (e.g. Corporate Net Zero, Clean Energy, etc.)",
      "stories": [
        {{
          "headline": "Story headline",
          "source": "Publication name",
          "summary": "2-3 sentence summary of the story and why it matters",
          "signal": "One sentence on what this means for sustainability professionals",
          "links": [
            {{"label": "Read more", "url": "https://full-article-url-here.com"}},
            {{"label": "Related", "url": "https://second-source-url-here.com"}}
          ]
        }}
      ]
    }}
  ],
  "closing": "One sentence forward-looking observation or question to watch"
}}

IMPORTANT for links:
- Include 1-2 real URLs per story taken directly from the research above
- Only include URLs that actually appeared in the research — do not invent or guess URLs
- If only one real URL is available for a story, include just one link
- Every URL must start with https://

Group stories by the 4 focus themes. Include only stories that are genuinely relevant and newsworthy. Aim for 6-10 total stories across all sections. Be concise and professional."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


# ── Step 3: Render as a beautiful HTML page ───────────────────────────────────
def render_html(digest: dict) -> str:
    """Converts the digest dict into a clean HTML page."""

    # Color palette: slate blue + warm amber accent — professional, not black/white
    HEADER_BG    = "#1e3a5f"   # deep navy blue
    HEADER_LABEL = "#93c5fd"   # soft sky blue
    HEADER_DATE  = "#94a3b8"   # muted slate
    ACCENT       = "#2563eb"   # vivid blue (section titles, borders, links)
    INTRO_BG     = "#eff6ff"   # pale blue tint
    INTRO_BORDER = "#bfdbfe"   # light blue border
    INTRO_TEXT   = "#1e3a5f"   # deep navy
    CARD_BG      = "#f8fafc"   # near-white with cool tint
    CARD_BORDER  = "#2563eb"   # vivid blue left border
    HEADLINE     = "#0f172a"   # very dark slate (not pure black)
    SOURCE       = "#64748b"   # medium slate
    BODY_TEXT    = "#334155"   # dark slate
    SIGNAL_COLOR = "#1d4ed8"   # rich blue for signal line
    LINK_COLOR   = "#2563eb"   # blue links
    SECTION_LINE = "#e2e8f0"   # light divider
    WATCH_BG     = "#f1f5f9"   # very light slate
    FOOTER_BG    = "#1e3a5f"   # matches header
    PAGE_BG      = "#e8edf5"   # soft blue-grey page background

    sections_html = ""
    for section in digest["sections"]:
        stories_html = ""
        for story in section["stories"]:

            # Build source links
            links_html = ""
            for link in story.get("links", []):
                url = link.get("url", "")
                label = link.get("label", "Read more")
                if url.startswith("https://"):
                    links_html += f'<a href="{url}" target="_blank" style="display:inline-block; margin-right:12px; font-size:12px; color:{LINK_COLOR}; text-decoration:none; font-weight:500; border-bottom:1px solid {LINK_COLOR}; padding-bottom:1px;">{label} →</a>'

            links_section = f'<div style="margin-top:10px;">{links_html}</div>' if links_html else ""

            stories_html += f"""
            <div style="margin-bottom:20px; padding:18px 20px; background:{CARD_BG}; border-left:3px solid {CARD_BORDER}; border-radius:6px;">
              <div style="font-weight:600; color:{HEADLINE}; margin-bottom:4px; font-size:15px; line-height:1.4;">{story['headline']}</div>
              <div style="font-size:11px; color:{SOURCE}; margin-bottom:10px; text-transform:uppercase; letter-spacing:0.05em; font-weight:500;">{story['source']}</div>
              <div style="color:{BODY_TEXT}; font-size:14px; line-height:1.7; margin-bottom:10px;">{story['summary']}</div>
              <div style="font-size:13px; color:{SIGNAL_COLOR}; font-style:italic; padding-top:8px; border-top:1px solid {SECTION_LINE};">→ {story['signal']}</div>
              {links_section}
            </div>"""

        sections_html += f"""
        <div style="margin-bottom:36px;">
          <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:{ACCENT}; margin-bottom:14px; padding-bottom:10px; border-bottom:2px solid {SECTION_LINE};">
            {section['theme']}
          </div>
          {stories_html}
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sustainability Digest — {TODAY}</title>
</head>
<body style="margin:0; padding:0; background:{PAGE_BG}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
  <div style="max-width:700px; margin:40px auto; background:#ffffff; border-radius:10px; overflow:hidden; box-shadow:0 2px 12px rgba(30,58,95,0.12);">

    <!-- Header -->
    <div style="background:{HEADER_BG}; padding:36px 44px;">
      <div style="font-size:10px; font-weight:700; letter-spacing:0.15em; color:{HEADER_LABEL}; text-transform:uppercase; margin-bottom:10px;">
        Weekly Intelligence Digest
      </div>
      <div style="font-size:26px; font-weight:700; color:#ffffff; line-height:1.25; letter-spacing:-0.01em;">
        Sustainability &amp; Climate Brief
      </div>
      <div style="font-size:13px; color:{HEADER_DATE}; margin-top:10px; font-weight:400;">
        Week of {TODAY}
      </div>
    </div>

    <!-- Intro -->
    <div style="padding:28px 44px; background:{INTRO_BG}; border-bottom:1px solid {INTRO_BORDER};">
      <div style="color:{INTRO_TEXT}; font-size:15px; line-height:1.8; font-weight:400;">{digest['intro']}</div>
    </div>

    <!-- Stories -->
    <div style="padding:36px 44px;">
      {sections_html}
    </div>

    <!-- To Watch -->
    <div style="padding:24px 44px; background:{WATCH_BG}; border-top:1px solid {SECTION_LINE};">
      <div style="color:{SOURCE}; font-size:13px; line-height:1.7;">
        <strong style="color:{HEADLINE}; font-weight:600;">To watch this week:</strong> {digest['closing']}
      </div>
    </div>

    <!-- Footer -->
    <div style="padding:20px 44px; background:{FOOTER_BG};">
      <div style="font-size:11px; color:{HEADER_DATE}; text-align:center; letter-spacing:0.03em;">
        Generated by Claude · {TODAY}
      </div>
    </div>

  </div>
</body>
</html>"""


# ── Step 4: Save the HTML file ────────────────────────────────────────────────
def save_digest(html: str) -> None:
    """Saves the digest as an HTML file in the current folder."""
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Digest saved as: {FILENAME}")
    print(f"  Open it in your browser with: open {FILENAME}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[{TODAY}] Fetching this week's sustainability news...")
    raw = fetch_news()
    print("✓ News fetched. Generating digest...")
    digest = summarize_into_digest(raw)
    print(f"✓ Digest ready: {len(digest['sections'])} sections, {sum(len(s['stories']) for s in digest['sections'])} stories")
    html = render_html(digest)
    save_digest(html)
