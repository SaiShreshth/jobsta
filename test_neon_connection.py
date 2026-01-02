#!/usr/bin/env python3
"""Test Neon connection with asyncpg driver"""

import os
import asyncio
import re
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    """Test if asyncpg can connect to Neon"""
    db_url = os.getenv('DATABASE_URL', '')
    
    if not db_url:
        print("❌ DATABASE_URL not set in .env")
        return False
    
    print(f"📍 Testing connection to: {db_url[:80]}...")
    
    # Convert to asyncpg URL
    async_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', db_url)
    
    try:
        print(f"🔄 Creating async engine...")
        engine = create_async_engine(async_url, echo=False)
        
        print(f"🔌 Connecting to database...")
        async with engine.connect() as conn:
            result = await conn.execute(text("select 'hello world' as greeting"))
            row = result.fetchone()
            print(f"✅ SUCCESS! Connection works!")
            print(f"   Query result: {row}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ FAILED! Error: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
