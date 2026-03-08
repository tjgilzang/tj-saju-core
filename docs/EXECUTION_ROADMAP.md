# TJ Saju Long-term Execution Roadmap

## Principle
1. Program-by-program reverse engineering
2. Local extraction and logic verification first
3. Program-level DB upload second (Firebase)
4. Cross-program normalization and consistency checks
5. App integration after validated canonical model

## Program Order
1. 라이프운세 (MDB ready)
2. 사주백과 (DB/MB/PX mixed)
3. 사주도사 (DB + DOL mixed)
4. 사주나라 (ISO analysis after mount/extract)

## Current Status (2026-03-08)
- Program archive base created
- 4-program inventory established
- 라이프운세 MDB extracted to CSV

## Artifacts
- sources/raw/: immutable source copy
- extract/<program_id>/: per-program raw extraction outputs
- normalized/<program_id>/: cleaned tables per program
- reports/: index, checksum, profiling results

## Immediate Next 3 Steps
1. 라이프운세 table-level semantic mapping
2. 사주백과 DB/MB/PX parser strategy
3. Firebase schema for per-program raw collections
