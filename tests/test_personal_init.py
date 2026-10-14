from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "bootstrap" / "personal_init.py"
SPEC = importlib.util.spec_from_file_location("personal_init", MODULE_PATH)
assert SPEC and SPEC.loader
personal_init = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = personal_init
SPEC.loader.exec_module(personal_init)

REF = "a" * 40
SYSTEM_PATH = "/usr/bin:/bin"


FAKE_PROGRAM = r'''#!/usr/bin/python3
import json
import os
import stat
import sys
from pathlib import Path

name = Path(sys.argv[0]).name
log = Path(os.environ["FAKE_LOG"])
with log.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps({"name": name, "args": sys.argv[1:], "cwd": os.getcwd()}) + "\n")

if name == "trellis":
    personal_index = Path(".trellis/spec/personal-index.md")
    personal_index.parent.mkdir(parents=True, exist_ok=True)
    personal_index.write_text("# fake personal index\n", encoding="utf-8")
    if os.environ.get("FAKE_TRELLIS_SKIP_REGISTRY") != "1":
        arguments = sys.argv[1:]
        source = arguments[arguments.index("--registry") + 1]
        template = arguments[arguments.index("--template") + 1]
        config = Path(".trellis/config.yaml")
        config.write_text(
            "registry:\n"
            "  spec:\n"
            f"    source: {source}\n"
            f"    template: {template}\n",
            encoding="utf-8",
        )
    message = os.environ.get("FAKE_TRELLIS_MESSAGE", "")
    if message:
        print(message, file=sys.stderr)
    raise SystemExit(int(os.environ.get("FAKE_TRELLIS_EXIT", "0")))

if name == "npm":
    package = sys.argv[-1]
    failed_package = os.environ.get("FAKE_FAIL_PACKAGE")
    if failed_package and failed_package in package:
        print("installer failed", file=sys.stderr)
        raise SystemExit(9)
    target = None
    if "codegraph" in package:
        target = "codegraph"
    elif "qmd" in package:
        target = "qmd"
    if target:
        path = Path(os.environ["FAKE_BIN"]) / target
        path.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
    raise SystemExit(0)

if name == "npx":
    arguments = sys.argv[1:]
    skills = [arguments[index + 1] for index, value in enumerate(arguments) if value == "--skill"]
    agent = arguments[arguments.index("-a") + 1]
    if agent == "codex":
        config = Path(os.environ.get("CODEX_HOME", str(Path(os.environ["HOME"]) / ".codex")))
    else:
        config = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path(os.environ["HOME"]) / ".claude")))
    failed_skill = os.environ.get("FAKE_FAIL_SKILL")
    for skill in skills:
        if failed_skill == skill:
            continue
        path = config / "skills" / skill / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fake skill\n", encoding="utf-8")
    if failed_skill in skills:
        print("skill failed", file=sys.stderr)
        raise SystemExit(8)
    raise SystemExit(int(os.environ.get("FAKE_NPX_EXIT_AFTER_INSTALL", "0")))

if name == "brew":
    if sys.argv[1:] == ["install", "gh"]:
        path = Path(os.environ["FAKE_BIN"]) / "gh"
        path.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
    raise SystemExit(0)

if name == "codegraph" and sys.argv[1:] == ["init"]:
    Path(".codegraph").mkdir(exist_ok=True)
raise SystemExit(0)
'''


class PersonalInitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project"
        self.project.mkdir()
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.home = self.base / "home"
        self.home.mkdir()
        self.log = self.base / "commands.jsonl"
        self.env = {
            "HOME": str(self.home),
            "PATH": f"{self.bin}:{SYSTEM_PATH}",
            "FAKE_BIN": str(self.bin),
            "FAKE_LOG": str(self.log),
            "PYTHONDONTWRITEBYTECODE": "1",
        }

    def fake(self, name: str) -> Path:
        path = self.bin / name
        path.write_text(FAKE_PROGRAM, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def add_all_tools(self, *, skills: bool = True) -> None:
        for name in ("trellis", "npm", "npx", "codegraph", "qmd", "gh"):
            self.fake(name)
        if skills:
            manifest = personal_init.load_manifest()
            for name in manifest["skills"]["names"]:
                target = self.home / ".codex" / "skills" / name / "SKILL.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("# existing\n", encoding="utf-8")

    def invoke(self, arguments, *, platform="linux"):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, self.env, clear=True), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = personal_init.main(arguments, platform_name=platform)
        return code, stdout.getvalue(), stderr.getvalue()

    def commands(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def report(self):
        return json.loads((self.project / ".trellis/personal/bootstrap-report.json").read_text(encoding="utf-8"))

    def test_dry_run_has_no_external_mutation_and_shows_fixed_ref(self):
        self.fake("trellis")
        before = sorted(path.relative_to(self.project) for path in self.project.rglob("*"))
        code, output, _ = self.invoke([
            "init", "--project", str(self.project), "--personal-ref", REF, "--dry-run", "--", "--codex",
        ])
        self.assertEqual(0, code)
        self.assertEqual(before, sorted(path.relative_to(self.project) for path in self.project.rglob("*")))
        self.assertEqual([], self.commands())
        plan = json.loads(output)
        command = plan["actions"][0]["command"]
        self.assertIn(f"git@github.com:zyf3313/personal-trellis#{REF}", command)
        self.assertIn("--codex", command)
        self.assertEqual("dry_run", plan["mode"])

    def test_native_arguments_and_owned_registry_are_applied_first(self):
        self.add_all_tools()
        (self.project / ".codegraph").mkdir()
        code, _, _ = self.invoke([
            "init", "--project", str(self.project), "--personal-ref", REF, "--", "--codex", "--user", "Alice",
        ])
        self.assertEqual(0, code)
        commands = self.commands()
        self.assertEqual(["trellis"], [item["name"] for item in commands])
        args = commands[0]["args"]
        self.assertEqual("init", args[0])
        self.assertEqual(f"git@github.com:zyf3313/personal-trellis#{REF}", args[args.index("--registry") + 1])
        self.assertEqual("personal-core", args[args.index("--template") + 1])
        self.assertIn("--append", args)
        self.assertEqual(["--codex", "--user", "Alice"], args[-3:])
        self.assertEqual("success", self.report()["native_init"]["status"])

    def test_conflicting_native_option_is_rejected_before_execution(self):
        self.fake("trellis")
        conflicts = (
            ["--registry", "other"],
            ["-r", "other"],
            ["-rother"],
            ["--template=other"],
            ["-tother"],
            ["--append"],
            ["--overwrite"],
        )
        for conflict in conflicts:
            with self.subTest(conflict=conflict):
                with mock.patch.dict(os.environ, self.env, clear=True), self.assertRaises(SystemExit) as caught:
                    personal_init.main([
                        "init", "--project", str(self.project), "--personal-ref", REF, "--", *conflict,
                    ])
                self.assertEqual(2, caught.exception.code)
        self.assertEqual([], self.commands())

    def test_dry_run_reports_unavailable_prerequisites_without_writing(self):
        self.fake("trellis")
        code, output, _ = self.invoke([
            "init", "--project", str(self.project), "--personal-ref", REF, "--dry-run",
        ])
        self.assertEqual(0, code)
        plan = json.loads(output)
        actions = {item["id"]: item for item in plan["actions"]}
        self.assertEqual("unsupported", actions["codegraph"]["action"])
        self.assertEqual("unsupported", actions["qmd"]["action"])
        self.assertEqual("unsupported", actions["skill:emil-design-eng"]["action"])
        self.assertFalse((self.project / ".trellis").exists())

    def test_dry_run_shows_one_pinned_emil_install_command(self):
        self.fake("trellis")
        self.fake("npx")
        manifest = personal_init.load_manifest()
        existing = manifest["skills"]["names"][0]
        target = self.home / ".codex" / "skills" / existing / "SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text("# existing\n", encoding="utf-8")

        code, output, _ = self.invoke([
            "init", "--project", str(self.project), "--personal-ref", REF, "--dry-run",
        ])

        self.assertEqual(0, code)
        plan = json.loads(output)
        actions = {item["id"]: item for item in plan["actions"]}
        missing = manifest["skills"]["names"][1:]
        expected = ["npx", "-y", "skills@1.7.0", "add", "emilkowalski/skills"]
        for name in missing:
            expected.extend(["--skill", name])
        expected.extend(["-g", "-a", "codex", "--yes"])
        self.assertEqual(expected, actions["emil_skills_install"]["command"])
        self.assertEqual(missing, actions["emil_skills_install"]["skills"])
        self.assertEqual("already_available", actions[f"skill:{existing}"]["action"])
        self.assertEqual([], self.commands())

    def test_native_failure_short_circuits_tool_preparation(self):
        self.fake("trellis")
        self.fake("npm")
        self.env["FAKE_TRELLIS_EXIT"] = "7"
        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])
        self.assertEqual(7, code)
        self.assertEqual(["trellis"], [item["name"] for item in self.commands()])
        report = self.report()
        self.assertEqual("failed", report["overall"])
        self.assertEqual([], report["tools"])

    def test_native_zero_exit_with_error_text_is_failure(self):
        self.fake("trellis")
        self.fake("npm")
        self.env["FAKE_TRELLIS_MESSAGE"] = "Error: registry is unavailable"
        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])
        self.assertEqual(1, code)
        self.assertEqual(["trellis"], [item["name"] for item in self.commands()])
        self.assertEqual("failed", self.report()["native_init"]["status"])

    def test_native_zero_exit_without_imported_personal_index_is_failure(self):
        self.fake("trellis")
        self.fake("npm")
        with mock.patch.object(personal_init, "native_init_succeeded", return_value=False):
            code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])
        self.assertEqual(1, code)
        self.assertEqual(["trellis"], [item["name"] for item in self.commands()])
        self.assertEqual("failed", self.report()["native_init"]["status"])

    def test_native_zero_exit_with_stale_index_but_no_fixed_registry_is_failure(self):
        self.fake("trellis")
        stale = self.project / ".trellis/spec/personal-index.md"
        stale.parent.mkdir(parents=True)
        stale.write_text("# stale personal index\n", encoding="utf-8")
        self.env["FAKE_TRELLIS_SKIP_REGISTRY"] = "1"

        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])

        self.assertEqual(1, code)
        self.assertEqual(["trellis"], [item["name"] for item in self.commands()])
        self.assertEqual("failed", self.report()["native_init"]["status"])

    def test_existing_tools_are_idempotent_and_missing_code_index_is_initialized(self):
        self.add_all_tools()
        (self.project / "package.json").write_text("{}\n", encoding="utf-8")
        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])
        self.assertEqual(0, code)
        self.assertEqual(["trellis", "codegraph"], [item["name"] for item in self.commands()])
        self.assertTrue((self.project / ".codegraph").is_dir())
        statuses = {item["id"]: item["status"] for item in self.report()["tools"]}
        self.assertEqual("already_available", statuses["codegraph"])
        self.assertEqual("installed", statuses["codegraph_project_index"])
        self.assertNotIn("npm", [item["name"] for item in self.commands()])
        self.assertNotIn("npx", [item["name"] for item in self.commands()])

    def test_missing_tools_install_and_deferred_boundaries_are_reported(self):
        for name in ("trellis", "npm", "npx"):
            self.fake(name)
        (self.project / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])
        self.assertEqual(0, code)
        names = [item["name"] for item in self.commands()]
        self.assertEqual("trellis", names[0])
        self.assertEqual(2, names.count("npm"))
        self.assertEqual(1, names.count("npx"))
        self.assertEqual("codegraph", names[-1])
        report = self.report()
        statuses = {item["id"]: item["status"] for item in report["tools"]}
        self.assertEqual("installed", statuses["codegraph"])
        self.assertEqual("installed", statuses["qmd"])
        self.assertEqual("unsupported", statuses["github_cli"])
        self.assertEqual("installed", statuses["skill:emil-design-eng"])
        self.assertEqual("installed", statuses["skill:mobile-native"])
        self.assertEqual("installed", statuses["codegraph_project_index"])
        self.assertEqual(
            {"qmd_collection_embed_model", "github_auth", "dbhub_connection_write", "exa_api_key"},
            {item["id"] for item in report["deferred"]},
        )

    def test_installer_failure_preserves_native_init_and_returns_partial(self):
        for name in ("trellis", "npm", "npx"):
            self.fake(name)
        self.env["FAKE_FAIL_PACKAGE"] = "@tobilu/qmd"
        (self.project / "src").mkdir()
        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])
        self.assertEqual(2, code)
        report = self.report()
        self.assertEqual("success", report["native_init"]["status"])
        self.assertEqual("partial", report["overall"])
        statuses = {item["id"]: item["status"] for item in report["tools"]}
        self.assertEqual("failed", statuses["qmd"])
        self.assertEqual("installed", statuses["codegraph"])
        self.assertEqual("installed", statuses["skill:mobile-native"])

    def test_emil_install_is_single_pinned_call_and_skips_existing_skill(self):
        for name in ("trellis", "npx", "codegraph", "qmd", "gh"):
            self.fake(name)
        manifest = personal_init.load_manifest()
        existing = manifest["skills"]["names"][0]
        existing_path = self.home / ".codex" / "skills" / existing / "SKILL.md"
        existing_path.parent.mkdir(parents=True)
        existing_path.write_text("# existing\n", encoding="utf-8")

        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])

        self.assertEqual(0, code)
        npx_calls = [item for item in self.commands() if item["name"] == "npx"]
        self.assertEqual(1, len(npx_calls))
        missing = manifest["skills"]["names"][1:]
        expected = ["-y", "skills@1.7.0", "add", "emilkowalski/skills"]
        for name in missing:
            expected.extend(["--skill", name])
        expected.extend(["-g", "-a", "codex", "--yes"])
        self.assertEqual(expected, npx_calls[0]["args"])
        statuses = {item["id"]: item["status"] for item in self.report()["tools"]}
        self.assertEqual("already_available", statuses[f"skill:{existing}"])
        for name in missing:
            self.assertEqual("installed", statuses[f"skill:{name}"])

    def test_missing_npx_reports_each_emil_skill_as_unsupported(self):
        for name in ("trellis", "codegraph", "qmd", "gh"):
            self.fake(name)

        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])

        self.assertEqual(0, code)
        self.assertNotIn("npx", [item["name"] for item in self.commands()])
        skills = [item for item in self.report()["tools"] if item["id"].startswith("skill:")]
        self.assertEqual(4, len(skills))
        self.assertEqual({"unsupported"}, {item["status"] for item in skills})
        self.assertTrue(all("next_action" in item for item in skills))

    def test_emil_install_verifies_codex_home(self):
        for name in ("trellis", "npx", "codegraph", "qmd", "gh"):
            self.fake(name)
        custom = self.base / "custom-codex"
        self.env["CODEX_HOME"] = str(custom)

        code, _, _ = self.invoke([
            "init", "--project", str(self.project), "--personal-ref", REF,
        ])

        self.assertEqual(0, code)
        manifest = personal_init.load_manifest()
        for name in manifest["skills"]["names"]:
            self.assertTrue((custom / "skills" / name / "SKILL.md").is_file())
        npx_call = next(item for item in self.commands() if item["name"] == "npx")
        self.assertEqual("codex", npx_call["args"][npx_call["args"].index("-a") + 1])

    def test_emil_install_verifies_claude_config_directory(self):
        for name in ("trellis", "npx", "codegraph", "qmd", "gh"):
            self.fake(name)
        custom = self.base / "custom-claude"
        self.env["CLAUDE_CONFIG_DIR"] = str(custom)

        code, _, _ = self.invoke([
            "init", "--project", str(self.project), "--personal-ref", REF,
            "--agent", "claude-code",
        ])

        self.assertEqual(0, code)
        manifest = personal_init.load_manifest()
        for name in manifest["skills"]["names"]:
            self.assertTrue((custom / "skills" / name / "SKILL.md").is_file())
        npx_call = next(item for item in self.commands() if item["name"] == "npx")
        self.assertEqual("claude-code", npx_call["args"][npx_call["args"].index("-a") + 1])

    def test_emil_nonzero_exit_uses_verified_files_and_returns_partial(self):
        for name in ("trellis", "npx", "codegraph", "qmd", "gh"):
            self.fake(name)
        self.env["FAKE_NPX_EXIT_AFTER_INSTALL"] = "8"

        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])

        self.assertEqual(2, code)
        report = self.report()
        self.assertEqual("partial", report["overall"])
        skills = [item for item in report["tools"] if item["id"].startswith("skill:")]
        self.assertEqual(4, len(skills))
        self.assertEqual({"installed"}, {item["status"] for item in skills})
        self.assertEqual({8}, {item["exit_code"] for item in skills})

    def test_emil_missing_output_is_failed_after_single_call(self):
        for name in ("trellis", "npx", "codegraph", "qmd", "gh"):
            self.fake(name)
        self.env["FAKE_FAIL_SKILL"] = "review-animations"

        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])

        self.assertEqual(2, code)
        self.assertEqual(1, [item["name"] for item in self.commands()].count("npx"))
        statuses = {item["id"]: item["status"] for item in self.report()["tools"]}
        self.assertEqual("failed", statuses["skill:review-animations"])
        self.assertEqual("installed", statuses["skill:emil-design-eng"])

    def test_macos_uses_existing_homebrew_for_missing_github_cli(self):
        self.add_all_tools()
        (self.bin / "gh").unlink()
        self.fake("brew")
        code, _, _ = self.invoke(
            ["init", "--project", str(self.project), "--personal-ref", REF],
            platform="darwin",
        )
        self.assertEqual(0, code)
        self.assertEqual(["trellis", "brew"], [item["name"] for item in self.commands()])
        statuses = {item["id"]: item["status"] for item in self.report()["tools"]}
        self.assertEqual("installed", statuses["github_cli"])

    def test_non_code_project_and_skip_tools_do_not_create_index(self):
        self.add_all_tools()
        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])
        self.assertEqual(0, code)
        statuses = {item["id"]: item["status"] for item in self.report()["tools"]}
        self.assertEqual("deferred", statuses["codegraph_project_index"])
        self.assertFalse((self.project / ".codegraph").exists())

        second = self.base / "second"
        second.mkdir()
        self.project = second
        code, _, _ = self.invoke([
            "init", "--project", str(second), "--personal-ref", REF, "--skip-tools",
        ])
        self.assertEqual(0, code)
        self.assertEqual("deferred", self.report()["tools"][0]["status"])

    def test_report_redacts_secret_arguments_and_error_text(self):
        self.fake("trellis")
        self.env["FAKE_TRELLIS_EXIT"] = "5"
        self.env["FAKE_TRELLIS_MESSAGE"] = "token=supersecret dsn=postgres://user:pass@db.local/app"
        code, _, _ = self.invoke([
            "init", "--project", str(self.project), "--personal-ref", REF, "--", "--api-key", "arg-secret",
        ])
        self.assertEqual(5, code)
        serialized = json.dumps(self.report())
        self.assertNotIn("supersecret", serialized)
        self.assertNotIn("arg-secret", serialized)
        self.assertNotIn("user:pass", serialized)
        self.assertIn("<redacted>", serialized)

    def test_report_path_and_terminal_redact_secret_like_project_component(self):
        secret = "path-secret"
        self.project = self.base / f"token={secret}"
        self.project.mkdir()
        self.fake("trellis")
        code, output, error = self.invoke([
            "init", "--project", str(self.project), "--personal-ref", REF, "--skip-tools",
        ])
        self.assertEqual(0, code)
        serialized = json.dumps(self.report())
        self.assertNotIn(secret, serialized)
        self.assertNotIn(secret, output)
        self.assertNotIn(secret, error)

    def test_report_parent_symlink_is_rejected_before_native_init(self):
        outside = self.base / "outside"
        outside.mkdir()
        (self.project / ".trellis").symlink_to(outside, target_is_directory=True)
        self.fake("trellis")
        with mock.patch.dict(os.environ, self.env, clear=True), self.assertRaises(SystemExit) as caught:
            personal_init.main([
                "init", "--project", str(self.project), "--personal-ref", REF,
            ])
        self.assertEqual(2, caught.exception.code)
        self.assertEqual([], self.commands())
        self.assertFalse((outside / "personal/bootstrap-report.json").exists())

    def test_invalid_project_usage_error_redacts_secret_like_path(self):
        secret = "missing-secret"
        missing = self.base / f"token={secret}"
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, self.env, clear=True), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                personal_init.main([
                    "init", "--project", str(missing), "--personal-ref", REF,
                ])
        self.assertEqual(2, caught.exception.code)
        self.assertNotIn(secret, stderr.getvalue())
        self.assertIn("<redacted>", stderr.getvalue())

    def test_unsafe_codegraph_path_is_not_initialized(self):
        self.add_all_tools()
        (self.project / "package.json").write_text("{}\n", encoding="utf-8")
        outside = self.base / "outside-codegraph"
        outside.mkdir()
        (self.project / ".codegraph").symlink_to(outside, target_is_directory=True)
        code, _, _ = self.invoke(["init", "--project", str(self.project), "--personal-ref", REF])
        self.assertEqual(0, code)
        self.assertEqual(["trellis"], [item["name"] for item in self.commands()])
        statuses = {item["id"]: item["status"] for item in self.report()["tools"]}
        self.assertEqual("unsupported", statuses["codegraph_project_index"])

    def test_agent_config_environment_controls_skill_detection_root(self):
        manifest = personal_init.load_manifest()
        custom_codex = self.base / "custom-codex"
        custom_claude = self.base / "custom-claude"
        self.assertEqual(
            custom_codex / "skills",
            personal_init.skill_root("codex", manifest, {"HOME": str(self.home), "CODEX_HOME": str(custom_codex)}),
        )
        self.assertEqual(
            custom_claude / "skills",
            personal_init.skill_root(
                "claude-code",
                manifest,
                {"HOME": str(self.home), "CLAUDE_CONFIG_DIR": str(custom_claude)},
            ),
        )

    def test_ref_inference_requires_expected_origin_and_full_head(self):
        with mock.patch.object(personal_init, "git_output", side_effect=["git@github.com:someone/other.git", REF]):
            with self.assertRaises(personal_init.UsageError):
                personal_init.resolve_personal_ref(None, self.base)
        with mock.patch.object(personal_init, "git_output", side_effect=["https://github.com/zyf3313/personal-trellis.git", REF]):
            self.assertEqual(REF, personal_init.resolve_personal_ref(None, self.base))
        with self.assertRaises(personal_init.UsageError):
            personal_init.resolve_personal_ref("abc", self.base)


if __name__ == "__main__":
    unittest.main()
