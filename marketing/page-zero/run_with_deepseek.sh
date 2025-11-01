#!/bin/bash
export DEEPSEEK_API_KEY="sk-c2b06f3ae3c442de82f4e529bcce71ed"
echo "all" | python3 weighted_multi_agent_finder.py 2>&1 | tee deepseek-8agent-full-execution.log
