# Evidence and quality gates

**Trigger:** Validate or reuse a previous result.

Run checks appropriate to the affected behavior, through existing project entry points. Record code state, environment, command, scope, deadline, exit code, duration, executed/pass/fail/skip counts and full-log location. Keep concise diagnostics in conversation. Reuse evidence only when state, environment, command and scope are unchanged; changes, merges, failures or skips require fresh relevant checks. Zero discovered tests are not behavioral coverage. Automated checks, environment gaps and real user/device acceptance are distinct. Indexes and generation/build success cannot replace runtime acceptance.
