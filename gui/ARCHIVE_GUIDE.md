# Archive completed runs without deleting evidence

The 60-run and size limits intentionally stop new work before an archive grows without bound. The archive command moves explicitly selected terminal runs into a new private directory. There is no automatic age-based deletion.

1. Stop the server with Ctrl+C. The command refuses the shared run lock if that archive is still in use.
2. Identify the full 32-character run IDs you want to retain elsewhere.
3. Preview, using a new destination on the same filesystem:

```bash
python3 -B app/archive_runs.py --config "$HOME/FilterFlip_v28_work/config.local.json" --destination "$HOME/FilterFlip_archive_01" --run-id YOUR_32_CHARACTER_RUN_ID
```

4. Check the listed IDs and destination. Run the same command with `--apply` to move them. Repeat `--run-id` for additional runs.
5. Restart the server. Archived records are retained on disk but are no longer available through its active-run URL.

The destination must be new, outside the active runs, release and model/input assets, with a user-owned parent that others cannot write. Each folder move is atomic on the same filesystem. A receipt records moved IDs after each move. A multi-run operation is not a single transaction: after interruption, inspect the receipt and both folders before continuing. The command never overwrites a destination or deletes evidence.

Running states and linked content are refused. If a historical interrupted job still says `running` in its saved state, retain it for manual review rather than changing its scientific status to make archiving succeed.

Operational files `.server.lock` and `security-events.jsonl` are not research runs. Security events rotate at 256 KiB with two backups (three files in total). These diagnostic logs have bounded retention; original run outputs remain separate.
