"""
Inline SVG architecture diagram for the Streamlit header.

Kept as a Python string (rather than a static asset) so the app stays a
single-file deploy with no image dependencies. Colors use a restrained
clinical palette.
"""

AGENT_DIAGRAM_SVG = """
<svg viewBox="0 0 900 470" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, Segoe UI, Roboto, sans-serif">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L8,3 L0,6 Z" fill="#7a8aa0"/>
    </marker>
    <linearGradient id="specGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#eef4fb"/>
      <stop offset="100%" stop-color="#dbe7f5"/>
    </linearGradient>
  </defs>

  <!-- Case input -->
  <rect x="330" y="12" width="240" height="46" rx="10" fill="#1f3a5f"/>
  <text x="450" y="32" text-anchor="middle" fill="#fff" font-size="14" font-weight="600">CASE (structured)</text>
  <text x="450" y="48" text-anchor="middle" fill="#c9d8ec" font-size="10.5">imaging · pathology · genomics · patient factors</text>

  <!-- Specialist agents row -->
  <g>
    <rect x="20"  y="100" width="160" height="60" rx="10" fill="url(#specGrad)" stroke="#9db6d6"/>
    <text x="100" y="126" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f3a5f">Medical</text>
    <text x="100" y="142" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f3a5f">Oncologist</text>

    <rect x="196" y="100" width="150" height="60" rx="10" fill="url(#specGrad)" stroke="#9db6d6"/>
    <text x="271" y="134" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f3a5f">Radiologist</text>

    <rect x="362" y="100" width="150" height="60" rx="10" fill="url(#specGrad)" stroke="#9db6d6"/>
    <text x="437" y="134" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f3a5f">Pathologist</text>

    <rect x="528" y="100" width="160" height="60" rx="10" fill="url(#specGrad)" stroke="#9db6d6"/>
    <text x="608" y="126" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f3a5f">Genomics /</text>
    <text x="608" y="142" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f3a5f">Molecular</text>

    <rect x="704" y="100" width="176" height="60" rx="10" fill="url(#specGrad)" stroke="#9db6d6"/>
    <text x="792" y="126" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f3a5f">Nurse</text>
    <text x="792" y="142" text-anchor="middle" font-size="12.5" font-weight="600" fill="#1f3a5f">Navigator</text>
  </g>
  <text x="450" y="180" text-anchor="middle" font-size="10.5" fill="#6b7a90" font-style="italic">each agent reasons over its own slice with deterministic domain logic</text>

  <!-- Moderator -->
  <rect x="345" y="205" width="210" height="46" rx="10" fill="#2e6b57"/>
  <text x="450" y="227" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">Moderator (Chair)</text>
  <text x="450" y="243" text-anchor="middle" fill="#cfe6dc" font-size="10">aggregates · scores agreement</text>

  <!-- Catfish -->
  <rect x="345" y="278" width="210" height="52" rx="10" fill="#b5651d"/>
  <text x="450" y="300" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">🐟 Catfish Agent</text>
  <text x="450" y="316" text-anchor="middle" fill="#f3e0cf" font-size="10">challenges consensus only on a real counter-signal</text>

  <!-- revise loop label -->
  <path d="M560 304 C 660 304, 690 150, 700 132" fill="none" stroke="#b5651d" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#arrow)"/>
  <text x="678" y="245" text-anchor="middle" font-size="9" fill="#b5651d">challenge →</text>
  <text x="678" y="257" text-anchor="middle" font-size="9" fill="#b5651d">revise (next round)</text>

  <!-- Oversight -->
  <rect x="345" y="357" width="210" height="52" rx="10" fill="#5a3d7a"/>
  <text x="450" y="379" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">Tiered Oversight</text>
  <text x="450" y="395" text-anchor="middle" fill="#e3d5f0" font-size="10">auto-finalize · senior review · urgent</text>

  <!-- Output -->
  <rect x="315" y="432" width="270" height="30" rx="8" fill="#1f3a5f"/>
  <text x="450" y="452" text-anchor="middle" fill="#fff" font-size="12" font-weight="600">Report + full agent trace</text>

  <!-- vertical arrows -->
  <line x1="450" y1="58" x2="450" y2="96" stroke="#7a8aa0" stroke-width="1.6" marker-end="url(#arrow)"/>
  <line x1="450" y1="185" x2="450" y2="203" stroke="#7a8aa0" stroke-width="1.6" marker-end="url(#arrow)"/>
  <line x1="450" y1="251" x2="450" y2="276" stroke="#7a8aa0" stroke-width="1.6" marker-end="url(#arrow)"/>
  <line x1="450" y1="330" x2="450" y2="355" stroke="#7a8aa0" stroke-width="1.6" marker-end="url(#arrow)"/>
  <line x1="450" y1="409" x2="450" y2="430" stroke="#7a8aa0" stroke-width="1.6" marker-end="url(#arrow)"/>

  <!-- fan-in lines from specialists to moderator -->
  <line x1="100" y1="160" x2="410" y2="205" stroke="#c2cfdf" stroke-width="1"/>
  <line x1="271" y1="160" x2="425" y2="205" stroke="#c2cfdf" stroke-width="1"/>
  <line x1="437" y1="160" x2="450" y2="205" stroke="#c2cfdf" stroke-width="1"/>
  <line x1="608" y1="160" x2="475" y2="205" stroke="#c2cfdf" stroke-width="1"/>
  <line x1="792" y1="160" x2="490" y2="205" stroke="#c2cfdf" stroke-width="1"/>
</svg>
"""
