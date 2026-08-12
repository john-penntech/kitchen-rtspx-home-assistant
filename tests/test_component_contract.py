from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "kitchen_rtspx"

EXPECTED_HASHES = {
    "README.md": "4955f1e12b1b9c98d8bf4f04ae7375d609e6195100e2c1363b6d34ebfaba20ee",
    "__init__.py": "efbcc40c5e279aa6c87498c94bb591c38d4409a6b8117653ba9b0844d82b413f",
    "camera.py": "b2262444f60c55dc4af1064a35b594203911dc2a6200cca643004e8bb9d4ad74",
    "manifest.json": "7d42a214f4ad7630821bc767951ed461d495fcf8405a922d544e0f57562015d7",
}


class ComponentContractTests(unittest.TestCase):
    def test_deployed_snapshot_hashes(self) -> None:
        actual = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in COMPONENT.iterdir()
            if path.is_file()
        }
        self.assertEqual(actual, EXPECTED_HASHES)

    def test_manifest_contract(self) -> None:
        manifest = json.loads((COMPONENT / "manifest.json").read_text("utf-8"))
        self.assertEqual(manifest["domain"], "kitchen_rtspx")
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(manifest["iot_class"], "local_polling")
        self.assertIsInstance(manifest["codeowners"], list)

    def test_yaml_configuration_schema_contract(self) -> None:
        tree = ast.parse((COMPONENT / "camera.py").read_text("utf-8"))
        constants = {
            node.targets[0].id: node.value.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        }
        self.assertEqual(
            {constants[name] for name in ("CONF_CAMERAS", "CONF_STREAM_SOURCE", "CONF_UNIQUE_ID")},
            {"cameras", "stream_source", "unique_id"},
        )

        required_names = {
            arg.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "vol"
            and node.func.attr == "Required"
            and node.args
            for arg in [node.args[0]]
            if isinstance(arg, ast.Name)
        }
        self.assertTrue(
            {"CONF_NAME", "CONF_UNIQUE_ID", "CONF_STREAM_SOURCE", "CONF_CAMERAS"}
            <= required_names
        )

    def test_no_high_risk_execution_or_write_primitives(self) -> None:
        tree = ast.parse((COMPONENT / "camera.py").read_text("utf-8"))
        imported_roots = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in (
                node.names
                if isinstance(node, ast.Import)
                else [ast.alias(name=node.module or "")]
            )
        }
        self.assertTrue({"os", "subprocess", "socket", "requests", "httpx"}.isdisjoint(imported_roots))

        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue({"eval", "exec", "compile", "open", "__import__"}.isdisjoint(called_names))


if __name__ == "__main__":
    unittest.main()
