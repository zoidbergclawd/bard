#!/usr/bin/env python3
import sys
import argparse
import subprocess
import urllib.request
import urllib.error
import re

def get_readme_content(repo_url):
    """
    Tries to fetch README.md (or README.rst/txt) from a GitHub repo URL.
    Handles 'github.com' -> 'raw.githubusercontent.com' transformation.
    """
    # Normalize URL: remove .git, ensure no trailing slash
    url = repo_url.rstrip("/").replace(".git", "")
    
    # Extract owner/repo
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
    if not match:
        print(f"Error: Could not parse GitHub URL: {url}")
        sys.exit(1)
        
    owner, repo = match.groups()
    base_raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}"
    
    # Try common branches and filenames
    branches = ["main", "master"]
    filenames = ["README.md", "README.rst", "README.txt", "readme.md"]
    
    for branch in branches:
        for filename in filenames:
            raw_url = f"{base_raw_url}/{branch}/{filename}"
            try:
                with urllib.request.urlopen(raw_url) as response:
                    return response.read().decode('utf-8')
            except urllib.error.HTTPError:
                continue
                
    print(f"Error: Could not find README in {repo_url} (checked main/master branches).")
    sys.exit(1)

def generate_song(readme_text, style, repo_name):
    """
    Calls the 'gemini' CLI tool to generate the song.
    """
    prompt = f"""
You are The Bard, an AI songwriter.
Here is the README for a software project named '{repo_name}':

---
{readme_text[:8000]} 
---
(Truncated if too long)

TASK:
Write a song about this project.
The style must be: "{style}".
Format the output EXACTLY for Suno AI generation:

**Title:** <Title>
**Style:** <Style Description>
**Lyrics:**
[Verse]
...
[Chorus]
...

Be creative, use specific technical terms from the README, and capture the 'vibe' of the project.
"""
    
    try:
        # Call gemini with the prompt. 
        # Note: If gemini expects prompt as arg, we use a list.
        result = subprocess.run(
            ["gemini", prompt], 
            capture_output=True, 
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error calling gemini: {e}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'gemini' CLI tool not found in PATH.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Bard: The Repo Rhapsody Generator")
    parser.add_argument("url", help="GitHub Repository URL")
    parser.add_argument("style", nargs="?", default="Epic Power Metal", help="Musical Style (default: Epic Power Metal)")
    
    args = parser.parse_args()
    
    repo_name = args.url.split("/")[-1].replace(".git", "")
    
    print(f"🎵 Tuning instruments for {repo_name}...")
    print(f"📜 Reading the sacred texts (README)...")
    readme_content = get_readme_content(args.url)
    
    print(f"🎸 Composing in the style of: {args.style}...")
    song = generate_song(readme_content, args.style, repo_name)
    
    print("\n" + "="*40)
    print(song)
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
