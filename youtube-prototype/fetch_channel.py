#!/usr/bin/env python3
"""
fetch_channel.py  –  YouTube channel metadata + transcript fetcher

No official YouTube API required.  Uses yt-dlp and youtube-transcript-api.

Usage:
  python fetch_channel.py <channel_url> [--workers N] [--output-dir DIR]

Restartable: videos already marked 'complete' are skipped on re-run.
Rate limiting: state is saved and the process exits with code 2.

Output layout (relative to --output-dir, default: directory of this script):
  channels_index.json                        central registry of all channels
  {channel_id}/channel_index.json            per-channel video index
  {channel_id}/videos/{video_id}/description.txt
  {channel_id}/videos/{video_id}/transcript.json   (timestamped segments)
  {channel_id}/videos/{video_id}/transcript.txt    (plain text, for readability)

The channel_index.json video entries include placeholder fields 'summary',
'summary_bullets', and 'ai_keywords' (all null) intended to be filled by a
separate LLM enrichment process.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import concurrent.futures
from datetime import datetime, timezone
from pathlib import Path

try:
    import yt_dlp
    from yt_dlp.utils import DownloadError
except ImportError:
    sys.exit("yt-dlp not installed. Run: pip install yt-dlp")

try:
    from youtube_transcript_api import (
        YouTubeTranscriptApi,
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )
except ImportError:
    sys.exit("youtube-transcript-api not installed. Run: pip install youtube-transcript-api")


RATE_LIMIT_MARKERS = [
    "429",
    "too many requests",
    "rate limit",
    "please sign in to confirm",
    "sign in to confirm your age",
]


class RateLimitError(Exception):
    pass


def _is_rate_limit(msg: str) -> bool:
    low = msg.lower()
    return any(m in low for m in RATE_LIMIT_MARKERS)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict | list | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _write_json(path: Path, data: dict | list, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────


class ChannelFetcher:
    def __init__(self, base_dir: Path, workers: int) -> None:
        self.base_dir = base_dir
        self.workers = workers
        self._lock = threading.Lock()
        self._stop = threading.Event()

    # ── central index ────────────────────────────────────────────────────────

    @property
    def _central_path(self) -> Path:
        return self.base_dir / "channels_index.json"

    def _load_central(self) -> dict:
        return _read_json(self._central_path) or {"channels": [], "last_updated": _now()}

    def _upsert_central(self, cid: str, name: str, url: str, status: str) -> None:
        with self._lock:
            idx = self._load_central()
            for ch in idx["channels"]:
                if ch["channel_id"] == cid:
                    ch.update({"channel_name": name, "status": status, "last_updated": _now()})
                    break
            else:
                idx["channels"].append({
                    "channel_id":   cid,
                    "channel_name": name,
                    "channel_url":  url,
                    "status":       status,
                    "last_updated": _now(),
                    "index_path":   f"{cid}/channel_index.json",
                })
            idx["last_updated"] = _now()
            _write_json(self._central_path, idx)

    # ── channel index ────────────────────────────────────────────────────────

    def _ch_index_path(self, cid: str) -> Path:
        return self.base_dir / cid / "channel_index.json"

    def _load_ch_index(self, cid: str) -> dict | None:
        return _read_json(self._ch_index_path(cid))

    def _save_ch_index(self, cid: str, idx: dict) -> None:
        idx["last_updated"] = _now()
        _write_json(self._ch_index_path(cid), idx)

    def _patch_video(self, cid: str, updated: dict) -> None:
        """Thread-safe replace of one video entry in the channel index."""
        with self._lock:
            idx = self._load_ch_index(cid)
            vid_id = updated["video_id"]
            idx["videos"] = [
                updated if v["video_id"] == vid_id else v
                for v in idx["videos"]
            ]
            self._save_ch_index(cid, idx)

    # ── yt-dlp helpers ───────────────────────────────────────────────────────

    def _flat_channel(self, url: str) -> dict:
        """Fetch the full video list for a channel without downloading anything."""
        opts = {
            "quiet":        True,
            "no_warnings":  True,
            "extract_flat": "in_playlist",
            "skip_download": True,
            "ignoreerrors": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except DownloadError as e:
            if _is_rate_limit(str(e)):
                raise RateLimitError(str(e)) from e
            raise
        if info is None:
            raise ValueError(f"yt-dlp returned nothing for {url!r}")
        return info

    def _video_info(self, vid_id: str) -> dict:
        """Fetch full metadata for a single video."""
        url = f"https://www.youtube.com/watch?v={vid_id}"
        opts = {
            "quiet":        True,
            "no_warnings":  True,
            "skip_download": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except DownloadError as e:
            if _is_rate_limit(str(e)):
                raise RateLimitError(str(e)) from e
            raise
        if info is None:
            raise ValueError(f"yt-dlp returned nothing for video {vid_id!r}")
        return info

    def _get_transcript(self, vid_id: str) -> list | None:
        """Return transcript segments or None if unavailable."""
        try:
            return YouTubeTranscriptApi.get_transcript(vid_id)
        except (TranscriptsDisabled, VideoUnavailable):
            return None
        except NoTranscriptFound:
            try:
                tl = YouTubeTranscriptApi.list_transcripts(vid_id)
                return tl.find_generated_transcript(["en"]).fetch()
            except Exception:
                return None
        except Exception as e:
            if _is_rate_limit(str(e)):
                raise RateLimitError(str(e)) from e
            return None

    # ── entry collection ─────────────────────────────────────────────────────

    @staticmethod
    def _collect_entries(info: dict) -> list[dict]:
        """Recursively flatten channel/playlist structure to individual video entries."""
        result: list[dict] = []
        for e in info.get("entries") or []:
            if e is None:
                continue
            if e.get("_type") == "playlist":
                result.extend(ChannelFetcher._collect_entries(e))
            elif e.get("id"):
                result.append(e)
        return result

    # ── video processing ─────────────────────────────────────────────────────

    def _process_video(self, cid: str, video: dict) -> str:
        """Fetch and store one video's info, description, and transcript."""
        if self._stop.is_set():
            return "skipped"

        vid_id = video["video_id"]
        print(f"  fetching {vid_id}  {video.get('title', '')[:60]}")

        try:
            info = self._video_info(vid_id)
            vid_dir = self.base_dir / cid / "videos" / vid_id
            vid_dir.mkdir(parents=True, exist_ok=True)

            (vid_dir / "description.txt").write_text(
                info.get("description") or "", encoding="utf-8"
            )

            transcript = self._get_transcript(vid_id)
            tr_path = None
            tr_status = "none"
            if transcript:
                _write_json(vid_dir / "transcript.json", transcript)
                plain = "\n".join(seg.get("text", "") for seg in transcript)
                (vid_dir / "transcript.txt").write_text(plain, encoding="utf-8")
                tr_path = f"{cid}/videos/{vid_id}/transcript.json"
                tr_status = "available"

            self._patch_video(cid, {
                **video,
                "title":             info.get("title") or video.get("title", ""),
                "keywords":          info.get("tags") or [],
                "upload_date":       info.get("upload_date"),
                "duration_seconds":  info.get("duration"),
                "view_count":        info.get("view_count"),
                "description_path":  f"{cid}/videos/{vid_id}/description.txt",
                "transcript_path":   tr_path,
                "transcript_status": tr_status,
                "status":            "complete",
                "error":             None,
                "last_updated":      _now(),
                # LLM-generated fields preserved if already populated
                "summary":           video.get("summary"),
                "summary_bullets":   video.get("summary_bullets"),
                "ai_keywords":       video.get("ai_keywords"),
            })
            return "complete"

        except RateLimitError as e:
            print(f"  RATE LIMITED: {e}", file=sys.stderr)
            self._stop.set()
            self._patch_video(cid, {
                **video,
                "status":       "rate_limited",
                "last_updated": _now(),
            })
            return "rate_limited"

        except Exception as e:
            print(f"  error {vid_id}: {e}", file=sys.stderr)
            self._patch_video(cid, {
                **video,
                "status":       "error",
                "error":        str(e),
                "last_updated": _now(),
            })
            return "error"

    # ── main run ─────────────────────────────────────────────────────────────

    def run(self, channel_url: str) -> None:
        # Phase 1: fetch video list ───────────────────────────────────────────
        print("Phase 1: fetching channel video list …")
        try:
            info = self._flat_channel(channel_url)
        except RateLimitError as e:
            sys.exit(f"Rate limited while fetching channel list. Wait and restart.\n{e}")

        cid = (
            info.get("channel_id")
            or info.get("uploader_id")
            or info.get("id")
            or "unknown"
        )
        cname = (
            info.get("channel")
            or info.get("uploader")
            or info.get("title")
            or cid
        )
        print(f"Channel: {cname!r}  (id={cid})")

        # Merge new videos into existing index (idempotent)
        ch_idx = self._load_ch_index(cid) or {
            "channel_id":   cid,
            "channel_name": cname,
            "channel_url":  channel_url,
            "status":       "in_progress",
            "videos":       [],
        }
        existing = {v["video_id"]: v for v in ch_idx.get("videos", [])}

        entries = self._collect_entries(info)
        print(f"Found {len(entries)} videos in channel")

        new_count = 0
        for e in entries:
            vid_id = e.get("id")
            if not vid_id or vid_id in existing:
                continue
            existing[vid_id] = {
                "video_id":          vid_id,
                "title":             e.get("title", ""),
                "url":               f"https://www.youtube.com/watch?v={vid_id}",
                "status":            "pending",
                "keywords":          [],
                "upload_date":       None,
                "duration_seconds":  None,
                "view_count":        None,
                "description_path":  None,
                "transcript_path":   None,
                "transcript_status": None,
                "error":             None,
                "last_updated":      _now(),
                "summary":           None,
                "summary_bullets":   None,
                "ai_keywords":       None,
            }
            new_count += 1

        if new_count:
            print(f"Added {new_count} new video(s) to index")

        ch_idx["videos"] = list(existing.values())
        self._save_ch_index(cid, ch_idx)
        self._upsert_central(cid, cname, channel_url, "in_progress")

        # Phase 2: fetch individual video details ─────────────────────────────
        pending = [v for v in ch_idx["videos"] if v["status"] != "complete"]
        n_done = len(ch_idx["videos"]) - len(pending)
        print(
            f"\nPhase 2: {n_done} already complete, {len(pending)} to fetch"
            f"  (workers={self.workers})"
        )

        if not pending:
            self._close_out(cid, cname, channel_url)
            return

        counts: dict[str, int] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as pool:
            futs = {pool.submit(self._process_video, cid, v): v for v in pending}
            for fut in concurrent.futures.as_completed(futs):
                if self._stop.is_set():
                    for f in futs:
                        f.cancel()
                    break
                r = fut.result()
                counts[r] = counts.get(r, 0) + 1
                done = sum(counts.values())
                print(f"  progress {done}/{len(pending)} | {counts}")

        self._close_out(cid, cname, channel_url)

    def _close_out(self, cid: str, cname: str, url: str) -> None:
        """Compute final status, persist it, and exit with code 2 if rate-limited."""
        ch_idx = self._load_ch_index(cid)
        statuses = {v["status"] for v in ch_idx["videos"]}

        if statuses <= {"complete"}:
            final = "complete"
        elif "rate_limited" in statuses:
            final = "rate_limited"
        else:
            final = "partial"

        ch_idx["status"] = final
        self._save_ch_index(cid, ch_idx)
        self._upsert_central(cid, cname, url, final)
        print(f"\nChannel status: {final}")

        if final == "rate_limited":
            sys.exit(
                "Rate limiting was detected. Please wait before restarting "
                "(re-run will skip completed videos)."
            )


# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch YouTube channel video metadata and transcripts "
            "without the official YouTube API."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "channel_url",
        help=(
            "YouTube channel URL.  "
            "Examples: https://youtube.com/@handle  "
            "or https://youtube.com/channel/UCxxxxxxx  "
            "Append /videos to target the Videos tab explicitly."
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers for fetching individual videos",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Base output directory (default: directory containing this script)",
    )
    args = parser.parse_args()

    base_dir: Path = args.output_dir or Path(__file__).parent
    base_dir.mkdir(parents=True, exist_ok=True)

    ChannelFetcher(base_dir=base_dir, workers=args.workers).run(args.channel_url)


if __name__ == "__main__":
    main()
