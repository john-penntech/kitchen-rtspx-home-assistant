from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "kitchen_rtspx"


def _load_const_module():
    spec = importlib.util.spec_from_file_location("kitchen_rtspx_const", COMPONENT / "const.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ComponentContractTests(unittest.TestCase):
    def test_release_hashes(self) -> None:
        for line in (ROOT / "SHA256SUMS").read_text("utf-8").splitlines():
            expected, relative_path = line.split("  ", 1)
            actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative_path)

    def test_manifest_is_hacs_ready(self) -> None:
        manifest = json.loads((COMPONENT / "manifest.json").read_text("utf-8"))
        self.assertEqual(manifest["domain"], "kitchen_rtspx")
        self.assertEqual(manifest["version"], "1.1.0")
        self.assertTrue(manifest["config_flow"])
        self.assertEqual(manifest["integration_type"], "device")
        self.assertEqual(manifest["iot_class"], "local_push")
        self.assertEqual(manifest["codeowners"], ["@john-penntech"])
        self.assertEqual(
            json.loads((ROOT / "hacs.json").read_text("utf-8"))["name"],
            "RTSPX Camera Bridge",
        )

    def test_translation_keys_match(self) -> None:
        strings = json.loads((COMPONENT / "strings.json").read_text("utf-8"))
        english = json.loads(
            (COMPONENT / "translations" / "en.json").read_text("utf-8")
        )
        self.assertEqual(strings, english)

    def test_config_entry_and_legacy_yaml_paths_exist(self) -> None:
        init_tree = ast.parse((COMPONENT / "__init__.py").read_text("utf-8"))
        camera_tree = ast.parse((COMPONENT / "camera.py").read_text("utf-8"))
        flow_tree = ast.parse((COMPONENT / "config_flow.py").read_text("utf-8"))

        init_functions = {
            node.name for node in init_tree.body if isinstance(node, ast.AsyncFunctionDef)
        }
        camera_functions = {
            node.name for node in camera_tree.body if isinstance(node, ast.AsyncFunctionDef)
        }
        flow_classes = {
            node.name for node in flow_tree.body if isinstance(node, ast.ClassDef)
        }
        self.assertEqual(
            init_functions, {"async_setup_entry", "async_unload_entry"}
        )
        self.assertTrue(
            {"async_setup_entry", "async_setup_platform"} <= camera_functions
        )
        self.assertIn("KitchenRtspxConfigFlow", flow_classes)

    def test_url_validation(self) -> None:
        const = _load_const_module()
        valid = "rtspx://camera.local:7441/AbCdEf"
        self.assertEqual(const.validate_rtspx_url(f"  {valid}  "), valid)

        for invalid in (
            "rtsp://camera.local:7441/AbCdEf",
            "rtspx:///AbCdEf",
            "rtspx://camera.local/",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(
                const.InvalidRtspxUrl
            ):
                const.validate_rtspx_url(invalid)

        for query in ("enableSrtp", "enableSrtp=true", "ENABLESRTP=false"):
            with self.subTest(query=query), self.assertRaises(
                const.EnableSrtpNotAllowed
            ):
                const.validate_rtspx_url(f"{valid}?{query}")

    def test_no_high_risk_execution_or_write_primitives(self) -> None:
        trees = [ast.parse(path.read_text("utf-8")) for path in COMPONENT.glob("*.py")]
        imported_roots = {
            alias.name.split(".", 1)[0]
            for tree in trees
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in (
                node.names
                if isinstance(node, ast.Import)
                else [ast.alias(name=node.module or "")]
            )
        }
        self.assertTrue(
            {"os", "subprocess", "socket", "requests", "httpx"}.isdisjoint(
                imported_roots
            )
        )

        called_names = {
            node.func.id
            for tree in trees
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(
            {"eval", "exec", "compile", "open", "__import__"}.isdisjoint(
                called_names
            )
        )


if __name__ == "__main__":
    unittest.main()
