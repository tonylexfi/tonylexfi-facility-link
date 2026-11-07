#!/usr/bin/env bash
# OPENROUTER_API_KEY is required by the harness, not the plugin.
# NANOAGENT: executable path; MODEL: provider model id; RUN_DIR: new external evidence directory.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
case_name="${1:-standard}"
[[ "$case_name" == standard || "$case_name" == boundary ]] || { echo 'case must be standard or boundary' >&2; exit 2; }
: "${OPENROUTER_API_KEY:?Set OPENROUTER_API_KEY for a real model run}"
run_dir="${RUN_DIR:-$root/../runs/tonylexfi-facility-link-$(date +%Y%m%dT%H%M%S)}"
mkdir -p "$run_dir"
cat > "$run_dir/config.yaml" <<YAML
_ > nanoagent.cli.plugin.PluginOpenRouterAgentConfig:
plugin: "$root"
task: tonylexfi-facility-link
arguments: "$root/tests/examples/$case_name.json"
inputs: []
timeout: 60.0
llm > nanoagent.llm.openrouter.OpenRouterConfig:
  model: "${MODEL:-deepseek/deepseek-v4-flash}"
  max_tokens: 4096
  max_attempts: 3
  read_timeout: 120.0
  input_price: 0.0
  output_price: 0.0
  temperature: 0.0
harness > nanoagent.harness.nanoagent.NanoAgentConfig:
  max_steps: 16
  cost_limit: null
  token_limit: 24000
  context_window: null
  hooks: []
  skills: null
  context_files: []
  events: null
YAML
"${NANOAGENT:-nanoagent}" plugin agent "config=$run_dir/config.yaml" "home=$run_dir/output"
