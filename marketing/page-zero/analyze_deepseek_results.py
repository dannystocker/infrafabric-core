#!/usr/bin/env python3
"""Analyze DeepSeek run vs baseline"""

import re

# Extract weighted confidences from both runs
def extract_confidences(filename):
    confidences = []
    with open(filename, 'r') as f:
        for line in f:
            match = re.search(r'Weighted Confidence: ([\d.]+)/100', line)
            if match:
                confidences.append(float(match.group(1)))
    return confidences

# Get baseline (6-agent, no LLM)
baseline_conf = extract_confidences('real-agent-execution.log')

# Get DeepSeek run (7-agent: 6 heuristic + DeepSeek)
deepseek_conf = extract_confidences('deepseek-8agent-full-execution.log')

print("=" * 80)
print("BASELINE VS DEEPSEEK COMPARISON")
print("=" * 80)
print()

print(f"Baseline (6 agents, no LLM):")
print(f"  Contacts: {len(baseline_conf)}")
print(f"  Average confidence: {sum(baseline_conf)/len(baseline_conf):.1f}/100")
print(f"  Min: {min(baseline_conf):.1f}, Max: {max(baseline_conf):.1f}")
print()

print(f"DeepSeek Run (7 agents: 6 heuristic + DeepSeek):")
print(f"  Contacts: {len(deepseek_conf)}")
print(f"  Average confidence: {sum(deepseek_conf)/len(deepseek_conf):.1f}/100")
print(f"  Min: {min(deepseek_conf):.1f}, Max: {max(deepseek_conf):.1f}")
print()

# Calculate boost
baseline_avg = sum(baseline_conf)/len(baseline_conf)
deepseek_avg = sum(deepseek_conf)/len(deepseek_conf)
boost = deepseek_avg - baseline_avg

print(f"Boost from DeepSeek:")
print(f"  Absolute: {boost:+.1f} points")
print(f"  Relative: {(boost/baseline_avg)*100:+.1f}%")
print()

if boost > 0:
    print("✅ DeepSeek IMPROVED performance")
elif boost == 0:
    print("➡️ DeepSeek had NO EFFECT")
else:
    print("❌ DeepSeek DECREASED performance")
print()

# Extract DeepSeek contribution counts
with open('deepseek-8agent-full-execution.log', 'r') as f:
    content = f.read()
    deepseek_mentions = content.count('DeepSeekCodeAgent       : confidence=')
    print(f"DeepSeek contributed to: {deepseek_mentions}/84 contacts")

# Check average DeepSeek confidence when it contributed
deepseek_confidences = []
with open('deepseek-8agent-full-execution.log', 'r') as f:
    for line in f:
        match = re.search(r'DeepSeekCodeAgent\s+: confidence=\s*(\d+)', line)
        if match:
            deepseek_confidences.append(int(match.group(1)))

if deepseek_confidences:
    print(f"DeepSeek average confidence when contributing: {sum(deepseek_confidences)/len(deepseek_confidences):.1f}/100")

