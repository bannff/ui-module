import subprocess
import sys

def run_command(command):
    print(f"Running: {command}")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        # Don't exit, try to continue

def main():
    print("Seeding UI Module Repo Features...")

    # 1. Create Repo (idempotent-ish check would be good, but 'gh repo create' handles existing safely mostly or fails fast)
    # Assumes we are in the repo root
    run_command("gh repo create ui-module --public --source=. --description 'MCP-first Server-Driven UI Framework' --push")

    # 2. Enable Features
    run_command("gh repo edit --enable-issues --enable-projects --enable-wiki --enable-discussions")

    # 3. Create Seed Issues
    issues = [
        {"title": "Implement Redis Store", "body": "Replace MemoryStore with Redis for production persistence."},
        {"title": "Add Auth Middleware", "body": "Integrate with the Entitlements module."},
        {"title": "React Client SDK", "body": "Create a reference React hook for consuming ui.render_view."}
    ]
    
    for issue in issues:
        run_command(f"gh issue create --title '{issue['title']}' --body '{issue['body']}' --label 'enhancement'")

    # 4. Create Discussion
    run_command("gh discussion create --category 'General' --title 'Welcome to UI Module' --body 'Discuss architecture and roadmap here.'")
    
    # 5. Wiki (Wiki usually requires a separate git push, but we can print instruction)
    print("Wiki seeding: Please clone the wiki repo (ui-module.wiki.git) and push initial content manually as API support is limited.")

    print("Seeding complete.")

if __name__ == "__main__":
    main()
