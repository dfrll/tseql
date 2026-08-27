#! /usr/bin/env python3
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
from cloudflare import Cloudflare


class MissingEnvironmentVariable(Exception):
    pass


def require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise MissingEnvironmentVariable(f"Missing environment variable: {name}")
    return value


@dataclass(frozen=True)
class Config:
    cloudflare_api_token: str
    d1_db_id: str
    account_id: str
    openai_api_key: str
    default_model: str = "gpt-4.1-mini"


@dataclass(frozen=True)
class Services:
    cf: Cloudflare
    llm: OpenAI
    d1_db_id: str
    account_id: str

    def query_d1(self, sql: str):
        return self.cf.d1.database.query(
            database_id=self.d1_db_id,
            account_id=self.account_id,
            sql=sql,
        )


def bootstrap() -> tuple[Services, Config]:
    load_dotenv(Path(__file__).resolve().parents[3] / ".env")

    cfg = Config(
        cloudflare_api_token=require("CLOUDFLARE_API_TOKEN"),
        d1_db_id=require("D1_DB_ID"),
        account_id=require("ACCOUNT_ID"),
        openai_api_key=require("OPENAI_API_KEY"),
    )

    services = Services(
        cf=Cloudflare(api_token=cfg.cloudflare_api_token),
        llm=OpenAI(api_key=cfg.openai_api_key),
        d1_db_id=cfg.d1_db_id,
        account_id=cfg.account_id,
    )

    return services, cfg
