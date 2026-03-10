# sources/raw

This folder contains the raw program archives that fuel the Firebase ingestion pipeline. Large binaries, such as `사주나라.iso`, are no longer kept directly under `sources/raw` because they prevent git pushes and Pages deployments.

- `사주나라.iso` has been relocated to `assets/large/사주나라.iso` (assets/ is git-ignored). Keep a local copy there for extraction, and use `reports/sajunara_iso.sha256` to verify integrity.
- When the ingestion script needs to process the ISO, copy it temporarily back into `sources/raw/` or point `source_paths` to the `assets/large` location.
