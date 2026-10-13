# TypeScript reference adaptation

Read the actual tsconfig files, project references and package scripts before changing types. Preserve existing strictness, target/module resolution and public declaration compatibility.

Use types that reflect real null/optional/union states; validate untrusted values at runtime instead of asserting them into trusted types. Reuse the project's protocol types and error model. Avoid any/ts-ignore used only to suppress a contract mismatch.

The acquired Handbook page is a reference for language concepts, not evidence that a project should change its compiler target or framework. Compile the correct project-reference scope and verify relevant runtime behavior separately.
