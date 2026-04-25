#!/usr/bin/env python3
"""
fetch_playlist.py  –  YouTube playlist metadata + transcript fetcher

No official YouTube API required.  Uses yt-dlp and youtube-transcript-api.

Usage:
  python fetch_playlist.py <playlist_url> [--workers N] [--output-dir DIR]

Restartable: videos already marked 'complete' are skipped on re-run.
Rate limiting: state is saved and the process exits with code 2.

Output layout (relative to --output-dir, default: directory of this script):
  playlists_index.json                       central registry of all playlists
  {playlist_id}/playlist_index.json          per-playlist video index
  {playlist_id}/videos/{video_id}/description.txt
  {playlist_id}/videos/{video_id}/transcript.json   (timestamped segments)
  {playlist_id}/videos/{video_id}/transcript.txt    (plain text, for readability)

The playlist_index.json video entries include placeholder fields 'summary',
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
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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


class PlaylistFetcher:
    def __init__(
        self,
        base_dir: Path,
        workers: int,
        cookies_from_browser: str | None = None,
        cookies_file: str | None = None,
    ) -> None:
        self.base_dir = base_dir
        self.workers = workers
        self._cookies_from_browser = cookies_from_browser
        self._cookies_file = cookies_file
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._local = threading.local()

    def _auth_opts(self) -> dict:
        """Return yt-dlp authentication options based on what the user provided."""
        opts: dict = {}
        if self._cookies_from_browser:
            opts["cookiesfrombrowser"] = (self._cookies_from_browser,)
        if self._cookies_file:
            opts["cookiefile"] = self._cookies_file
        return opts

    # ── central index ────────────────────────────────────────────────────────

    @property
    def _central_path(self) -> Path:
        return self.base_dir / "playlists_index.json"

    def _load_central(self) -> dict:
        return _read_json(self._central_path) or {"playlists": [], "last_updated": _now()}

    def _upsert_central(self, pid: str, name: str, url: str, status: str) -> None:
        with self._lock:
            idx = self._load_central()
            for pl in idx["playlists"]:
                if pl["playlist_id"] == pid:
                    pl.update({"playlist_name": name, "status": status, "last_updated": _now()})
                    break
            else:
                idx["playlists"].append({
                    "playlist_id":   pid,
                    "playlist_name": name,
                    "playlist_url":  url,
                    "status":        status,
                    "last_updated":  _now(),
                    "index_path":    f"{pid}/playlist_index.json",
                })
            idx["last_updated"] = _now()
            _write_json(self._central_path, idx)

    # ── playlist index ───────────────────────────────────────────────────────

    def _pl_index_path(self, pid: str) -> Path:
        return self.base_dir / pid / "playlist_index.json"

    def _load_pl_index(self, pid: str) -> dict | None:
        return _read_json(self._pl_index_path(pid))

    def _save_pl_index(self, pid: str, idx: dict) -> None:
        idx["last_updated"] = _now()
        _write_json(self._pl_index_path(pid), idx)

    def _patch_video(self, pid: str, updated: dict) -> None:
        """Thread-safe replace of one video entry in the playlist index."""
        with self._lock:
            idx = self._load_pl_index(pid)
            vid_id = updated["video_id"]
            idx["videos"] = [
                updated if v["video_id"] == vid_id else v
                for v in idx["videos"]
            ]
            self._save_pl_index(pid, idx)

    # ── yt-dlp helpers ───────────────────────────────────────────────────────

    def _flat_playlist(self, url: str) -> dict:
        """Fetch the full video list for a playlist without downloading anything."""
        opts = {
            "quiet":               True,
            "no_warnings":         True,
            "extract_flat":        "in_playlist",
            "skip_download":       True,
            "ignoreerrors":        True,
            "nocheckcertificate":  True,
            **self._auth_opts(),
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
            "quiet":              True,
            "no_warnings":        True,
            "skip_download":      True,
            "nocheckcertificate": True,
            **self._auth_opts(),
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

    def _transcript_api(self) -> YouTubeTranscriptApi:
        if not getattr(self._local, "api", None):
            session = requests.Session()
            session.verify = False
            self._local.api = YouTubeTranscriptApi(http_client=session)
        return self._local.api

    def _get_transcript(self, vid_id: str) -> list | None:
        """Return transcript segments or None if unavailable."""
        api = self._transcript_api()
        try:
            return [{"text": s.text, "start": s.start, "duration": s.duration}
                    for s in api.fetch(vid_id)]
        except (TranscriptsDisabled, VideoUnavailable):
            return None
        except NoTranscriptFound:
            try:
                tl = api.list(vid_id)
                return [{"text": s.text, "start": s.start, "duration": s.duration}
                        for s in tl.find_generated_transcript(["en"]).fetch()]
            except Exception:
                return None
        except Exception as e:
            if _is_rate_limit(str(e)):
                raise RateLimitError(str(e)) from e
            return None

    # ── entry collection ─────────────────────────────────────────────────────

    @staticmethod
    def _collect_entries(info: dict) -> list[dict]:
        """Recursively flatten playlist structure to individual video entries."""
        result: list[dict] = []
        for e in info.get("entries") or []:
            if e is None:
                continue
            if e.get("_type") == "playlist":
                result.extend(PlaylistFetcher._collect_entries(e))
            elif e.get("id"):
                result.append(e)
        return result

    # ── video processing ─────────────────────────────────────────────────────

    def _process_video(self, pid: str, video: dict) -> str:
        """Fetch and store one video's info, description, and transcript."""
        if self._stop.is_set():
            return "skipped"

        vid_id = video["video_id"]
        print(f"  fetching {vid_id}  {video.get('title', '')[:60]}")

        try:
            info = self._video_info(vid_id)
            vid_dir = self.base_dir / pid / "videos" / vid_id
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
                tr_path = f"{pid}/videos/{vid_id}/transcript.json"
                tr_status = "available"

            self._patch_video(pid, {
                **video,
                "title":             info.get("title") or video.get("title", ""),
                "keywords":          info.get("tags") or [],
                "upload_date":       info.get("upload_date"),
                "duration_seconds":  info.get("duration"),
                "view_count":        info.get("view_count"),
                "description_path":  f"{pid}/videos/{vid_id}/description.txt",
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
            self._patch_video(pid, {
                **video,
                "status":       "rate_limited",
                "last_updated": _now(),
            })
            return "rate_limited"

        except Exception as e:
            print(f"  error {vid_id}: {e}", file=sys.stderr)
            self._patch_video(pid, {
                **video,
                "status":       "error",
                "error":        str(e),
                "last_updated": _now(),
            })
            return "error"

    # ── main run ─────────────────────────────────────────────────────────────

    def run(self, playlist_url: str) -> None:
        # Phase 1: fetch video list ───────────────────────────────────────────
        print("Phase 1: fetching playlist video list …")
        try:
            info = self._flat_playlist(playlist_url)
        except RateLimitError as e:
            sys.exit(f"Rate limited while fetching playlist. Wait and restart.\n{e}")

        pid = info.get("id") or "unknown"
        pname = info.get("title") or pid
        print(f"Playlist: {pname!r}  (id={pid})")

        # Merge new videos into existing index (idempotent)
        pl_idx = self._load_pl_index(pid) or {
            "playlist_id":   pid,
            "playlist_name": pname,
            "playlist_url":  playlist_url,
            "status":        "in_progress",
            "videos":        [],
        }
        existing = {v["video_id"]: v for v in pl_idx.get("videos", [])}

        entries = self._collect_entries(info)
        print(f"Found {len(entries)} videos in playlist")

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

        pl_idx["videos"] = list(existing.values())
        self._save_pl_index(pid, pl_idx)
        self._upsert_central(pid, pname, playlist_url, "in_progress")

        # Phase 2: fetch individual video details ─────────────────────────────
        pending = [v for v in pl_idx["videos"] if v["status"] != "complete"]
        n_done = len(pl_idx["videos"]) - len(pending)
        print(
            f"\nPhase 2: {n_done} already complete, {len(pending)} to fetch"
            f"  (workers={self.workers})"
        )

        if not pending:
            self._close_out(pid, pname, playlist_url)
            return

        counts: dict[str, int] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as pool:
            futs = {pool.submit(self._process_video, pid, v): v for v in pending}
            for fut in concurrent.futures.as_completed(futs):
                if self._stop.is_set():
                    for f in futs:
                        f.cancel()
                    break
                r = fut.result()
                counts[r] = counts.get(r, 0) + 1
                done = sum(counts.values())
                print(f"  progress {done}/{len(pending)} | {counts}")

        self._close_out(pid, pname, playlist_url)

    def _close_out(self, pid: str, pname: str, url: str) -> None:
        """Compute final status, persist it, and exit with code 2 if rate-limited."""
        pl_idx = self._load_pl_index(pid)
        statuses = {v["status"] for v in pl_idx["videos"]}

        if statuses <= {"complete"}:
            final = "complete"
        elif "rate_limited" in statuses:
            final = "rate_limited"
        else:
            final = "partial"

        pl_idx["status"] = final
        self._save_pl_index(pid, pl_idx)
        self._upsert_central(pid, pname, url, final)
        print(f"\nPlaylist status: {final}")

        if final == "rate_limited":
            sys.exit(
                "Rate limiting was detected. Please wait before restarting "
                "(re-run will skip completed videos)."
            )


# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch YouTube playlist video metadata and transcripts "
            "without the official YouTube API."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "playlist_url",
        help=(
            "YouTube playlist URL.  "
            "Example: https://www.youtube.com/playlist?list=PLxxxxxxx"
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
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        default=None,
        help="Extract cookies from this browser (chrome, firefox, safari, edge, brave, …)",
    )
    parser.add_argument(
        "--cookies-file",
        metavar="FILE",
        default=None,
        help="Path to a Netscape-format cookies file exported from your browser",
    )
    args = parser.parse_args()

    base_dir: Path = args.output_dir or Path(__file__).parent
    base_dir.mkdir(parents=True, exist_ok=True)

    PlaylistFetcher(
        base_dir=base_dir,
        workers=args.workers,
        cookies_from_browser=args.cookies_from_browser,
        cookies_file=args.cookies_file,
    ).run(args.playlist_url)


if __name__ == "__main__":
    main()
