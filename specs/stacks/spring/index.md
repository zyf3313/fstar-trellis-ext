# Spring Boot conventions

**Trigger:** Project declares Spring Boot 3 or 4.

Read the actual Boot/BOM/plugin/JDK and module configuration. Preserve dependency direction, bean ownership, transaction boundaries, validation/error mapping and existing application entry points. Reuse the project's service/repository/adapter design rather than introducing a second component scan or data-access layer. Keep configuration and secrets with their actual environment owner.

Confirm version-specific package/API/configuration behavior from the appropriate Boot documentation and actual source. Validate selected modules through their real Maven/Gradle reactor and tests; a context startup test does not prove external database readiness. These are shared engineering contracts, not a claim that APIs in Boot 3 and 4 are interchangeable.

Source: https://docs.spring.io/spring-boot/ ; record source/target versions and local adjustments before implementation.
