# Week-6 generation logging v1.1 — 24 October 2026

This is a generation-only amendment made before any new Week-6 answer call. The original v1 release and original answer queue remain unchanged. Use the separately versioned queue whose manifest binds this code. The request payloads, model identity, options, budgets and filter outputs are byte-identical to the original queue.

The worker now saves bounded raw HTTP response bytes (base64), their SHA-256 and request hash before parsing or validating them. Truncated, malformed and HTTP-error bodies therefore remain available when the unchanged fail-stop rule rejects them. Bodies exceeding the 2 MiB read limit are flagged as limited captures. Transport failures without a received body still have only fault metadata. No new retry, fallback, increased token budget or altered scoring is introduced.

`generate.py` supplies a fixed run-local response-log path. Capture files are evidence, never executable input. Synthetic tests cover retained malformed/incomplete bytes, size-limit flags and symlink refusal, alongside the existing suite. Preserved helper modules are needed for the original code identity and imports; do not use this directory to rebuild or run the old prepared filter panel. No new filter or challenge preparation is part of this amendment.
