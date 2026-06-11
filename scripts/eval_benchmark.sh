#!/bin/bash
# eval_benchmark.sh - Automating Agent Evaluation & Comparison

set -e

echo "🚀 Starting Hackathon Evaluation Benchmark..."

# 1. Run Evaluation on the baseline (or optimized) agent
echo "📊 Running evaluation on iRobot risk scenarios..."
agents-cli eval run \
  --dataset tests/eval/datasets/irobot_risk_scenarios.jsonl \
  --config tests/eval/eval_config.yaml \
  --output tests/eval/results/latest_eval.json

# 2. Grade the results
echo "💯 Grading evaluation results..."
agents-cli eval grade \
  --results tests/eval/results/latest_eval.json \
  --config tests/eval/eval_config.yaml \
  --output tests/eval/results/latest_graded.json

# 3. (Optional) Compare with a previous baseline
if [ -f "tests/eval/results/baseline_graded.json" ]; then
  echo "⚖️ Comparing current results with baseline..."
  agents-cli eval compare \
    --base tests/eval/results/baseline_graded.json \
    --candidate tests/eval/results/latest_graded.json \
    --output tests/eval/results/comparison_report.md
  echo "✅ Comparison report generated at tests/eval/results/comparison_report.md"
else
  echo "ℹ️ No baseline found. Saving current results as baseline for future comparisons."
  cp tests/eval/results/latest_graded.json tests/eval/results/baseline_graded.json
fi

echo "🏁 Benchmark complete. View results in tests/eval/results/"
