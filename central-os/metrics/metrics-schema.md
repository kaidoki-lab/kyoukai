# metrics-schema.md
# KYOUKAI observations.json schema

PHASE 6 の観測データ管理レイヤーで扱う `central-os/observations/observations.json` の項目定義。

## Root

- `version`: schema version
- `items`: observation records or manual seed observations

## Item Fields

| field | type | required | note |
|---|---|---|---|
| `id` | string | yes | stable observation id |
| `date` | string | yes | observation date or planned date |
| `type` | string | yes | observation type |
| `source` | string | yes | where the observation starts |
| `targetRoom` | string | yes | target room or layer |
| `targetRoute` | string | yes | confirmed route or `未確定` |
| `event` | string | yes | observed or planned event |
| `value` | number/string | yes | count, rate, or qualitative value |
| `notes` | string | no | operational note |
| `risk` | string | yes | privacy/worldview/implementation risk |
| `reflected` | boolean | yes | true only after human-approved reflection |

## Rule

PHASE 6 initial data is manual/temporary. It is not live analytics.
