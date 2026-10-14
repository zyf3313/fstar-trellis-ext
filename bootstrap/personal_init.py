#!/usr/bin/env python3
"""Safe wrapper around native ``trellis init`` for the personal library."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


EXPECTED_ORIGIN = "github.com/zyf3313/personal-trellis"
REGISTRY_REPOSITORY = "git@github.com:zyf3313/personal-trellis"
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
NATIVE_ERROR_RE = re.compile(r"^\s*Error:\s", re.MULTILINE)
SECRET_OPTION_RE = re.compile(r"(?:token|password|passwd|secret|api[-_]?key|dsn|credential)", re.I)
URI_CREDENTIAL_RE = re.compile(r"(?P<scheme>[a-z][a-z0-9+.-]*://)(?P<userinfo>[^/@\s]+)@", re.I)
QUERY_SECRET_RE = re.compile(
    r"([?&](?:token|password|passwd|secret|api[-_]?key|dsn|credential)=)[^&#\s]+",
    re.I,
)
ASSIGNMENT_SECRET_RE = re.compile(
    r"\b((?:token|password|passwd|secret|api[-_]?key|dsn|credential)\s*[=:]\s*)[^\s,;]+",
    re.I,
)
CONFLICTING_NATIVE_OPTIONS = ("--registry", "-r", "--template", "-t", "--append", "--overwrite")
REPORT_RELATIVE_PATH = Path(".trellis/personal/bootstrap-report.json")


class UsageError(ValueError):
    """Raised for wrapper usage that would break ownership boundaries."""


@dataclass
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class Runner:
    def __init__(self, env: Optional[Mapping[str, str]] = None) -> None:
        self.env = dict(os.environ if env is None else env)

    def which(self, executable: str) -> Optional[str]:
        return shutil.which(executable, path=self.env.get("PATH"))

    def run(self, argv: Sequence[str], cwd: Path, timeout_seconds: int = 900) -> CommandResult:
        try:
            completed = subprocess.run(
                list(argv),
                cwd=str(cwd),
                env=self.env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(124, "", f"command timed out after {timeout_seconds} seconds")
        except OSError as error:
            return CommandResult(127, "", str(error))
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_manifest() -> Dict[str, Any]:
    path = Path(__file__).with_name("tools.json")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("schema_version") != 1:
        raise UsageError("Unsupported bootstrap/tools.json schema_version")
    return data


def normalize_origin(value: str) -> str:
    normalized = value.strip().lower().replace("\\", "/")
    if normalized.startswith("git@github.com:"):
        normalized = "github.com/" + normalized.split(":", 1)[1]
    elif normalized.startswith("ssh://git@github.com/"):
        normalized = "github.com/" + normalized.split("github.com/", 1)[1]
    elif normalized.startswith("https://github.com/"):
        normalized = "github.com/" + normalized.split("github.com/", 1)[1]
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized.rstrip("/")


def git_output(root: Path, args: Sequence[str]) -> Optional[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def resolve_personal_ref(explicit: Optional[str], root: Optional[Path] = None) -> str:
    if explicit:
        if not SHA_RE.fullmatch(explicit):
            raise UsageError("--personal-ref must be a full 40-character Git commit SHA")
        return explicit.lower()

    checkout = repository_root() if root is None else root
    origin = git_output(checkout, ["remote", "get-url", "origin"])
    head = git_output(checkout, ["rev-parse", "HEAD"])
    if normalize_origin(origin or "") != EXPECTED_ORIGIN or not head or not SHA_RE.fullmatch(head):
        raise UsageError(
            "Cannot infer a trusted personal ref: run from the zyf3313/personal-trellis "
            "checkout or pass --personal-ref with a full commit SHA"
        )
    return head.lower()


def validate_native_args(args: Sequence[str]) -> None:
    for value in args:
        for owned in CONFLICTING_NATIVE_OPTIONS:
            attached_short_value = owned in {"-r", "-t"} and value.startswith(owned) and value != owned
            if value == owned or value.startswith(owned + "=") or attached_short_value:
                raise UsageError(
                    f"Native option {owned} is owned by trellis-personal and cannot be passed after --"
                )


def redact_text(value: str) -> str:
    value = URI_CREDENTIAL_RE.sub(lambda match: match.group("scheme") + "<redacted>@", value)
    value = QUERY_SECRET_RE.sub(lambda match: match.group(1) + "<redacted>", value)
    value = ASSIGNMENT_SECRET_RE.sub(lambda match: match.group(1) + "<redacted>", value)
    return value


def redact_argv(argv: Sequence[str]) -> List[str]:
    redacted: List[str] = []
    hide_next = False
    for raw in argv:
        value = str(raw)
        if hide_next:
            redacted.append("<redacted>")
            hide_next = False
            continue
        if value.startswith("-") and "=" in value:
            key, _ = value.split("=", 1)
            if SECRET_OPTION_RE.search(key):
                redacted.append(key + "=<redacted>")
                continue
        if value.startswith("-") and SECRET_OPTION_RE.search(value):
            redacted.append(value)
            hide_next = True
            continue
        redacted.append(redact_text(value))
    return redacted


def result_item(item_id: str, status: str, **details: Any) -> Dict[str, Any]:
    item = {"id": item_id, "status": status}
    item.update(details)
    return item


def is_code_project(project: Path) -> bool:
    markers = (
        "package.json",
        "pyproject.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "go.mod",
        "Cargo.toml",
        "Package.swift",
        "CMakeLists.txt",
    )
    if any((project / marker).is_file() for marker in markers):
        return True
    if any((project / directory).is_dir() for directory in ("src", "app", "lib")):
        return True
    extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs", ".swift", ".c", ".cc", ".cpp", ".h"}
    ignored = {".git", ".trellis", "node_modules", ".venv", "venv", "dist", "build"}
    visited = 0
    for current, dirs, files in os.walk(project):
        dirs[:] = [name for name in dirs if name not in ignored]
        for filename in files:
            visited += 1
            if Path(filename).suffix.lower() in extensions:
                return True
            if visited >= 500:
                return False
    return False


def home_directory(env: Mapping[str, str]) -> Path:
    configured = env.get("HOME")
    return Path(configured).expanduser() if configured else Path.home()


def skill_root(agent: str, manifest: Mapping[str, Any], env: Mapping[str, str]) -> Path:
    agents = manifest["skills"]["agents"]
    if agent not in agents:
        raise UsageError(f"Unsupported skill agent: {agent}")
    if agent == "codex" and env.get("CODEX_HOME"):
        return Path(env["CODEX_HOME"]).expanduser() / "skills"
    if agent == "claude-code" and env.get("CLAUDE_CONFIG_DIR"):
        return Path(env["CLAUDE_CONFIG_DIR"]).expanduser() / "skills"
    return home_directory(env) / agents[agent]


def skills_install_command(
    skills: Mapping[str, Any], missing_names: Sequence[str], agent: str
) -> List[str]:
    command = list(skills["installer"])
    for name in missing_names:
        command.extend([str(skills["skill_option"]), name])
    command.extend([
        str(skills["global_option"]),
        str(skills["agent_option"]),
        agent,
        str(skills["yes_option"]),
    ])
    return command


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def safe_report_destination(project: Path) -> Path:
    """Reject existing links/non-directories that could redirect the personal report."""
    destination = project / REPORT_RELATIVE_PATH
    current = project
    for index, part in enumerate(REPORT_RELATIVE_PATH.parts):
        current = current / part
        if current.is_symlink():
            raise UsageError(
                f"Refusing personal report path through symbolic link: {redact_text(str(current))}"
            )
        if index < len(REPORT_RELATIVE_PATH.parts) - 1 and current.exists() and not current.is_dir():
            raise UsageError(
                f"Personal report parent is not a directory: {redact_text(str(current))}"
            )
        if index == len(REPORT_RELATIVE_PATH.parts) - 1 and current.exists() and not current.is_file():
            raise UsageError(
                f"Personal report destination is not a regular file: {redact_text(str(current))}"
            )
    resolved_parent = destination.parent.resolve(strict=False)
    if not path_is_within(resolved_parent, project):
        raise UsageError("Personal report path resolves outside the target project")
    return destination


def codegraph_index_state(project: Path) -> str:
    path = project / ".codegraph"
    if path.is_symlink():
        return "unsafe"
    if not path.exists():
        return "missing"
    return "available" if path.is_dir() else "invalid"


def write_report(project: Path, report: Mapping[str, Any]) -> Path:
    destination = safe_report_destination(project)
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(destination.parent),
        prefix=".bootstrap-report.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(serialized)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(str(temporary), str(destination))
    return destination


def native_command(personal_ref: str, native_args: Sequence[str]) -> List[str]:
    registry = f"{REGISTRY_REPOSITORY}#{personal_ref}"
    return [
        "trellis",
        "init",
        "--registry",
        registry,
        "--template",
        "personal-core",
        "--append",
        *native_args,
    ]


def native_registry_matches(project: Path, personal_ref: str) -> bool:
    """Confirm native Trellis persisted the wrapper-owned fixed registry selection."""
    config = project / ".trellis/config.yaml"
    try:
        lines = config.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return False

    expected_source = f"{REGISTRY_REPOSITORY}#{personal_ref}"
    in_registry = False
    in_spec = False
    values: Dict[str, str] = {}
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        if indent == 0:
            in_registry = stripped == "registry:"
            in_spec = False
            continue
        if not in_registry:
            continue
        if indent == 2:
            in_spec = stripped == "spec:"
            continue
        if not in_spec or indent <= 2 or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key not in {"source", "template"}:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values == {"source": expected_source, "template": "personal-core"}


def native_init_succeeded(result: CommandResult, project: Path, personal_ref: str) -> bool:
    combined = result.stdout + "\n" + result.stderr
    return (
        result.returncode == 0
        and not NATIVE_ERROR_RE.search(combined)
        and (project / ".trellis/spec/personal-index.md").is_file()
        and native_registry_matches(project, personal_ref)
    )


def planned_actions(
    project: Path,
    personal_ref: str,
    native_args: Sequence[str],
    agent: str,
    skip_tools: bool,
    manifest: Mapping[str, Any],
    runner: Runner,
    platform_name: str,
) -> Dict[str, Any]:
    actions: List[Dict[str, Any]] = [
        {"id": "native_trellis_init", "command": redact_argv(native_command(personal_ref, native_args))}
    ]
    if not skip_tools:
        for item_id, config in manifest["automatic"].items():
            executable = config["executable"]
            if runner.which(executable):
                actions.append({"id": item_id, "action": "already_available"})
            elif item_id == "github_cli":
                if platform_name == "darwin" and runner.which("brew"):
                    actions.append({"id": item_id, "command": config["macos_installer"]})
                else:
                    actions.append({
                        "id": item_id,
                        "action": "unsupported",
                        "next_action": "Install GitHub CLI with the official package instructions, then rerun the wrapper.",
                    })
            elif not runner.which("npm"):
                actions.append({
                    "id": item_id,
                    "action": "unsupported",
                    "next_action": "Install Node.js/npm, then rerun the wrapper.",
                })
            else:
                actions.append({"id": item_id, "command": config["installer"]})
        skills = manifest["skills"]
        root = skill_root(agent, manifest, runner.env)
        missing_skills: List[str] = []
        for name in skills["names"]:
            if (root / name / "SKILL.md").is_file():
                actions.append({"id": f"skill:{name}", "action": "already_available"})
            else:
                missing_skills.append(name)
        if missing_skills and runner.which("npx"):
            actions.append({
                "id": "emil_skills_install",
                "command": skills_install_command(skills, missing_skills, agent),
                "skills": missing_skills,
            })
        elif missing_skills:
            for name in missing_skills:
                actions.append({
                    "id": f"skill:{name}",
                    "action": "unsupported",
                    "next_action": skills["next_action"],
                })
        if is_code_project(project):
            index_state = codegraph_index_state(project)
            if index_state == "missing" and (runner.which("codegraph") or runner.which("npm")):
                actions.append({"id": "codegraph_project_index", "command": ["codegraph", "init"]})
            elif index_state == "missing":
                actions.append({
                    "id": "codegraph_project_index",
                    "action": "unsupported",
                    "next_action": "Install CodeGraph, then rerun the wrapper to initialize the project index.",
                })
            elif index_state in {"unsafe", "invalid"}:
                actions.append({
                    "id": "codegraph_project_index",
                    "action": "unsupported",
                    "next_action": "Review and move or remove the non-directory/symbolic-link .codegraph path.",
                })
    return {
        "schema_version": 1,
        "mode": "dry_run",
        "project": redact_text(str(project)),
        "personal_ref": personal_ref,
        "agent": agent,
        "actions": actions,
        "deferred": manifest["deferred"],
    }


def install_executable(
    item_id: str,
    config: Mapping[str, Any],
    command: Sequence[str],
    runner: Runner,
    project: Path,
) -> Dict[str, Any]:
    result = runner.run(command, project)
    if result.returncode != 0:
        return result_item(
            item_id,
            "failed",
            command=redact_argv(command),
            exit_code=result.returncode,
            message=f"installer exited with code {result.returncode}; inspect the installer directly for diagnostics",
        )
    executable = str(config["executable"])
    if not runner.which(executable):
        return result_item(
            item_id,
            "failed",
            command=redact_argv(command),
            exit_code=0,
            message=f"installer exited successfully but {executable} is still unavailable on PATH",
        )
    return result_item(item_id, "installed", command=redact_argv(command), source=config.get("source"))


def prepare_tools(
    project: Path,
    agent: str,
    manifest: Mapping[str, Any],
    runner: Runner,
    platform_name: str,
) -> Tuple[List[Dict[str, Any]], bool]:
    results: List[Dict[str, Any]] = []
    automatic = manifest["automatic"]

    for item_id in ("codegraph", "qmd"):
        config = automatic[item_id]
        if runner.which(config["executable"]):
            results.append(result_item(item_id, "already_available"))
            continue
        if not runner.which("npm"):
            results.append(result_item(item_id, "unsupported", next_action="Install Node.js/npm, then rerun the wrapper."))
            continue
        results.append(install_executable(item_id, config, config["installer"], runner, project))

    gh = automatic["github_cli"]
    if runner.which(gh["executable"]):
        results.append(result_item("github_cli", "already_available"))
    elif platform_name == "darwin" and runner.which("brew"):
        results.append(install_executable("github_cli", gh, gh["macos_installer"], runner, project))
    elif platform_name.startswith("linux"):
        results.append(result_item(
            "github_cli",
            "unsupported",
            next_action="Install GitHub CLI with the official package instructions for this Linux distribution; no sudo command is run automatically.",
        ))
    else:
        results.append(result_item(
            "github_cli",
            "unsupported",
            next_action="Install GitHub CLI from https://cli.github.com/ and rerun the wrapper.",
        ))

    skills = manifest["skills"]
    root = skill_root(agent, manifest, runner.env)
    missing_skills: List[str] = []
    for name in skills["names"]:
        item_id = f"skill:{name}"
        installed_path = root / name / "SKILL.md"
        if installed_path.is_file():
            results.append(result_item(item_id, "already_available", agent=agent))
            continue
        missing_skills.append(name)

    skills_command_failed = False
    if missing_skills and not runner.which("npx"):
        for name in missing_skills:
            results.append(result_item(
                f"skill:{name}",
                "unsupported",
                agent=agent,
                next_action=skills["next_action"],
            ))
    elif missing_skills:
        command = skills_install_command(skills, missing_skills, agent)
        install_result = runner.run(command, project)
        skills_command_failed = install_result.returncode != 0
        for name in missing_skills:
            item_id = f"skill:{name}"
            details: Dict[str, Any] = {
                "agent": agent,
                "command": redact_argv(command),
                "source": skills.get("source"),
            }
            if install_result.returncode != 0:
                details["exit_code"] = install_result.returncode
            if (root / name / "SKILL.md").is_file():
                if install_result.returncode != 0:
                    details["message"] = (
                        "The installer exited non-zero, but this Skill was verified in the target directory."
                    )
                results.append(result_item(item_id, "installed", **details))
            else:
                details["message"] = (
                    "The Emil Skills installer did not create SKILL.md in the selected Agent directory."
                )
                results.append(result_item(item_id, "failed", **details))

    codegraph_result = next(item for item in results if item["id"] == "codegraph")
    if not is_code_project(project):
        results.append(result_item(
            "codegraph_project_index",
            "deferred",
            reason="The target is not currently identifiable as a code project.",
        ))
    elif codegraph_index_state(project) == "available":
        results.append(result_item("codegraph_project_index", "already_available"))
    elif codegraph_index_state(project) in {"unsafe", "invalid"}:
        results.append(result_item(
            "codegraph_project_index",
            "unsupported",
            next_action="Move or remove the non-directory/symbolic-link .codegraph path, then rerun after reviewing it.",
        ))
    elif codegraph_result["status"] in {"installed", "already_available"} and runner.which("codegraph"):
        command = ["codegraph", "init"]
        result = runner.run(command, project)
        if result.returncode == 0 and codegraph_index_state(project) == "available":
            results.append(result_item("codegraph_project_index", "installed", command=command))
        elif result.returncode == 0:
            results.append(result_item(
                "codegraph_project_index",
                "failed",
                command=command,
                exit_code=0,
                message="codegraph init exited successfully but .codegraph was not created",
            ))
        else:
            results.append(result_item(
                "codegraph_project_index",
                "failed",
                command=command,
                exit_code=result.returncode,
                message=f"codegraph init exited with code {result.returncode}; inspect it directly for diagnostics",
            ))
    else:
        results.append(result_item(
            "codegraph_project_index",
            "failed",
            message="CodeGraph is unavailable, so the project index was not initialized.",
        ))

    return results, skills_command_failed or any(item["status"] == "failed" for item in results)


def deferred_results(manifest: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [result_item(item["id"], "deferred", reason=item["reason"]) for item in manifest["deferred"]]


def parser_for(manifest: Mapping[str, Any]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trellis-personal")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init = subparsers.add_parser("init", help="Run native Trellis init and safe personal preparation")
    init.add_argument("--project", default=".", help="Existing target project directory")
    init.add_argument("--personal-ref", help="Full 40-character personal-library commit SHA")
    init.add_argument("--dry-run", action="store_true", help="Print the plan without running or writing anything")
    init.add_argument("--skip-tools", action="store_true", help="Run native init but defer tool preparation")
    init.add_argument("--agent", choices=sorted(manifest["skills"]["agents"]), default="codex")
    init.add_argument("native_args", nargs=argparse.REMAINDER, help="Native trellis init arguments after --")
    return parser


def execute_init(
    namespace: argparse.Namespace,
    manifest: Mapping[str, Any],
    runner: Runner,
    platform_name: str,
) -> int:
    if platform_name != "darwin" and not platform_name.startswith("linux"):
        raise UsageError("trellis-personal init currently supports only macOS and Linux")
    project = Path(namespace.project).expanduser().resolve()
    if not project.is_dir():
        raise UsageError(
            f"--project must name an existing directory: {redact_text(str(project))}"
        )
    native_args = list(namespace.native_args)
    if native_args and native_args[0] == "--":
        native_args = native_args[1:]
    validate_native_args(native_args)
    personal_ref = resolve_personal_ref(namespace.personal_ref)
    safe_report_destination(project)

    if namespace.dry_run:
        plan = planned_actions(
            project,
            personal_ref,
            native_args,
            namespace.agent,
            namespace.skip_tools,
            manifest,
            runner,
            platform_name,
        )
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    command = native_command(personal_ref, native_args)
    native = runner.run(command, project)
    native_success = native_init_succeeded(native, project, personal_ref)
    report: Dict[str, Any] = {
        "schema_version": 1,
        "mode": "apply",
        "project": redact_text(str(project)),
        "personal_ref": personal_ref,
        "agent": namespace.agent,
        "native_init": {
            "status": "success" if native_success else "failed",
            "exit_code": native.returncode,
            "command": redact_argv(command),
        },
        "tools": [],
        "deferred": deferred_results(manifest),
        "overall": "complete",
    }
    if not native_success:
        report["native_init"]["message"] = (
            "trellis init did not complete the personal-core import; inspect the native command directly "
            f"(reported exit code {native.returncode})"
        )
        report["overall"] = "failed"
        destination = write_report(project, report)
        print(f"Native Trellis initialization failed; report: {redact_text(str(destination))}", file=sys.stderr)
        return native.returncode or 1

    if namespace.skip_tools:
        report["tools"] = [result_item(
            "tool_preparation",
            "deferred",
            reason="Tool preparation was disabled with --skip-tools.",
        )]
    else:
        tool_results, failed = prepare_tools(project, namespace.agent, manifest, runner, platform_name)
        report["tools"] = tool_results
        if failed:
            report["overall"] = "partial"

    destination = write_report(project, report)
    print(f"Personal Trellis initialization {report['overall']}; report: {redact_text(str(destination))}")
    return 2 if report["overall"] == "partial" else 0


def main(argv: Optional[Sequence[str]] = None, *, platform_name: Optional[str] = None) -> int:
    manifest = load_manifest()
    parser = parser_for(manifest)
    try:
        namespace = parser.parse_args(argv)
        if namespace.command != "init":
            raise UsageError("Only the init command is supported")
        return execute_init(namespace, manifest, Runner(), platform_name or sys.platform)
    except UsageError as error:
        parser.error(str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
