# Spring Boot 2 compatibility baseline

**Trigger:** The target package uses major 2. Do not apply the major-3+ profile here.

- Confirm Boot 2 BOM/plugin, JDK and actual javax-era dependency contracts. Preserve the selected Spring/Security versions; do not replace javax APIs or security configuration with Boot 3/4 examples.

- Keep bean ownership, transaction boundaries and MVC/WebFlux/request scope explicit. Validation/error/configuration semantics follow the actual Boot 2 project rather than a modern starter template.

- Validate modules through the real reactor/tasks, including context, transactions and external integration. Record support/maintenance constraints and migration gaps separately; acquiring this legacy guide does not upgrade the application.

Source: [Version-specific reference](https://docs.spring.io/spring-boot/docs/2.7.18/reference/html/). Reviewed 2026-10-13. Confirm exact patch, dependencies and current maintenance policy in the project.
