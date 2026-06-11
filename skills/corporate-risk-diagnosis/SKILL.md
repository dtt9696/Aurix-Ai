---
name: corporate-risk-diagnosis
description: Comprehensive US corporate risk diagnosis and report generation. Use when a user provides a company name (CN/EN) and needs a deep-dive risk analysis report with data grounding and HTML rendering.
---

# Corporate Risk Diagnosis Skill

This skill guides the agent through the end-to-end process of corporate risk diagnosis for US companies.

## Workflow

1.  **Entity Resolution**: Use `google_search` to map fuzzy names (e.g., "Nvidia") to official US legal names and tickers (e.g., "NVIDIA Corporation (NVDA)").
2.  **Multidimensional Data Collection**: Refer to [references/risk_domains.md](references/risk_domains.md) for data sources and metrics.
3.  **Automated Audit**: 
    *   Compare the retrieved financial metrics against the generated conclusions.
    *   Verify the company against OFAC sanctions lists.
    *   Check for significant pending litigation via CourtListener.
4.  **Rich HTML Report Generation**:
    *   Produce a self-contained HTML document.
    *   Use a professional deep-blue palette.
    *   Include a "Verification Log" with source citations.

## Guidelines

- **Grounding**: Never state a risk without a specific data point (e.g., " Altman Z-Score of 1.43 indicates high bankruptcy risk").
- **Language**: Always accept Chinese or English input, but output the technical data accurately based on US sources.
- **Traceability**: Every conclusion must link back to a specific tool output.
