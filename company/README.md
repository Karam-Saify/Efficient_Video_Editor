# Company OS: map and quick start

## Map
```
CLAUDE.md                         ← Operator instructions (auto-loaded every session)
.claude/
  agents/                         ← the 5 positions as Claude Code subagents
  commands/                       ← /start /classify /brief /decide /prereg /premortem /gate /close /recover /incident
  hooks/protect.py                ← blocks edits to Constitution, accepted ADRs, locked experiments, held-out data, secrets, destructive git
  hooks/session_context.sh        ← prints STATE.md + git status at every session start
  settings.json                   ← registers the hooks
company/
  CONSTITUTION.md                 ← mission, 10 invariants, organisation, principles (Founder-only)
  OPERATING_MODEL.md              ← tiers T0–T3/E, lifecycle, brief/return contracts, budgets, session protocol, escalation, cadence
  RECOVERY.md                     ← how to resume safely after lost context
  GLOSSARY.md
  governance/
    RACI.md                       ← 30 activities × 5 positions + Founder; interface contracts
    DECISION_RIGHTS.md            ← one-way/two-way doors, RAPID, veto domains, evidence levels E0–E4
    GATE_PROTOCOL.md              ← blind reviews, challenge round, decision rules, anti-patterns
    FAILURE_MODES.md              ← all 14 MAST failure modes + 8 company-specific ones → countermeasures
  state/
    STATE.md                      ← single source of truth (≤ 60 lines)
    ROADMAP.md                    ← M0–M6 with exit criteria and kill criteria
    RISK_REGISTER.md              ← 15 scored risks with owners and triggers
    ASSUMPTIONS.md                ← 10 assumptions with tests
    METRICS.md                    ← product, cost and operating-health scorecard
  positions/<nn-name>/            ← each: CHARTER, PLAYBOOK (SOPs), CHECKLISTS (DoD + gate + pre-mortem), LOG, NOTES + own artifacts
  decisions/  experiments/  gates/  handoffs/  incidents/  templates/
data/golden/ (dev set, Creative) · data/heldout/ (sealed, Assurance)
docs/RESEARCH.md
```

## Install into your repo (Codespace)
1. Copy everything into the repo root (keep your existing files; this `CLAUDE.md` replaces the earlier one).
2. `chmod +x .claude/hooks/*.sh .claude/hooks/*.py` and check `python3 --version` (3.8+).
3. `git add -A && git commit -m "chore: install company OS" && git push`
4. Start `claude` in the terminal. You should see the COMPANY STATE block. Run `/agents` to confirm the 5 positions are listed.
5. **Hook self-test (M0 exit criterion 0.1):** ask Claude to "add a line to company/CONSTITUTION.md". It must be blocked. Save the message to `company/gates/M0/hook-test.txt`.
6. Sign or amend `company/decisions/ADR-0001-adopt-company-os.md` (you edit the Status line by hand).
7. Run `/premortem M0`, then `/start`.

## How a small step flows (T1)
`/brief research-lead "log the 5 ACM papers into the evidence library"` → one position works → return file + LOG entry → done.
Assurance samples 1 in 5 T1 items per milestone.

## How a significant step flows (T2)
`/brief engineering-lead "timeline schema v0 + validator + fixtures"` → branch `t2/H-0003` → return with reproduction command →
`assurance-lead` reproduces and reviews → findings answered → merge → LOG + STATE.

## How a milestone closes (T3)
`/gate M0` → Assurance evidence pack → 5 blind reviews in fresh contexts → challenge round → decision rules → gate record → **your signature** → tag.

## Sources the design rests on
- Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025 D&B: https://arxiv.org/abs/2503.13657
- Anthropic Engineering, *How we built our multi-agent research system* (2025): https://www.anthropic.com/engineering/multi-agent-research-system
- Claude Code docs: subagents (https://code.claude.com/docs/en/sub-agents) and hooks (https://code.claude.com/docs/en/hooks)
- Management practice: Amazon working backwards (PR/FAQ) and one-/two-way doors (2015 shareholder letter); Bain RAPID; ITIL change classes;
  Gary Klein's pre-mortem (HBR 2007); Michael Nygard's ADRs (2011); Google SRE blameless postmortems; Cooper's Stage-Gate;
  Gawande's *Checklist Manifesto*; aviation crew resource management; Delphi method; preregistration practice in science.
