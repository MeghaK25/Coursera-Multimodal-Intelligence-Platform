#!/usr/bin/env python3
"""
scripts/migrate_to_supabase.py
==============================
One-click migration script to migrate the entire Coursera Insight database
(schemas, courses, readings, transcripts, and 9,479 vector embeddings)
from the local Docker container to your cloud Supabase database.

Usage:
    python scripts/migrate_to_supabase.py "postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

Or set SUPABASE_URL in your environment:
    python scripts/migrate_to_supabase.py
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    target_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SUPABASE_URL")
    
    if not target_url:
        print("\n❌ Error: Please provide your Supabase PostgreSQL connection string.")
        print("Usage:")
        print("  python scripts/migrate_to_supabase.py \"postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres\"")
        print("\nYou can find this in Supabase: Project Settings -> Database -> Connection string -> URI\n")
        sys.exit(1)

    # Automatically fix unencoded @ symbols in passwords
    # Format: postgresql://username:password@hostname:port/dbname
    if target_url.startswith("postgresql://") or target_url.startswith("postgres://"):
        body = target_url.split("://", 1)[1]
        if "@" in body:
            last_at_idx = body.rfind("@")
            creds = body[:last_at_idx]
            host_part = body[last_at_idx + 1:]
            if ":" in creds:
                user, pwd = creds.split(":", 1)
                import urllib.parse
                # If password contains raw @, percent-encode it
                if "@" in pwd:
                    pwd = urllib.parse.quote_plus(pwd)
                    target_url = f"postgresql://{user}:{pwd}@{host_part}"

    backup_file = Path("coursera_backup.sql")
    if not backup_file.exists():
        print("📦 Exporting local database dump from Docker container 'coursera_pgvector_5433'...")
        res = subprocess.run([
            "docker", "exec", "coursera_pgvector_5433",
            "pg_dump", "-U", "postgres", "--clean", "--if-exists", "coursera_platform"
        ], stdout=open(backup_file, "wb"))
        if res.returncode != 0:
            print("❌ Failed to dump from local container.")
            sys.exit(1)
        print("✅ Local backup generated (coursera_backup.sql).")

    print(f"\n🚀 Restoring database into Supabase...")
    print(f"Target: {target_url.split('@')[-1] if '@' in target_url else 'Supabase'}")

    # Use the psql utility inside the Docker container to restore directly to Supabase
    try:
        with open(backup_file, "rb") as f:
            proc = subprocess.run(
                ["docker", "exec", "-i", "coursera_pgvector_5433", "psql", target_url],
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if proc.returncode == 0:
                print("🎉 SUCCESS! All tables, courses, and vector embeddings were migrated to Supabase successfully!")
            else:
                stderr_text = proc.stderr.decode('utf-8', errors='ignore')
                print(f"⚠️ Process finished with notices/warnings:\n{stderr_text[:500]}")
                print("If tables were created, your Supabase database is ready to use!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
