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
    module_name = f"doris_db_util_{path.parent.parent.name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DorisDbUtilTest(unittest.TestCase):
    def test_driver_url_and_connection_test_sql(self):
        for path in DB_UTIL_PATHS:
            with self.subTest(plugin=path.parent.parent.name):
                module = load_db_util(path)
                with patch.object(module, "create_engine") as create_engine:
                    db = module.DbUtil(
                        db_type="DORIS",
                        username="doris-user",
                        password="doris-password",
                        host="doris.example.com",
                        port="9030",
                        database="catalog.analytics",
                        properties="connect_timeout=10&charset=utf8mb4",
                    )

                expected_url = (
                    "mysql+pymysql://doris-user:doris-password@"
                    "doris.example.com:9030/catalog.analytics"
                    "?connect_timeout=10&charset=utf8mb4"
                )
                self.assertEqual(db.get_driver_name(), "mysql+pymysql")
                self.assertEqual(db.get_url(), expected_url)
                self.assertEqual(db.test_sql(), "SELECT 1")
                create_engine.assert_called_once_with(
                    expected_url, pool_size=100, pool_recycle=36
                )

    def test_both_plugins_expose_doris(self):
        selector_files = (
            ROOT / "db_query" / "tools" / "sql_query.yaml",
            ROOT / "db_query_pre_auth" / "provider" / "db_query.yaml",
        )

        for path in selector_files:
            with self.subTest(selector=path):
                content = path.read_text(encoding="utf-8")
                self.assertIn("- value: doris", content)
                self.assertIn("en_US: Apache Doris", content)


if __name__ == "__main__":
    unittest.main()
