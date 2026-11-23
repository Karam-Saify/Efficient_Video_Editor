# PROMPT COLLECTION FORM (content only; hosting = Founder's tool choice) · H-0031
Status: DRAFT · No collection starts until Founder picks the tool AND approves the consent block (assurance-lead reviews consent at the daily review).
Purpose of the form: collect 50 real prompts creators/businesses would type to an Arabic Shorts editor, so recipes (ADR-0008) and Creative Director (ADR-0007) are built from real language, not our guesses. Feeds M1 exit evidence; all business inferences stay E0 until real data.
Cost line: Founder minutes ~60 (pick tool, paste copy, share link) · tokens 0 · compute 0. Respondent time target: under 4 minutes.

## Target and quotas (50 valid prompts; 1 prompt = 1 respondent-written instruction)
| Slice | Quota | Persona |
|---|---|---|
| Explainer / talking-head creators | 20 | P2 |
| Small business / store owners | 20 | P3 |
| Founder-network creators and other | 10 | P1-like |
| Language of prompt: Arabic (dialect or MSA) | >= 25 | |
| Language: code-switched ar+en or ar+fr | >= 10 | ADR-0010 |
| Language: English only | <= 10 | |
Valid = consent given, prompt >= 5 words, not a duplicate. Stop at 50 valid or at 14 days, whichever first. Kill: if fewer than 20 valid after 14 days, the channel is wrong; stop and report (no extra spend).

## Consent block (show first; checkbox required to continue)
**AR:** هذا الاستبيان يجمع أمثلة عن الطلبات التي تكتبها لمحرّر فيديو ذكي، لنفهم لغتك واحتياجاتك. المشاركة لمن عمره 18 سنة أو أكثر. نحفظ إجاباتك (النص، اللغة، المجال، والبريد الإلكتروني إن أردت) ونستخدمها فقط لتصميم منتجنا، ولا نستخدمها لتدريب نماذج. تُحفظ الإجابات في **<اسم أداة الاستمارة>**، وقد نحلّلها بمساعدة Claude من شركة Anthropic. لا نبيعها ولا نعطيها لأي جهة أخرى. لا ترفع أي فيديو. تُحذف الإجابات بعد 90 يومًا كحدّ أقصى من تاريخ إرسالها، ولا يبقى بعدها إلا أرقام إجمالية مجهولة (مثل: "20 طلبًا عن الترجمة"). لطلب الحذف دون بريد إلكتروني: أرسل كلمة «احذف» مع الرمز الذي تختاره في السؤال 0 إلى **<رقم واتساب أو حساب الرسائل>**، ونحذف خلال 7 أيام. المشاركة اختيارية ويمكنك الانسحاب في أي وقت. ☐ عمري 18 سنة أو أكثر وأوافق.
**EN:** This survey collects examples of requests you would type to an AI video editor so we can understand your language and needs. It is for people aged 18 or over. We store your answers (prompt text, language, field, and your email only if you give it) and use them only to design our product; we do not train models on them. Answers are stored in **<form tool name>**, and we may analyse them with the help of Claude by Anthropic. We do not sell them or give them to anyone else. Do not upload video. Answers are deleted at most 90 days after you submit them; after that only anonymous totals remain (e.g. "20 requests about captions"). To ask for deletion without email: send "DELETE" and the code you choose in question 0 to **<WhatsApp number or DM account>**; we delete within 7 days. Taking part is optional and you can withdraw any time. ☐ I am 18 or over and I agree.
(H-0034 fast-lane patch by assurance-lead for H-0033 F1/F2. The two placeholders must be filled before publishing; Assurance re-reads the filled text. Retention: ADR-0024 (Proposed, Founder signs). Prompts are sensitive per ADR-0013.)

## Questions
| # | Field type | Required | AR | EN |
|---|---|---|---|---|
| 0 | Short text | yes | اختر رمزًا قصيرًا تتذكره (كلمة أو أرقام، ليس اسمك) لتطلب الحذف لاحقًا | Choose a short code you will remember (a word or digits, not your name) to ask for deletion later |
| 1 | Single choice | yes | ما وصفك الأقرب؟ (صانع محتوى يشرح / صاحب متجر أو نشاط / أخرى) | Which describes you best? (explainer creator / shop or business owner / other) |
| 2 | Short text | yes | ما مجال محتواك أو نشاطك؟ (مثال: رياضة، أزياء، طبخ) | What is your niche or business? (e.g. sports, fashion, cooking) |
| 3 | Single choice | yes | بأي لغة تتكلم في فيديوهاتك؟ (لهجة لبنانية / فصحى / مزيج مع إنجليزي أو فرنسي / أخرى) | What language do you speak in videos? (Lebanese dialect / MSA / mixed with English or French / other) |
| 4 | Long text (Arabic, English or mixed) | yes | اكتب كما تكتب لمحرّر ذكي: "ماذا تريد أن يفعل بفيديوك؟" مثال: "قصّلي أحسن 30 ثانية وحط ترجمة". اكتب ما شئت بلغتك. | Write what you would tell an AI editor to do with your video. Example: "cut the best 30 seconds and add captions". Write in your own language, mixing is fine. |
| 5 | Long text | optional | أضف طلبًا ثانيًا أو ثالثًا إن وُجد. | Add a second or third request if you have one. |
| 6 | Single choice | yes | كم فيديو قصير تنشر بالأسبوع؟ (0 / 1-2 / 3-5 / أكثر) | How many short videos do you post a week? (0 / 1-2 / 3-5 / more) |
| 7 | Single choice | yes | كيف تعدّل اليوم؟ (CapCut / برنامج آخر / شخص يعدّل لي / لا أعدّل) | How do you edit today? (CapCut / other tool / someone edits for me / I don't) |
| 8 | Single choice | optional | ما الأصعب؟ (القص / الترجمة العربية / الموسيقى والنص / الوقت / الكلفة) | Hardest part? (cutting / Arabic captions / music and text / time / cost) |
| 9 | Email | optional | بريدك إن أردت أن نخبرك عند الإطلاق (منفصل عن إجاباتك ويُحذف مع طلبك) | Email if you want a launch note (stored separately from answers, deleted on request) |

Rules: no name, no phone, no video upload, no platform handles. Q4 stripped of any personal detail before it enters any repo file (DATA_POLICY item 2). Raw responses stay in the Founder's chosen tool, access-controlled, never committed. **No prompt text, excerpt or paraphrase enters any repo file** (DATA_POLICY item 5, ADR-0013): `RECIPE_BACKLOG.md` gets only intent tags (cut, captions, music, text, hook, format), niche and language tags, and counts. Delete raw responses and exports at day 90 and log the date (ADR-0024).

## Success / use
Pass: 50 valid prompts with the quotas above. Output: tally of top intents (cut, captions, music, text, hook, format) as E1 evidence of demand for recipes; not evidence of willingness to pay.
