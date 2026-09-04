import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
DB_UTIL_PATHS = (
    ROOT / "db_query" / "tools" / "db_util.py",
    ROOT / "db_query_pre_auth" / "tools" / "db_util.py",
)

sys.modules.setdefault("oracledb", types.ModuleType("oracledb"))


def load_db_util(path: Path):
    module_name = f"kingbase_db_util_{path.parent.parent.name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class KingbaseDbUtilTest(unittest.TestCase):
    def test_driver_url_and_connection_test_sql(self):
        for path in DB_UTIL_PATHS:
            with self.subTest(plugin=path.parent.parent.name):
                module = load_db_util(path)
                with patch.object(module, "create_engine") as create_engine:
                    database = module.DbUtil(
                        db_type="KINGBASE",
                        username="kingbase-user",
                        password="kingbase-password",
                        host="kingbase.example.com",
                        port="54321",
                        database="application_db",
                        properties="connect_timeout=10&sslmode=prefer",
                    )

                expected_url = (
                    "kingbase+psycopg2://kingbase-user:kingbase-password@"
                    "kingbase.example.com:54321/application_db"
                    "?connect_timeout=10&sslmode=prefer"
                )
                self.assertEqual(database.get_driver_name(), "kingbase+psycopg2")
                self.assertEqual(database.get_url(), expected_url)
                self.assertEqual(database.test_sql(), "SELECT 1")
                create_engine.assert_called_once_with(
                    expected_url, pool_size=100, pool_recycle=36
                )

    def test_kingbase_server_version_is_parsed(self):
        for path in DB_UTIL_PATHS:
            with self.subTest(plugin=path.parent.parent.name):
                module = load_db_util(path)
                connection = MagicMock()
                connection.exec_driver_sql.return_value.scalar.return_value = (
                    "KingbaseES V009R003C010"
                )

                dialect = module.KingbaseDialect()

                self.assertEqual(
                    dialect._get_server_version_info(connection),
                    (9, 3, 10),
                )
                connection.exec_driver_sql.assert_called_once_with(
                    "select pg_catalog.version()"
                )

    def test_both_plugins_expose_kingbase(self):
        selector_files = (
            ROOT / "db_query" / "tools" / "sql_query.yaml",
            ROOT / "db_query_pre_auth" / "provider" / "db_query.yaml",
        )

        for path in selector_files:
            with self.subTest(selector=path):
                content = path.read_text(encoding="utf-8")
                self.assertIn("- value: kingbase", content)
                self.assertIn("en_US: KingbaseES", content)
                self.assertIn("zh_Hans: 人大金仓 KingbaseES", content)

    def test_kingbase_reuses_existing_psycopg2_dependency(self):
        requirement_files = (
            ROOT / "db_query" / "requirements.txt",
            ROOT / "db_query_pre_auth" / "requirements.txt",
        )

        for path in requirement_files:
            with self.subTest(requirements=path):
                requirements = path.read_text(encoding="utf-8").splitlines()
                self.assertIn("psycopg2-binary==2.9.10", requirements)
                self.assertFalse(
                    any(
                        requirement.lower().startswith("ksycopg2")
                        for requirement in requirements
                    )
                )


if __name__ == "__main__":
    unittest.main()
