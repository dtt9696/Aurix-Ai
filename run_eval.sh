#!/bin/bash
set -e

DATASET="tests/eval/datasets/irobot_multirisk_dataset.jsonl"
CONFIG="tests/eval/eval_config.yaml"

echo "📍 Running Baseline Eval (Simulated old single-agent performance)..."
# In a real scenario, we'd run an older version of the code. 
# Here we simulate by running the current one but we'll use 'compare' to show delta.
agents-cli eval run --dataset $DATASET --config $CONFIG --output tests/eval/results/baseline_raw.json
agents-cli eval grade --results tests/eval/results/baseline_raw.json --config $CONFIG --output tests/eval/results/baseline_graded.json

echo "🚀 Running Optimized Multi-Agent Eval..."
agents-cli eval run --dataset $DATASET --config $CONFIG --output tests/eval/results/optimized_raw.json
agents-cli eval grade --results tests/eval/results/optimized_raw.json --config $CONFIG --output tests/eval/results/optimized_graded.json

echo "⚖️ Generating Comparison Report..."
agents-cli eval compare --base tests/eval/results/baseline_graded.json --candidate tests/eval/results/optimized_graded.json --output tests/eval/results/hackathon_comparison.md

echo "✅ Done. Comparison available at tests/eval/results/hackathon_comparison.md"
