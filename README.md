# BugDork

> Google dorking for ethical hackers — powered by Google Custom Search API.

## Features

- Async Google dorking via Custom Search JSON API
- Round-robin API key rotation with quota-exhaustion tracking
- Retry + exponential backoff on 429/5xx
- Pagination up to 100 results per dork (API cap)
- Output: `txt`, `json`, `csv`
- Proxy / proxy-file rotation
- Secure config (chmod 600, key redaction in logs)

## Install

```bash
pipx install git+https://github.com/pakulab/BugDork
# or
pip install git+https://github.com/pakulab/BugDork
