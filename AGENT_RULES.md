# AGENT EXECUTION RULES (NON-NEGOTIABLE)

You MUST follow these rules:

1. You MUST NOT manually run `git commit`
2. You MUST call `scripts/agent_guard.sh` after each task
3. If guard fails:
   - Attempt fix ONCE
   - If still failing → rollback
4. You MUST update CHECKLIST.md after each task
5. You MUST STOP after PROJECT COMPLETE
6. Use bash environment to run the scripts
Violation = FAILURE
