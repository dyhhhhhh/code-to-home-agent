# Home Agent Runtime

This is the first executable runtime prototype for the project.

It is intentionally small, but it is not a fan-only demo. The runtime treats
home devices as declared capabilities, then runs the same loop a code agent
uses in a repository:

```text
observe state
plan action
check policy
execute tool
verify result
write audit log
```

The first adapter is a dry-run Home Assistant adapter. It lets the runtime run
without real devices, so the safety and verification loop can be tested before
touching a home.

## Run the Dry-Run Demo

```bash
cd runtime
python -m home_agent_runtime --config examples/home.yaml --request "turn on the bedroom fan"
```

Expected behavior:

- Loads a home graph with multiple rooms and device types.
- Plans a high-level action from the request.
- Checks the action against local policy.
- Executes against the dry-run adapter.
- Verifies the result using declared verification rules.
- Appends an audit record to `runtime/examples/audit.log`.

## Design Boundary

The model should not receive raw, unlimited Home Assistant access. It should see
safe tools such as:

- `observe_home`
- `turn_on`
- `turn_off`
- `set_level`
- `set_temperature`
- `verify`

The runtime maps those tools to real devices only after policy checks pass.

## Real Home Assistant

The real Home Assistant adapter is the next implementation step. It should
translate approved runtime actions into Home Assistant API calls, while keeping
the same policy and verification layer.
