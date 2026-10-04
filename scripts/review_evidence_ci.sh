#!/usr/bin/env bash
# Consumer-repository helper. Evaluation and conversion happen before this script.
set -u -o pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo 'Usage: bash review_evidence_ci.sh PROJECT ARTIFACT_DIR [EVAL_EXIT] [EXPORT_EXIT]' >&2
  exit 2
fi
project=$1
artifacts=$2
eval_exit=${3-0}
export_exit=${4-0}
for status in "$eval_exit" "$export_exit"; do
  if [[ ! $status =~ ^(0|[1-9][0-9]{0,2})$ ]] || (( status > 255 )); then
    echo 'Upstream exit codes must be integers from 0 to 255.' >&2
    exit 2
  fi
done
mkdir -p "$artifacts" || exit 1
status_file="$artifacts/review-status.txt"
printf 'eval_exit=%s\nexport_exit=%s\n' "$eval_exit" "$export_exit" > "$status_file" || exit 1

if (( eval_exit != 0 || export_exit != 0 )); then
  printf 'gate_status=failed\nreview=skipped_due_to_upstream_failure\n' >> "$status_file"
  cat "$status_file"
  if [[ -n ${GITHUB_STEP_SUMMARY:-} ]]; then
    printf '### OpenEvalGate evidence review failed\n\nEvaluation or conversion failed. Review was skipped; inspect the uploaded logs.\n' >> "$GITHUB_STEP_SUMMARY"
  fi
  exit 1
fi

# Keep diagnostics even if structural validation fails or the report is blocked.
openevalgate check "$project" --format json > "$artifacts/check.json" 2> "$artifacts/check.stderr.log"
check_exit=$?
openevalgate report "$project" --format json --fail-on-blocked > "$artifacts/report.json" 2> "$artifacts/report.stderr.log"
report_exit=$?
openevalgate report "$project" --format card --fail-on-blocked 2> "$artifacts/card.stderr.log" | tee "$artifacts/decision-card.md"
card_pipeline=("${PIPESTATUS[@]}")
card_exit=${card_pipeline[0]}
tee_exit=${card_pipeline[1]}

printf 'check_exit=%s\nreport_exit=%s\ncard_exit=%s\ntee_exit=%s\n' \
  "$check_exit" "$report_exit" "$card_exit" "$tee_exit" >> "$status_file" || exit 1
gate_exit=0
if (( check_exit != 0 || report_exit != 0 || card_exit != 0 || tee_exit != 0 )); then
  gate_exit=1
fi
if (( gate_exit == 0 )); then
  printf 'gate_status=passed\n' >> "$status_file" || exit 1
else
  printf 'gate_status=failed\n' >> "$status_file" || exit 1
fi
if [[ -n ${GITHUB_STEP_SUMMARY:-} ]]; then
  {
    printf '### OpenEvalGate evidence review\n\n'
    cat "$status_file"
    printf '\n'
    cat "$artifacts/decision-card.md"
  } >> "$GITHUB_STEP_SUMMARY" || exit 1
fi
exit "$gate_exit"
