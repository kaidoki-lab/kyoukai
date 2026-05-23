# KYOUKAI cycle-map schema

PHASE 7 self-propagation entry layer.

This schema records how observation, proposal, generated content, route, and re-observation are connected.
It does not execute automation.

## File

`central-os/cycle/cycle-map.json`

## Root

- `version`: schema version string
- `items`: cycle connection records

## Item fields

- `id`: cycle record id
- `observationId`: related observation id
- `proposalId`: related supervisor proposal id
- `generatedId`: related generated content id
- `targetRoom`: target room label
- `targetRoute`: target route when already defined
- `flow`: short explanation of the circulation path
- `status`: current status
- `risk`: risk or caution
- `nextAction`: next manual action
- `humanApprovalRequired`: boolean. Initial records must be `true`

## Status values

- `未接続`
- `接続候補`
- `確認待ち`
- `採用候補`
- `反映済み`
- `保留`

## Rule

Cycle records are planning records only.
They must not trigger automatic implementation, posting, generation, or route changes.
