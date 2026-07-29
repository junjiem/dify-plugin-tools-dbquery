import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
DB_UTIL_PATHS = (
    ROOT / "db_query" / "tools" / "db_util.py",
    ROOT / "db_query_pre_auth" / "tools" / "db_util.py",
)

sys.modules.setdefault("oracledb", types.ModuleType("oracledb"))


def load_db_util(path: Path):
    module_name = f"db_util_{path.parent.parent.name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DamengDbUtilTest(unittest.TestCase):
    def test_driver_url_and_connection_test_sql(self):
        for path in DB_UTIL_PATHS:
            with self.subTest(plugin=path.parent.parent.name):
                module = load_db_util(path)
                with patch.object(module, "create_engine") as create_engine:
                    db = module.DbUtil(
                        db_type="DM",
                        username="user@name",
                        password="p@ss/word",
                        host="127.0.0.1",
                        port="5236",
                        database="APP_SCHEMA",
                        properties="login_timeout=10",
                    )

                expected_url = (
                    "dm+dmPython://user%40name:p%40ss%2Fword@127.0.0.1:5236/"
                    "APP_SCHEMA?login_timeout=10"
                )
                self.assertEqual(db.get_driver_name(), "dm+dmPython")
                self.assertEqual(db.get_url(), expected_url)
                self.assertEqual(db.test_sql(), "SELECT 1 FROM DUAL")
                create_engine.assert_called_once_with(
                    expected_url, pool_size=100, pool_recycle=36
                )

    def test_connection_logging_does_not_expose_credentials(self):
        for path in DB_UTIL_PATHS:
            with self.subTest(plugin=path.parent.parent.name):
                module = load_db_util(path)
                with (
                    patch.object(module, "create_engine"),
                    patch.object(module.logging, "info") as log_info,
                ):
                    module.DbUtil(
                        db_type="dm",
                        username="sensitive-user",
                        password="sensitive-password",
                        host="database.internal",
                        port="5236",
                    )

                log_output = " ".join(
                    str(value) for call in log_info.call_args_list for value in call.args
                )
                self.assertNotIn("sensitive-user", log_output)
                self.assertNotIn("sensitive-password", log_output)

    def test_both_plugins_expose_dameng_and_include_official_drivers(self):
        selector_files = (
            ROOT / "db_query" / "tools" / "sql_query.yaml",
            ROOT / "db_query_pre_auth" / "provider" / "db_query.yaml",
        )
        requirement_files = (
            ROOT / "db_query" / "requirements.txt",
            ROOT / "db_query_pre_auth" / "requirements.txt",
        )

        for path in selector_files:
            with self.subTest(selector=path):
                content = path.read_text(encoding="utf-8")
                self.assertIn("- value: dm", content)
                self.assertIn("en_US: Dameng (DM)", content)
                self.assertIn("zh_Hans: 达梦数据库", content)

        for path in requirement_files:
            with self.subTest(requirements=path):
                requirements = path.read_text(encoding="utf-8").splitlines()
                self.assertIn("dmPython==2.5.32", requirements)
                self.assertIn("dmSQLAlchemy==2.0.17", requirements)


if __name__ == "__main__":
    unittest.main()
