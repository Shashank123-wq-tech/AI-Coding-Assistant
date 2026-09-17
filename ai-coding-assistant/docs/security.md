# Security

Generated code must never execute directly on the host machine.

The execution layer uses Docker sandboxing.

Security controls:

- Network isolation
- CPU limits
- Memory limits
- PID limits
- Non-root execution
- Repository path validation
- Test timeouts
- Agent iteration limits
- Patch validation
- Controlled tool execution
