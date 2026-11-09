# BugDork v3.0 — Omni-Recon

BugDork v3.0 preserves the original BugDork Google Custom Search Engine (CSE) workflow and adds modular OSINT URL discovery.

## Preserved from the original project

- Async Google CSE dorking
- Round-robin API key rotation and quota tracking
- Retry with exponential backoff for transient errors
- Pagination (Google CSE maximum 100 results per query)
- TXT / JSON / CSV output
- Proxy and proxy-file support
- Secure provider config permissions and API-key redaction
- Existing Docker, CI, and pytest workflow

## New in v3.0

- Passive URL collection through GAU and Internet Archive CDX (Wayback)
- Optional active Katana crawling
- URL normalization, in-scope filtering, deduplication, and result caps
- Regex URL filtering
- Separate recon modules under `dorker/recon/`
- Recon does not require Google API credentials

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`

## Google dorking (original workflow)

```bash
bugdork -q "site:example.com inurl:admin"
bugdork -l dorks.txt -o results.txt
bugdork -l dorks.txt --format json -o results.json
```

Configure Google CSE credentials in the provider config file created on first run:

```yaml
google:
  - YOUR_API_KEY:YOUR_CSE_ID
```

Default config path is managed by `appdirs` under the user's config directory. Use `-cp /path/to/provider-config.yaml` to select a custom file.

## Omni-Recon

Passive sources only (no live target crawling):

```bash
bugdork -T example.com --urls-only
# or
bugdork -T example.com --recon
```

Passive + live Katana crawl (requires explicit confirmation):

```bash
bugdork -T example.com --recon --active
```

Choose execution mode:

```bash
bugdork -T example.com --urls-only --tool-mode auto
bugdork -T example.com --urls-only --tool-mode local
bugdork -T example.com --urls-only --tool-mode docker
```

- `auto`: prefer locally installed binary; otherwise Docker.
- `local`: use installed `gau` / `katana` binaries only.
- `docker`: use Docker containers only.

Install GAU and Katana separately if using local mode. Docker mode uses `ghcr.io/lc/gau:latest` and `projectdiscovery/katana:latest`.

Useful options:

- `-T, --target`: target domain.
- `--urls-only`: passive URL collection only.
- `--recon`: run recon workflow (passive by default).
- `--active`: add Katana live crawling; requires typing the domain to confirm.
- `--include-subdomains`: include subdomain URLs in results. Default scope is exact host only.
- `--max-urls`: cap output count (default 10,000).
- `--tool-mode auto|local|docker`: provider execution mode.
- `--format txt|json|csv`: output format.
- `-o, --output`: output path.

## Filter an existing URL list

```bash
bugdork -l urls.txt --filter "admin|login|\\.env"
bugdork -l urls.txt --filter "admin|login" -o filtered.txt
```

Filtering only matches URL strings. It does not fetch or disclose the contents of `.env`, `.git`, backup, or configuration resources.

## Safety / authorization

Use only domains you own or are explicitly authorized to assess. GAU and Wayback are passive URL sources; Katana sends requests to the live target and is disabled unless `--active` is supplied and the operator types the normalized target domain. Conservative rate and concurrency defaults are used. This tool discovers and filters URLs; it does not exploit vulnerabilities or bypass access controls.

Passive archive data may include old or sensitive-looking paths. Handle output as sensitive assessment data and store it securely.

## Project layout

```text
dorker/
  core/       # Original Google CSE engine and key pool
  recon/      # GAU, Wayback, Katana, URL scope and filtering
  output/     # Original report writers
  cli.py
  handler.py
  config.py
  models.py
tests/
```

## Development

```bash
pytest -q
ruff check dorker tests
black --check dorker tests
```

Docker test suite:

```bash
docker compose run --rm test
```
