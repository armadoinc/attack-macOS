# Security posture and deployment assumptions

## Purpose

This document states trust boundaries for running attack-macOS maintainer tooling in pipelines, labs, or integrations, and separates controls implemented in this repository from controls expected in the deployment environment.

## Responsible use and liability

**The project owner and contributors disclaim responsibility for misuse** of any script, YAML procedure, builder output, or documentation in this repository—including unauthorized access to systems, violation of law, or breach of policy.

Use this project only in environments you control or where you have **explicit, documented authorization**. A short public notice also appears in the root [README.md](README.md) under **Disclaimer (authorized use only)**.

## Assumptions

1. The organization operating the tooling controls access to the repository checkout (clone integrity, branch protection, and review before merge).
2. Pipeline and lab hosts are patched, least-privilege accounts are used for jobs, and network egress is restricted according to organizational policy.
3. Operators who invoke `cicd/` fetch or convert commands are authorized for those actions within their environment.
4. Maintainer Python applies CLI input checks documented in `docs/CICD/python_cli_security.md` and `cicd/validate_input.py` where wired; those checks reduce misuse of URLs and path tokens but do not replace host-level integrity controls.

## Audience

Security teams, DevOps engineers, and auditors evaluating how attack-macOS should run in controlled environments.

## Scope

In scope: repository-supplied maintainer scripts, documented CLI safety expectations, and deployment assumptions for integrity and isolation.

Out of scope: Organizational SOC2, ISO, or incident-response programs; configuration of specific commercial CI products.

## Details

### Controls provided in this repository

- `cicd/validate_input.py` and related patterns restrict URL schemes and token shapes for selected maintainer CLIs.
- `docs/CICD/python_cli_security.md` documents expectations (for example, avoiding `shell=True` with user-controlled strings).

### Controls expected in the deployment environment

- Checkout integrity and protected branches.
- Runner or container isolation, secrets management, and egress rules for steps that fetch third-party content (Atomic Red Team, LOOBins, and similar).
- Identity and access management for operators and service accounts.

### Optional integration patterns

Many teams run CI steps in containers or ephemeral VMs with read-only roots and network policies. Runtime choice (for example Docker, Kubernetes, or containerd-backed stacks) is an organizational decision.

## Exceptions

- Projects that vendor or repackage this repository may impose additional controls not listed here.

## References

- [README.md](README.md) — public disclaimer and credits.
- `docs/CICD/python_cli_security.md`
- `docs/Shipped_procedures_upstream_sources_and_maintainer_scripts.md`
- `docs/Standards/README.md`
- `cicd/README.md`

---

Last modified: 2026-05-15  
Last modified by: Documentation maintainers  
Version: 1.2.0
