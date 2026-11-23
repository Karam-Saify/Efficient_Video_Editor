# PARTNER FEEDBACK FORM (one per job, ADR-0023) · owner: assurance-lead · H-0034
Version FF-v0.1 · DRAFT · Used only for partners with a signed consent kit (CK-v0.1). Not legal advice.
A job = one request from the partner, delivered as ≥ 2 versions. Part J is filled by the Operator when the job opens
and when it is delivered; Part F is filled by the partner after viewing. Versions are shown with neutral labels
(A / B), in a random order recorded by the Operator, with no hint of which is which recipe.
Storage: outside git. Only the mapped fields below (no names, no handles, no links to the partner's accounts) may
enter an annotation record, and only if the partner ticked permission 1 or 2.

## Part J: job header (Operator, with the partner's words)
| # | Field | AR (question to the partner) | EN |
|---|---|---|---|
| J1 | Brief | ماذا تريد من هذا الفيديو؟ اكتب طلبك بكلماتك. | What do you want from this video? Your request in your words. |
| J2 | Audience | لمن هذا الفيديو بالتحديد؟ | Who exactly is this video for? |
| J3 | Platform | على أي منصة ستنشره؟ (TikTok / Reels / Shorts / Snapchat / WhatsApp Status / أخرى) | Which platform will you post it on? |
| J4 | Objective | ما النتيجة التي تريدها؟ (مبيعات / متابعين / تعريف بمنتج / عرض محدود / أخرى) | What result do you want? (sales / followers / product awareness / limited offer / other) |
| J5 | Edits delivered | — (Operator: version labels, recipe IDs, timeline hashes, delivery date) | Operator only |

## Part F: feedback (partner)
| # | Field | AR | EN | Type |
|---|---|---|---|---|
| F1 | Partner choice | أي نسخة تختار؟ (A / B / ولا واحدة) | Which version do you pick? (A / B / neither) | single choice, required |
| F2 | Likes / dislikes | ما الذي أعجبك؟ وما الذي لم يعجبك؟ (في كل نسخة) | What did you like? What did you not like? (per version) | two short texts per version |
| F3 | Corrections | ماذا تغيّر قبل النشر؟ (مثال: "احذف أول 3 ثوانٍ"، "الترجمة خطأ في كلمة ...") | What would you change before posting? (e.g. "cut the first 3 s", "caption wrong on the word …") | list of free-text items |
| F4 | Would publish | هل تنشر النسخة التي اخترتها كما هي؟ (نعم كما هي / نعم بعد التعديلات / لا) | Would you post the chosen version? (yes as is / yes after my corrections / no) | single choice, required |
| F5 | Would pay | لو كانت هذه الخدمة مدفوعة، هل تدفع مقابل فيديو كهذا؟ (لا / نعم حتى 5$ / 5–15$ / أكثر من 15$) | If this were paid, would you pay for a video like this? (no / yes up to $5 / $5–15 / more than $15) | single choice; a stated intent, **not** willingness-to-pay evidence |
| F6 | Published version | (بعد النشر) هل نشرت؟ أي نسخة، وهل عدّلتها؟ أرسل الملف إن أردت. | (After posting) Did you post it? Which version, did you change it? Send the file if you wish. | follow-up, 3–7 days later; optional |

## Mapping to the ADR-0023 job fields (1:1; Engineering builds `annotation.schema.json` from this)
| ADR-0023 job field | Form field | Proposed key | Type / values | Filled by | `label_origin` |
|---|---|---|---|---|---|
| brief | J1 | `job.brief` | string, ≤ 1,000 chars | partner (via Operator) | human_verified |
| audience | J2 | `job.audience` | string, ≤ 300 chars | partner | human_verified |
| platform | J3 | `job.platform` | enum `tiktok, ig_reels, yt_shorts, snapchat, wa_status, other` | partner | human_verified |
| objective | J4 | `job.objective` | enum `sales, followers, awareness, offer, other` + optional text | partner | human_verified |
| partner's published version | F6 | `job.published_version` | object `{published: bool \| null, version_label, modified: bool \| null, file_ref \| null}` | partner | human_verified |
| likes/dislikes | F2 | `job.likes_dislikes` | object per version label `{likes: string, dislikes: string}` | partner | human_verified |
| edits delivered | J5 | `job.edits_delivered` | array `{version_label, recipe_id, timeline_sha256, delivered_on}` | Operator (machine data) | machine |
| partner choice | F1 | `job.partner_choice` | enum `A, B, …, none` + `display_order` | partner | human_verified |
| corrections | F3 | `job.corrections` | array of `{version_label, text, t_start_s \| null}` (times filled by code, not by the LLM) | partner | human_verified |
| would-publish | F4 | `job.would_publish` | enum `as_is, after_corrections, no` | partner | human_verified |
| would-pay | F5 | `job.would_pay` | enum `no, le_5, 5_15, gt_15` | partner | human_verified (stated intent) |

11 ADR fields → 11 form fields; no ADR field is unmapped and no form field is unmapped. Required admin keys on every job
record (not ADR content fields): `job_id`, `partner_id`, `rights_ids[]`, `consent_version`, `permissions
{evaluation, product_development, training_consented}` plus `training_usable`, which code keeps `false` while ADR-0020 stands,
whatever the partner ticked.
Personal data guard: free-text fields (`brief`, `audience`, `likes_dislikes`, `corrections`) are sensitive (ADR-0013)
and must be bounded in length by the schema (see H-0033 F13).
