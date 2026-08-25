import zipfile
import os

def create_submission_zip():
    zip_name = "skylark_bi_agent.zip"
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'dist', '.venv', 'venv'}
    exclude_files = {zip_name, 'ui_overview.png', 'ui_query_response.png'}

    print(f"Creating {zip_name} package...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            for file in files:
                if file in exclude_files or file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"\nSuccessfully generated submission ZIP package: {zip_name} (Size: {os.path.getsize(zip_name)/1024:.1f} KB)")

if __name__ == "__main__":
    create_submission_zip()
