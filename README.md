# Gandi Dynamic DNS

Dynamic DNS Update Client for Gandi's LiveDNS.

## Run

#### Docker

Run this image with the `make run` shortcut, or manually with `docker run`. You'll need to define several environment variables for this container, and they are detailed below.

```shell
docker run --name gandi-ddns \
           --rm \
           -e GANDI_PAT="12343123abcd" \
           -e GANDI_DOMAIN="mydomain.net" \
           areg97/gandi-ddns:1.0
```

## Configuration

Configuration is accomplished through the use of environment variables. The inclusive list is below.

#### Environment Variables

| Variable          | Default                             | Description                                                                                                                                     |
| ----------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `GANDI_URL`       | `https://api.gandi.net/v5/livedns/domains/` | URL of the Gandi API.                                                                                                                           |
| `GANDI_PAT`       | -                                   | Personal Access Token for your [Gandi.net account](https://docs.gandi.net/en/managing_an_organization/organizations/personal_access_token.html) |
| `GANDI_DOMAIN`    | -                                   | Your Gandi.net domain name                                                                                                                      |
| `GANDI_RECORD`    | `@`                                 | Record to update with your IP address                                                                                                           |
| `GANDI_TTL`       | -                                   | TTL in seconds for the updated records                                                                                                          |
| `UPDATE_SCHEDULE` | `*/5 * * * *`                       | Cron-style schedule for dynamic-dns updates.                                                                                                    |
