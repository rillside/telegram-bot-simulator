import os
import sys
from pathlib import Path

# CRITICAL: Isolate test database from user's main database!
# All tests must run against test_simulator.db, NEVER touching telegram_simulator.db.
TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
TEST_DB_FILE = TEST_DATA_DIR / "test_simulator.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

import pytest
from backend.app.core.database import engine, Base

@pytest.fixture(autouse=True)
async def clean_test_database():
    await engine.dispose()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
