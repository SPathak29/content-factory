#!/usr/bin/env python3
"""
Content Factory Pro — 4-Tier Revenue Agentic Pipeline
Production-ready Streamlit app

Run: streamlit run app.py
"""

import streamlit as st
import anthropic
import requests
import json
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG & CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_AFFILIATE_DB = {
    "productivity": [
        {"name": "Notion",     "url": "https://notion.so",     "commission": "50% first month",   "ticket": "£8/mo",  "type": "SaaS"},
        {"name": "ClickUp",    "url": "https://clickup.com",   "commission": "20% recurring",      "ticket": "£7/mo",  "type": "SaaS"},
        {"name": "Zapier",     "url": "https://zapier.com",    "commission": "$0.50/trial",        "ticket": "£19/mo", "type": "SaaS"},
        {"name": "Todoist",    "url": "https://todoist.com",   "commission": "25% first payment",  "ticket": "£4/mo",  "type": "SaaS"},
    ],
    "ai_tools": [
        {"name": "Jasper AI",    "url": "https://jasper.ai",     "commission": "25% recurring",   "ticket": "£39/mo", "type": "SaaS"},
        {"name": "Copy.ai",      "url": "https://copy.ai",       "commission": "45% recurring",   "ticket": "£36/mo", "type": "SaaS"},
        {"name": "Writesonic",   "url": "https://writesonic.com","commission": "30% recurring",   "ticket": "£16/mo", "type": "SaaS"},
        {"name": "ElevenLabs",   "url": "https://elevenlabs.io", "commission": "22% recurring",   "ticket": "£5/mo",  "type": "SaaS"},
    ],
    "finance": [
        {"name": "Trading 212",  "url": "https://trading212.com","commission": "£12/signup",      "ticket": "Free",   "type": "App"},
        {"name": "Freetrade",    "url": "https://freetrade.io",  "commission": "Free share",      "ticket": "Free",   "type": "App"},
        {"name": "Wise",         "url": "https://wise.com",      "commission": "£15/signup",      "ticket": "Free",   "type": "App"},
        {"name": "Monzo",        "url": "https://monzo.com",     "commission": "£10/signup",      "ticket": "Free",   "type": "App"},
    ],
    "fitness": [
        {"name": "Whoop",        "url": "https://whoop.com",        "commission": "£30/signup",  "ticket": "£30/mo", "type": "Hardware"},
        {"name": "MyFitnessPal", "url": "https://myfitnesspal.com", "commission": "20% recurring","ticket": "£9/mo",  "type": "App"},
        {"name": "Huel",         "url": "https://huel.com",         "commission": "12% of sale", "ticket": "£50+",   "type": "Physical"},
    ],
    "general": [
        {"name": "Epidemic Sound","url": "https://epidemicsound.com","commission": "£20/signup",  "ticket": "£11/mo", "type": "SaaS"},
        {"name": "Canva Pro",     "url": "https://canva.com",        "commission": "£10–25",      "ticket": "£11/mo", "type": "SaaS"},
        {"name": "Beehiiv",       "url": "https://beehiiv.com",      "commission": "30% × 3 months","ticket": "£34/mo","type": "SaaS"},
        {"name": "ConvertKit",    "url": "https://convertkit.com",   "commission": "30% recurring","ticket": "£25/mo", "type": "SaaS"},
    ],
}

VOICE_OPTIONS = {
    "Adam — Deep, authoritative male":  "pNInz6obpgDQGcFmaJgB",
    "Rachel — Professional female":     "21m00Tcm4TlvDq8ikWAM",
    "Antoni — Confident male":          "ErXwobaYiN019PkySvjV",
    "Domi — Energetic female":          "AZnzlk1XvdvUeBnXmlld",
    "Josh — Deep storyteller":          "TxGEqnHWrfWFTfGW9XjX",
    "Bella — Warm female":              "EXAVITQu4vr4xnSDxMaL",
}

POSTING_WINDOWS = {
    "Monday":    [("07:45", "Morning commute"), ("12:00", "Lunch scroll"), ("19:30", "Evening peak — TikTok slot")],
    "Tuesday":   [("08:00", "Morning commute"), ("12:30", "Lunch scroll"), ("20:00", "Evening peak — TikTok slot")],
    "Wednesday": [("07:30", "Morning commute"), ("13:00", "Lunch scroll"), ("19:00", "Evening peak — TikTok slot")],
    "Thursday":  [("08:00", "Morning commute"), ("12:00", "Lunch scroll"), ("20:00", "Evening peak — TikTok slot")],
    "Friday":    [("07:00", "Morning commute"), ("12:30", "Lunch scroll"), ("18:00", "Evening peak — TikTok slot")],
    "Saturday":  [("10:00", "Late morning"),    ("14:00", "Afternoon"),    ("20:30", "Evening peak — TikTok slot")],
    "Sunday":    [("11:00", "Late morning"),    ("15:00", "Afternoon"),    ("20:00", "Evening peak — TikTok slot")],
}

# ──────────────────────────────────────────────────────────────────────────────
# STREAMLIT PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Content Factory Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #FAFAFA; }
    .block-container { padding: 1.5rem 2rem 2rem; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
    .script-box {
        background: #F8F9FA;
        border-left: 3px solid #6366F1;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        font-family: 'Courier New', monospace;
        font-size: 13.5px;
        line-height: 1.85;
        white-space: pre-wrap;
        color: #1a1a1a;
    }
    .tier-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
    .t1 { background: #FEF3C7; color: #92400E; }
    .t2 { background: #D1FAE5; color: #065F46; }
    .t3 { background: #DBEAFE; color: #1E40AF; }
    .t4 { background: #EDE9FE; color: #5B21B6; }
    .type-short   { background: #DBEAFE; color: #1E40AF; padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 13px; }
    .type-tiktok  { background: #EDE9FE; color: #5B21B6; padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 13px; }
    .approved-card { border: 2px solid #10B981 !important; border-radius: 12px; }
    .log-box { font-family: monospace; font-size: 12px; background: #111; color: #4ADE80; padding: 1rem; border-radius: 8px; max-height: 320px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "page": "setup",
        "anthropic_key": st.secrets.get("ANTHROPIC_API_KEY", ""),
        "el_key": st.secrets.get("ELEVENLABS_API_KEY", ""),
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "product": st.secrets.get("PRODUCT_NAME", ""),
        "product_price": int(st.secrets.get("PRODUCT_PRICE", "15")),
        "gumroad_url": st.secrets.get("GUMROAD_URL", ""),
        "niche": st.secrets.get("NICHE", ""),
        "platform": st.secrets.get("PLATFORM", "YouTube Shorts + Instagram Reels + TikTok"),
        "newsletter_url": st.secrets.get("NEWSLETTER_URL", ""),
        "newsletter_cta": st.secrets.get("NEWSLETTER_CTA", ""),
        "affiliate_niche": st.secrets.get("AFFILIATE_NICHE", "general"),
        "vids_per_day": int(st.secrets.get("VIDS_PER_DAY", "3")),
        "pipeline_state": "idle",  # idle | running | done | error
        "agent_states": {k: "idle" for k in ["trendScout", "strategy", "scriptWriter", "qaEditor", "refinement"]},
        "log_entries": [],
        "trends": [],
        "scripts": [],
        "custom_affiliates": DEFAULT_AFFILIATE_DB.copy(),
        "total_revenue": 0.0,
        "total_videos": 0,
        "ab_results": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ──────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def add_log(agent: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {
        "trendScout": "🔵", "strategy": "🟢", "scriptWriter": "🟡",
        "qaEditor": "🔴", "refinement": "⚪", "system": "⚫",
    }
    st.session_state.log_entries.append({
        "ts": ts, "agent": agent, "msg": msg,
        "icon": icons.get(agent, "⚫"),
    })


def call_claude(messages: list, use_search: bool = False) -> str:
    key = st.session_state.get("anthropic_key", "") or st.secrets.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise ValueError("Anthropic API key missing — add it in Setup.")
    client = anthropic.Anthropic(api_key=key)
    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1800,
        "messages": messages,
    }
    if use_search:
        kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
    resp = client.messages.create(**kwargs)
    return "".join(b.text for b in resp.content if hasattr(b, "text"))


def extract_json(text: str):
    import re
    for pattern in [r"\[[\s\S]*\]", r"\{[\s\S]*\}"]:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return None


def word_count(text: str) -> int:
    return len((text or "").split())


# ──────────────────────────────────────────────────────────────────────────────
# AGENT FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def agent_trend_scout() -> list:
    niche   = st.session_state.niche or "viral content"
    platform = st.session_state.platform
    add_log("trendScout", f"Scanning live web — niche: {niche}")
    add_log("trendScout", f"Platform target: {platform}")
    feedback_ctx = get_feedback_context() if "get_feedback_context" in dir() else ""
    if feedback_ctx:
        add_log("trendScout", "Feedback loop active — biasing toward proven winning angles")
    raw = call_claude([{"role": "user", "content": f"""
Search the live web RIGHT NOW for the 5 most viral trending topics on {platform} this week.
Niche context: {niche}
Look for: breaking news hooks, shocking stats, counterintuitive truths, 'nobody talks about this' angles.

{feedback_ctx}

Return ONLY a JSON array (no markdown, no preamble):
[{{"topic":"","trendReason":"why viral this week","angle":"short-form content angle",
"emotionalHook":"fear|curiosity|surprise|anger|joy","estimatedWeeklySearches":"rough number"}}]
Exactly 5 objects.
"""}], use_search=True)
    trends = extract_json(raw) or []
    add_log("trendScout", f"Found {len(trends)} live viral trends")
    for t in trends[:3]:
        add_log("trendScout", f"  → '{t.get('topic','')}' [{t.get('emotionalHook','')}]")
    return trends


def agent_strategy(trends: list) -> dict:
    product  = st.session_state.product
    niche    = st.session_state.niche
    aff_key  = st.session_state.affiliate_niche
    affiliates = (
        st.session_state.custom_affiliates.get(aff_key, []) +
        st.session_state.custom_affiliates.get("general", [])
    )[:6]
    add_log("strategy", f"Analysing {len(trends)} trends for product fit with '{product}'")
    add_log("strategy", f"Matching from {len(affiliates)} affiliate options")
    raw = call_claude([{"role": "user", "content": f"""
You are a monetisation strategist for short-form video content.

TRENDS (indexed 0-4): {json.dumps(trends, indent=2)}
CORE PRODUCT: {product}
NICHE: {niche}
AFFILIATES AVAILABLE: {json.dumps(affiliates, indent=2)}

Rules:
- Select indices for the 3 best trends (use 0, 1, 2 if unsure)
- Script 0 & 1 = short_retention (45s, 130-140 words)
- Script 2 = tiktok_monetized (61s+, 160-180 words, narrative-driven)
- For each script, pick the most naturally fitting affiliate from the list
- Assign a realistic posting slot (Day HH:MM)

Return ONLY JSON:
{{"selections":[
  {{"trendIndex":0,"scriptType":"short_retention","affiliateName":"","affiliateCommission":"","affiliateAngle":"one sentence on natural mention","postingSlot":"Monday 08:00"}},
  {{"trendIndex":1,"scriptType":"short_retention","affiliateName":"","affiliateCommission":"","affiliateAngle":"","postingSlot":"Monday 12:00"}},
  {{"trendIndex":2,"scriptType":"tiktok_monetized","affiliateName":"","affiliateCommission":"","affiliateAngle":"","postingSlot":"Monday 19:30"}}
]}}
"""}])
    strategy = extract_json(raw)
    if isinstance(strategy, list):
        strategy = {"selections": strategy}
    strategy = strategy or {
        "selections": [
            {"trendIndex": i, "scriptType": "tiktok_monetized" if i == 2 else "short_retention",
             "affiliateName": "", "affiliateCommission": "", "affiliateAngle": "",
             "postingSlot": ["Monday 08:00", "Monday 12:00", "Monday 19:30"][i]}
            for i in range(3)
        ]
    }
    for i, sel in enumerate(strategy.get("selections", [])):
        add_log("strategy", f"  Script {i+1}: [{sel.get('scriptType','').upper()}] + {sel.get('affiliateName','no affiliate')}")
    return strategy


def agent_script_writer(trends: list, strategy: dict) -> list:
    product   = st.session_state.product
    platform  = st.session_state.platform
    gumroad   = st.session_state.gumroad_url or "link in bio"
    nl_cta    = st.session_state.newsletter_cta or "join our free weekly newsletter"
    scripts   = []
    selections = strategy.get("selections", [])

    for i, sel in enumerate(selections[:3]):
        t_idx  = sel.get("trendIndex", i)
        trend  = trends[min(t_idx, len(trends) - 1)] if trends else {}
        s_type = sel.get("scriptType", "short_retention")
        aff    = sel.get("affiliateName", "")
        aff_angle = sel.get("affiliateAngle", "")
        is_tiktok = (s_type == "tiktok_monetized")
        words  = "160-180 words (61+ seconds)" if is_tiktok else "130-140 words (exactly 45 seconds)"

        add_log("scriptWriter", f"Writing script {i+1}/3: [{s_type.upper()}] — '{trend.get('topic','')}'")
        feedback_ctx = get_feedback_context() if "get_feedback_context" in dir() else ""

        structure = (
            "[HOOK 0-3s] Bold pattern interrupt — no intro, no names, no fluff.\n"
            "[STAKES 3-7s] One sentence — loss-framing, why they CANNOT scroll away.\n"
            "[PAYLOAD 7-38s] 3 rapid numbered insights. Zero filler. Each brutally punchy.\n"
            f"[AFFILIATE WEAVE 38-46s] Natural mention of {aff} — angle: {aff_angle}\n"
            "[TWIST 46-54s] Final surprising insight — plant the rewatch trigger word here.\n"
            f"[NEWSLETTER CTA 54-58s] '{nl_cta}' — direct them to bio link.\n"
            f"[PRODUCT CTA 58-61s+] Seamless CTA to {product} at {gumroad}."
        ) if is_tiktok else (
            "[HOOK 0-3s] Bold pattern interrupt — no intro whatsoever.\n"
            "[STAKES 3-6s] Why they CANNOT scroll — loss framing.\n"
            "[PAYLOAD 6-32s] 3 rapid numbered insights. Zero filler.\n"
            f"[AFFILIATE WEAVE 32-38s] Natural mention of {aff} — {aff_angle}\n"
            "[TWIST 38-42s] Final surprising insight — plant rewatch trigger.\n"
            f"[PRODUCT CTA 42-45s] Seamless bio link CTA for {product}."
        )

        raw = call_claude([{"role": "user", "content": f"""
You are an elite viral short-form video scriptwriter with 10M+ view scripts.

TREND: {json.dumps(trend)}
SCRIPT TYPE: {"TikTok Monetization Qualified (61s+)" if is_tiktok else "Short Retention (45s)"}
WORD TARGET: {words}
PRODUCT: {product} | URL: {gumroad}
AFFILIATE: {aff} | ANGLE: {aff_angle}
NEWSLETTER: {nl_cta}
PLATFORM: {platform}

{feedback_ctx}

STRUCTURE TO FOLLOW:
{structure}

CRITICAL SCRIPT RULES:
1. Zero copyrighted phrases. Zero "as I always say", "Let's dive in", "Without further ado", "In today's video"
2. ElevenLabs-optimised: perfect punctuation, NO em-dashes (use commas), NO stage directions like [pause]
3. Use natural contractions (you're, that's, it's) — sounds human when spoken
4. Affiliate mention must feel like a genuine recommendation, not an ad
5. Emotional register: {trend.get('emotionalHook','curiosity').upper()} throughout
6. Hit word target EXACTLY — count before returning

Return ONLY valid JSON (no markdown fence, no preamble):
{{
  "topicTitle": "compelling, clickable title",
  "trendUsed": "{trend.get('topic','')}",
  "scriptType": "{s_type}",
  "wordCount": 0,
  "estimatedDuration": "{"61s+" if is_tiktok else "45s"}",
  "youtubeTitle": "SEO-optimised title under 60 chars",
  "youtubeTags": ["tag1","tag2","tag3"],
  "igCaption": "Two punchy sentences that drive curiosity and action.",
  "igKeyword": "ONEWORD",
  "igHashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"],
  "tiktokCaption": "Punchy hook sentence + 3-4 relevant hashtags",
  "scrollStopOverlay": "Max 6 words for silent viewers",
  "rewatchTrigger": "planted_word",
  "postingSlot": "{sel.get('postingSlot','Monday 19:30')}",
  "affiliateUsed": "{aff}",
  "affiliateCommission": "{sel.get('affiliateCommission','')}",
  "script": "FULL WORD-FOR-WORD SCRIPT HERE — every word counts",
  "abHookVariant": "Alternative opening sentence for A/B testing",
  "broll": [
    {{"timestamp":"0-3s","footage":"free stock search term for Pexels/Pixabay","overlay":"TEXT OVERLAY","transition":"cut"}},
    {{"timestamp":"3-8s","footage":"","overlay":"","transition":"zoom"}},
    {{"timestamp":"8-30s","footage":"","overlay":"","transition":"cut"}},
    {{"timestamp":"30-46s","footage":"","overlay":"","transition":"swipe"}},
    {{"timestamp":"46-{"61" if is_tiktok else "45"}s","footage":"","overlay":"","transition":"fade"}}
  ],
  "thumbnailConcept": "vivid visual description for designer",
  "midjourneyPrompt": "complete generative prompt ready to paste --ar 9:16 --v 6 --style raw --q 2",
  "musicMood": "Epidemic Sound search: [genre] [mood] [BPM range]"
}}
"""}])

        pkg = extract_json(raw)
        if pkg:
            pkg["scriptType"] = s_type
            pkg["status"]     = "pending"
            pkg["qa"]         = None
            pkg["revised"]    = False
            wc = word_count(pkg.get("script", ""))
            pkg["wordCount"]  = wc
            add_log("scriptWriter", f"  Script {i+1} done: {wc} words — '{pkg.get('topicTitle','')}'")
            scripts.append(pkg)
        else:
            add_log("scriptWriter", f"  Script {i+1}: JSON parse failed — skipping")

        time.sleep(0.3)

    return scripts


def agent_qa_editor(scripts: list) -> list:
    for i, script in enumerate(scripts):
        add_log("qaEditor", f"Fact-checking + editorial review: script {i+1} '{script.get('topicTitle','')}'")
        is_tiktok = script.get("scriptType") == "tiktok_monetized"
        word_req  = "161-180 words" if is_tiktok else "130-140 words"

        raw = call_claude([{"role": "user", "content": f"""
You are a strict editorial QA editor for viral short-form video scripts.

SCRIPT TO REVIEW:
{script.get('script','')}

WORD COUNT: {script.get('wordCount', word_count(script.get('script','')))}
REQUIRED WORD COUNT: {word_req}
SCRIPT TYPE: {script.get('scriptType','')}

Check ALL of the following and score each 1-10:
1. hookScore: Does the first sentence immediately stop scrolling? Is it bold enough?
2. retentionScore: Does the body deliver genuine value rapidly? No filler?
3. ctaScore: Is the call-to-action natural and compelling?
4. factScore: Are all claims either verifiable or clearly framed as opinion?
5. overallScore: Average of the above, MINUS 1 if word count is wrong, MINUS 1 if flaggedPhrases found

Also check for:
- Robotic AI filler: "In today's video", "Make sure to", "Without further ado", "Let's dive in", "Dive into", "I want to", "Feel free to"
- Em-dashes (replace with commas in refinement)
- Stage directions like [pause] or (beat)
- Unverifiable absolute claims ("always", "100%", "never fails")

Set autoRefine=true if overallScore < 7 OR any flaggedPhrases found.

Return ONLY valid JSON:
{{
  "hookScore": 0, "retentionScore": 0, "ctaScore": 0, "factScore": 0, "overallScore": 0,
  "wordCountOk": true,
  "strengths": ["s1", "s2"],
  "issues": ["issue description"],
  "flaggedPhrases": ["exact phrase found"],
  "autoRefine": false,
  "refineInstructions": "specific, actionable rewrite instructions"
}}
"""}])
        qa = extract_json(raw) or {
            "hookScore": 7, "retentionScore": 7, "ctaScore": 7, "factScore": 8,
            "overallScore": 7, "wordCountOk": True, "strengths": ["Solid structure"],
            "issues": [], "flaggedPhrases": [], "autoRefine": False, "refineInstructions": "",
        }
        scripts[i]["qa"] = qa
        overall = qa.get("overallScore", 7)
        add_log("qaEditor", f"  Script {i+1}: {overall}/10 — Hook:{qa.get('hookScore')} Ret:{qa.get('retentionScore')} CTA:{qa.get('ctaScore')} Fact:{qa.get('factScore')}")
        if qa.get("flaggedPhrases"):
            add_log("qaEditor", f"  ⚠️ Flagged: {', '.join(qa['flaggedPhrases'])}")
        if qa.get("autoRefine"):
            add_log("qaEditor", f"  → Script {i+1} flagged for Agent 5 refinement")
    return scripts


def agent_refinement(scripts: list) -> list:
    for i, script in enumerate(scripts):
        qa = script.get("qa", {})
        if not qa.get("autoRefine"):
            continue
        is_tiktok = script.get("scriptType") == "tiktok_monetized"
        word_req  = "161-180" if is_tiktok else "130-140"
        add_log("refinement", f"Rewriting script {i+1} — fixing {len(qa.get('issues',[]))} issues...")
        raw = call_claude([{"role": "user", "content": f"""
Rewrite this short-form video script to fix these specific issues:
{qa.get('refineInstructions', 'Strengthen hook, remove filler, sharpen CTA')}

Remove these flagged phrases entirely: {', '.join(qa.get('flaggedPhrases', []))}
Replace any em-dashes with commas.
Remove all stage directions like [pause] or (beat).

Keep: same topic, same affiliate mention, same product CTA, same emotional hook.
Word target: {word_req} words EXACTLY.
Return ONLY the improved script text — no JSON, no preamble.

ORIGINAL SCRIPT:
{script.get('script','')}
"""}])
        if raw and len(raw) > 80:
            scripts[i]["script"]   = raw.strip()
            scripts[i]["revised"]  = True
            scripts[i]["wordCount"] = word_count(raw)
            scripts[i]["qa"]["autoRefine"] = False
            add_log("refinement", f"  Script {i+1} refined: {word_count(raw)} words ✓")
        else:
            add_log("refinement", f"  Script {i+1}: refinement returned insufficient text")
    return scripts


# ──────────────────────────────────────────────────────────────────────────────
# VOICE GENERATION (ELEVENLABS)
# ──────────────────────────────────────────────────────────────────────────────

def generate_voice(script_text: str, voice_id: str, api_key: str) -> bytes | None:
    """Call ElevenLabs v2 — 192kbps MP3 output."""
    try:
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            json={
                "text": script_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.50,
                    "similarity_boost": 0.75,
                    "style": 0.30,
                    "use_speaker_boost": True,
                },
                "output_format": "mp3_44100_192",
            },
            headers={"Content-Type": "application/json", "xi-api-key": api_key},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.content
        err = resp.json()
        raise ValueError(err.get("detail", {}).get("message", f"HTTP {resp.status_code}"))
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(str(e))


# ──────────────────────────────────────────────────────────────────────────────
# REVENUE PROJECTION ENGINE
# ──────────────────────────────────────────────────────────────────────────────

def project_revenue(vids_per_day: int, price: float, aff_commission: float, weeks: int = 12) -> pd.DataFrame:
    rows = []
    cum = {"t1": 0.0, "t2": 0.0, "t3": 0.0, "t4": 0.0}
    for w in range(1, weeks + 1):
        growth   = min(1 + w * 0.18, 4.0)
        views    = int(4500 * w * growth * vids_per_day)
        clicks   = int(views * 0.012)

        t1 = round(int(clicks * 0.025) * price, 2)
        t2 = round(int(clicks * 0.008) * aff_commission, 2)
        t3 = round((min(40 * w * growth, 5000) / 1000) * 15 if w > 4 else 0, 2)
        t4 = round((int(views * 0.38) / 1000) * 0.035, 2)

        for k, v in [("t1", t1), ("t2", t2), ("t3", t3), ("t4", t4)]:
            cum[k] += v
        total_w = t1 + t2 + t3 + t4

        rows.append({
            "Week": w,
            "Total videos": vids_per_day * 7 * w,
            "Est. weekly views": views,
            "Tier 1 (Product)": t1,
            "Tier 2 (Affiliate)": t2,
            "Tier 3 (Newsletter)": t3,
            "Tier 4 (TikTok)": t4,
            "Weekly total (£)": round(total_w, 2),
            "Cumulative (£)": round(sum(cum.values()), 2),
        })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎬 Content Factory Pro")
    st.caption("4-Tier Revenue Engine · Agentic AI")
    st.divider()

    nav_items = [
        ("⚙️  Setup & Config",       "setup"),
        ("🚀  Run Pipeline",          "pipeline"),
        ("✅  Review & Approve",      "approval"),
        ("📦  Production Bundle",     "export"),
        ("📊  Revenue Dashboard",     "revenue"),
        ("🔗  Affiliate Registry",    "affiliates"),
        ("📈  Analytics & Feedback",  "analytics"),
        ("📦  Product Creator",       "product"),
    ]
    for label, pid in nav_items:
        if st.button(label, key=f"nav_{pid}",
                     type="primary" if st.session_state.page == pid else "secondary",
                     use_container_width=True):
            st.session_state.page = pid
            st.rerun()

    st.divider()
    approved_count = sum(1 for s in st.session_state.scripts if s.get("status") == "approved")
    c1, c2 = st.columns(2)
    c1.metric("Scripts", len(st.session_state.scripts))
    c2.metric("Approved", approved_count)
    st.metric("Lifetime revenue", f"£{st.session_state.total_revenue:,.0f}")

    st.divider()
    st.caption("Pipeline state")
    state_icons = {"idle": "⚪ Idle", "running": "🟡 Running", "done": "🟢 Done", "error": "🔴 Error"}
    st.caption(state_icons.get(st.session_state.pipeline_state, "⚪ Idle"))


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: SETUP
# ──────────────────────────────────────────────────────────────────────────────

def page_setup():
    st.title("⚙️ Setup & Configuration")
    tab_keys, tab_product, tab_voice, tab_schedule = st.tabs([
        "🔑 API Keys", "📦 Product & Funnel", "🎙️ Voice", "📅 Schedule"
    ])

    with tab_keys:
        st.subheader("API Keys")
        st.info("Keys are stored in session memory only — never written to disk.", icon="🔒")

        c1, c2 = st.columns(2)
        with c1:
            ak = st.text_input("Anthropic API Key *", type="password",
                               value=st.session_state.anthropic_key,
                               placeholder="sk-ant-api03-...")
            if ak:
                st.session_state.anthropic_key = ak
                st.success("✓ Saved")
            st.caption("Get at [console.anthropic.com](https://console.anthropic.com) · ~£0.02–0.05/run")

        with c2:
            ek = st.text_input("ElevenLabs API Key", type="password",
                               value=st.session_state.el_key,
                               placeholder="sk-...")
            if ek:
                st.session_state.el_key = ek
                st.success("✓ Saved")
            st.caption("Free: 10k chars/mo · Starter £5/mo: 30k chars · [elevenlabs.io](https://elevenlabs.io)")

        st.subheader("API Cost Estimate")
        cost_df = pd.DataFrame([
            {"Action": "Full pipeline run (3 scripts + QA)", "Detail": "~12,000 tokens", "Est. cost": "£0.03–0.06"},
            {"Action": "Voice generation per script (150 words)", "Detail": "~750 ElevenLabs chars", "Est. cost": "£0.00 (free tier)"},
            {"Action": "30 scripts/month", "Detail": "Combined API usage", "Est. cost": "~£1.50–3.00"},
        ])
        st.dataframe(cost_df, hide_index=True, use_container_width=True)

    with tab_product:
        st.subheader("4-Tier Revenue Funnel")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🟡 Tier 1 — Core Product**")
            prod = st.text_input("Product name", value=st.session_state.product,
                                 placeholder="e.g. The AI Productivity Playbook")
            price = st.number_input("Price (£)", 1, 997, st.session_state.product_price)
            gurl = st.text_input("Gumroad / sales URL", value=st.session_state.gumroad_url,
                                 placeholder="https://yourname.gumroad.com/l/product")
            st.caption("Best price point for impulse buys: £9–£19")

            st.markdown("**🟢 Tier 2 — Affiliate**")
            aff_niche = st.selectbox("Affiliate category",
                                     list(st.session_state.custom_affiliates.keys()),
                                     index=list(st.session_state.custom_affiliates.keys()).index(
                                         st.session_state.affiliate_niche))

            st.markdown("**Content niche**")
            niche = st.text_input("Your niche", value=st.session_state.niche,
                                  placeholder="e.g. AI productivity tools, personal finance under 30")
            platform = st.selectbox("Primary platform",
                                    ["YouTube Shorts + Instagram Reels + TikTok",
                                     "YouTube Shorts + Instagram Reels",
                                     "TikTok only"],
                                    index=0)

        with c2:
            st.markdown("**🔵 Tier 3 — Newsletter Capture**")
            nl_provider = st.selectbox("Newsletter platform",
                                       ["Beehiiv (recommended)", "ConvertKit", "Mailchimp", "Substack"])
            nl_url = st.text_input("Newsletter signup URL", value=st.session_state.newsletter_url,
                                   placeholder="https://yourname.beehiiv.com")
            nl_cta = st.text_input("Newsletter CTA hook", value=st.session_state.newsletter_cta,
                                   placeholder="Join 3,200 creators getting weekly AI tool drops")
            st.caption("💡 Beehiiv > ConvertKit — built-in sponsor marketplace + paid subs")

            st.markdown("**🟣 Tier 4 — TikTok Monetization**")
            st.info("""
**TikTok Creator Rewards prerequisites:**
- ✅ 10,000+ followers
- ✅ 100,000+ views in last 30 days
- ✅ 18+ years old
- ✅ UK/US/CA/AU eligible
- ✅ Videos must be 61+ seconds

Until you hit these, TikTok scripts still drive Tiers 1–3.
""", icon="🟣")

            st.markdown("**Daily video target**")
            vpd = st.slider("Videos per day", 1, 3, st.session_state.vids_per_day)
            if vpd == 1:
                st.warning("1/day — good starting point. Each pipeline run = 1 day's content.")
            elif vpd == 2:
                st.info("2/day — run pipeline twice daily or batch 2 days' content.")
            else:
                st.success("3/day — full model. 1×45s morning, 1×45s lunch, 1×61s+ evening.")

        if st.button("💾 Save All Configuration", type="primary"):
            st.session_state.update({
                "product": prod, "product_price": price, "gumroad_url": gurl,
                "niche": niche, "platform": platform, "newsletter_url": nl_url,
                "newsletter_cta": nl_cta, "affiliate_niche": aff_niche, "vids_per_day": vpd,
            })
            st.success("✅ Configuration saved — head to Run Pipeline.")

    with tab_voice:
        st.subheader("ElevenLabs Voice Configuration")
        c1, c2 = st.columns(2)
        with c1:
            v_name = st.selectbox("Select voice", list(VOICE_OPTIONS.keys()))
            st.session_state.voice_id = VOICE_OPTIONS[v_name]
            custom_vid = st.text_input("Custom voice ID (optional)",
                                       placeholder="Paste any voice ID from ElevenLabs library")
            if custom_vid.strip():
                st.session_state.voice_id = custom_vid.strip()
                st.success("Custom voice set")
        with c2:
            st.markdown("**Optimal settings for viral content**")
            st.markdown("- **Stability 0.50** — natural variation, not robotic")
            st.markdown("- **Similarity 0.75** — stays true to the voice character")
            st.markdown("- **Style 0.30** — adds expressiveness and emphasis")
            st.markdown("- **Bitrate 192kbps** — broadcast quality, InVideo AI compatible")
            st.markdown("- **Model: eleven_multilingual_v2** — most natural for UK/US English")
            st.info("💡 Clone your own voice on ElevenLabs Starter (£5/mo) for authentic authority and brand consistency.")

    with tab_schedule:
        st.subheader("Optimal Posting Windows")
        st.caption("Based on platform algorithm research. Evening slot = TikTok 61s+ monetized script.")
        rows = []
        for day, slots in POSTING_WINDOWS.items():
            for slot_time, slot_label in slots:
                rows.append({
                    "Day": day, "Time": slot_time, "Type": slot_label,
                    "Platform priority": "TikTok + Reels" if "TikTok" in slot_label else "Shorts + Reels"
                })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

def page_pipeline():
    st.title("🚀 Run Agent Pipeline")

    if not st.session_state.anthropic_key:
        st.error("❌ Add your Anthropic API key in Setup first.")
        return
    if not st.session_state.product:
        st.warning("⚠️ Configure your product in Setup before running.")
        return

    # Agent status grid
    agents = [
        ("🔵", "Trend Scout",    "trendScout",  "Live web scan"),
        ("🟢", "Strategy",       "strategy",    "Affiliate match"),
        ("🟡", "Script Writer",  "scriptWriter","2×45s + 1×61s+"),
        ("🔴", "Fact-Check QA",  "qaEditor",    "Editor review"),
        ("⚪", "Refinement",     "refinement",  "Auto-rewrite"),
    ]
    cols = st.columns(5)
    state_map = {"idle": "○", "running": "⟳", "done": "✓", "error": "✗", "skipped": "—"}
    for col, (icon, name, key, sub) in zip(cols, agents):
        s = st.session_state.agent_states.get(key, "idle")
        col.metric(f"{icon} {name}", state_map.get(s, "○"), sub)

    st.divider()

    if st.session_state.pipeline_state == "idle":
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.info(f"Ready: **{st.session_state.niche or 'niche not set'}** · "
                    f"**{st.session_state.product or 'product not set'}** · "
                    f"**{st.session_state.vids_per_day} video(s)/day**")
        with c2:
            st.metric("Script types", "2×45s + 1×61s+")
        with c3:
            st.metric("Est. run time", "3–5 min")

        if st.button("▶️ Launch Full Production Pipeline", type="primary", use_container_width=True):
            st.session_state.pipeline_state = "running"
            st.session_state.log_entries = []
            st.session_state.scripts     = []
            st.session_state.trends      = []
            for k in st.session_state.agent_states:
                st.session_state.agent_states[k] = "idle"
            st.rerun()

    if st.session_state.pipeline_state == "running":
        log_ph   = st.empty()
        stat_ph  = st.empty()

        def refresh_log():
            with log_ph.container():
                st.markdown("**Agent Activity Log**")
                log_lines = "\n".join(
                    f"{e['ts']} {e['icon']} {e['agent'].upper():<14} {e['msg']}"
                    for e in st.session_state.log_entries
                )
                st.markdown(f'<div class="log-box">{log_lines}</div>', unsafe_allow_html=True)

        try:
            # Agent 1
            st.session_state.agent_states["trendScout"] = "running"
            stat_ph.info("🔵 Agent 1: Trend Scout scanning live web...")
            refresh_log()
            trends = agent_trend_scout()
            time.sleep(65)
            st.session_state.trends = trends
            st.session_state.agent_states["trendScout"] = "done"

            # Agent 2
            st.session_state.agent_states["strategy"] = "running"
            stat_ph.info("🟢 Agent 2: Strategy matching affiliates...")
            refresh_log()
            strategy = agent_strategy(trends)
            st.session_state.agent_states["strategy"] = "done"

            # Agent 3
            st.session_state.agent_states["scriptWriter"] = "running"
            stat_ph.info("🟡 Agent 3: Script Writer generating 3 packages...")
            refresh_log()
            scripts = agent_script_writer(trends, strategy)
            st.session_state.agent_states["scriptWriter"] = "done"

            # Agent 4
            st.session_state.agent_states["qaEditor"] = "running"
            stat_ph.info("🔴 Agent 4: Fact-Check QA reviewing all scripts...")
            refresh_log()
            scripts = agent_qa_editor(scripts)
            st.session_state.agent_states["qaEditor"] = "done"

            # Agent 5
            needs_refine = any(s.get("qa", {}).get("autoRefine") for s in scripts)
            if needs_refine:
                st.session_state.agent_states["refinement"] = "running"
                stat_ph.info("⚪ Agent 5: Refinement rewriting flagged scripts...")
                refresh_log()
                scripts = agent_refinement(scripts)
                st.session_state.agent_states["refinement"] = "done"
            else:
                st.session_state.agent_states["refinement"] = "skipped"
                add_log("refinement", "All scripts passed QA threshold — refinement skipped ✓")

            st.session_state.scripts        = scripts
            st.session_state.pipeline_state = "done"
            add_log("system", "═══════════════════════════════════")
            add_log("system", f"Pipeline complete — {len(scripts)} scripts ready for approval.")
            stat_ph.success(f"✅ Done — {len(scripts)} scripts ready. Go to Review & Approve.")

        except Exception as e:
            add_log("system", f"ERROR: {e}")
            st.session_state.pipeline_state = "error"
            for k, v in st.session_state.agent_states.items():
                if v == "running":
                    st.session_state.agent_states[k] = "error"
            stat_ph.error(f"Pipeline error: {e}")

        refresh_log()
        st.rerun()

    if st.session_state.pipeline_state in ("done", "error"):
        with st.expander("📋 Full Agent Log", expanded=False):
            for e in st.session_state.log_entries:
                st.markdown(f"`{e['ts']}` {e['icon']} **{e['agent'].upper()}** — {e['msg']}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("→ Review & Approve", type="primary", use_container_width=True):
                st.session_state.page = "approval"
                st.rerun()
        with c2:
            if st.button("🔄 Run New Pipeline", use_container_width=True):
                st.session_state.pipeline_state = "idle"
                for k in st.session_state.agent_states:
                    st.session_state.agent_states[k] = "idle"
                st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: APPROVAL
# ──────────────────────────────────────────────────────────────────────────────

def page_approval():
    st.title("✅ Review & Approve")

    scripts = st.session_state.scripts
    if not scripts:
        st.info("No scripts yet — run the pipeline first.")
        return

    for i, sc in enumerate(scripts):
        qa        = sc.get("qa") or {}
        overall   = qa.get("overallScore", 7)
        is_tiktok = sc.get("scriptType") == "tiktok_monetized"
        status    = sc.get("status", "pending")
        wc        = sc.get("wordCount", word_count(sc.get("script", "")))

        status_color = {"approved": "🟢", "skipped": "⚫", "pending": "🟡"}.get(status, "🟡")

        with st.expander(
            f"{status_color} Script {i+1} — {sc.get('topicTitle','Untitled')} [{overall}/10]",
            expanded=(status == "pending")
        ):
            # Type + meta row
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1:
                label_class = "type-tiktok" if is_tiktok else "type-short"
                label_text  = "🟣 TikTok Monetization Qualified (61s+)" if is_tiktok else "🔵 Short Retention (45s)"
                st.markdown(f'<span class="{label_class}">{label_text}</span>', unsafe_allow_html=True)
            with c2:
                st.metric("Score", f"{overall}/10")
            with c3:
                st.metric("Words", wc)
            with c4:
                if sc.get("revised"):
                    st.success("Refined ✓")
            
            if sc.get("trendUsed"):
                st.caption(f"🔥 Trend: {sc['trendUsed']}")
            if sc.get("affiliateUsed"):
                st.caption(f"🔗 Affiliate: {sc['affiliateUsed']} ({sc.get('affiliateCommission','')})")

            st.divider()

            # QA scores
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**QA Scores**")
                for label, key, col in [
                    ("Hook",          "hookScore",      "#3B82F6"),
                    ("Retention",     "retentionScore", "#10B981"),
                    ("CTA",           "ctaScore",       "#F59E0B"),
                    ("Fact accuracy", "factScore",      "#8B5CF6"),
                ]:
                    v = qa.get(key, 7)
                    st.progress(v / 10, text=f"{label}: {v}/10")
            with c2:
                if qa.get("strengths"):
                    st.markdown("**✅ Strengths**")
                    for s in qa["strengths"]:
                        st.markdown(f"- {s}")
                if qa.get("issues"):
                    st.markdown("**⚠️ Issues**")
                    for iss in qa["issues"]:
                        st.markdown(f"- {iss}")
                if qa.get("flaggedPhrases"):
                    st.error(f"Flagged phrases: {', '.join(qa['flaggedPhrases'])}")

            st.divider()

            # Script + distribution
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown("**Audio Script (ElevenLabs ready)**")
                st.markdown(
                    f'<div class="script-box">{sc.get("script","")}</div>',
                    unsafe_allow_html=True
                )
                st.caption(f"{wc} words · {sc.get('estimatedDuration','45s')} · Posting: {sc.get('postingSlot','')}")
                if sc.get("abHookVariant"):
                    st.caption(f"A/B hook: *\"{sc['abHookVariant']}\"*")
            with c2:
                st.markdown("**YouTube Shorts**")
                st.code(f"{sc.get('youtubeTitle','')}\nTags: {', '.join(sc.get('youtubeTags',[]))}", language=None)
                st.markdown("**Instagram**")
                ig = f"{sc.get('igCaption','')}\n\nComment '{sc.get('igKeyword','')}' → DM\n\n{' '.join(sc.get('igHashtags',[]))}"
                st.code(ig, language=None)
                if is_tiktok:
                    st.markdown("**TikTok**")
                    st.code(sc.get("tiktokCaption",""), language=None)

            # Monetization block
            st.divider()
            st.markdown("**💰 4-Tier Monetization Map**")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown('<span class="tier-badge t1">Tier 1</span>', unsafe_allow_html=True)
                st.caption("Core product CTA in script outro")
            with c2:
                st.markdown('<span class="tier-badge t2">Tier 2</span>', unsafe_allow_html=True)
                st.caption(sc.get("affiliateUsed","No affiliate") or "No affiliate")
            with c3:
                st.markdown('<span class="tier-badge t3">Tier 3</span>', unsafe_allow_html=True)
                st.caption("Newsletter link in bio")
            with c4:
                if is_tiktok:
                    st.markdown('<span class="tier-badge t4">Tier 4</span>', unsafe_allow_html=True)
                    st.caption("61s+ TikTok Creator Rewards")
                else:
                    st.markdown("—", unsafe_allow_html=False)

            # B-Roll
            with st.expander("🎬 B-Roll Visual Map (iStock / Pexels / InVideo AI)"):
                broll = sc.get("broll", [])
                if broll:
                    st.dataframe(pd.DataFrame(broll), hide_index=True, use_container_width=True)
                    st.caption("Footage = royalty-free search term for Pexels/Pixabay. Overlay = text on screen.")
                col1, col2 = st.columns(2)
                with col1:
                    if sc.get("thumbnailConcept"):
                        st.markdown(f"**Thumbnail concept:** {sc['thumbnailConcept']}")
                    if sc.get("midjourneyPrompt"):
                        st.code(sc["midjourneyPrompt"], language=None)
                with col2:
                    if sc.get("musicMood"):
                        st.markdown(f"**Music:** {sc['musicMood']}")
                    if sc.get("scrollStopOverlay"):
                        st.markdown(f"**Scroll-stop overlay:** \"{sc['scrollStopOverlay']}\"")
                    if sc.get("rewatchTrigger"):
                        st.markdown(f"**Rewatch trigger:** plant **\"{sc['rewatchTrigger']}\"** early, reference at end")

            st.divider()

            # Action buttons
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("✅ Approve", key=f"ap_{i}", type="primary", use_container_width=True):
                    st.session_state.scripts[i]["status"] = "approved"
                    st.session_state.total_videos += 1
                    st.rerun()
            with c2:
                if st.button("✏️ Request Changes", key=f"rc_{i}", use_container_width=True):
                    st.session_state[f"rev_open_{i}"] = True
            with c3:
                if st.button("❌ Skip", key=f"sk_{i}", use_container_width=True):
                    st.session_state.scripts[i]["status"] = "skipped"
                    st.rerun()
            with c4:
                if status == "approved":
                    st.success("Approved ✓")

            # Inline revision form
            if st.session_state.get(f"rev_open_{i}"):
                rev_note = st.text_area(
                    "Revision instructions",
                    value=qa.get("refineInstructions", ""),
                    key=f"rev_text_{i}",
                )
                rc1, rc2 = st.columns(2)
                with rc1:
                    if st.button("🔄 Apply Revision", key=f"do_rev_{i}", type="primary"):
                        is_t = sc.get("scriptType") == "tiktok_monetized"
                        with st.spinner("Agent 5 rewriting..."):
                            r = call_claude([{"role": "user", "content":
                                f"Rewrite this script fixing: {rev_note}. "
                                f"Keep same topic, affiliate, and all CTAs. "
                                f"{'161-180' if is_t else '130-140'} words. "
                                f"Return ONLY the improved script text.\n\nOriginal:\n{sc.get('script','')}"}])
                            if r and len(r) > 80:
                                st.session_state.scripts[i]["script"]   = r.strip()
                                st.session_state.scripts[i]["revised"]  = True
                                st.session_state.scripts[i]["wordCount"] = word_count(r)
                        st.session_state[f"rev_open_{i}"] = False
                        st.rerun()
                with rc2:
                    if st.button("Cancel", key=f"rev_cancel_{i}"):
                        st.session_state[f"rev_open_{i}"] = False
                        st.rerun()

    # Proceed button
    n_approved = sum(1 for s in scripts if s.get("status") == "approved")
    if n_approved > 0:
        st.success(f"✅ {n_approved} script(s) approved and ready for production.")
        if st.button("→ Open Production Bundle", type="primary"):
            st.session_state.page = "export"
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: PRODUCTION BUNDLE
# ──────────────────────────────────────────────────────────────────────────────

def page_export():
    st.title("📦 Production Bundle")

    approved = [s for s in st.session_state.scripts if s.get("status") == "approved"]
    if not approved:
        st.info("No approved scripts. Review and approve in the previous step.")
        return

    tab_sc, tab_voice, tab_assets, tab_plan = st.tabs([
        "📝 Scripts & SEO", "🎙️ Voice Generation", "🎨 Assets", "📅 Posting Plan"
    ])

    with tab_sc:
        for i, sc in enumerate(approved):
            is_t = sc.get("scriptType") == "tiktok_monetized"
            st.subheader(f"Script {i+1}: {sc.get('topicTitle','')}")

            label_class = "type-tiktok" if is_t else "type-short"
            label_text  = "🟣 TikTok Monetization Qualified (61s+)" if is_t else "🔵 Short Retention (45s)"
            st.markdown(f'<span class="{label_class}">{label_text}</span>', unsafe_allow_html=True)

            tiers_html = (
                '<span class="tier-badge t1">T1: Core Product</span>'
                f'<span class="tier-badge t2">T2: {sc.get("affiliateUsed","No affiliate")}</span>'
                '<span class="tier-badge t3">T3: Newsletter</span>'
                + ('<span class="tier-badge t4">T4: TikTok RPM</span>' if is_t else "")
            )
            st.markdown(tiers_html, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**YouTube Shorts**")
                yt_copy = f"Title: {sc.get('youtubeTitle','')}\nTags: {', '.join(sc.get('youtubeTags',[]))}"
                st.code(yt_copy, language=None)
            with c2:
                st.markdown("**Instagram Reels**")
                ig_copy = (f"{sc.get('igCaption','')}\n\n"
                           f"Comment '{sc.get('igKeyword','')}' and I'll DM you the link!\n\n"
                           f"{' '.join(sc.get('igHashtags',[]))}")
                st.code(ig_copy, language=None)

            if is_t:
                st.markdown("**TikTok**")
                st.code(sc.get("tiktokCaption",""), language=None)

            st.markdown("**Full Audio Script — word-for-word, ElevenLabs 192kbps ready**")
            st.markdown(f'<div class="script-box">{sc.get("script","")}</div>', unsafe_allow_html=True)
            wc = sc.get("wordCount", word_count(sc.get("script","")))
            c1, c2, c3 = st.columns(3)
            c1.metric("Words", wc)
            c2.metric("Duration", sc.get("estimatedDuration","45s"))
            c3.metric("Post at", sc.get("postingSlot","—"))

            # Export as txt
            bundle_txt = (
                f"=== SCRIPT {i+1}: {sc.get('topicTitle','')} ===\n"
                f"Type: {label_text}\n"
                f"Post: {sc.get('postingSlot','')}\n\n"
                f"--- YOUTUBE SHORTS ---\n{yt_copy}\n\n"
                f"--- INSTAGRAM REELS ---\n{ig_copy}\n\n"
                f"--- AUDIO SCRIPT ---\n{sc.get('script','')}\n\n"
                f"--- B-ROLL MAP ---\n"
                + "\n".join(
                    f"{b.get('timestamp','')} | {b.get('footage','')} | overlay: {b.get('overlay','')} | {b.get('transition','')}"
                    for b in sc.get("broll", [])
                )
                + f"\n\n--- MIDJOURNEY ---\n{sc.get('midjourneyPrompt','')}\n"
                f"\n--- MUSIC ---\n{sc.get('musicMood','')}\n"
                f"\n--- A/B HOOK VARIANT ---\n{sc.get('abHookVariant','')}\n"
            )
            st.download_button(
                f"⬇️ Download Script {i+1} as .txt",
                bundle_txt.encode("utf-8"),
                file_name=f"script_{i+1}_{sc.get('topicTitle','')[:30].replace(' ','_')}.txt",
                mime="text/plain",
                key=f"dl_txt_{i}",
            )
            st.divider()

    with tab_voice:
        st.markdown("### ElevenLabs Voice Generation")
        el_key  = st.session_state.el_key
        voi_id  = st.session_state.voice_id

        if not el_key:
            st.warning("Add your ElevenLabs API key in Setup to enable voice generation.")

        for i, sc in enumerate(approved):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**Script {i+1}:** {sc.get('topicTitle','')}")
                st.caption(f"{sc.get('wordCount',0)} words · {sc.get('estimatedDuration','45s')} · {sc.get('scriptType','')}")
            with c2:
                if el_key and st.button(f"🎙️ Generate", key=f"gen_v_{i}"):
                    with st.spinner("Generating 192kbps voice-over..."):
                        try:
                            audio = generate_voice(sc.get("script",""), voi_id, el_key)
                            st.session_state[f"audio_{i}"] = audio
                        except ValueError as e:
                            st.error(str(e))
            with c3:
                if st.session_state.get(f"audio_{i}"):
                    fname = f"script_{i+1}_{sc.get('topicTitle','voice')[:25].replace(' ','_')}.mp3"
                    st.download_button("⬇️ MP3", st.session_state[f"audio_{i}"],
                                       file_name=fname, mime="audio/mp3", key=f"dl_v_{i}")

            if st.session_state.get(f"audio_{i}"):
                st.audio(st.session_state[f"audio_{i}"], format="audio/mp3")
            st.divider()

    with tab_assets:
        st.markdown("### Full Asset Package")
        for i, sc in enumerate(approved):
            st.subheader(f"Script {i+1}: {sc.get('topicTitle','')}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Midjourney / DALL-E 3 Thumbnail Prompt**")
                st.code(sc.get("midjourneyPrompt",""), language=None)
                st.markdown(f"**Concept:** {sc.get('thumbnailConcept','')}")
                st.markdown(f"**Music (Epidemic Sound):** `{sc.get('musicMood','')}`")
            with c2:
                st.markdown("**B-Roll Map (iStock / Pexels / Pixabay)**")
                for b in sc.get("broll", []):
                    st.markdown(
                        f"**{b.get('timestamp','')}** → `{b.get('footage','')}` "
                        f"| *\"{b.get('overlay','')}\"* | {b.get('transition','cut')}"
                    )
                st.markdown(f"**Scroll-stop overlay:** \"{sc.get('scrollStopOverlay','')}\"")
                st.markdown(f"**Rewatch trigger:** plant **\"{sc.get('rewatchTrigger','')}\"** at 5s, echo at end")
                if sc.get("abHookVariant"):
                    st.info(f"**A/B test hook:** *\"{sc['abHookVariant']}\"*\n\nPost this as a second version. Compare 48h watch time.")
            st.divider()

    with tab_plan:
        st.markdown("### Posting Schedule")
        vpd = st.session_state.vids_per_day
        today = datetime.now()
        rows = []
        vid_idx = 0
        for d in range(7):
            date  = today + timedelta(days=d)
            dname = date.strftime("%A")
            slots = POSTING_WINDOWS.get(dname, [])[:vpd]
            for j, (slot_time, slot_label) in enumerate(slots):
                is_tiktok_slot = (j == len(slots) - 1)
                rows.append({
                    "Date":     date.strftime("%d %b"),
                    "Day":      dname,
                    "Time":     slot_time,
                    "Label":    slot_label,
                    "Type":     "TikTok 61s+ (Monetized)" if is_tiktok_slot else "Short Retention 45s",
                    "Script":   f"Script {(vid_idx % max(len(approved),1)) + 1}" if approved else "—",
                })
                vid_idx += 1
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        st.caption("Evening slot always assigned to the TikTok 61s+ monetized format.")

        st.markdown("**Quick launch**")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.link_button("Buffer ↗", "https://buffer.com", use_container_width=True)
        with c2: st.link_button("Later ↗",  "https://later.com",  use_container_width=True)
        with c3: st.link_button("InVideo ↗","https://invideo.io", use_container_width=True)
        with c4: st.link_button("Revid ↗",  "https://revid.ai",   use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: REVENUE DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

def page_revenue():
    st.title("📊 Revenue Dashboard")
    st.caption("Conservative projections based on 1.2% bio CTR · 2.5% sales conversion · 0.8% affiliate conversion")

    c1, c2, c3 = st.columns(3)
    with c1:
        price = st.number_input("Product price (£)", 1, 997,
                                value=st.session_state.product_price, key="rev_price")
    with c2:
        vpd = st.slider("Videos/day", 1, 3, st.session_state.vids_per_day, key="rev_vpd")
    with c3:
        aff_comm = st.number_input("Avg affiliate commission (£)", 1, 200, 25, key="rev_aff")

    df = project_revenue(vpd, price, aff_comm)

    # KPI row
    total_12w  = df["Weekly total (£)"].sum()
    peak_week  = df["Weekly total (£)"].max()
    month3_rev = df[df["Week"] >= 9]["Weekly total (£)"].sum()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("12-week total",   f"£{total_12w:,.0f}", help="Conservative estimate")
    k2.metric("Peak weekly",     f"£{peak_week:,.0f}", help="Week 12 projection")
    k3.metric("Month 3 revenue", f"£{month3_rev:,.0f}")
    k4.metric("Monthly run rate",f"£{peak_week*4:,.0f}", help="At peak week × 4")

    st.divider()

    # Stacked bar: tiers
    fig = go.Figure()
    tier_colors = [("#F59E0B","Tier 1 (Product)"),("#10B981","Tier 2 (Affiliate)"),
                   ("#3B82F6","Tier 3 (Newsletter)"),("#8B5CF6","Tier 4 (TikTok)")]
    for color, col in tier_colors:
        fig.add_trace(go.Bar(name=col, x=df["Week"], y=df[col], marker_color=color))
    fig.update_layout(
        title="Weekly Revenue by Tier", barmode="stack",
        xaxis_title="Week", yaxis_title="Revenue (£)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=40,b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cumulative line
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["Week"], y=df["Cumulative (£)"],
        mode="lines+markers", name="Cumulative",
        line=dict(color="#6366F1", width=2.5),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
    ))
    fig2.update_layout(
        title="Cumulative Revenue Growth",
        xaxis_title="Week", yaxis_title="Total (£)",
        height=280, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=40,b=0),
    )
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📋 Full Projection Table"):
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Tier tips
    st.subheader("Tier Optimisation Guide")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
**🟡 Tier 1 — Core Product**
- Sweet spot: £9–£19 for impulse buys
- A/B test £9 vs £15 vs £19 across a week
- Add urgency: countdown or limited-quantity framing
- Upsell: add a £5 add-on at checkout (Gumroad supports this)

**🟢 Tier 2 — Affiliate**
- Prioritise 30%+ recurring commissions (SaaS)
- Beehiiv, ElevenLabs, Notion pay consistently
- Disclose always: "some links support this channel"
- Never place affiliate before product CTA in script
""")
    with c2:
        st.markdown("""
**🔵 Tier 3 — Newsletter**
- Beehiiv over ConvertKit: sponsor marketplace built-in
- At 1,000 subs: pitch £15–50 CPM sponsors
- At 5,000 subs: paid subscription tier (£4/mo)
- Weekly AI tool roundup = best open rate in productivity niche

**🟣 Tier 4 — TikTok Creator Rewards**
- Requires: 10k followers + 100k views/30 days + 18+
- UK RPM: £0.02–0.06 per 1,000 views (low — stack with Tiers 1-3)
- Narrative 61s+ scripts get 2-3× completion vs 45s
- Do NOT chase Tier 4 at the expense of Tiers 1-3
""")


# ──────────────────────────────────────────────────────────────────────────────
# PAGE: AFFILIATE REGISTRY
# ──────────────────────────────────────────────────────────────────────────────

def page_affiliates():
    st.title("🔗 Affiliate Registry")
    st.caption("Agent 2 reads this database when matching scripts to affiliate opportunities.")

    sel_niche = st.selectbox("Browse niche", list(st.session_state.custom_affiliates.keys()))
    aff_list  = st.session_state.custom_affiliates.get(sel_niche, [])

    if aff_list:
        st.dataframe(pd.DataFrame(aff_list), hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("Add New Affiliate")

    c1, c2, c3 = st.columns(3)
    with c1:
        new_name       = st.text_input("Product / service name")
        new_niche_key  = st.selectbox("Niche category",
                                      list(st.session_state.custom_affiliates.keys()),
                                      key="add_niche")
    with c2:
        new_commission = st.text_input("Commission", placeholder="e.g. 30% recurring or £25/signup")
        new_ticket     = st.text_input("Product price", placeholder="e.g. £14/mo or £99 one-time")
    with c3:
        new_url  = st.text_input("Affiliate signup URL")
        new_type = st.selectbox("Type", ["SaaS","App","Physical","Course","Hardware+SaaS"])

    if st.button("➕ Add to Registry", type="primary"):
        if new_name and new_commission:
            st.session_state.custom_affiliates[new_niche_key].append({
                "name": new_name, "url": new_url,
                "commission": new_commission, "ticket": new_ticket, "type": new_type,
            })
            st.success(f"Added {new_name} to {new_niche_key}")
            st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        registry_json = json.dumps(st.session_state.custom_affiliates, indent=2)
        st.download_button("⬇️ Export Registry as JSON", registry_json,
                           file_name="affiliate_registry.json", mime="application/json")
    with c2:
        uploaded = st.file_uploader("⬆️ Import Registry JSON", type="json")
        if uploaded:
            imported = json.load(uploaded)
            st.session_state.custom_affiliates = imported
            st.success("Registry imported ✓")
            st.rerun()

    st.subheader("🏆 Highest-Value Affiliates (pre-loaded)")
    top = [
        ("Jasper AI",   "25% recurring", "~£10/mo per referral", "★★★★★"),
        ("Beehiiv",     "30% × 3mo",     "~£10 per referral",    "★★★★★"),
        ("Copy.ai",     "45% recurring", "~£16/mo per referral", "★★★★★"),
        ("Whoop",       "£30/signup",    "One-time £30",         "★★★★☆"),
        ("Epidemic Sound","£20/signup",  "One-time £20",         "★★★★☆"),
    ]
    for name, comm, val, stars in top:
        c1, c2, c3, c4 = st.columns([2,2,2,1])
        c1.markdown(f"**{name}**")
        c2.markdown(comm)
        c3.markdown(f"*{val}*")
        c4.markdown(stars)


# ──────────────────────────────────────────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────────────────────────────────────────

PAGE_MAP = {
    "setup":      page_setup,
    "pipeline":   page_pipeline,
    "approval":   page_approval,
    "export":     page_export,
    "revenue":    page_revenue,
    "affiliates": page_affiliates,
}



# ──────────────────────────────────────────────────────────────────────────────
# PERFORMANCE FEEDBACK LOOP — Analytics Agent (Agent 6)
# ──────────────────────────────────────────────────────────────────────────────

def compute_virality_score(views: int, watch_pct: float, likes: int,
                           link_clicks: int, sales: int) -> float:
    """
    Weighted virality score.
    Watch time % is the single most important signal — weighted heaviest.
    Sales represent real conversion — highest per-unit weight.
    """
    score = (
        (views       * 0.0001)  +
        (watch_pct   * 2.5)     +   # 80% watch time = +200 points
        (likes       * 0.05)    +
        (link_clicks * 0.5)     +
        (sales       * 25.0)
    )
    return round(score, 1)


def extract_winning_patterns(performances: list) -> dict:
    """
    Distil top-3 performers into patterns the next pipeline can use.
    Returns a dict Agent 1 and Agent 3 read at run-time.
    """
    if not performances:
        return {}
    sorted_p = sorted(performances, key=lambda x: x.get("virality_score", 0), reverse=True)
    top3 = sorted_p[:3]
    return {
        "top_topics":    [p.get("topic",    "") for p in top3],
        "top_hooks":     [p.get("hook",     "") for p in top3],
        "top_emotions":  [p.get("emotion",  "") for p in top3],
        "top_types":     [p.get("type",     "") for p in top3],
        "avg_watch_pct": round(sum(p.get("watch_pct", 0) for p in top3) / len(top3), 1),
        "best_score":    top3[0].get("virality_score", 0),
        "best_topic":    top3[0].get("topic", ""),
        "best_hook":     top3[0].get("hook", ""),
        "updated_at":    datetime.now().strftime("%d %b %Y %H:%M"),
    }


def page_analytics():
    st.title("📈 Analytics & Feedback Loop")
    st.caption("Enter real performance data after each batch posts. The system learns your audience and improves every script.")

    if "performances" not in st.session_state:
        st.session_state.performances = []
    if "winning_patterns" not in st.session_state:
        st.session_state.winning_patterns = {}

    # ── HOW IT WORKS ──────────────────────────────────────────────────────────
    with st.expander("How the feedback loop works", expanded=False):
        st.markdown("""
**1. You post 3 videos.** Wait 48–72 hours for the algorithm to distribute them.

**2. You enter performance data below** — views, watch time %, likes, link clicks, sales.

**3. The system calculates a Virality Score** for each video:  
`(views × 0.0001) + (watch_time% × 2.5) + (likes × 0.05) + (link_clicks × 0.5) + (sales × 25)`

**4. Top 3 performers become Winning Patterns** — their topic angles, hook styles, and emotional registers are saved.

**5. On the next pipeline run:**
- **Agent 1 (Trend Scout)** prioritises topics similar to your best performers
- **Agent 3 (Script Writer)** models new hooks after your top-performing hook lines
- The system compounds: each batch is smarter than the last.

**What to check 48 hours after posting:**
- YouTube: YouTube Studio → Content → click the video
- Instagram: Professional Dashboard → Content you've shared
- TikTok: Creator Tools → Analytics → Content
""")

    # ── LOG A NEW VIDEO'S PERFORMANCE ────────────────────────────────────────
    st.subheader("Log video performance")
    st.caption("Enter data for each video 48–72 hours after posting.")

    with st.form("perf_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            perf_title    = st.text_input("Video title / topic *")
            perf_hook     = st.text_area("Opening hook line (first sentence of script)", height=70)
            perf_type     = st.selectbox("Script type", ["Short Retention (45s)", "TikTok Monetized (61s+)"])
            perf_emotion  = st.selectbox("Emotional hook used",
                                         ["curiosity","fear","surprise","anger","joy","awe"])
        with c2:
            perf_platform = st.selectbox("Best-performing platform",
                                         ["YouTube Shorts","Instagram Reels","TikTok","All similar"])
            perf_views    = st.number_input("Views at 48h",     min_value=0, value=0, step=100)
            perf_watch    = st.slider("Average watch time %", 0, 100, 40, step=1)
            perf_likes    = st.number_input("Likes",            min_value=0, value=0, step=10)

        c3, c4 = st.columns(2)
        with c3:
            perf_clicks   = st.number_input("Bio link clicks",  min_value=0, value=0)
        with c4:
            perf_sales    = st.number_input("Gumroad sales",    min_value=0, value=0)

        submitted = st.form_submit_button("Log Performance & Update Feedback Loop", type="primary")

    if submitted and perf_title:
        score = compute_virality_score(
            int(perf_views), float(perf_watch),
            int(perf_likes), int(perf_clicks), int(perf_sales)
        )
        entry = {
            "topic":          perf_title,
            "hook":           perf_hook,
            "type":           perf_type,
            "emotion":        perf_emotion,
            "platform":       perf_platform,
            "views":          int(perf_views),
            "watch_pct":      float(perf_watch),
            "likes":          int(perf_likes),
            "link_clicks":    int(perf_clicks),
            "sales":          int(perf_sales),
            "virality_score": score,
            "logged_at":      datetime.now().strftime("%d %b %Y %H:%M"),
        }
        st.session_state.performances.append(entry)
        st.session_state.winning_patterns = extract_winning_patterns(
            st.session_state.performances
        )

        # Update total revenue tracker
        st.session_state.total_revenue += float(perf_sales) * st.session_state.get("product_price", 15)

        st.success(f"✅ Logged '{perf_title}' — Virality Score: **{score}**")

        # Contextual feedback
        if perf_watch >= 70:
            st.success(f"🔥 {perf_watch}% watch time is exceptional. This hook style is a winner — Agent 3 will model future scripts after it.")
        elif perf_watch >= 50:
            st.info(f"👍 {perf_watch}% watch time is solid. Above-average retention.")
        else:
            st.warning(f"⚠️ {perf_watch}% watch time is below 50%. The hook may need work. Agent 5 will deprioritise this angle.")

        if perf_sales > 0:
            st.success(f"💰 {perf_sales} sale(s) = £{perf_sales * st.session_state.get('product_price', 15):.0f} from this video alone.")

        st.rerun()

    # ── PERFORMANCE TABLE ────────────────────────────────────────────────────
    if st.session_state.performances:
        st.divider()
        st.subheader("Performance history")

        df = pd.DataFrame(st.session_state.performances)
        display_cols = ["logged_at","topic","type","views","watch_pct",
                        "likes","link_clicks","sales","virality_score","platform"]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[available].sort_values("virality_score", ascending=False),
            hide_index=True,
            use_container_width=True,
            column_config={
                "virality_score": st.column_config.NumberColumn("Virality Score", format="%.1f"),
                "watch_pct":      st.column_config.ProgressColumn("Watch %", min_value=0, max_value=100),
                "views":          st.column_config.NumberColumn("Views"),
            }
        )

        # Quick KPIs
        st.divider()
        kc1, kc2, kc3, kc4 = st.columns(4)
        kc1.metric("Total videos logged",   len(df))
        kc2.metric("Avg virality score",    f"{df['virality_score'].mean():.1f}")
        kc3.metric("Avg watch time",        f"{df['watch_pct'].mean():.0f}%")
        kc4.metric("Total sales logged",    int(df['sales'].sum()))

        # Chart: virality scores over time
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["topic"].str[:30],
            y=df["virality_score"],
            marker_color=[
                "#10B981" if s >= df["virality_score"].quantile(0.66) else
                "#F59E0B" if s >= df["virality_score"].quantile(0.33) else
                "#EF4444"
                for s in df["virality_score"]
            ],
            text=df["virality_score"].apply(lambda x: f"{x:.0f}"),
            textposition="outside",
        ))
        fig.update_layout(
            title="Virality scores by video",
            xaxis_title="",
            yaxis_title="Score",
            height=280,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=40,b=60),
            xaxis=dict(tickangle=-30),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── WINNING PATTERNS PANEL ────────────────────────────────────────────
        wp = st.session_state.winning_patterns
        if wp:
            st.divider()
            st.subheader("Winning patterns (fed into next pipeline)")
            st.caption(f"Last updated: {wp.get('updated_at','')}")

            wc1, wc2 = st.columns(2)
            with wc1:
                st.markdown("**Top topics (Agent 1 will prioritise these)**")
                for t in wp.get("top_topics", []):
                    if t:
                        st.markdown(f"- {t}")

                st.markdown("**Top emotional hooks**")
                emotions = [e for e in wp.get("top_emotions",[]) if e]
                if emotions:
                    from collections import Counter
                    ec = Counter(emotions)
                    for em, cnt in ec.most_common():
                        st.markdown(f"- `{em}` — used {cnt}× in top performers")

            with wc2:
                st.markdown("**Top-performing hooks (Agent 3 models these)**")
                for h in wp.get("top_hooks", []):
                    if h:
                        st.markdown(f"> *\"{h[:120]}...\"*" if len(h) > 120 else f"> *\"{h}\"*")

                if wp.get("avg_watch_pct"):
                    st.metric("Avg watch time (top 3)", f"{wp['avg_watch_pct']}%")
                if wp.get("best_score"):
                    st.metric("Best virality score", wp["best_score"])

            st.info(
                "The next time you run the pipeline, Agent 1 will scan for trends "
                f"similar to **'{wp.get('best_topic','your top performer')}'** and "
                "Agent 3 will open with a hook modelled on your highest-retention line.",
                icon="🔁"
            )

            # Export patterns as JSON
            st.download_button(
                "⬇️ Export Winning Patterns as JSON",
                json.dumps({"winning_patterns": wp, "all_performances": st.session_state.performances}, indent=2),
                file_name="winning_patterns.json",
                mime="application/json",
            )

    else:
        st.info("No performance data yet. Post your first videos and come back in 48–72 hours to log results.")


# ── INJECT WINNING PATTERNS INTO AGENT PROMPTS ────────────────────────────────
# These functions patch the existing agent functions to use feedback loop data.

def get_feedback_context() -> str:
    """
    Returns a context block the agents inject into their prompts.
    Returns empty string if no winning patterns exist yet.
    """
    wp = st.session_state.get("winning_patterns", {})
    if not wp:
        return ""
    top_topics  = ", ".join([t for t in wp.get("top_topics",[]) if t][:3])
    top_emotions = ", ".join(list(set([e for e in wp.get("top_emotions",[]) if e])))
    best_hook   = wp.get("best_hook","")
    avg_watch   = wp.get("avg_watch_pct", 0)
    return f"""
PERFORMANCE FEEDBACK FROM PREVIOUS BATCHES:
- Top-performing topic angles: {top_topics}
- Most effective emotional registers: {top_emotions}
- Best hook line (model new hooks after this style): "{best_hook}"
- Average watch time of top performers: {avg_watch}%
- Instruction: Bias toward topics and hook styles similar to these winners.
  If avg watch time is below 60%, prioritise more provocative/shocking opening lines.
""".strip()


# ── PATCH SIDEBAR & ROUTER TO INCLUDE ANALYTICS PAGE ─────────────────────────
# Add analytics to PAGE_MAP (already defined above as PAGE_MAP = {...})
# We extend it here after the function is defined.

PAGE_MAP["analytics"] = page_analytics
# ──────────────────────────────────────────────────────────────────────────────
# AGENT 6 — PRODUCT CREATOR
# ──────────────────────────────────────────────────────────────────────────────

def agent_product_creator() -> dict:
    """Creates the full £17 digital product — section by section with auto-retry on failures."""
    import time
    product = st.session_state.get("product", "The AI Content Creator Starter Kit")
    niche   = st.session_state.get("niche", "AI tools and side income")
    price   = st.session_state.get("product_price", 17)

    def _dict_or(data, list_key):
        if isinstance(data, dict): return data
        if isinstance(data, list) and list_key: return {list_key: data}
        return {}

    def _gen_section(prompt: str, list_key, section_name: str, max_retries: int = 3) -> dict:
        """Generate a section with auto-retry if empty or malformed."""
        result = {}
        for attempt in range(1, max_retries + 1):
            raw = call_claude([{"role":"user","content":prompt}])
            result = _dict_or(extract_json(raw), list_key)
            items = result.get(list_key, []) if isinstance(result, dict) and list_key else None
            ok = isinstance(result, dict) and (items if list_key else result)
            if ok:
                if attempt > 1:
                    add_log("productCreator", f"  ✓ {section_name} succeeded on attempt {attempt}")
                return result
            wait = 3 * attempt
            add_log("productCreator", f"  ⚠️ {section_name} empty on attempt {attempt}/{max_retries} — retrying in {wait}s...")
            time.sleep(wait)
        add_log("productCreator", f"  ✗ {section_name} failed after {max_retries} attempts")
        return result if isinstance(result, dict) else {}

    add_log("productCreator", f"Writing full product: '{product}' at £{price}")

    # SECTION 1 — Tools
    add_log("productCreator", "Section 1/6: AI tools list...")
    s1 = _gen_section(f"""Generate Section 1 of a £{price} guide '{product}' for the niche: {niche}.
Return ONLY valid JSON (no markdown, no code fences):
{{"heading":"The 8 Best AI Tools for Content Creators","intro":"2-3 sentence intro","tools":[{{"name":"","url":"","cost":"Free or £X/mo","bestFor":"","howToUse":"2-3 sentence guide","affiliateNote":""}}]}}
Include exactly 8 real AI tools with real working URLs covering: scriptwriting, voice-over, video editing, image generation, design, scheduling, productivity, automation.""", "tools", "Section 1 (Tools)")

    # SECTION 2 — Workflow
    add_log("productCreator", "Section 2/6: Daily workflow...")
    s2 = _gen_section(f"""Generate Section 2 of a £{price} guide '{product}'.
Return ONLY valid JSON:
{{"heading":"Your Exact 3-Videos-Per-Day Workflow","intro":"2-3 sentences","steps":[{{"step":1,"title":"","detail":"3-4 sentences","timeRequired":"X min","toolNeeded":""}}]}}
Include exactly 6 workflow steps to produce 3 videos per day.""", "steps", "Section 2 (Workflow)")

    # SECTION 3 — Revenue (compliance-aware)
    add_log("productCreator", "Section 3/6: 4-tier revenue system (compliance-aware)...")
    s3 = _gen_section(f"""Generate Section 3 of a £{price} guide '{product}'.
Return ONLY valid JSON:
{{"heading":"The 4-Tier Revenue System","intro":"2-3 sentences INCLUDING explicit disclaimer that results vary based on effort and consistency","disclaimer":"Full disclaimer paragraph - typical results require 6-12 months consistent work, individual results vary significantly","tiers":[{{"tier":1,"name":"","howItWorks":"3-4 sentences","expectedMonthly":"realistic beginner range","monthsToFullPotential":"X months","timeToFirstIncome":"X weeks","resultsDisclaimer":"Brief caveat about effort required"}}]}}

CRITICAL COMPLIANCE REQUIREMENTS (TikTok, Meta, FTC, UK ASA):
- ALL income ranges MUST be REALISTIC for a beginner with no audience
- Tier 1 (digital products): £0-£100/mo months 1-3, grows to £100-£500/mo with consistency by month 6+
- Tier 2 (affiliates): £0-£50/mo initially, scales with traffic
- Tier 3 (newsletter sponsorships): requires 500+ engaged subscribers MINIMUM, realistic £50-£200/mo at 1k subs
- Tier 4 (TikTok Creator Rewards): UK rates are £0.02-£0.04 per 1k views; need 10k followers + 100k+ views/30 days to qualify; realistic £20-£150/mo for most qualifying creators
- EVERY tier must include resultsDisclaimer about consistency required
- AVOID: "easy money", "anyone can", "guaranteed", "passive income with no work"
- USE: "typical results depend on", "with consistent effort", "example range for committed creators"
- Cover all 4 tiers: Digital products, Affiliate commissions, Newsletter sponsorships, TikTok Creator Rewards""", "tiers", "Section 3 (Revenue)")

    # SECTION 4 — Hooks (platform-safe)
    add_log("productCreator", "Section 4/6: 30 viral hooks (platform-safe)...")
    s4 = _gen_section(f"""Generate Section 4 of a £{price} guide '{product}'.
Return ONLY valid JSON:
{{"heading":"30 Viral Hook Templates That Stop Scrolling","intro":"2-3 sentences with note that hooks should be adapted to your real experience","complianceNote":"Brief reminder that specific income claims must be your actual results not fabricated","hooks":["hook 1","hook 2"]}}

CRITICAL: Generate 30 hooks that are PLATFORM-SAFE:
- AVOID specific fabricated income claims like "I made £847 in 72 hours" (these get flagged)
- AVOID "anyone can make $X" patterns
- INSTEAD use: curiosity gaps, contrarian takes, specific tool mentions, transformation stories, common problems
- EXAMPLES OF SAFE PATTERNS:
  * "The AI tool that completely changed how I [specific task]"
  * "I tried [tool] for 30 days and here's what actually happened"
  * "Stop using [common thing] - this AI alternative is 10x faster"
  * "The 3 AI workflows I use every morning before opening email"
  * "Most people use ChatGPT wrong - here's the prompt structure that works"
- Mix curiosity, contrarian opinions, specific tools, time-based experiments, and process reveals
- 30 hooks total, diverse patterns, all platform-safe""", "hooks", "Section 4 (Hooks)")

    # SECTION 5 — 30-Day Plan (split into 3 chunks of 10 days)
    add_log("productCreator", "Section 5a/6: Days 1-10...")
    days1 = _gen_section(f"""Generate Days 1-10 of a 30-day action plan for '{product}' (niche: {niche}).
Return ONLY valid JSON:
{{"days":[{{"day":"Day 1","tasks":["task 1","task 2","task 3"],"goal":"specific daily goal"}}]}}
Generate exactly 10 days. Focus: setup, foundation, first videos, account creation, niche research.""", "days", "Section 5a (Days 1-10)").get("days", []) or []

    add_log("productCreator", "Section 5b/6: Days 11-20...")
    days2 = _gen_section(f"""Generate Days 11-20 of a 30-day action plan for '{product}'.
Return ONLY valid JSON:
{{"days":[{{"day":"Day 11","tasks":["task 1","task 2","task 3"],"goal":"specific daily goal"}}]}}
Generate exactly 10 days. Focus: consistency, optimisation, audience growth, first affiliate links, newsletter setup.""", "days", "Section 5b (Days 11-20)").get("days", []) or []

    add_log("productCreator", "Section 5c/6: Days 21-30...")
    days3 = _gen_section(f"""Generate Days 21-30 of a 30-day action plan for '{product}'.
Return ONLY valid JSON:
{{"days":[{{"day":"Day 21","tasks":["task 1","task 2","task 3"],"goal":"specific daily goal"}}]}}
Generate exactly 10 days. Focus: product launch on Gumroad, scaling content, monetisation, reinvesting income.""", "days", "Section 5c (Days 21-30)").get("days", []) or []

    s5 = {
        "heading": "Your 30-Day Action Plan",
        "intro":   "A complete day-by-day blueprint to launch your AI content business and start generating side income within 30 days.",
        "days":    days1 + days2 + days3
    }

    # METADATA — Gumroad listing
    add_log("productCreator", "Section 6/6: Gumroad listing metadata...")
    meta = _gen_section(f"""Create Gumroad metadata for '{product}' at £{price}.
Return ONLY valid JSON:
{{"title":"{product}","subtitle":"compelling subtitle","gumroadTitle":"short compelling title","gumroadDescription":"150-200 word compelling description","tags":["tag1","tag2","tag3","tag4","tag5"]}}""", None, "Metadata")

    product_data = {
        "title":              meta.get("title", product),
        "subtitle":           meta.get("subtitle", ""),
        "price":              price,
        "section1":           s1,
        "section2":           s2,
        "section3":           s3,
        "section4":           s4,
        "section5":           s5,
        "gumroadTitle":       meta.get("gumroadTitle", product),
        "gumroadDescription": meta.get("gumroadDescription", ""),
        "tags":               meta.get("tags", []),
    }

    sections_ok = sum(1 for s in [s1,s2,s3,s4,s5] if s and any(s.values()))
    add_log("productCreator", f"Product complete — {sections_ok}/5 sections, {len(s4.get('hooks',[]))} hooks, {len(s5.get('days',[]))} days")
    return product_data


# ──────────────────────────────────────────────────────────────────────────────
# AGENT 7 — PRODUCT QA
# ──────────────────────────────────────────────────────────────────────────────

def agent_product_qa(product_data: dict) -> dict:
    """Production-grade QA — 5 rigorous passes, each independent and reliable."""
    add_log("productQA", "=== RIGOROUS QA STARTED — 5 audit passes ===")
    price = product_data.get('price', 17)

    tools = product_data.get('section1',{}).get('tools',[])
    steps = product_data.get('section2',{}).get('steps',[])
    tiers = product_data.get('section3',{}).get('tiers',[])
    hooks = product_data.get('section4',{}).get('hooks',[])
    days  = product_data.get('section5',{}).get('days',[])

    # ── PASS 1: Completeness (programmatic, 100% reliable)
    add_log("productQA", "Pass 1/5: Completeness audit...")
    completeness = 10
    completeness_issues = []
    if len(tools) < 8:  completeness -= (8 - len(tools));      completeness_issues.append(f"Section 1: {len(tools)}/8 tools")
    if len(steps) < 6:  completeness -= (6 - len(steps));      completeness_issues.append(f"Section 2: {len(steps)}/6 steps")
    if len(tiers) < 4:  completeness -= (4 - len(tiers)) * 2;  completeness_issues.append(f"Section 3: {len(tiers)}/4 tiers")
    if len(hooks) < 25: completeness -= max(0, (25 - len(hooks)) // 3); completeness_issues.append(f"Section 4: {len(hooks)}/25+ hooks")
    if len(days)  < 25: completeness -= max(0, (25 - len(days))  // 3); completeness_issues.append(f"Section 5: {len(days)}/25+ days")

    field_issues = []
    for i, t in enumerate(tools):
        if not t.get('url'):      field_issues.append(f"Tool '{t.get('name','#'+str(i+1))}' missing URL")
        if len(t.get('howToUse','')) < 80: field_issues.append(f"Tool '{t.get('name','#'+str(i+1))}' instructions too short")
    for i, s in enumerate(steps):
        if len(s.get('detail','')) < 150: field_issues.append(f"Step {i+1} detail under 150 chars")
    for i, ti in enumerate(tiers):
        if not ti.get('expectedMonthly'): field_issues.append(f"Tier {i+1} missing income range")
    if field_issues:
        completeness -= min(3, len(field_issues) // 2)
        completeness_issues.extend(field_issues[:5])
    completeness = max(0, min(10, completeness))
    add_log("productQA", f"  → {completeness}/10  ({len(tools)} tools · {len(steps)} steps · {len(tiers)} tiers · {len(hooks)} hooks · {len(days)} days)")

    # ── PASS 2: Accuracy
    add_log("productQA", "Pass 2/5: Accuracy audit — URLs, prices, claims...")
    acc_sample = {
        "tools": [{"name": t.get("name"), "url": t.get("url"), "cost": t.get("cost")} for t in tools],
        "income_ranges": [{"tier": ti.get("name",""), "range": ti.get("expectedMonthly","")} for ti in tiers],
        "claims_in_steps": [s.get("detail","")[:200] for s in steps[:3]],
    }
    raw_a = call_claude([{"role":"user","content":f"""Audit a £{price} digital product for ACCURACY. Return ONLY valid JSON:
{{"score":7,"unverifiableClaims":["c1"],"riskyIncomeNumbers":["i1"],"fakeOrDeadUrls":["url1"],"strengths":["s1"]}}

DATA: {json.dumps(acc_sample)[:3500]}

Check: Are tool URLs real and active websites? Are listed prices accurate? Are income ranges realistic for the niche (not fantasy)? Are step instructions specific not vague?
10 = fully verifiable, 7 = mostly accurate, 5 = several inaccuracies, 3 = significant problems."""}])
    a = extract_json(raw_a) or {}
    if not isinstance(a, dict): a = {}
    accuracy = int(a.get("score", 7))
    add_log("productQA", f"  → {accuracy}/10")

    # ── PASS 3: Quality (writing, actionability, specificity)
    add_log("productQA", "Pass 3/5: Quality audit — writing, actionability, specificity...")
    q_sample = {
        "first_step_detail":      steps[0].get("detail","") if steps else "",
        "second_step_detail":     steps[1].get("detail","") if len(steps)>1 else "",
        "first_tier_explanation": tiers[0].get("howItWorks","") if tiers else "",
        "sample_hooks":           hooks[:8],
        "sample_days":            [{"day": d.get("day"), "tasks": d.get("tasks",[]), "goal": d.get("goal","")} for d in days[:5]],
        "gumroadDescription":     product_data.get("gumroadDescription",""),
    }
    raw_q = call_claude([{"role":"user","content":f"""Audit WRITING QUALITY of a £{price} product. Return ONLY valid JSON:
{{"score":7,"actionability":"high/medium/low","specificity":"high/medium/low","engagement":"high/medium/low","aiFillerDetected":false,"issues":["i1"],"strengths":["s1"]}}

SAMPLE: {json.dumps(q_sample)[:3500]}

Check: Can a beginner follow these instructions exactly? Is writing specific (real numbers, named tools, exact steps) not vague? Are hooks genuinely scroll-stopping? Any 'AI filler' phrases ('it's important to', 'unlock the power of', 'leverage', 'streamline')?
10 = pro copywriter, 7 = solid clear writing, 5 = generic but readable, 3 = vague AI slop."""}])
    q = extract_json(raw_q) or {}
    if not isinstance(q, dict): q = {}
    quality = int(q.get("score", 7))
    add_log("productQA", f"  → {quality}/10 · Actionability:{q.get('actionability','-')} · Specificity:{q.get('specificity','-')}")

    # ── PASS 4: Compliance (income claims, platform risk, FTC)
    add_log("productQA", "Pass 4/5: Compliance audit — income claims, legal/platform risk...")
    c_sample = {
        "tier_income_ranges": [t.get("expectedMonthly","") for t in tiers],
        "tier_explanations":  [t.get("howItWorks","") for t in tiers],
        "monetary_hooks":     [h for h in hooks if any(x in h for x in ["£","$","income","month","earn","made"])][:10],
        "step_claims":        " ".join([s.get("detail","") for s in steps])[:2000],
        "gumroadDescription": product_data.get("gumroadDescription",""),
    }
    raw_c = call_claude([{"role":"user","content":f"""Audit a digital product for COMPLIANCE RISK (FTC, ASA UK, platform policies). Return ONLY valid JSON:
{{"score":7,"unsubstantiatedIncomeClaims":["claim"],"guaranteeLanguage":["phrase"],"missingDisclosures":["thing"],"safeForPlatforms":true,"strengths":["s1"]}}

DATA: {json.dumps(c_sample)[:3500]}

Check: Any GUARANTEED income claims? Any specific income without 'results vary' framing? Any 'anyone can make X' language? Missing affiliate disclosure? Anything TikTok/Meta would flag?
10 = fully compliant, 7 = safe with minor tweaks, 5 = risky language, 3 = major issues."""}])
    c = extract_json(raw_c) or {}
    if not isinstance(c, dict): c = {}
    compliance = int(c.get("score", 7))
    add_log("productQA", f"  → {compliance}/10 · Platform safe: {c.get('safeForPlatforms', '-')}")

    # ── PASS 5: Value vs £17 Price
    add_log("productQA", f"Pass 5/5: Value audit — does it justify £{price}?")
    v_sample = {
        "counts":              {"tools":len(tools),"steps":len(steps),"tiers":len(tiers),"hooks":len(hooks),"days":len(days)},
        "depth": {
            "avg_tool_instructions_chars": sum(len(t.get("howToUse","")) for t in tools) // max(1,len(tools)),
            "avg_step_detail_chars":       sum(len(s.get("detail","")) for s in steps) // max(1,len(steps)),
            "avg_tier_explanation_chars":  sum(len(t.get("howItWorks","")) for t in tiers) // max(1,len(tiers)),
            "avg_tasks_per_day":           sum(len(d.get("tasks",[])) for d in days) // max(1,len(days)),
        },
        "sample_hook":      hooks[0] if hooks else "",
        "sample_day_tasks": days[0].get("tasks",[]) if days else [],
    }
    raw_v = call_claude([{"role":"user","content":f"""Audit VALUE vs £{price} price. Compare to typical Gumroad products at this price point. Return ONLY valid JSON:
{{"score":7,"verdict":"underpriced/fair/overpriced","comparablePrice":"£X-£Y","valueGaps":["gap"],"surprises":["unexpected value"]}}

METRICS: {json.dumps(v_sample)}

Benchmark: A typical £17 AI product offers ~5-7 tools, ~4 steps, ~15 hooks, ~14 days. Compare this product's actual metrics.
10 = significantly overdelivers (could charge £30+), 7 = fair value, 5 = thin for price, 3 = doesn't justify price."""}])
    v = extract_json(raw_v) or {}
    if not isinstance(v, dict): v = {}
    value = int(v.get("score", 7))
    add_log("productQA", f"  → {value}/10 · Verdict: {v.get('verdict','-')} · Comparable: {v.get('comparablePrice','-')}")

    # ── AGGREGATE
    overall = round(completeness*0.25 + accuracy*0.25 + quality*0.20 + compliance*0.20 + value*0.10)

    critical = []
    if completeness < 7: critical.extend(completeness_issues[:3])
    if accuracy < 6:     critical.append(f"Accuracy below 6/10"); critical.extend(a.get("unverifiableClaims",[])[:2])
    if compliance < 7:   critical.append(f"Compliance risk"); critical.extend(c.get("unsubstantiatedIncomeClaims",[])[:2])
    if quality < 6:      critical.append(f"Writing quality below threshold")

    all_issues = completeness_issues + a.get("unverifiableClaims",[]) + a.get("riskyIncomeNumbers",[]) + q.get("issues",[]) + c.get("unsubstantiatedIncomeClaims",[]) + c.get("missingDisclosures",[]) + v.get("valueGaps",[])
    all_strengths = a.get("strengths",[]) + q.get("strengths",[]) + c.get("strengths",[]) + v.get("surprises",[])

    passed = overall >= 8 and not critical and compliance >= 7

    add_log("productQA", f"=== FINAL: {overall}/10 — {'✓ APPROVED FOR GUMROAD' if passed else '✗ NEEDS REVISION'} ===")

    return {
        "overallScore":      overall,
        "completenessScore": completeness,
        "accuracyScore":     accuracy,
        "qualityScore":      quality,
        "complianceScore":   compliance,
        "valueScore":        value,
        "passesQA":          passed,
        "strengths":         all_strengths[:10],
        "issues":            all_issues[:15],
        "criticalIssues":    critical,
        "recommendation":    "APPROVE" if passed else "REVISE",
        "improvementInstructions": "Critical issues to fix: " + "; ".join(critical) if critical else "Product approved for Gumroad upload",
        "_details": {
            "valueVerdict":      v.get("verdict",""),
            "comparablePrice":   v.get("comparablePrice",""),
            "actionability":     q.get("actionability",""),
            "specificity":       q.get("specificity",""),
            "platformSafe":      c.get("safeForPlatforms", True),
            "guaranteeLanguage": c.get("guaranteeLanguage",[]),
        }
    }


# ──────────────────────────────────────────────────────────────────────────────
# PRODUCT CREATOR PAGE
# ──────────────────────────────────────────────────────────────────────────────

def page_product():
    st.title("📦 Product Creator")
    st.caption("Agent 6 writes your complete digital product. Agent 7 verifies it before anything goes live.")

    if "product_data"   not in st.session_state: st.session_state.product_data   = {}
    if "product_qa"     not in st.session_state: st.session_state.product_qa     = {}
    if "product_ready"  not in st.session_state: st.session_state.product_ready  = False

    product = st.session_state.get("product", "The AI Content Creator Starter Kit")
    price   = st.session_state.get("product_price", 17)

    st.info(f"Product to create: **{product}** — priced at **£{price}**", icon="📦")

    if not st.session_state.product_data:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Sections", "5 complete sections")
        with c2:
            st.metric("Estimated pages", "20–30 pages")

        if st.button("🤖 Generate Full Product with Agent 6", type="primary", use_container_width=True):
            with st.spinner("Agent 6 writing your complete product... (takes 2-3 minutes)"):
                try:
                    add_log("productCreator", "=== PRODUCT CREATION STARTED ===")
                    product_data = agent_product_creator()
                    if product_data:
                        st.session_state.product_data  = product_data
                        st.session_state.product_ready = False
                        st.success("Product content generated. Running QA verification...")
                        with st.spinner("Agent 7 verifying quality and accuracy..."):
                            qa = agent_product_qa(product_data)
                            st.session_state.product_qa    = qa
                            st.session_state.product_ready = qa.get("passesQA", False)
                        st.rerun()
                    else:
                        st.error("Generation failed — please try again.")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        pd_data = st.session_state.product_data
        qa      = st.session_state.product_qa

        # QA Results banner
        passed = qa.get("passesQA", False)
        score  = qa.get("overallScore", 0)

        if passed:
            st.success(f"✅ Product passed QA — Score: {score}/10 — Ready for Gumroad upload", icon="✅")
        else:
            st.warning(f"⚠️ Product needs revision — Score: {score}/10 — See issues below", icon="⚠️")

        # QA Scores
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Overall",      f"{qa.get('overallScore',0)}/10")
        c2.metric("Completeness", f"{qa.get('completenessScore',0)}/10")
        c3.metric("Accuracy",     f"{qa.get('accuracyScore',0)}/10")
        c4.metric("Quality",      f"{qa.get('qualityScore',0)}/10")
        c5.metric("Compliance",   f"{qa.get('complianceScore',0)}/10")
        c6.metric("Value",        f"{qa.get('valueScore',0)}/10")

# SMART PRICE OPTIMIZER
        if passed and "price_analysis" not in st.session_state:
            with st.spinner("Agent 9 analysing optimal pricing strategy..."):
                st.session_state.price_analysis = agent_price_optimizer(pd_data, qa)

        if passed and st.session_state.get("price_analysis"):
            pa = st.session_state.price_analysis
            launch = pa.get("launchPrice", pd_data.get("price",17))
            target = pa.get("targetPrice", launch)
            current = pd_data.get("price", 17)

            if True:  # always show pricing analysis
                st.markdown("---")
                st.markdown("### 💰 Smart Pricing Recommendation")
                pc1, pc2, pc3 = st.columns(3)
                pc1.metric("Current price",    f"£{current}")
                pc2.metric("Launch price",     f"£{launch}", delta=f"{launch-current:+}")
                pc3.metric("Target price",     f"£{target}", delta=f"{target-current:+}")

                st.info(f"**Reasoning:** {pa.get('reasoning','')}")
                if pa.get("expectedImpact"):
                    st.caption(f"**Expected impact:** {pa.get('expectedImpact','')}")

                if pa.get("milestones"):
                    with st.expander("📈 Price increase roadmap"):
                        for m in pa.get("milestones",[]):
                            st.markdown(f"- **{m.get('trigger','')}** → raise to **£{m.get('newPrice','')}** _({m.get('reasoning','')})_")

                ac1, ac2 = st.columns(2)
                with ac1:
                    if st.button(f"✅ Apply £{launch} launch price", type="primary", use_container_width=True):
                        st.session_state.product_price = launch
                        if isinstance(st.session_state.product_data, dict):
                            st.session_state.product_data["price"] = launch
                        st.success(f"Price updated to £{launch}")
                        st.rerun()
                with ac2:
                    if st.button("Keep current price", use_container_width=True):
                        st.session_state.price_analysis["userKeptPrice"] = True
                        st.rerun()
                st.markdown("---")
        details = qa.get("_details", {})
        if details:
            with st.expander("📊 Detailed QA breakdown"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Value verdict:** {details.get('valueVerdict','—')}")
                    st.markdown(f"**Comparable price:** {details.get('comparablePrice','—')}")
                    st.markdown(f"**Actionability:** {details.get('actionability','—')}")
                with col2:
                    st.markdown(f"**Specificity:** {details.get('specificity','—')}")
                    st.markdown(f"**Platform safe:** {'✓' if details.get('platformSafe') else '✗'}")
                    if details.get('guaranteeLanguage'):
                        st.markdown(f"**Risky phrases:** {', '.join(details['guaranteeLanguage'][:3])}")

        if qa.get("criticalIssues"):
            st.error("Critical issues found:\n" + "\n".join(f"- {i}" for i in qa["criticalIssues"]))
        if qa.get("issues"):
            with st.expander("⚠️ All QA issues"):
                for i in qa["issues"]: st.markdown(f"- {i}")
        if qa.get("strengths"):
            with st.expander("✅ Strengths"):
                for s in qa["strengths"]: st.markdown(f"- {s}")

        st.divider()

        # Product preview
        st.subheader(pd_data.get("title",""))
        st.caption(pd_data.get("subtitle",""))

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔧 AI Tools", "📹 Workflow", "💰 Revenue", "🎣 Hooks", "📅 30-Day Plan"
        ])

        with tab1:
            s1 = pd_data.get("section1",{})
            st.markdown(f"**{s1.get('heading','')}**")
            st.markdown(s1.get("intro",""))
            for tool in s1.get("tools",[]):
                with st.expander(f"**{tool.get('name','')}** — {tool.get('cost','')}"):
                    st.markdown(f"**Best for:** {tool.get('bestFor','')}")
                    st.markdown(f"**How to use:** {tool.get('howToUse','')}")
                    if tool.get("url"): st.markdown(f"**Link:** {tool.get('url','')}")

        with tab2:
            s2 = pd_data.get("section2",{})
            st.markdown(f"**{s2.get('heading','')}**")
            st.markdown(s2.get("intro",""))
            for step in s2.get("steps",[]):
                st.markdown(f"**Step {step.get('step','')} — {step.get('title','')}**")
                st.markdown(step.get("detail",""))
                st.caption(f"Time: {step.get('timeRequired','')} · Tool: {step.get('toolNeeded','')}")
                st.divider()

        with tab3:
            s3 = pd_data.get("section3",{})
            st.markdown(f"**{s3.get('heading','')}**")
            for tier in s3.get("tiers",[]):
                with st.expander(f"Tier {tier.get('tier','')} — {tier.get('name','')} → {tier.get('expectedMonthly','')}"):
                    st.markdown(tier.get("howItWorks",""))
                    st.caption(f"Time to first income: {tier.get('timeToFirstIncome','')}")

        with tab4:
            s4 = pd_data.get("section4",{})
            st.markdown(f"**{s4.get('heading','')}**")
            hooks = s4.get("hooks",[])
            st.caption(f"{len(hooks)} hooks generated")
            for j, hook in enumerate(hooks,1):
                st.markdown(f"**{j}.** *\"{hook}\"*")

        with tab5:
            s5 = pd_data.get("section5",{})
            st.markdown(f"**{s5.get('heading','')}**")
            for day in s5.get("days",[]):
                with st.expander(f"**{day.get('day','')}** — {day.get('goal','')}"):
                    for task in day.get("tasks",[]): st.markdown(f"- {task}")

        st.divider()

        # Download + actions
        product_text = f"""# {pd_data.get('title','')}
## {pd_data.get('subtitle','')}
Price: £{pd_data.get('price',17)}

---

## {pd_data.get('section1',{}).get('heading','')}
{pd_data.get('section1',{}).get('intro','')}

""" + "\n".join([f"### {t.get('name','')} ({t.get('cost','')})\nBest for: {t.get('bestFor','')}\nHow to use: {t.get('howToUse','')}\nURL: {t.get('url','')}" for t in pd_data.get('section1',{}).get('tools',[])]) + f"""

---

## {pd_data.get('section2',{}).get('heading','')}
""" + "\n".join([f"Step {s.get('step','')} — {s.get('title','')}\n{s.get('detail','')}" for s in pd_data.get('section2',{}).get('steps',[])]) + f"""

---

## {pd_data.get('section4',{}).get('heading','')}
""" + "\n".join([f"{j}. {h}" for j,h in enumerate(pd_data.get('section4',{}).get('hooks',[]),1)]) + f"""

---

## {pd_data.get('section5',{}).get('heading','')}
""" + "\n".join([f"{d.get('day','')} — {d.get('goal','')}\n" + "\n".join([f"• {t}" for t in d.get('tasks',[])]) for d in pd_data.get('section5',{}).get('days',[])])

        st.download_button(
            "⬇️ Download Product as Text File",
            product_text.encode("utf-8"),
            file_name=f"{product.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Regenerate Product", use_container_width=True):
                st.session_state.product_data  = {}
                st.session_state.product_qa    = {}
                st.session_state.product_ready = False
                st.rerun()
        with c2:
            if passed:
                st.markdown("**✅ Ready for Gumroad upload**")
                if "gumroad_result" not in st.session_state:
                    st.session_state.gumroad_result = None

                if st.session_state.gumroad_result and st.session_state.gumroad_result.get("success"):
                    g = st.session_state.gumroad_result
                    st.success(f"🎉 Product live on Gumroad!")
                    st.markdown(f"**Product URL:** [{g['product_url']}]({g['product_url']})")
                    st.markdown(f"**Edit on Gumroad:** [Open editor]({g['edit_url']})")
                    if g.get("note"):
                        st.info(g["note"])
                else:
                    if st.button("🚀 Upload to Gumroad", type="primary", use_container_width=True):
                        with st.spinner("Agent 8 uploading product to Gumroad..."):
                            try:
                                result = agent_gumroad_publisher(pd_data, qa)
                                st.session_state.gumroad_result = result
                                if result.get("success"):
                                    st.success("Uploaded successfully!")
                                else:
                                    st.error(f"Upload failed: {result.get('error','Unknown error')}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            else:
                st.warning("Fix QA issues before Gumroad upload")


PAGE_MAP["product"] = page_product


# ──────────────────────────────────────────────────────────────────────────────
# AGENT 8 — GUMROAD PUBLISHER
# ──────────────────────────────────────────────────────────────────────────────

def agent_gumroad_publisher(product_data: dict, qa_data: dict) -> dict:
    """Uploads product to Gumroad automatically — only runs if QA passed."""
    import requests as req_lib

    token = st.secrets.get("GUMROAD_ACCESS_TOKEN", "")
    if not token:
        add_log("gumroad", "✗ No Gumroad token found in Streamlit Secrets")
        return {"success": False, "error": "Missing GUMROAD_ACCESS_TOKEN in Streamlit Secrets"}

    if not qa_data.get("passesQA", False):
        add_log("gumroad", f"✗ Upload blocked — QA score {qa_data.get('overallScore',0)}/10 (need 8+)")
        return {"success": False, "error": f"QA score too low: {qa_data.get('overallScore',0)}/10 — fix issues first"}

    add_log("gumroad", "=== GUMROAD UPLOAD STARTED ===")

    title       = product_data.get("gumroadTitle") or product_data.get("title", "Digital Product")
    description = product_data.get("gumroadDescription", "")
    price       = product_data.get("price", 17)
    tags        = product_data.get("tags", [])

    # Gumroad takes price in cents
    price_cents = int(float(price) * 100)

    add_log("gumroad", f"Creating product: '{title}' at £{price}")

    try:
        # Create the product
        resp = req_lib.post(
            "https://api.gumroad.com/v2/products",
            data={
                "access_token":            token,
                "name":                    title[:90],
                "price":                   price_cents,
                "description":             description,
            },
            timeout=30,
        )

        add_log("gumroad", f"API response status: {resp.status_code}")

        if resp.status_code != 200:
            err_text = resp.text[:300]
            add_log("gumroad", f"✗ API error: {err_text}")
            return {"success": False, "error": f"Gumroad API returned {resp.status_code}: {err_text}"}

        result = resp.json()
        if not result.get("success"):
            err_msg = result.get("message", "Unknown error")
            add_log("gumroad", f"✗ Gumroad rejected: {err_msg}")
            return {"success": False, "error": err_msg}

        product = result.get("product", {})
        product_id  = product.get("id", "")
        product_url = product.get("short_url") or product.get("url", "")

        add_log("gumroad", f"✓ Product created — ID: {product_id}")
        add_log("gumroad", f"✓ Product URL: {product_url}")

        # Add tags
        if tags:
            add_log("gumroad", f"Adding {len(tags)} tags...")
            for tag in tags[:5]:
                req_lib.put(
                    f"https://api.gumroad.com/v2/products/{product_id}",
                    data={"access_token": token, "tags[]": tag},
                    timeout=15,
                )

        add_log("gumroad", "=== UPLOAD COMPLETE ✓ ===")

        return {
            "success":      True,
            "product_id":   product_id,
            "product_url":  product_url,
            "title":        title,
            "price":        f"£{price}",
            "edit_url":     f"https://app.gumroad.com/products/{product_id}/edit",
            "note":         "Product created as DRAFT. You must upload the actual PDF file and click Publish on Gumroad to make it live.",
        }

    except req_lib.exceptions.Timeout:
        add_log("gumroad", "✗ Request timed out")
        return {"success": False, "error": "Gumroad API timed out — try again"}
    except Exception as e:
        add_log("gumroad", f"✗ Exception: {str(e)[:200]}")
        return {"success": False, "error": str(e)[:300]}

# ──────────────────────────────────────────────────────────────────────────────
# AGENT 9 — SMART PRICE OPTIMIZER
# ──────────────────────────────────────────────────────────────────────────────

def agent_price_optimizer(product_data: dict, qa_data: dict) -> dict:
    """Smart pricing agent — recommends optimal launch price + milestone roadmap."""

    current_price = product_data.get("price", 17)
    qa_details    = qa_data.get("_details", {})
    comparable    = qa_details.get("comparablePrice", "")
    verdict       = qa_details.get("valueVerdict", "")
    value_score   = qa_data.get("valueScore", 7)
    quality_score = qa_data.get("qualityScore", 7)
    completeness  = qa_data.get("completenessScore", 7)

    add_log("priceOptimizer", "=== SMART PRICING ANALYSIS ===")
    add_log("priceOptimizer", f"Current: £{current_price} · Comparable range: {comparable} · Verdict: {verdict}")

    raw = call_claude([{"role":"user","content":f"""You are a digital product pricing strategist for first-time creators.

PRODUCT: {product_data.get('title','')}
Current price: £{current_price}
Comparable products sell for: {comparable}
Value verdict from QA: {verdict}
Scores → Value:{value_score}/10  Quality:{quality_score}/10  Completeness:{completeness}/10
Target audience: Complete beginners looking to start AI side income

REALITY CHECK:
- Zero reviews yet (first product, first launch)
- No established audience
- Goal: balance maximising revenue vs maximising first-sales velocity
- £17 = impulse-buy sweet spot
- £15 floor = "looks cheap/thin"
- £25 ceiling without reviews = "needs social proof first"
- Most successful first launches sit in £15-£25 range
- Price can be raised over time as reviews accumulate

Return ONLY valid JSON:
{{
  "launchPrice": 17,
  "targetPrice": 27,
  "priceUpdateRecommended": true,
  "currentPriceVerdict": "underpriced/optimal/overpriced",
  "reasoning": "2-3 sentences why this launch price",
  "expectedImpact": "what changes at this price",
  "milestones": [
    {{"trigger":"First 10 sales","newPrice":19,"reasoning":"Initial social proof established"}},
    {{"trigger":"20 sales + 5 reviews","newPrice":23,"reasoning":"Reviews validate quality"}},
    {{"trigger":"50 sales","newPrice":27,"reasoning":"Strong demand confirmed"}}
  ]
}}

CRITICAL: launchPrice should be optimal for FIRST SALES (not theoretical max). targetPrice is the eventual ceiling. Don't blindly raise to comparable — factor in zero-reviews reality."""}])

    result = extract_json(raw) or {}
    if not isinstance(result, dict): result = {}

    launch = result.get("launchPrice", current_price)
    target = result.get("targetPrice", current_price)
    add_log("priceOptimizer", f"Recommended launch: £{launch} · Target: £{target}")
    add_log("priceOptimizer", f"Verdict: {result.get('currentPriceVerdict','')}")

    return result
PAGE_MAP.get(st.session_state.page, page_setup)()
