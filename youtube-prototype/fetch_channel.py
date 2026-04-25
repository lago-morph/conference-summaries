#!/usr/bin/env python3
"""
fetch_channel.py  –  YouTube channel metadata + transcript fetcher

No official YouTube API required.

Usage:
  python fetch_channel.py <channel_url> [--scraper firecrawl|ytdlp] [--workers N] [--output-dir DIR]

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
import os
import re
import sys
import threading
import concurrent.futures
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path


RATE_LIMIT_MARKERS = [
    "429",
    "too many requests",
    "rate limit",
    "please sign in to confirm",
    "sign in to confirm your age",
]

_FIRECRAWL_CREDS = Path.home() / ".config" / "firecrawl-cli" / "credentials.json"


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


def _load_firecrawl_api_key() -> str | None:
    """Read API key saved by `firecrawl init`, or from the environment."""
    if key := os.environ.get("FIRECRAWL_API_KEY"):
        return key
    if _FIRECRAWL_CREDS.exists():
        try:
            return json.loads(_FIRECRAWL_CREDS.read_text())["apiKey"]
        except Exception:
            pass
    return None


# ── Scraper abstraction ──────────────────────────────────────────────────────


class BaseScraper(ABC):
    """Pluggable scraping backend.  All methods must be thread-safe."""

    @abstractmethod
    def fetch_channel_listing(self, url: str) -> tuple[str, str, list[dict]]:
        """Return (channel_id, channel_name, [{id, title}, ...])."""
        ...

    @abstractmethod
    def fetch_video_info(self, video_id: str) -> dict:
        """Return a dict with: title, description, keywords,
        upload_date, duration_seconds, view_count."""
        ...

    @abstractmethod
    def fetch_transcript(self, video_id: str) -> list | None:
        """Return [{text, start, duration}, ...] or None if unavailable."""
        ...


# ── yt-dlp backend ───────────────────────────────────────────────────────────


class YtDlpScraper(BaseScraper):
    def __init__(
        self,
        cookies_from_browser: str | None = None,
        cookies_file: str | None = None,
    ) -> None:
        try:
            import yt_dlp
            from yt_dlp.utils import DownloadError
        except ImportError:
            sys.exit("yt-dlp not installed. Run: pip install yt-dlp")
        self._yt_dlp = yt_dlp
        self._DownloadError = DownloadError

        try:
            from youtube_transcript_api import (
                YouTubeTranscriptApi,
                TranscriptsDisabled,
                NoTranscriptFound,
                VideoUnavailable,
            )
        except ImportError:
            sys.exit("youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
        self._TranscriptApi = YouTubeTranscriptApi
        self._TranscriptsDisabled = TranscriptsDisabled
        self._NoTranscriptFound = NoTranscriptFound
        self._VideoUnavailable = VideoUnavailable

        self._cookies_from_browser = cookies_from_browser
        self._cookies_file = cookies_file

    def _auth_opts(self) -> dict:
        opts: dict = {}
        if self._cookies_from_browser:
            opts["cookiesfrombrowser"] = (self._cookies_from_browser,)
        if self._cookies_file:
            opts["cookiefile"] = self._cookies_file
        return opts

    @staticmethod
    def _collect_entries(info: dict) -> list[dict]:
        result: list[dict] = []
        for e in info.get("entries") or []:
            if e is None:
                continue
            if e.get("_type") == "playlist":
                result.extend(YtDlpScraper._collect_entries(e))
            elif e.get("id"):
                result.append(e)
        return result

    def fetch_channel_listing(self, url: str) -> tuple[str, str, list[dict]]:
        opts = {
            "quiet":              True,
            "no_warnings":        True,
            "extract_flat":       "in_playlist",
            "skip_download":      True,
            "ignoreerrors":       True,
            "nocheckcertificate": True,
            **self._auth_opts(),
        }
        try:
            with self._yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except self._DownloadError as e:
            if _is_rate_limit(str(e)):
                raise RateLimitError(str(e)) from e
            raise
        if info is None:
            raise ValueError(f"yt-dlp returned nothing for {url!r}")

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
        entries = [
            {"id": e["id"], "title": e.get("title", "")}
            for e in self._collect_entries(info)
        ]
        return cid, cname, entries

    def fetch_video_info(self, video_id: str) -> dict:
        url = f"https://www.youtube.com/watch?v={video_id}"
        opts = {
            "quiet":              True,
            "no_warnings":        True,
            "skip_download":      True,
            "nocheckcertificate": True,
            **self._auth_opts(),
        }
        try:
            with self._yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except self._DownloadError as e:
            if _is_rate_limit(str(e)):
                raise RateLimitError(str(e)) from e
            raise
        if info is None:
            raise ValueError(f"yt-dlp returned nothing for video {video_id!r}")
        return {
            "title":            info.get("title", ""),
            "description":      info.get("description", ""),
            "keywords":         info.get("tags") or [],
            "upload_date":      info.get("upload_date"),
            "duration_seconds": info.get("duration"),
            "view_count":       info.get("view_count"),
        }

    def fetch_transcript(self, video_id: str) -> list | None:
        try:
            return self._TranscriptApi.get_transcript(video_id)
        except (self._TranscriptsDisabled, self._VideoUnavailable):
            return None
        except self._NoTranscriptFound:
            try:
                tl = self._TranscriptApi.list_transcripts(video_id)
                return tl.find_generated_transcript(["en"]).fetch()
            except Exception:
                return None
        except Exception as e:
            if _is_rate_limit(str(e)):
                raise RateLimitError(str(e)) from e
            return None


# ── Firecrawl backend ────────────────────────────────────────────────────────


class FirecrawlScraper(BaseScraper):
    def __init__(self, api_key: str) -> None:
        try:
            from firecrawl import V1FirecrawlApp
        except ImportError:
            sys.exit("firecrawl-py not installed. Run: pip install firecrawl-py")
        self._app = V1FirecrawlApp(api_key=api_key)

    def _guard_rate_limit(self, text: str) -> None:
        if _is_rate_limit(text):
            raise RateLimitError(text)

    def fetch_channel_listing(self, url: str) -> tuple[str, str, list[dict]]:
        videos_url = url.rstrip("/")
        if not videos_url.endswith("/videos"):
            videos_url += "/videos"

        try:
            map_result = self._app.map_url(videos_url, search="watch?v=", limit=500)
        except Exception as e:
            self._guard_rate_limit(str(e))
            raise

        seen: set[str] = set()
        video_entries: list[dict] = []
        for link in (map_result.links or []):
            m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", link)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                video_entries.append({"id": m.group(1), "title": ""})

        channel_name = "unknown"
        channel_id = "unknown"
        try:
            page = self._app.scrape_url(videos_url, formats=["markdown"])
            if page.title:
                channel_name = page.title.replace(" - YouTube", "").strip()
            cid_match = re.search(r'"channelId"\s*:\s*"(UC[^"]+)"', page.markdown or "")
            if cid_match:
                channel_id = cid_match.group(1)
            else:
                channel_id = re.sub(r"[^a-zA-Z0-9_-]", "_", channel_name)
        except Exception:
            pass

        return channel_id, channel_name, video_entries

    def fetch_video_info(self, video_id: str) -> dict:
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            result = self._app.scrape_url(url, formats=["markdown"])
        except Exception as e:
            self._guard_rate_limit(str(e))
            raise

        markdown = result.markdown or ""
        self._guard_rate_limit(markdown)

        title = (result.title or "").replace(" - YouTube", "").strip()
        description = result.description or ""

        upload_date = None
        date_match = re.search(
            r"\b(20\d{2})([-/])(0[1-9]|1[0-2])\3(0[1-9]|[12]\d|3[01])\b", markdown
        )
        if date_match:
            upload_date = date_match.group(0).replace("-", "").replace("/", "")

        view_count = None
        view_match = re.search(r"([\d,]+)\s+views", markdown)
        if view_match:
            try:
                view_count = int(view_match.group(1).replace(",", ""))
            except ValueError:
                pass

        return {
            "title":            title,
            "description":      description,
            "keywords":         [],
            "upload_date":      upload_date,
            "duration_seconds": None,
            "view_count":       view_count,
        }

    def fetch_transcript(self, video_id: str) -> list | None:
        # Transcripts are dynamically loaded and not accessible via page scraping
        return None


# ── Channel fetcher (scraper-agnostic) ───────────────────────────────────────


class ChannelFetcher:
    def __init__(self, base_dir: Path, workers: int, scraper: BaseScraper) -> None:
        self.base_dir = base_dir
        self.workers = workers
        self._scraper = scraper
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

    # ── video processing ─────────────────────────────────────────────────────

    def _process_video(self, cid: str, video: dict) -> str:
        """Fetch and store one video's info, description, and transcript."""
        if self._stop.is_set():
            return "skipped"

        vid_id = video["video_id"]
        print(f"  fetching {vid_id}  {video.get('title', '')[:60]}")

        try:
            info = self._scraper.fetch_video_info(vid_id)
            vid_dir = self.base_dir / cid / "videos" / vid_id
            vid_dir.mkdir(parents=True, exist_ok=True)

            (vid_dir / "description.txt").write_text(
                info.get("description") or "", encoding="utf-8"
            )

            transcript = self._scraper.fetch_transcript(vid_id)
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
                "keywords":          info.get("keywords") or [],
                "upload_date":       info.get("upload_date"),
                "duration_seconds":  info.get("duration_seconds"),
                "view_count":        info.get("view_count"),
                "description_path":  f"{cid}/videos/{vid_id}/description.txt",
                "transcript_path":   tr_path,
                "transcript_status": tr_status,
                "status":            "complete",
                "error":             None,
                "last_updated":      _now(),
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
            cid, cname, entries = self._scraper.fetch_channel_listing(channel_url)
        except RateLimitError as e:
            sys.exit(f"Rate limited while fetching channel list. Wait and restart.\n{e}")

        print(f"Channel: {cname!r}  (id={cid})")

        ch_idx = self._load_ch_index(cid) or {
            "channel_id":   cid,
            "channel_name": cname,
            "channel_url":  channel_url,
            "status":       "in_progress",
            "videos":       [],
        }
        existing = {v["video_id"]: v for v in ch_idx.get("videos", [])}

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
        "--scraper",
        choices=["firecrawl", "ytdlp"],
        default="firecrawl",
        help="Scraping backend to use",
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
    # Firecrawl options
    parser.add_argument(
        "--firecrawl-api-key",
        metavar="KEY",
        default=None,
        help=(
            "Firecrawl API key (overrides FIRECRAWL_API_KEY env var and "
            "~/.config/firecrawl-cli/credentials.json)"
        ),
    )
    # yt-dlp options
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        default=None,
        help="(ytdlp only) Extract cookies from this browser (chrome, firefox, safari, …)",
    )
    parser.add_argument(
        "--cookies-file",
        metavar="FILE",
        default=None,
        help="(ytdlp only) Path to a Netscape-format cookies file",
    )
    args = parser.parse_args()

    base_dir: Path = args.output_dir or Path(__file__).parent
    base_dir.mkdir(parents=True, exist_ok=True)

    if args.scraper == "firecrawl":
        api_key = args.firecrawl_api_key or _load_firecrawl_api_key()
        if not api_key:
            sys.exit(
                "No Firecrawl API key found. Provide one via --firecrawl-api-key, "
                "the FIRECRAWL_API_KEY environment variable, or run: "
                "npx -y firecrawl-cli@latest init -k YOUR_KEY"
            )
        scraper: BaseScraper = FirecrawlScraper(api_key=api_key)
        print(f"Using scraper: firecrawl")
    else:
        scraper = YtDlpScraper(
            cookies_from_browser=args.cookies_from_browser,
            cookies_file=args.cookies_file,
        )
        print(f"Using scraper: ytdlp")

    ChannelFetcher(
        base_dir=base_dir,
        workers=args.workers,
        scraper=scraper,
    ).run(args.channel_url)


if __name__ == "__main__":
    main()
