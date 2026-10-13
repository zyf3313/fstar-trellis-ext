# Rust project adaptation

Applies to Rust 1.x ownership/error/module contracts; edition and MSRV remain project constraints.

- Read Cargo.toml, workspace membership, features and actual modules. Keep ownership and borrowing explicit; avoid clones added only to hide unclear ownership.
- Preserve Result/Option contracts and existing error conversion. Do not add panic/unwrap to a recoverable boundary without a documented invariant.
- Keep unsafe code confined to justified boundaries with a stated safety contract and appropriate verification. Prefer existing safe abstractions.
- Follow existing formatting/lint/test commands and feature selection. Workspace tests and one package's tests have different coverage; record the selected scope.
- Verify resource/cancellation and async runtime ownership when applicable. Do not add a second runtime or change MSRV to fit helper code.

Confirm edition, MSRV and dependency-specific APIs before adopting examples from newer documentation.
