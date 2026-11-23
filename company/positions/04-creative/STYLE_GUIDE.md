# Style Guide v0 (Shorts)
Each rule maps to a timeline schema field, so Engineering can implement it and Assurance can check it.

| Rule | Value (v0) | Schema field |
|---|---|---|
| Canvas | 1080×1920, 30 fps | `canvas` |
| Safe zone | Keep captions between 18% and 72% of height; nothing in the right 12% (platform buttons) | `captions[].position` |
| Caption length | ≤ 2 lines, ≤ ~12 words on screen | validator rule |
| Caption timing | Word-level or phrase-level synced; min 0.7 s on screen | `captions[].start_ms/end_ms` |
| Font | One Arabic font with full Latin coverage, license recorded (candidates: Noto Sans Arabic, IBM Plex Sans Arabic, Cairo; all OFL; to be confirmed by Assurance) | `captions[].style` |
| Hook caption | Larger, highlighted, first 1.5 s | `style: "hook"` |
| Emphasis | Highlight max 1 keyword per caption | `captions[].emphasis` |
| Zoom | 1.05–1.20 scale, 300–500 ms ease, max one per 3 s | `effects[type=zoom]` |
| Music | −18 to −22 dB under speech, ducked | `audio[].gain_db`, `duck_under_speech` |
| Loudness | Integrated around −14 LUFS | render config |
| Ending | Last 1 s: payoff line or loop back to the hook | edit rule |
