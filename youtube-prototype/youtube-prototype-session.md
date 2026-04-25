# YouTube Prototype – Session Summary

> **WHEN TO READ THIS**: Read this if you are picking up work on the YouTube channel
> fetcher in `youtube-prototype/`. It documents what was built, every issue hit during
> testing, and exactly where to continue.

---

## What Was Built

A Python script (`youtube-prototype/fetch_channel.py`) that downloads video metadata,
descriptions, and transcripts for every video on a YouTube channel or playlist, without
using the official YouTube Data API. It uses:

- **yt-dlp** – channel/playlist enumeration and per-video metadata
- **youtube-transcript-api** – transcript fetching (with auto-generated fallback)

### Design Goals (all implemented)

- Restartable / idempotent: re-running skips videos already marked `complete`
- Rate-limit aware: detects HTTP 429, saves state, exits with code 2
- Configurable parallelism: `--workers N`
- No automatic retry (by design): user restarts manually
- Placeholder fields in index for a future LLM enrichment pass

---

## File Layout

```
youtube-prototype/
├── fetch_channel.py       # main script
├── requirements.txt       # yt-dlp, youtube-transcript-api

# Created at runtime (not committed):
├── channels_index.json                        # central registry of all channels processed
└── CHANNEL_ID/
    ├── channel_index.json                     # per-channel video index
    └── videos/
        └── VIDEO_ID/
            ├── description.txt
            ├── transcript.json                # timestamped segments [{text, start, duration}]
            └── transcript.txt                 # plain text version
```

---

## JSON Schema

### channels_index.json
```json
{
  "channels": [
    {
      "channel_id": "...",
      "channel_name": "...",
      "channel_url": "...",
      "status": "complete | in_progress | partial | rate_limited",
      "last_updated": "<ISO timestamp>",
      "index_path": "CHANNEL_ID/channel_index.json"
    }
  ],
  "last_updated": "<ISO timestamp>"
}
```

### CHANNEL_ID/channel_index.json
```json
{
  "channel_id": "...",
  "channel_name": "...",
  "channel_url": "...",
  "status": "complete | in_progress | partial | rate_limited",
  "last_updated": "<ISO timestamp>",
  "videos": [
    {
      "video_id": "...",
      "title": "...",
      "url": "https://www.youtube.com/watch?v=VIDEO_ID",
      "status": "pending | complete | error | rate_limited",
      "keywords": ["tag1", "tag2"],
      "upload_date": "YYYYMMDD",
      "duration_seconds": 1234,
      "view_count": 56789,
      "description_path": "CHANNEL_ID/videos/VIDEO_ID/description.txt",
      "transcript_path": "CHANNEL_ID/videos/VIDEO_ID/transcript.json",
      "transcript_status": "available | none",
      "error": null,
      "last_updated": "<ISO timestamp>",
      "summary": null,
      "summary_bullets": null,
      "ai_keywords": null
    }
  ]
}
```

The `summary`, `summary_bullets`, and `ai_keywords` fields are always written as `null`
by the fetcher. They are reserved for a separate LLM enrichment process (not yet built).

---

## How to Run

```bash
cd conference-summaries
pip install -r youtube-prototype/requirements.txt

# Basic run (sequential)
python youtube-prototype/fetch_channel.py 'CHANNEL_OR_PLAYLIST_URL'

# With parallelism
python youtube-prototype/fetch_channel.py 'CHANNEL_OR_PLAYLIST_URL' --workers 3

# With cookie auth (required – see Issues below)
python youtube-prototype/fetch_channel.py 'CHANNEL_OR_PLAYLIST_URL' --cookies-from-browser chrome

# With exported cookies file
python youtube-prototype/fetch_channel.py 'CHANNEL_OR_PLAYLIST_URL' --cookies-file /path/to/cookies.txt

# To resume after rate limiting: re-run the same command unchanged.
# Videos with status "complete" are skipped automatically.
```

**Important**: always single-quote the URL to prevent the shell from interpreting
`?`, `=`, and `&` as special characters. Do not wrap the URL in `<>`.

---

## Issues Hit During Testing & Fixes Applied

### 1. SSL certificate verification failure
**Symptom**: `[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate`

**Cause**: Environment has an SSL inspection proxy that inserts its own certificate.

**Fix**: Added `"nocheckcertificate": True` to all yt-dlp option dicts.
(Note: the Python API key is `nocheckcertificate`; the CLI flag is `--no-check-certificate`.)

### 2. YouTube bot detection on individual video fetches
**Symptom**: `Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies`

**Cause**: YouTube flags unauthenticated requests for full video metadata as bots.
Phase 1 (playlist enumeration) passes; Phase 2 (per-video detail) fails.

**Fix**: Added `--cookies-from-browser BROWSER` and `--cookies-file FILE` CLI flags.
These pass through to yt-dlp's `cookiesfrombrowser` and `cookiefile` options.
Auth opts are applied to both `_flat_channel` and `_video_info` calls.

### 3. Shell argument parsing – "unrecognized arguments: URL"
**Symptom**: `error: unrecognized arguments: https://...`

**Cause**: The URL was passed without quoting. The shell split it on `?`, `&`, or
other special characters, or the user used `<URL>` notation literally.

**Fix**: Always single-quote URLs in shell commands. This was a documentation issue,
not a code issue.

---

## Current Status

- Code is complete and on `main` (merged from `claude/youtube-prototype-HbifB`)
- **Not tested end-to-end** because the development sandbox blocks YouTube
  (`Host not in allowlist`)
- Testing reached Phase 2 on the user's local machine; hit the bot detection error
  (issue #2 above, now fixed)
- Cookie auth fix is committed but **not yet confirmed working** – user needs to re-run
  with `--cookies-from-browser chrome` (or their browser of choice)

---

## Next Steps

1. **Confirm cookie auth works**: re-run the playlist test with `--cookies-from-browser`
   and verify `channels_index.json`, `channel_index.json`, and video files are created

2. **LLM enrichment process** (explicitly out of scope for this session): a separate
   script that reads `channel_index.json`, sends description + transcript to an LLM,
   and fills in `summary`, `summary_bullets`, and `ai_keywords` for each video

3. **Potential issues to watch for at scale**:
   - Lock contention on `channel_index.json` with high `--workers` values (the index
     is fully read-written on every video completion; fine for hundreds of videos,
     may need batching for thousands)
   - Transcript availability: many videos have no captions; `transcript_status: "none"`
     is expected and handled
   - yt-dlp updates: YouTube changes its internal API frequently; keep yt-dlp current

---

## Branch History

```
main
├── f2c140f  Merge youtube-prototype
├── a1a78b0  Add cookie authentication support
├── 1ab3c3d  Disable SSL certificate verification
└── 3e2ca5a  Add YouTube channel metadata + transcript fetcher prototype
```
