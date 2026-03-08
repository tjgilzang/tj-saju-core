import argparse
import hashlib
import json
import logging
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:  # pragma: no cover
    firebase_admin = None
    credentials = None
    firestore = None


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
REPORTS_DIR = ROOT / "reports"

PROGRAMS = [
    {
        "program_id": "lifeunse",
        "collection": "saju_raw_lifeunse",
        "source_paths": [ROOT / "sources" / "raw" / "라이프운세"],
        "schema_version": "1.0.0",
    },
    {
        "program_id": "sajubaekgwa",
        "collection": "saju_raw_sajubaekgwa",
        "source_paths": [ROOT / "sources" / "raw" / "사주백과"],
        "schema_version": "1.0.1",
    },
    {
        "program_id": "sajudosa",
        "collection": "saju_raw_sajudosa",
        "source_paths": [ROOT / "sources" / "raw" / "사주도사(작명소_만세력)"],
        "schema_version": "0.9.0",
    },
    {
        "program_id": "sajunara",
        "collection": "saju_raw_sajunara",
        "source_paths": [ROOT / "sources" / "raw" / "사주나라.iso"],
        "schema_version": "0.1.0",
    },
]

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"
CHUNK_SIZE = 1 << 20  # 1MB


def ensure_dirs() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger() -> None:
    ensure_dirs()
    log_path = LOG_DIR / "firestore_ingestion.log"
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s:%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )


def get_firestone_client(project_id: Optional[str]) -> Optional[firestore.Client]:
    if not firebase_admin or not credentials or not firestore:
        return None
    cred_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not cred_path or not Path(cred_path).exists():
        return None
    options: Dict[str, str] = {}
    if project_id:
        options["projectId"] = project_id
    if firebase_admin._apps:
        app = firebase_admin.get_app()
    else:
        app = firebase_admin.initialize_app(credentials.Certificate(cred_path), options)
    return firestore.client(app)


class FileWalker:
    def __init__(self, paths: Iterable[Path], limit: Optional[int] = None):
        self.paths = paths
        self.limit = limit
        self._count = 0

    def __iter__(self) -> Iterator[Path]:
        for path in self.paths:
            if path.is_dir():
                for root, _, files in os.walk(path):
                    for name in files:
                        if self.limit and self._count >= self.limit:
                            return
                        full_path = Path(root) / name
                        self._count += 1
                        yield full_path
            elif path.is_file():
                if self.limit and self._count >= self.limit:
                    return
                self._count += 1
                yield path


def sha256_of_file(path: Path) -> str:
    hash_sha = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hash_sha.update(chunk)
    return hash_sha.hexdigest()


def read_preview(path: Path, max_bytes: int = 1024) -> Optional[str]:
    if path.suffix.lower() in {".txt", ".cfg", ".ini", ".json", ".csv", ".tsv"}:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_bytes)
        except OSError:
            return None
    return None


def payload_summary(path: Path) -> Dict:
    stat = path.stat()
    mime, _ = mimetypes.guess_type(path.as_posix())
    return {
        "file_name": path.name,
        "file_size": stat.st_size,
        "mime_type": mime or "application/octet-stream",
        "content_preview": read_preview(path),
    }


def doc_id_from_hash(program_id: str, sha: str) -> str:
    clean_hash = sha[:24]
    return f"{program_id}_{clean_hash}"


def ingest_file(
    client: Optional[firestore.Client],
    collection: str,
    program_id: str,
    schema_version: str,
    path: Path,
    dry_run: bool,
    retries: int = 3,
) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    file_hash = sha256_of_file(path)
    doc_id = doc_id_from_hash(program_id, file_hash)
    rel_path = path.relative_to(ROOT).as_posix()
    extracted_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime(DATE_FMT)
    document = {
        "program_id": program_id,
        "collection": collection,
        "source_path": rel_path,
        "content_hash": file_hash,
        "schema_version": schema_version,
        "extracted_at": extracted_at,
        "payload_summary": payload_summary(path),
        "ingested_at": datetime.now(tz=timezone.utc).strftime(DATE_FMT),
    }
    if dry_run or not client:
        logging.info("[DRY RUN] %s -> %s", rel_path, collection)
        return True, []
    for attempt in range(1, retries + 1):
        try:
            client.collection(collection).document(doc_id).set(document)
            logging.info("%s -> %s (attempt %s)", rel_path, collection, attempt)
            return True, []
        except Exception as exc:
            msg = f"{rel_path} attempt {attempt} failed: {exc}"
            logging.warning(msg)
            errors.append(msg)
            if attempt == retries:
                return False, errors
    return False, errors


def build_summary(result_counters: Dict[str, Dict]) -> Dict:
    global_success = sum(ctx["success"] for ctx in result_counters.values())
    global_failure = sum(ctx["failure"] for ctx in result_counters.values())
    global_retries = sum(ctx["retries"] for ctx in result_counters.values())
    return {
        "generated_at": datetime.now(tz=timezone.utc).strftime(DATE_FMT),
        "global": {
            "success_count": global_success,
            "failure_count": global_failure,
            "retry_count": global_retries,
        },
        "programs": {
            pid: {
                "collection": ctx["collection"],
                "documents_attempted": ctx["attempts"],
                "success_count": ctx["success"],
                "failure_count": ctx["failure"],
                "errors": ctx["errors"],
            }
            for pid, ctx in result_counters.items()
        },
    }


def write_summary(summary: Dict) -> None:
    summary_path = REPORTS_DIR / "firestore_ingestion_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    logging.info("Summary written to %s", summary_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="TJ Saju Firebase ingestion pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Skip actual Firestore writes")
    parser.add_argument("--limit", type=int, help="Limit files per program")
    parser.add_argument("--project-id", help="Override Firestore project ID (for credentials)")
    args = parser.parse_args()

    ensure_dirs()
    setup_logger()
    client = None
    if not args.dry_run:
        client = get_firestone_client(args.project_id)
        if not client:
            logging.warning("Firestore client not initialized; forcing dry run")
            args.dry_run = True
    summary_stats: Dict[str, Dict] = {}
    for config in PROGRAMS:
        program_id = config["program_id"]
        collection = config["collection"]
        summary_stats[program_id] = {
            "collection": collection,
            "attempts": 0,
            "success": 0,
            "failure": 0,
            "retries": 0,
            "errors": [],
        }
        walker = FileWalker(config["source_paths"], limit=args.limit)
        for file_path in walker:
            summary_stats[program_id]["attempts"] += 1
            success, errors = ingest_file(
                client,
                collection,
                program_id,
                config["schema_version"],
                file_path,
                dry_run=args.dry_run,
            )
            if success:
                summary_stats[program_id]["success"] += 1
            else:
                summary_stats[program_id]["failure"] += 1
                summary_stats[program_id]["retries"] += len(errors)
                summary_stats[program_id]["errors"].extend(errors)

    summary = build_summary(summary_stats)
    write_summary(summary)
    print("총 파일", sum(ctx["attempts"] for ctx in summary_stats.values()), "개 처리 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
