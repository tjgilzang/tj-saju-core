#!/usr/bin/env bash
set -euo pipefail

if ! command -v mdb-tables >/dev/null 2>&1; then
  echo "ERROR: mdbtools not found (mdb-tables)." >&2
  exit 1
fi

if [ "${#}" -lt 2 ]; then
  echo "Usage: $0 <program_id> <mdb_file_or_dir>" >&2
  echo "Example: $0 lifeunse '/path/to/LifeUnse'" >&2
  exit 1
fi

PROGRAM_ID="$1"
TARGET="$2"
BASE="/Users/tj/.openclaw/workspace/agents/architect/projects/tj-saju-master"
OUT_BASE="$BASE/extract/$PROGRAM_ID/mdb"

mkdir -p "$OUT_BASE"

MDB_FILES=()
if [ -d "$TARGET" ]; then
  while IFS= read -r f; do
    MDB_FILES+=("$f")
  done < <(find "$TARGET" -type f -iname '*.mdb' | sort)
else
  MDB_FILES+=("$TARGET")
fi

if [ "${#MDB_FILES[@]}" -eq 0 ]; then
  echo "No .mdb files found for: $TARGET" >&2
  exit 1
fi

INDEX_TSV="$OUT_BASE/index.tsv"
echo -e "mdb_file\ttable\trows\tcsv_path" > "$INDEX_TSV"

for MDB in "${MDB_FILES[@]}"; do
  MDB_BASENAME="$(basename "$MDB" .mdb)"
  MDB_DIR="$OUT_BASE/$MDB_BASENAME"
  mkdir -p "$MDB_DIR/tables"
  mdb-schema "$MDB" > "$MDB_DIR/schema.sql" || true
  mdb-tables -1 "$MDB" > "$MDB_DIR/tables.txt"

  while IFS= read -r TABLE; do
    [ -z "$TABLE" ] && continue
    CSV_PATH="$MDB_DIR/tables/${TABLE}.csv"
    mdb-export "$MDB" "$TABLE" > "$CSV_PATH" || true
    ROWS=0
    if [ -f "$CSV_PATH" ]; then
      # subtract header row if present
      LINE_COUNT="$(wc -l < "$CSV_PATH" | tr -d ' ')"
      if [ "$LINE_COUNT" -gt 0 ]; then
        ROWS=$((LINE_COUNT - 1))
      fi
    fi
    echo -e "${MDB}\t${TABLE}\t${ROWS}\t${CSV_PATH}" >> "$INDEX_TSV"
  done < "$MDB_DIR/tables.txt"
done

awk -F '\t' 'NR>1 {files[$1]=1; tables++; rows+=$3} END {print "mdb_files="length(files)" tables="tables" rows="rows}' "$INDEX_TSV" > "$OUT_BASE/summary.txt"
echo "DONE: $OUT_BASE"
