#!/bin/bash
export OPENROUTER_API_KEY="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"
echo "all" | python3 weighted_multi_agent_finder.py 2>&1 | tee qwen-7agent-full-execution.log
