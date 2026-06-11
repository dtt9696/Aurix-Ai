# Iterative Refinement & Deep-Dive Workflow

## 1. Decision Recommendation Logic (决策建议)
The agent must categorize recommendations based on the risk profile:
- **Financial**: Restructure debt, hedge currency, adjust credit terms.
- **Legal/Compliance**: Update AML/KYC protocols, reserve litigation funds, exit high-risk markets.
- **Human Capital**: Succession planning, talent retention bonuses, visa strategy adjustment.
- **Supply Chain**: Diversify supplier base, increase safety stock, vertical integration.

## 2. Interactive Refinement (报告修订)
Users can provide natural language feedback (e.g., "Focus more on the litigation risk in California" or "Summarize the financial section for a non-technical board").
- **Action**: The agent re-runs the specific analysis module with the new focus and patches the HTML report.

## 3. Deep-Dive Analysis (深入挖掘)
When a user asks to "dig deeper" into a specific finding (e.g., "Tell me more about the plaintiff in that lawsuit"):
1. **Identify**: Isolate the specific entity or event.
2. **Search**: Run targeted MCP queries (CourtListener dockets, Google Search for plaintiff background).
3. **Synthesize**: Append a "Deep Dive Supplement" to the report.

## 4. Customization via Natural Language
Users can define their "Risk Appetite" (e.g., "I am highly risk-averse, give me conservative recommendations"). The agent adjusts the threshold logic and tone accordingly.
