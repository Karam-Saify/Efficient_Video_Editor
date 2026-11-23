# PARTNER INTAKE FORM (Founding Creator pilot, ADR-0023) · owner: assurance-lead · H-0034
Version IF-v0.1 · DRAFT · Sent together with `CONSENT_KIT.md` (CK-v0.1). Not legal advice.
Rule: no clip is touched until §C is complete for that clip **and** the consent kit is signed. Each accepted clip gets
one DATA_RIGHTS row (`RR-P<partner>-<n>`, e.g. `RR-P003-02`); that ID is the `rights_id` in the annotation record.
Storage: answers stay in the form tool / Founder storage, **outside git**. The repo receives only partner ID, clip
IDs, the rights declaration ticks and dates.

## A. Business (النشاط)
| # | Field | Req. | AR | EN |
|---|---|---|---|---|
| A1 | Short text | yes | اسم النشاط أو الصفحة | Business or page name |
| A2 | Single choice | yes | نوع النشاط (متجر / مطعم أو مقهى / خدمات / صانع محتوى / أخرى) | Type (shop / restaurant or café / services / content creator / other) |
| A3 | Short text | yes | ماذا تبيع أو تقدّم؟ (جملة واحدة) | What do you sell or offer? (one sentence) |
| A4 | Single choice | yes | البلد والمدينة الرئيسية | Main country and city |
| A5 | Short text | optional | ملاحظة عن هوية علامتك: الأسلوب، الألوان، كلمات تستعملها أو تتجنبها (150 كلمة كحد أقصى) | Brand note: style, colours, words you use or avoid (max 150 words) |

## B. Platforms and audience (المنصات والجمهور)
| # | Field | Req. | AR | EN |
|---|---|---|---|---|
| B1 | Multi choice | yes | أين تنشر؟ (TikTok / Instagram Reels / YouTube Shorts / Snapchat / WhatsApp Status / أخرى) | Where do you post? (TikTok / Instagram Reels / YouTube Shorts / Snapchat / WhatsApp Status / other) |
| B2 | Single choice | yes | كم فيديو قصير بالأسبوع؟ (0 / 1-2 / 3-5 / أكثر) | Short videos per week? (0 / 1-2 / 3-5 / more) |
| B3 | Short text | yes | من جمهورك؟ (العمر التقريبي، البلد، الاهتمام) | Who is your audience? (rough age, country, interest) |
| B4 | Single choice | yes | لغة الفيديوهات (لهجة لبنانية / لهجة أخرى / فصحى / مزيج مع إنجليزي أو فرنسي) | Video language (Lebanese dialect / other dialect / MSA / mixed with English or French) |
| B5 | Single choice | yes | ما هدفك الأول من الفيديو؟ (مبيعات / متابعين / تعريف بالمنتج / عروض) | Main goal of your videos? (sales / followers / product awareness / offers) |
| B6 | Single choice | optional | كيف تعدّل اليوم؟ (CapCut / برنامج آخر / شخص يعدّل لي / لا أعدّل) | How do you edit today? (CapCut / other / someone edits for me / I don't) |
Do not ask for follower counts, handles or analytics screenshots in v0.1 (not needed for the pilot; minimise).

## C. Footage list with a rights declaration per clip (قائمة المقاطع وحقوق كل مقطع)
One row per clip. The partner fills columns C1–C9; the Operator fills C10–C11.
| # | Column | AR | EN | Accept rule |
|---|---|---|---|---|
| C1 | Clip name | اسم الملف | File name | — |
| C2 | Raw or published | خام أم منشور؟ (إن نُشر: على أي منصة) | Raw or published? (if published: where) | — |
| C3 | Who filmed it | من صوّره؟ (أنا / موظف / مصوّر مستقل / وكالة / غير ذلك) | Who filmed it? (me / staff / freelancer / agency / other) | Freelancer or agency → C4 must be "yes, in writing" or the clip is rejected |
| C4 | Ownership / permission | هل المقطع ملكك أو لديك إذن باستعماله؟ (ملكي / إذن كتابي / إذن شفهي / لا أعرف) | Do you own it or have permission? (mine / written permission / verbal permission / don't know) | "don't know" → reject |
| C5 | People in the clip | هل يظهر أو يُسمع فيه أشخاص غيرك؟ (لا / نعم ووافقوا / نعم ولم أسألهم) | Are other people seen or heard? (no / yes and they agreed / yes, not asked) | "not asked" → reject |
| C6 | Minors | هل يظهر فيه أطفال دون 18 سنة؟ (لا / نعم) | Does it show children under 18? (no / yes) | "yes" → reject in the pilot |
| C7 | Music | هل فيه موسيقى؟ (لا / من مكتبة المنصة / من مكتبة مجانية: اذكرها / أغنية تجارية / لا أعرف) | Music? (none / platform library / free library: name it / commercial song / don't know) | Commercial song or "don't know" → accepted for internal eval only; we do not reuse its audio in any version we send |
| C8 | Third-party content | هل فيه شعارات أو مقاطع أو صور من غيرك؟ (لا / نعم: ما هي) | Logos, clips or images from others? (no / yes: what) | "yes" → Assurance decides per clip |
| C9 | Restrictions | أي شيء لا تريدنا أن نفعله بهذا المقطع؟ | Anything you do not want us to do with this clip? | Recorded in the RR row |
| C10 | rights_id | — | Operator: `RR-P<partner>-<n>` | Must exist before ingest |
| C11 | Received on | — | Operator: date received (day 0 of the 90 days) | — |

☐ **AR:** أؤكد أن ما كتبته عن كل مقطع صحيح. · ☐ **EN:** I confirm what I wrote about each clip is true.
