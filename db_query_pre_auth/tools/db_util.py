import datetime
import logging
import re
from typing import Optional
from urllib import parse
from uuid import UUID

import oracledb
import pandas as pd
from pandas import Timestamp
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.engine import Connection


class KingbaseDialect(PGDialect_psycopg2):
    """Psycopg2 dialect with support for the KingbaseES version format."""

    name = 'kingbase'

    def _get_server_version_info(self, connection: Connection) -> tuple[int, ...]:
        version = connection.exec_driver_sql("select pg_catalog.version()").scalar()
        match = (
            re.match(r"KingbaseES V(\d{3})R(\d{3})C(\d{3})", version)
            if isinstance(version, str)
            else None
        )
        if match:
            return tuple(int(part) for part in match.groups())
        return super()._get_server_version_info(connection)


registry.register("kingbase.psycopg2", __name__, "KingbaseDialect")


class DbUtil:

    def __init__(self, db_type: str,
                 username: str, password: str,
                 host: str, port: Optional[str] = None,
                 database: Optional[str] = None,
                 properties: Optional[str] = None) -> None:
        self.db_type = db_type.lower()
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.properties = properties
        if self.db_type == 'oracle11g':
            # To change from the default python-oracledb Thin mode to Thick mode
            oracledb.init_oracle_client()
        self.engine = create_engine(self.get_url(), pool_size=100, pool_recycle=36)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_driver_name(self):
        driver_name = self.db_type
        if self.db_type in {'mysql', 'doris'}:
            driver_name = 'mysql+pymysql'
        elif self.db_type in {'oracle', 'oracle11g'}:
            driver_name = 'oracle+oracledb'
        elif self.db_type == 'postgresql':
            driver_name = 'postgresql+psycopg2'
        elif self.db_type == 'kingbase':
            driver_name = 'kingbase+psycopg2'
        elif self.db_type == 'mssql':
            driver_name = 'mssql+pymssql'
        elif self.db_type == 'dm':
            driver_name = 'dm+dmPython'
        return driver_name

    def get_url(self):
        '''
        Get url
        '''
        parsed_username = parse.quote_plus(self.username)
        parsed_password = parse.quote_plus(self.password)
        parsed_host = parse.quote_plus(self.host)
        url = f"{self.get_driver_name()}://{parsed_username}:{parsed_password}@{parsed_host}"
        if self.is_not_empty(self.port):
            url = f"{url}:{str(self.port)}"
        url = f"{url}/"
        if self.is_not_empty(self.database):
            parsed_database = parse.quote_plus(self.database)
            url = f"{url}{parsed_database}"
        if self.is_not_empty(self.properties):
            url = f"{url}?{self.properties}"
        logging.info("Creating %s database connection", self.db_type)
        return url

    def close(self):
        """Close all connections in the engine."""
        self.engine.dispose()

    def run_query(self, query_sql: str) -> list[dict]:
        if self.engine.dialect.paramstyle in {"format", "pyformat"}:
            query_sql = query_sql.replace("%", "%%")
        df = pd.read_sql_query(sql=query_sql, con=self.engine, parse_dates="%Y-%m-%d %H:%M:%S")
        records = df.to_dict(orient="records")
        for record in records:
            for key, value in record.items():
                if pd.api.types.is_scalar(value) and pd.isna(value):
                    record[key] = ''
                elif isinstance(value, Timestamp):
                    record[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, datetime.date):
                    record[key] = value.strftime('%Y-%m-%d')
                elif isinstance(value, UUID):
                    record[key] = str(value)
                elif isinstance(value, float):
                    if value.is_integer():
                        record[key] = int(value)
        return records

    def test_sql(self):
        if self.db_type in {'oracle', 'oracle11g', 'dm'}:
            return "SELECT 1 FROM DUAL"
        else:
            return "SELECT 1"

    @staticmethod
    def is_not_empty(s: str):
        return s is not None and s.strip() != ""
