# Authoring notes — v2.7

- The first local preview launch was prevented from opening a socket. Temporary connection permission was granted; the application started without changing its security controls.
- An inherited control test expected changing a saved condition to discard the loaded case. v2.7 intentionally selects another condition from that same frozen packet. Its assertion was updated to require the new condition and export identity; changing the question still clears all evidence and disables export.
- An initial preview process ended; a replacement preview tab recovered access. Final screenshots include the copy label and back button. A separate synthetic live-worker browser attempt failed to connect and timed out; no Run click or synthetic/model generation occurred. The backend fixture was not changed to bypass this.
- All production generation code and data remain unchanged. The final display was exercised over frozen data and synthetic unit-test transport; browser-based fresh generation was not run.
