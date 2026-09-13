# Gandi Dynamic DNS

Dynamic DNS Update Client for Gandi's LiveDNS. Sends a notification via [Shoutrrr](https://containrrr.dev/shoutrrr/) when a DNS record is updated.

## Run

#### Docker

Run this image with the `make run` shortcut, or manually with `docker run`. You'll need to define several environment variables for this container, and they are detailed below.

```shell
docker run --name gandi-ddns \
           --rm \
           -e GANDI_PAT="12343123abcd" \
           -e GANDI_DOMAIN="mydomain.net" \
           -e SHOUTRRR_URL="telegram://token@telegram?chats=channel-1" \
           ghcr.io/tonio6797/gandi-ddns-updater:latest
```

Authentication is required. Use either a PAT or an API key.

## Configuration

Configuration is accomplished through the use of environment variables. The inclusive list is below.

#### Environment Variables

| Variable          | Default                             | Description                                                                                                                                     |
| ----------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `GANDI_URL`       | `https://api.gandi.net/v5/livedns/domains/` | URL of the Gandi API.                                                                                                                           |
| `GANDI_PAT`       | -                                   | Personal Access Token for your [Gandi.net account](https://docs.gandi.net/en/managing_an_organization/organizations/personal_access_token.html). **Required** if `GANDI_API_KEY` is not set. |
| `GANDI_API_KEY`   | -                                   | Gandi API key. **Required** if `GANDI_PAT` is not set. ⚠️ Deprecated by Gandi but still functional.                                            |
| `GANDI_DOMAIN`    | -                                   | Your Gandi.net domain name. **Required.**                                                                                                       |
| `GANDI_RECORD`    | `@`                                 | Record to update with your IP address                                                                                                           |
| `GANDI_TTL`       | -                                   | TTL in seconds for the updated records                                                                                                          |
| `SHOUTRRR_URL`    | -                                   | [Shoutrrr](https://containrrr.dev/shoutrrr/) notification URL(s). Comma-separated for multiple destinations (e.g. `telegram://...,slack://...`). |
| `UPDATE_SCHEDULE` | `*/5 * * * *`                       | Cron-style schedule for dynamic-dns updates.                                                                                                    |

> If both `GANDI_PAT` and `GANDI_API_KEY` are set, `GANDI_PAT` takes precedence.

## Notifications

When `SHOUTRRR_URL` is set, a notification is sent every time an `A` or `AAAA` record is updated, as well as when an update fails. No notification is sent when the external IP address is unchanged, or when the current public IP address cannot be fetched.

The notification body is the same text as the matching log line. On a successful update:

```
Set IP to 1.2.3.4 for A record '@' for mydomain.net
Set IP to 2a01:cb00::1 for AAAA record '@' for mydomain.net
```

On a failed update, the underlying error is appended:

```
Unable to update A record '@' for mydomain.net: 401 Client Error: Unauthorized for url: https://api.gandi.net/v5/livedns/domains/mydomain.net/records/@/A
```

`'@'` is the value of `GANDI_RECORD` and `mydomain.net` the value of `GANDI_DOMAIN`.
