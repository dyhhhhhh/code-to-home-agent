# Home Agent Runtime

The runtime is the part that turns a language model into a household operator.
It is the home equivalent of the execution shell around a code agent.

The model is not allowed to touch every device API directly. The runtime gives
it a controlled workbench:

```text
user request
  -> observe home state
  -> choose a high-level action
  -> check local policy
  -> execute through a device adapter
  -> verify with state or sensors
  -> write an audit log
```

## Not A Fan Demo

The first dry-run example includes a fan because a fan is low risk, easy to
verify, and useful for early testing. The runtime itself is device-neutral.

The example config already contains multiple device classes:

- fan: low-risk power control with wattage verification
- light: low-risk state control
- climate: medium-risk control with presence precondition
- lock: high-risk action requiring confirmation
- gas valve: critical action denied by default

That mix is intentional. A home agent should be able to see the whole home, but
it should not be able to freely mutate the whole home.

## Runtime Responsibilities

The runtime owns the parts that should remain local and deterministic:

- device and room registry
- action risk levels
- allowed and denied operations
- confirmation requirements
- precondition checks
- adapter calls
- verification rules
- audit log

The language model can help interpret a request and propose a plan. The runtime
decides whether that plan is allowed to touch the home.

## Device Capability Shape

Every device is declared as a set of actions:

```yaml
devices:
  fan:
    entity_id: switch.bedroom_fan
    type: fan
    risk_level: low
    actions:
      turn_on:
        risk_level: low
        requires_confirmation: false
        service: switch.turn_on
        verify:
          sensor: fan_power
          operator: ">"
          value: 10
```

This means the runtime knows:

- what the device is
- where the real backend entity lives
- what actions exist
- how risky each action is
- whether a human must confirm
- how to verify the action after execution

## Why This Mirrors Code Agents

A code agent does not just produce code. It reads files, edits them, runs tests,
checks errors, and reports the result.

A home agent should not just produce a command. It reads home state, executes an
approved action, checks sensors or device state, then reports the result.

```text
code agent: edit file -> run tests -> inspect failure
home agent: control device -> read sensors -> inspect failure
```

## Next Adapter

The current adapter is dry-run only. The next adapter should connect to Home
Assistant:

- read states from `/api/states`
- call services through `/api/services/<domain>/<service>`
- map runtime devices to Home Assistant entity IDs
- keep all policy and verification logic in the runtime

The model should still see only safe runtime tools, not raw Home Assistant
service access.
