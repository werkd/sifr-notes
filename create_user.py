import asyncio
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL is not set in .env")
    sys.exit(1)


async def create_user(username: str, password: str) -> None:
    from app.auth import hash_password
    from app.models import User

    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with Session() as session:
        result = await session.execute(select(User).where(User.username == username))
        existing = result.scalar_one_or_none()

        if existing:
            print(f"ERROR: User'{username}' already exists. ")
            await engine.dispose()
            sys.exit(1)

        user = User(username=username, hashed_password=hash_password(password))
        session.add(user)
        await session.commit()
        print(f"User '{username}' created successfully (id={user.id}). ")

    await engine.dispose()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create sifr-notes user.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    if len(args.password) < 8:
        print("ERROR: Password must be atleast 8 characters long.")
        sys.exit(1)

    asyncio.run(create_user(args.username, args.password))


