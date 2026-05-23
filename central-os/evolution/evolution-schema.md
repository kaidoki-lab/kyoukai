# KYOUKAI evolution log schema

PHASE 7 evolution records explain how KYOUKAI changes over time.

## File

`central-os/evolution/evolution-log.json`

## Root

- `version`: schema version string
- `items`: evolution records

## Item fields

- `id`: evolution record id
- `date`: date of the change or record
- `title`: short title
- `trigger`: what caused the change or review
- `changedArea`: affected area
- `reason`: why the change exists
- `result`: what happened
- `nextObservation`: what should be watched next
- `status`: current status

## Status values

- `記録`
- `確認待ち`
- `反映済み`
- `保留`

## Rule

Evolution records are historical and planning notes.
They do not authorize automatic implementation.
