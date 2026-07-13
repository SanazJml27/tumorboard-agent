"""
Framework landscape figure for TumorBoard-Agent.

Mirrors the three-band conceptual structure common in agentic-healthcare
survey figures (Perception -> Agent Capabilities -> Application Ecosystem),
but every box is populated with a component that actually exists in THIS
repository. It's a "where does my project sit in the field" figure -- useful
at the top of the README and as a portfolio talking point.

Rendered to a static PNG/SVG by scripts/render_figures.py.
"""

LANDSCAPE_SVG = """
<svg viewBox="0 0 1180 700" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, Segoe UI, Roboto, sans-serif">
  <defs>
    <marker id="fig-arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L7,3 L0,6 Z" fill="#5b6b82"/>
    </marker>
  </defs>

  <rect x="0" y="0" width="1180" height="700" fill="#ffffff"/>

  <!-- ============ BAND 1: PERCEPTION (inputs) ============ -->
  <rect x="24" y="24" width="300" height="652" rx="14" fill="#f4f6f9" stroke="#dbe2ec"/>
  <rect x="44" y="40" width="260" height="40" rx="9" fill="#eceff4" stroke="#cfd8e3"/>
  <text x="174" y="66" text-anchor="middle" font-size="19" font-weight="700" fill="#1f2d3d">Perception (Inputs)</text>
  <text x="174" y="96" text-anchor="middle" font-size="11.5" fill="#6b7a90" font-style="italic">the structured case fields the panel reasons over</text>

  <g font-size="13" fill="#22303f">
    <rect x="44" y="120" width="260" height="86" rx="10" fill="#fff" stroke="#cbd6e4"/>
    <text x="60" y="144" font-size="14" font-weight="700" fill="#1f3a5f">Imaging findings</text>
    <text x="60" y="166" font-size="11.5" fill="#5b6b82">radiology summary text</text>
    <text x="60" y="184" font-size="11.5" fill="#5b6b82">(stable / progression / equivocal)</text>

    <rect x="44" y="218" width="260" height="86" rx="10" fill="#fff" stroke="#cbd6e4"/>
    <text x="60" y="242" font-size="14" font-weight="700" fill="#1f3a5f">Pathology findings</text>
    <text x="60" y="264" font-size="11.5" fill="#5b6b82">histology · receptor status ·</text>
    <text x="60" y="282" font-size="11.5" fill="#5b6b82">biomarker report text</text>

    <rect x="44" y="316" width="260" height="86" rx="10" fill="#fff" stroke="#cbd6e4"/>
    <text x="60" y="340" font-size="14" font-weight="700" fill="#1f3a5f">Genomic findings</text>
    <text x="60" y="362" font-size="11.5" fill="#5b6b82">EGFR · ALK · HER2 · BRCA ·</text>
    <text x="60" y="380" font-size="11.5" fill="#5b6b82">KRAS G12C · MSI-H · TMB · PD-L1</text>

    <rect x="44" y="414" width="260" height="86" rx="10" fill="#fff" stroke="#cbd6e4"/>
    <text x="60" y="438" font-size="14" font-weight="700" fill="#1f3a5f">Patient factors</text>
    <text x="60" y="460" font-size="11.5" fill="#5b6b82">ECOG performance status ·</text>
    <text x="60" y="478" font-size="11.5" fill="#5b6b82">comorbidities · stated preferences</text>

    <rect x="44" y="512" width="260" height="120" rx="10" fill="#eef4fb" stroke="#bcd0e8"/>
    <text x="60" y="536" font-size="14" font-weight="700" fill="#1f3a5f">Ingestion formats</text>
    <text x="60" y="558" font-size="11.5" fill="#5b6b82">JSON (native schema)</text>
    <text x="60" y="577" font-size="11.5" fill="#5b6b82">CSV (one row per case)</text>
    <text x="60" y="596" font-size="11.5" fill="#5b6b82">Free-text vignette → rule-based</text>
    <text x="60" y="614" font-size="11.5" fill="#5b6b82">field extraction (best-effort)</text>
  </g>

  <!-- ============ BAND 2: AGENT CAPABILITIES ============ -->
  <rect x="344" y="24" width="812" height="384" rx="14" fill="#f4f6f9" stroke="#dbe2ec"/>
  <rect x="364" y="40" width="772" height="40" rx="9" fill="#eceff4" stroke="#cfd8e3"/>
  <text x="750" y="66" text-anchor="middle" font-size="19" font-weight="700" fill="#1f2d3d">Agent Capabilities</text>

  <!-- Specialist panel -->
  <text x="380" y="108" font-size="15" font-weight="700" fill="#1f2d3d">Role-Specialized Panel</text>
  <g font-size="11.5">
    <rect x="380" y="120" width="150" height="40" rx="8" fill="#eef4fb" stroke="#9db6d6"/>
    <text x="455" y="145" text-anchor="middle" font-weight="600" fill="#1f3a5f">Medical Oncologist</text>
    <rect x="380" y="168" width="150" height="40" rx="8" fill="#eef4fb" stroke="#9db6d6"/>
    <text x="455" y="193" text-anchor="middle" font-weight="600" fill="#1f3a5f">Radiologist</text>
    <rect x="380" y="216" width="150" height="40" rx="8" fill="#eef4fb" stroke="#9db6d6"/>
    <text x="455" y="241" text-anchor="middle" font-weight="600" fill="#1f3a5f">Pathologist</text>
    <rect x="380" y="264" width="150" height="40" rx="8" fill="#eef4fb" stroke="#9db6d6"/>
    <text x="455" y="289" text-anchor="middle" font-weight="600" fill="#1f3a5f">Genomics / Molecular</text>
    <rect x="380" y="312" width="150" height="40" rx="8" fill="#eef4fb" stroke="#9db6d6"/>
    <text x="455" y="337" text-anchor="middle" font-weight="600" fill="#1f3a5f">Nurse Navigator</text>
  </g>
  <text x="455" y="372" text-anchor="middle" font-size="10.5" fill="#6b7a90" font-style="italic">deterministic domain logic per agent</text>

  <!-- Planning & reasoning -->
  <text x="558" y="108" font-size="15" font-weight="700" fill="#1f2d3d">Planning &amp; Reasoning</text>
  <g font-size="11">
    <rect x="558" y="120" width="128" height="52" rx="8" fill="#fff" stroke="#cbd6e4"/>
    <text x="622" y="142" text-anchor="middle" font-weight="600" fill="#22303f">Independent</text>
    <text x="622" y="158" text-anchor="middle" fill="#5b6b82">opinion + confidence</text>

    <rect x="558" y="182" width="128" height="52" rx="8" fill="#fff" stroke="#cbd6e4"/>
    <text x="622" y="204" text-anchor="middle" font-weight="600" fill="#22303f">Evidence citation</text>
    <text x="622" y="220" text-anchor="middle" fill="#5b6b82">(RAG over KB)</text>

    <rect x="558" y="244" width="128" height="52" rx="8" fill="#fff" stroke="#cbd6e4"/>
    <text x="622" y="266" text-anchor="middle" font-weight="600" fill="#22303f">Bounded revision</text>
    <text x="622" y="282" text-anchor="middle" fill="#5b6b82">on challenge</text>

    <rect x="558" y="306" width="128" height="60" rx="8" fill="#fff" stroke="#cbd6e4"/>
    <text x="622" y="330" text-anchor="middle" font-weight="600" fill="#22303f">Confidence-aware</text>
    <text x="622" y="346" text-anchor="middle" fill="#5b6b82">consensus scoring</text>
  </g>

  <!-- Governance / collaboration -->
  <text x="714" y="108" font-size="15" font-weight="700" fill="#1f2d3d">Orchestration &amp; Governance</text>
  <g>
    <rect x="714" y="120" width="424" height="56" rx="9" fill="#e7f1ec" stroke="#8dbfa9"/>
    <text x="730" y="143" font-size="13.5" font-weight="700" fill="#2e6b57">Moderator (Chair)</text>
    <text x="730" y="163" font-size="11" fill="#4a6b5d">aggregates opinions · scores agreement · finalizes consensus</text>

    <rect x="714" y="186" width="424" height="56" rx="9" fill="#f6e9dc" stroke="#cE9a6a"/>
    <text x="730" y="209" font-size="13.5" font-weight="700" fill="#b5651d">🐟 Catfish Agent — anti-groupthink</text>
    <text x="730" y="229" font-size="11" fill="#8a5a2b">challenges consensus only on a real, rule-detected counter-signal</text>

    <rect x="714" y="252" width="424" height="56" rx="9" fill="#efe7f5" stroke="#a98cc4"/>
    <text x="730" y="275" font-size="13.5" font-weight="700" fill="#5a3d7a">Tiered Oversight</text>
    <text x="730" y="295" font-size="11" fill="#6b5487">auto-finalize · senior review · urgent escalation</text>

    <rect x="714" y="318" width="424" height="48" rx="9" fill="#eef2f7" stroke="#c2cfdf"/>
    <text x="730" y="339" font-size="12.5" font-weight="700" fill="#1f3a5f">Explainability</text>
    <text x="730" y="356" font-size="11" fill="#5b6b82">full step-by-step agent trace · pluggable LLM (prose only)</text>
  </g>

  <!-- ============ BAND 3: APPLICATION / OUTPUT ============ -->
  <rect x="344" y="424" width="812" height="252" rx="14" fill="#f4f6f9" stroke="#dbe2ec"/>
  <rect x="364" y="440" width="772" height="40" rx="9" fill="#eceff4" stroke="#cfd8e3"/>
  <text x="750" y="466" text-anchor="middle" font-size="19" font-weight="700" fill="#1f2d3d">Application / Output</text>

  <text x="380" y="506" font-size="14" font-weight="700" fill="#1f2d3d">Recommendation categories</text>
  <g font-size="11.5">
    <rect x="380" y="518" width="230" height="34" rx="7" fill="#fff" stroke="#cbd6e4"/>
    <text x="495" y="540" text-anchor="middle" fill="#22303f">Continue current therapy</text>
    <rect x="380" y="558" width="230" height="34" rx="7" fill="#fff" stroke="#cbd6e4"/>
    <text x="495" y="580" text-anchor="middle" fill="#22303f">Targeted therapy</text>
    <rect x="380" y="598" width="230" height="34" rx="7" fill="#fff" stroke="#cbd6e4"/>
    <text x="495" y="620" text-anchor="middle" fill="#22303f">Immunotherapy</text>
    <rect x="626" y="518" width="230" height="34" rx="7" fill="#fff" stroke="#cbd6e4"/>
    <text x="741" y="540" text-anchor="middle" fill="#22303f">Clinical trial</text>
    <rect x="626" y="558" width="230" height="34" rx="7" fill="#fff" stroke="#cbd6e4"/>
    <text x="741" y="580" text-anchor="middle" fill="#22303f">Palliative / supportive care</text>
    <rect x="626" y="598" width="230" height="34" rx="7" fill="#fff" stroke="#cbd6e4"/>
    <text x="741" y="620" text-anchor="middle" fill="#22303f">Insufficient evidence</text>
  </g>

  <text x="884" y="506" font-size="14" font-weight="700" fill="#1f2d3d">Delivered as</text>
  <g font-size="11.5">
    <rect x="884" y="518" width="254" height="52" rx="8" fill="#eef4fb" stroke="#bcd0e8"/>
    <text x="900" y="540" font-weight="600" fill="#1f3a5f">Tumor board report</text>
    <text x="900" y="559" fill="#5b6b82">consensus · confidence · dissent · tier</text>

    <rect x="884" y="580" width="254" height="52" rx="8" fill="#eef4fb" stroke="#bcd0e8"/>
    <text x="900" y="602" font-weight="600" fill="#1f3a5f">Reproducible evaluation</text>
    <text x="900" y="621" fill="#5b6b82">recommendation · tier · catfish calibration</text>
  </g>

  <!-- flow arrows between bands -->
  <line x1="324" y1="350" x2="342" y2="350" stroke="#5b6b82" stroke-width="1.8" marker-end="url(#fig-arrow)"/>
  <line x1="750" y1="408" x2="750" y2="422" stroke="#5b6b82" stroke-width="1.8" marker-end="url(#fig-arrow)"/>
</svg>
"""
