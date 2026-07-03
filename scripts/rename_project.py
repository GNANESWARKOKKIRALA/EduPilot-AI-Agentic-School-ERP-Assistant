import os

def rename_occurrences():
    root_dir = os.getcwd()
    print(f"Starting project rename in: {root_dir}")
    
    replacements = [
        ("CampusPilot AI - School ERP Assistant", "EduPilot AI – Agentic School ERP Assistant"),
        ("CampusPilot AI - ERP Assistant", "EduPilot AI – Agentic School ERP Assistant"),
        ("CampusPilot AI", "EduPilot AI"),
        ("CampusPilot", "EduPilot")
    ]
    
    exclude_dirs = {".git", ".venv", "venv", ".idea", ".vscode", "appdata"}
    exclude_files = {"rename_project.py", "campus_pilot.db", "campuspilot.db", "architecture_diagram.png", "api_docs.pdf"}
    
    modified_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude directories in-place
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for filename in filenames:
            if filename in exclude_files:
                continue
                
            file_path = os.path.join(dirpath, filename)
            
            # Skip binary files
            if filename.endswith(('.png', '.pdf', '.jpg', '.db', '.pyc')):
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                original = content
                for old_val, new_val in replacements:
                    content = content.replace(old_val, new_val)
                    
                if content != original:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Updated: {os.path.relpath(file_path, root_dir)}")
                    modified_count += 1
            except Exception as e:
                # Silently skip files that aren't readable as UTF-8 text
                pass
                
    print(f"Project renaming complete. {modified_count} files modified.")

if __name__ == "__main__":
    rename_occurrences()
