"""
Streamlit demo UI for TumorBoard-Agent.

Thin presentation layer over the same TumorBoardOrchestrator used by
cli.py and eval.py -- one pipeline, three front ends.

Run locally:
    streamlit run app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from tumorboard_agent.case_loader import CaseParseError, parse_upload
from tumorboard_agent.landscape import LANDSCAPE_SVG
from tumorboard_agent.llm_provider import get_llm_provider as build_llm_provider
from tumorboard_agent.orchestrator import TumorBoardOrchestrator
from tumorboard_agent.schemas import Case, EscalationTier

DEMO_PATH = Path(__file__).resolve().parent / "data" / "synthetic_cases.json"

TIER_BADGE = {
    EscalationTier.AUTO_FINALIZE: "🟢 AUTO-FINALIZE",
    EscalationTier.SENIOR_REVIEW: "🟡 SENIOR REVIEW",
    EscalationTier.URGENT_ESCALATION: "🔴 URGENT ESCALATION",
}

st.set_page_config(page_title="TumorBoard-Agent", page_icon="🧬", layout="wide")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      .hero {
        background: linear-gradient(120deg, #1f3a5f 0%, #2e6b57 100%);
        padding: 26px 32px; border-radius: 16px; color: #fff; margin-bottom: 8px;
      }
      .hero h1 { margin: 0 0 6px 0; font-size: 30px; }
      .hero p { margin: 0; color: #d6e4f0; font-size: 15px; line-height: 1.5; }
      .pill {
        display: inline-block; background: rgba(255,255,255,0.16); color:#fff;
        padding: 3px 11px; border-radius: 999px; font-size: 12px; margin-right: 6px;
        margin-top: 10px;
      }
      /* --- sidebar polish --- */
      .sb-logo {
        background: linear-gradient(135deg, #1f3a5f 0%, #2e6b57 100%);
        border-radius: 14px; padding: 18px 16px; text-align: center;
        color: #fff; margin-bottom: 14px;
      }
      .sb-logo .icon { font-size: 40px; line-height: 1; }
      .sb-logo .title { font-size: 18px; font-weight: 700; margin-top: 6px; letter-spacing: .2px; }
      .sb-logo .sub { font-size: 11.5px; color: #cfe0f0; margin-top: 3px; }
      .sb-section {
        display: flex; align-items: center; gap: 8px;
        font-size: 15px; font-weight: 700; color: #1f2d3d;
        margin: 4px 0 6px 0;
      }
      .sb-note {
        background: #eef4fb; border-left: 3px solid #2e6b57;
        border-radius: 8px; padding: 10px 12px; font-size: 12px; color: #44566b;
        line-height: 1.45;
      }
      .sb-footer { font-size: 11px; color: #8a97a8; margin-top: 6px; line-height: 1.5; }
      section[data-testid="stSidebar"] { background: #f7f9fc; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_orchestrator(provider: str, api_key: str) -> TumorBoardOrchestrator:
    # Cache key includes provider + key so changing them rebuilds the panel.
    # An empty key/provider falls through to offline template mode.
    llm = build_llm_provider(provider or None, api_key or None)
    return TumorBoardOrchestrator(llm=llm)


@st.cache_data
def load_cases():
    with open(DEMO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def render_round(round_) -> None:
    st.markdown(
        f"**Round {round_.round_number}** — majority: `{round_.majority_recommendation.value}` "
        f"({round_.agreement_score:.0%} agreement)"
    )
    cols = st.columns(len(round_.opinions))
    for col, o in zip(cols, round_.opinions):
        with col:
            st.caption(o.agent_name)
            st.write(f"**{o.recommendation.value.replace('_', ' ')}**")
            st.progress(o.confidence, text=f"conf {o.confidence:.0%}")
    if round_.catfish_challenge:
        c = round_.catfish_challenge
        st.warning(f"🐟 **Catfish [{c.rule_id}]**: {c.challenge_text}")


def render_report(report) -> None:
    for r in report.rounds:
        render_round(r)
        st.divider()

    st.markdown(f"## {TIER_BADGE[report.oversight.tier]}")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Final consensus")
        st.success(f"**{report.consensus.final_recommendation.value.replace('_', ' ')}**")
        st.write(report.consensus.summary_text)
        if report.consensus.dissenting_agents:
            st.caption(f"Dissenting: {', '.join(report.consensus.dissenting_agents)}")
    with col2:
        st.metric("Confidence", f"{report.consensus.final_confidence:.0%}")
        st.metric("Agreement", f"{report.consensus.final_agreement_score:.0%}")
        st.metric("Rounds", report.consensus.rounds_conducted)
        st.metric("Catfish intervened", "Yes" if report.consensus.catfish_intervened else "No")

    st.subheader("Oversight reasoning")
    for reason in report.oversight.reasons:
        st.write(f"- {reason}")

    with st.expander("Full agent trace"):
        for e in report.trace:
            st.text(f"[{e.timestamp}] {e.agent} :: {e.action} -> {e.detail}")


def run_and_render(case: Case) -> None:
    provider = st.session_state.get("_llm_provider", "")
    api_key = st.session_state.get("_llm_api_key", "")
    with st.spinner("Convening the tumor board..."):
        report = get_orchestrator(provider, api_key).run(case)
    render_report(report)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <h1>🧬 TumorBoard-Agent</h1>
      <p>A simulated multi-agent molecular tumor board. Five specialist agents assess a case
      and debate; a catfish agent challenges premature consensus; a tiered oversight agent
      decides whether the panel can auto-finalize or must escalate to human review.</p>
      <span class="pill">multi-agent debate</span>
      <span class="pill">anti-groupthink</span>
      <span class="pill">tiered oversight</span>
      <span class="pill">explainable trace</span>
    </div>
    """,
    unsafe_allow_html=True,
)

def render_svg(svg: str, height: int) -> None:
    """Render a raw SVG reliably via an iframe.

    st.markdown sanitizes/escapes multi-element SVG and can render only the
    first node, dumping the rest as text; components.html renders the SVG
    faithfully inside an iframe. The wrapper forces the SVG to scale to the
    container width so it never clips.
    """
    import streamlit.components.v1 as components

    styled = svg.replace(
        "<svg ", '<svg style="width:100%;height:auto;display:block" ', 1
    )
    components.html(
        f'<div style="background:#fff;padding:4px">{styled}</div>',
        height=height,
        scrolling=False,
    )


from pathlib import Path as _Path

LANDSCAPE_PNG = _Path(__file__).resolve().parent / "docs" / "landscape.png"


def render_landscape() -> None:
    """Show the framework figure.

    Prefer the image file in docs/landscape.png (so you can replace it with
    your own edited version without touching code); fall back to the
    code-generated SVG only if that file is missing.
    """
    if LANDSCAPE_PNG.exists():
        st.image(str(LANDSCAPE_PNG), use_container_width=True)
    else:
        render_svg(LANDSCAPE_SVG, height=720)


with st.expander("How it works — where this project sits in the field", expanded=True):
    st.caption(
        "How this project maps onto the field's Perception → Agent Capabilities "
        "→ Application structure — every box is a component that actually exists "
        "in this repo."
    )
    render_landscape()

with st.sidebar:
    st.markdown(
        """
        <div class="sb-logo">
          <div class="icon">🧬🩺</div>
          <div class="title">TumorBoard-Agent</div>
          <div class="sub">multi-agent molecular tumor board</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-section">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown(
        "Portfolio/demo project — **not a medical device**, not for real clinical use. "
        "All bundled cases are synthetic."
    )
    # TODO: replace <your-username> with your GitHub handle before publishing.
    st.markdown("🔗 [View source on GitHub](https://github.com/<your-username>/tumorboard-agent)")
    st.divider()

    st.markdown('<div class="sb-section">✍️ Rationale phrasing (LLM)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-note">Decisions are always made by deterministic, auditable '
        "logic. The LLM <b>only rewrites the already-decided rationale into nicer "
        "prose</b> — it never changes a recommendation. Leave this off to run fully "
        "offline.</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    provider_label = st.radio(
        "Prose backend",
        ["🔒 Offline template (no key)", "🤖 Anthropic (Claude)", "🤖 OpenAI (GPT)"],
        index=0,
    )
    provider_map = {
        "🔒 Offline template (no key)": "",
        "🤖 Anthropic (Claude)": "anthropic",
        "🤖 OpenAI (GPT)": "openai",
    }
    provider_choice = provider_map[provider_label]

    api_key_input = ""
    if provider_choice:
        sdk_module = "anthropic" if provider_choice == "anthropic" else "openai"
        vendor = "Anthropic" if provider_choice == "anthropic" else "OpenAI"
        import importlib.util

        if importlib.util.find_spec(sdk_module) is None:
            st.warning(
                f"The `{sdk_module}` package isn't installed, so this backend "
                f"can't run. Install it with `pip install {sdk_module}`, or use "
                "offline mode. (Prose will fall back to offline template.)"
            )

        api_key_input = st.text_input(
            f"🔑 {vendor} API key",
            type="password",
            help="Used only for this session to phrase rationale text. It is not "
            "written to disk or logged. For a deployed app, prefer Streamlit "
            "secrets over pasting a key here.",
            placeholder="sk-...",
        )
        if not api_key_input:
            st.info("Enter a key to enable this backend, or it falls back to offline mode.")
        elif importlib.util.find_spec(sdk_module) is not None:
            st.success(f"✅ {vendor} backend active for this session.")

    # Stash the effective selection for run_and_render.
    st.session_state["_llm_provider"] = provider_choice if api_key_input else ""
    st.session_state["_llm_api_key"] = api_key_input if provider_choice else ""

    st.divider()
    st.markdown(
        '<div class="sb-footer">Built by Sanaz Jamalzadeh, PhD · '
        "AI &amp; Digital Health<br>Design inspired by recent agentic-healthcare "
        "research (see README).</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Tabs: demo cases vs. upload
# ---------------------------------------------------------------------------
tab_demo, tab_upload = st.tabs(["▶️  Run a demo case", "📤  Upload your own case"])

with tab_demo:
    cases = load_cases()
    labels = [f"{c['case_id']} ({c['cancer_type']})" for c in cases]
    choice = st.selectbox("Choose a synthetic case", labels)
    selected = cases[labels.index(choice)]
    with st.expander("View raw case data"):
        st.json(selected)
    if st.button("Convene tumor board", type="primary", key="demo_run"):
        run_and_render(Case(**selected))

with tab_upload:
    st.markdown(
        "Upload a **`.json`**, **`.csv`**, or **`.txt`** file describing one or more "
        "cases. See the format guide below before uploading."
    )

    with st.expander("📄  Input format guide & conversion notes", expanded=False):
        st.markdown(
            """
**All fields are optional except that a case is only as good as the data you give it.**
Missing fields simply make the relevant specialist agent fall back to
"insufficient evidence" — which is realistic behavior, not a crash.

**Fields**

| Field | Meaning | Example |
|---|---|---|
| `case_id` | any identifier | `"case-042"` |
| `cancer_type` | tumor type | `"lung"` |
| `stage` | optional stage text | `"IV (metastatic)"` |
| `imaging_findings` | free-text radiology summary | `"Stable disease, no new lesions."` |
| `pathology_findings` | free-text pathology / biomarkers | `"Adenocarcinoma, HER2 positive (3+)"` |
| `genomic_findings` | list of molecular findings | `["EGFR exon 19 deletion"]` |
| `performance_status` | ECOG status | `"ECOG 1"` |
| `comorbidities` | list | `["hypertension"]` |
| `patient_preferences` | stated goals | `"Prefers comfort-focused care"` |

**1. JSON** (native format) — a single object or a list:
```json
[{"case_id": "case-042", "cancer_type": "lung",
  "imaging_findings": "Stable disease, no new lesions.",
  "pathology_findings": "Adenocarcinoma. EGFR exon 19 deletion on NGS.",
  "genomic_findings": ["EGFR exon 19 deletion"],
  "patient_factors": {"performance_status": "ECOG 1",
                       "comorbidities": [],
                       "patient_preferences": "Wants effective treatment"}}]
```

**2. CSV** — one row per case. Use `;` to separate multiple genomic findings
or comorbidities in a single cell. Columns:
`case_id, cancer_type, stage, imaging_findings, pathology_findings,
genomic_findings, performance_status, comorbidities, patient_preferences`
```
case_id,cancer_type,imaging_findings,pathology_findings,genomic_findings,performance_status
c1,breast,stable no new lesions,HER2 positive 3+,HER2 amplification,ECOG 1
```

**3. Plain text (`.txt`)** — a free-text clinical vignette. A lightweight,
rule-based converter extracts the fields for you (cancer type, ECOG status,
listed biomarkers, and imaging/pathology/preference sentences). Separate
multiple vignettes with a line containing only `---`. This path is
best-effort and will tell you what it could and couldn't parse, so review
the extracted case before trusting it.

> **Conversion tips:** if your source is a PDF or Word document, copy the
> relevant text into a `.txt` file first. If you have an EHR/FHIR export,
> map the fields you care about into the CSV columns above — the app does
> not ingest raw FHIR bundles directly in this demo.
"""
        )

    uploaded = st.file_uploader("Upload case file", type=["json", "csv", "txt"])
    if uploaded is not None:
        try:
            parsed_cases, warnings = parse_upload(uploaded.name, uploaded.getvalue())
        except CaseParseError as exc:
            st.error(f"Could not read that file: {exc}")
        else:
            st.success(f"Parsed {len(parsed_cases)} case(s) from **{uploaded.name}**.")
            for w in warnings:
                st.warning(w)

            if len(parsed_cases) > 1:
                idx = st.selectbox(
                    "Choose which uploaded case to run",
                    range(len(parsed_cases)),
                    format_func=lambda i: parsed_cases[i].case_id,
                )
            else:
                idx = 0

            chosen = parsed_cases[idx]
            with st.expander("Preview parsed case (verify before running)"):
                st.json(chosen.model_dump())

            if st.button("Convene tumor board", type="primary", key="upload_run"):
                run_and_render(chosen)
