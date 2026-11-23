# FAKE DOOR COPY (H-0031 + Addendum) · DRAFT
Doors: 1 Brand Brain, 2 Auto-posting, 3 Per-video pricing, 4 Extra variants (optional).
Honesty rules: on click, the modal says plainly it is not built yet; no fake functionality, no payment capture, no price charged. Measure clicks and waitlist joins only. Waitlist stores email only, with consent line, 90-day max retention (Assurance to confirm), deletion on request, no sharing (ADR-0013 / DATA_POLICY).
Cost line: Founder minutes ~45 (place 4 buttons on the page, hosting is Founder's tool) · tokens 0. All demand claims E0 until data. Hosting out of scope.
Common waitlist consent (under every email field): AR: نستخدم بريدك فقط لإخبارك عند الإطلاق، ونحذفه بعد 90 يومًا أو عند طلبك. / EN: We use your email only to tell you when this launches and delete it after 90 days or on request.

Metric definitions: click rate = door clicks / unique visitors who saw the door; join rate = waitlist joins / clicks. Minimum sample before reading: 100 unique visitors per door, else "no decision, keep running to 14 days; at day 14 still < 100 = inconclusive, not a kill". Visitors come from the Founder network and the prompt form; not representative (E0).

## Door 1: Brand Brain
- Button AR: خلّي الفيديوهات تحكي بأسلوب علامتي | EN: Make my videos sound like my brand
- Modal AR: "ميزة 'عقل العلامة' غير جاهزة بعد. قريبًا. سجّل بريدك لننضمك إلى قائمة الانتظار." | EN: "Brand Brain is not available yet. Coming soon. Join the waitlist."
- Confirmation AR: شكرًا، سجلناك. لم يُسحب منك أي مبلغ ولا شيء مفعّل بعد. | EN: Thanks, you're on the list. Nothing was charged and nothing is active yet.
- Threshold: GO to build if click rate >= 8 % AND join rate >= 25 % of clickers (and EXP-011 passes). NO-GO if click rate < 3 % or join rate < 10 %. Between: keep as is, rerun with better copy once.

## Door 2: Auto-posting
- Button AR: انشر تلقائيًا على حساباتي | EN: Auto-post to my accounts
- Modal AR: "النشر التلقائي غير جاهز بعد. قريبًا. سجّل بريدك للانضمام إلى قائمة الانتظار." | EN: "Auto-posting is not available yet. Coming soon. Join the waitlist."
- Confirmation AR: شكرًا، سجلناك. لا نطلب أي حساب ولا كلمة سر، ولم يُفعّل شيء. | EN: Thanks, you're on the list. We asked for no accounts or passwords and nothing is active.
- Threshold: GO to spec if click rate >= 10 % AND join rate >= 25 %. NO-GO if click rate < 4 % or join rate < 10 % (park; platform API risk not worth it).

## Door 3: Per-video pricing
- Reference only: AdKraft lists optional ad packs of 5 ads for $15 (about $3/ad), see COMPETITORS.md. We do not copy it; this door tests our own anchor.
- Test design: no price is charged or captured. Visitors see one price shown as a question, random split between two anchors (Founder confirms the numbers before launch; UNIT_ECONOMICS sets the floor): Anchor A "pay per exported video", Anchor B "monthly bundle". Product proposes initial anchor values after reading UNIT_ECONOMICS; here they are placeholders marked [X].
- Button AR: كم تدفع للفيديو؟ جرّب السعر [X] لكل فيديو | EN: See per-video pricing: [X] per video
- Modal AR: "لم نبدأ البيع بعد، والسعر لم يُحدَّد نهائيًا. هل هذا السعر يناسبك؟ سجّل بريدك لنخبرك عند الإطلاق. لن يُسحب منك أي مبلغ." | EN: "We are not selling yet and the price is not final. Does this price work for you? Join the waitlist and we'll tell you at launch. Nothing will be charged."
- Confirmation AR: شكرًا، سجلناك ولم تدفع شيئًا. | EN: Thanks, you're on the list and you paid nothing.
- Threshold: pricing signal PASS if click rate >= 10 % AND join rate >= 30 % at the anchor. FAIL if join rate < 12 % (anchor too high or value unclear; revise once). This is a stated-interest signal, not willingness to pay (E0).

## Door 4 (optional): Extra variants
- Button AR: أنشئ 3 نسخ مختلفة من الفيديو نفسه | EN: Generate 3 different versions of the same video
- Modal AR: "النسخ الإضافية غير جاهزة بعد. قريبًا. سجّل بريدك للانضمام إلى قائمة الانتظار." | EN: "Extra versions are not available yet. Coming soon. Join the waitlist."
- Confirmation AR: شكرًا، سجلناك ولم يُفعّل شيء. | EN: Thanks, you're on the list and nothing is active.
- Threshold: GO if click rate >= 8 % AND join rate >= 25 %; NO-GO if click rate < 3 %.

## Kill rule across doors
A door under its NO-GO threshold at >= 100 visitors is removed from the roadmap backlog; honoured even if it was championed. No door may cause a build before the M1 exit criteria are met.
