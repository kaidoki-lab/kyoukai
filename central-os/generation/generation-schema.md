# generation-schema.md
# KYOUKAI generated-content.json schema

PHASE 5 の生成物管理レイヤーで扱う `central-os/generated/generated-content.json` の項目定義。

## Root

- `version`: schema version
- `items`: generated content candidates

## Item Fields

| field | type | required | note |
|---|---|---|---|
| `id` | string | yes | `gen_001` style stable id |
| `title` | string | yes | short human-readable title |
| `type` | string | yes | `image`, `short-video`, `music`, `text`, `room-event`, `sns-post`, `hyougi-log` |
| `targetRoom` | string | yes | target room name or system area |
| `targetRoute` | string | yes | route when confirmed, otherwise `未確定` |
| `source` | string | yes | origin of the idea or generation |
| `content` | string | yes | compact description of what would be generated |
| `usage` | string | yes | where/how it may be used after human review |
| `status` | string | yes | `候補`, `確認待ち`, `採用`, `使用済み`, `却下`, `保留` |
| `adopted` | boolean | yes | true only after human approval |
| `risk` | string | yes | implementation/worldview risk note |
| `notes` | string | no | operational note |

## Rule

Items are management records only. They do not mean assets have been generated or adopted.
