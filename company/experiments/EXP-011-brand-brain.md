# EXP-011: Brand Brain blind A/B (brand-tuned vs generic)
- **Lock:** DRAFT  <!-- not locked; research-lead reviews and signs later; Assurance locks -->
- **Owner:** research-lead (draft by product-lead, H-0031) · **Milestone:** M1 · **Linked assumption(s):** TBD by research-lead (Brand Brain value) · **Decision it feeds:** build Brand Brain (ADR-0007 Creative Director) or drop it

## 0. Decision brief (ADR-0012)
- **Recommendation:** Do not build Brand Brain until this test passes. Run a manual (Founder-operated, prompt-only) version first.
- **Reasoning:** Brand-specific tuning is plausible value for P3 (small business) but is E0: no data. A cheap blind test separates "feels branded" from "is better".
- **First experiment:** 3 businesses x 5 posts, blind A/B: A = brand-tuned (brand notes in the prompt), B = generic. 15 pairs.
- **Success threshold (numeric):** brand-tuned preferred in >= 11 of 15 pairs (>= 73 %) AND preferred for >= 2 of 3 businesses by the owner's own blind pick.
- **If it fails, then:** (<= 8 of 15) kill Brand Brain as a build item, drop it from the roadmap and keep generic recipes. (9-10 of 15) one revision of the brand notes, one rerun, then decide. No third run.

## 1. Question
Does adding a business's brand notes (tone, vocabulary, colours, do/don't) to the edit request produce Shorts that the business owner prefers over generic output?
## 2. Hypothesis (falsifiable)
H1: brand-tuned wins >= 73 % of blind pairs. H0: win rate <= 50 % (no preference).
## 3. Variables
- Independent: brand notes present (A) vs absent (B).
- Dependent: pick rate of A = A-picks / total pairs, per business and overall; secondary: owner's one-line reason (code-switched, kept).
- Controlled: same source clip/post brief, same model and version, same recipe set, same render settings, same length (30-60 s), randomised A/B position, seed logged.
## 4. Dataset
3 businesses (>= 1 Arabic-speaking small business; P3-like) x 5 posts = 15 pairs. Business footage/briefs are the businesses' own; not golden-set; no held-out use. Business selection is by the Founder's network (ADR scope: no cold contact in this brief).
## 5. Procedure
1. Founder approves the consent tool and text (below). No business data is touched before that.
2. Per business: the owner signs `company/positions/05-assurance/CONSENT_KIT.md` (CK-v0.1) and fills the per-clip rights table of `PARTNER_INTAKE_FORM.md` §C. Assurance records one DATA_RIGHTS row per clip (I-9) before any clip is touched. Then collect a brand note (<= 150 words) and 5 post briefs/clips.
3. Generate A and B per post with the same pipeline; Engineering strips metadata; Creative randomises positions and keeps the key sealed.
4. Each owner views 5 pairs blind and picks one + a one-line reason; Creative also rates quality blind (Arabic correctness gate must pass for both arms; failures excluded and counted).
5. Unseal, tally, report per business and overall.
## 6. Metrics and thresholds (set NOW, never changed after)
| Metric | Pass | Kill |
|---|---|---|
| Brand-tuned pick rate (15 pairs) | >= 11/15 and >= 2 of 3 businesses | <= 8/15 |
| Arabic quality gate failures | <= 2 of 30 videos | > 5 of 30 |
| Cost per pair (tokens + compute) | <= $0.50 | > $2.00 |
Between thresholds: the "if it fails" rule revise-once applies.
## 7. Analysis plan
Exact binomial test vs 0.5 (n=15: 11/15 gives one-sided p ~0.06; accepted as a go/no-go screen, not proof). Declared small-n, E1 evidence at best. Ties are re-asked once; still tied = counted as not preferred. Excluded pairs reported.
## 8. Threats to validity
Internal: owners guess which arm is branded (mitigate: identical render, no watermarks, randomised order). Demand effect: owners favour output with their own notes (mitigate: ask "which would you post", not "which is better"). External: 3 friendly businesses, n=15; not generalisable (E0 for market). Construct: pick rate is not willingness to pay (use the fake door for that).
## 9. Budget
Founder minutes ~90 (recruit, consent, relay picks). Tokens <= 150k. Compute <= 30 CPU min. Tool calls <= 40. Personal data: brand notes, clips and picks are sensitive (ADR-0013); consent text covers purpose, 90-day max retention, deletion on request, no training; copy in `PROMPT_COLLECTION_FORM.md` consent block adapted. Escalate if any step needs real business data before Founder approves tool and consent.
## 10. Roles
Research (design/analysis, lock) · Engineering (identical pipelines, metadata strip) · Creative (blinding, Arabic quality rating) · Assurance (lock + consent check) · Product (this draft, go/no-go on the roadmap).

### Consent (AR / EN, short form for businesses)
AR: نستخدم ملاحظات علامتك وفيديوهاتك فقط لهذا الاختبار، ولا ندرّب نماذج عليها. تُعالج على GitHub Codespaces (Microsoft)، وقد يقرأ Claude من Anthropic النص المنطوق وصورًا ثابتة قليلة منها، لا الفيديو كاملًا. لا نعطيها لأي جهة أخرى. تؤكد أن المقاطع ملكك أو لديك إذن باستعمالها، وأن كل شخص يظهر فيها وافق، ولا يظهر فيها أطفال دون 18 سنة. نحذفها بعد 90 يومًا كحدّ أقصى من تاريخ استلامها، أو خلال 7 أيام عند طلبك: أرسل «احذف» مع رمزك عبر واتساب أو الرسائل الخاصة. لا يبقى بعدها إلا أرقام إجمالية مجهولة. المشاركة اختيارية. النص الكامل: CONSENT_KIT.md.
EN: We use your brand notes and clips only for this test and do not train models on them. They are processed on GitHub Codespaces (Microsoft), and Claude by Anthropic may read the spoken text and a few still frames, never the full video. We give them to no one else. You confirm the clips are yours or you have permission, that everyone shown in them agreed, and that no children under 18 appear. We delete them at most 90 days after we receive them, or within 7 days if you ask: send "DELETE" with your code on WhatsApp or DM. Only anonymous totals remain. Taking part is optional. Full text: CONSENT_KIT.md.
(H-0034 fast-lane patch by assurance-lead for H-0033 F1-F3. EXP-011 is DRAFT; Assurance checks this again at lock.)
