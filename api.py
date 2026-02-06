from pathlib import Path
import os

# 1. Reference the folder relative to the script
# If your script is in the root, '.' refers to the repo root
base_dir = Path("AUTO_CODES")

# 2. Use rglob to find all .sql files in any child directory
for sql_file in base_dir.rglob("*.py"):

    # This gives you the path the GitHub API needs (e.g., SQL_QUERIES/Sub/file.sql)
    # We use .as_posix() to ensure it uses forward slashes (/) for the API
    api_path = sql_file.as_posix()

    print(f"Processing file for GitHub: {api_path}")

    # Your GitHub API logic here...
    # upload_to_github(path=api_path, content=sql_file.read_text())