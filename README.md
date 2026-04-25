# streaming-domains

A merged, deduplicated domain list for major streaming services, auto-updated daily via GitHub Actions.

## Included sources

| Service | Upstream |
|---|---|
| Amazon Prime Video | `v2fly/domain-list-community/data/primevideo` |
| Disney+ | `v2fly/domain-list-community/data/disney` |
| Hulu | `v2fly/domain-list-community/data/hulu` |
| HBO / Max | `v2fly/domain-list-community/data/hbo` |
| Netflix | `v2fly/domain-list-community/data/netflix` |
| **Custom** | `lists/custom.txt` (yours to edit) |

## Output

The merged list is written to **`streaming-domains.txt`** in the root of the repo after every run.

```
https://raw.githubusercontent.com/<YOUR_USERNAME>/<YOUR_REPO>/main/streaming-domains.txt
```

## Adding custom domains

Edit [`lists/custom.txt`](lists/custom.txt).

```
# exact domain
domain:mystreaming.tv

# full subdomain
full:watch.example.com

# keyword match
keyword:vod

# regex
regexp:\.stream$
```

Pushing a change to `lists/custom.txt` automatically triggers a re-merge.

## How it works

```
GitHub Actions (daily 06:00 UTC  OR  on push to main)
        │
        ▼
  merge.py fetches all 5 upstream sources
        │
        ▼
  Merges + deduplicates with lists/custom.txt
        │
        ▼
  Writes streaming-domains.txt
        │
        ▼
  Commits & pushes (only if file changed)
```

## Manual trigger

Go to **Actions → Update streaming domains → Run workflow** to trigger an immediate update.

## Entry format reference

| Prefix | Meaning |
|---|---|
| `domain:` | Matches the domain and all subdomains |
| `full:` | Exact FQDN match only |
| `keyword:` | Matches if the domain contains this string |
| `regexp:` | Matches against the full domain using a regex |
