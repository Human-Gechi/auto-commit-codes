#Import necessary libraries
import os
from dotenv import load_dotenv
import requests
import base64
from datetime import datetime
import hashlib

load_dotenv()
token = os.getenv("GITHUB_TOKEN") #Token Variable

def fetch_github_metrics(repo_owner, repo_name, token=token):
    """Fetch repository information"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    headers = {"Authorization": f"token {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub: {e}")
        return None

def check_file_exists(repo_owner, repo_name, file_path, token):
    """Check if file exists and get its SHA"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}

    try:
        response = requests.get(url, headers=headers) #Get request
        if response.status_code == 200:
            return response.json().get("sha")
        return None
    except requests.exceptions.RequestException: #Request Error
        return None
def get_blob_sha(local_file_path):
    with open(local_file_path,'rb') as f:
        content = f.read()

        # Get github prefixes afor blob storage
        header = f"blob {len(content)}\0".encode('utf-8')
        combined = header + content

        return hashlib.sha1(combined).hexdigest()

def upload_queries_to_github(local_directory):
    """Upload SQL files from local subdirectories to GitHub"""
    repo_owner = "Human-Gechi"
    repo_name = "DAILY_SQL_PROBLEMS"

    # Verify repository access
    fetch = fetch_github_metrics(repo_owner, repo_name)
    if not fetch:
        print("Failed to connect to repository")
        return

    print(f"Connected to: {fetch.get('full_name')}\n")

    uploaded_count = 0 #Updated count
    updated_count = 0 #Updated files
    failed_count = 0 #Failed uploads
    skipped_count = 0 #Skipped

    # Walk through all subdirectories
    for root, dir, files in os.walk(local_directory):
        for file in files:
            if file.endswith('.sql'):
                # Full local file path
                local_file_path = os.path.join(root, file)

                # Calculate relative path from base directory
                relative_path = os.path.relpath(local_file_path, local_directory)

                # Convert Windows backslashes to forward slashes for GitHub
                github_path = relative_path.replace('\\', '/')

                print(f"\n Processing: {github_path}")

                try:
                    # Read file content
                    with open(local_file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Check if file already exists on GitHub repos
                    existing_sha = check_file_exists(repo_owner, repo_name, github_path, token)

                    date = datetime.now().strftime("%Y-%m-%d")
                    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{github_path}"
                    headers = {
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json"
                    }

                    # Encode content to base64 to be acceptable by the API
                    content_encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
                    local_sha = get_blob_sha(local_file_path)
                    with open(local_file_path, "rb") as f:
                        binary_content = f.read()

                    local_sha = get_blob_sha(local_file_path)
                    content_encoded = base64.b64encode(binary_content).decode("utf-8")

                    if existing_sha:
                        if existing_sha == local_sha:
                            print(f"😪 {github_path} matches GitHub. Skipping.")
                            skipped_count += 1
                            continue

                        # File exists exists but changed
                        print(f"🔄 Changes detected. Updating............")
                        data = {
                            "message": f"Update {github_path} on {date}",
                            "content": content_encoded,
                            "sha": existing_sha
                        }
                        action = "updated"
                    else:
                        print(f"New file found. Uploading............")
                        data = {
                            "message": f"Add {github_path} on {date}",
                            "content": content_encoded
                        }

                        print(f"Uploading a new file")
                        action = "uploaded"
                    response = requests.put(url, headers=headers, json=data)
                    response.raise_for_status()

                    print(f"✅ Successfully {action}: {github_path}")

                    if action == "uploaded":
                        uploaded_count += 1
                    else:
                        updated_count += 1

                except requests.exceptions.HTTPError as e:
                    print(f"HTTP Error: {e}")
                    if hasattr(response, 'text'):
                        print(f"Response: {response.text}")
                    failed_count += 1

                except Exception as e:
                    print(f"Error message: {e}")
                    failed_count += 1
            else:
                skipped_count += 1

    # Print summary
    print(f"\n{'='*30}")
    print(f"📊 UPLOAD SUMMARY")
    print(f"{'='*30}")
    print(f"New files uploaded:  {uploaded_count}")
    print(f"Files updated:       {updated_count}")
    print(f"Failed:              {failed_count}")
    print(f"Skipped (not .sql):  {skipped_count}")
    print(f"{'='*30}")

if __name__ == "__main__":
    local_dir = r"C:\Users\HP\OneDrive\Desktop\SQL_QUERIES"

    upload_queries_to_github(local_dir)
