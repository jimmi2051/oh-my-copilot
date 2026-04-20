Use oh-my-copilot project conventions:

- Prefer modular architecture: `orchestrator`, `agents`, `execution`, `state`, `cli`, `installer`.
- Keep generated artifacts and execution logs in `.omc/`.
- Follow autonomous loop discipline: plan -> execute -> review -> test -> fix.
- When using compatibility commands, preserve OMC-style semantics where possible.
