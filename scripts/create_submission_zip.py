import os
import zipfile

def create_submission_zip(output_filename, include_data=False):
    print(f"Building {output_filename} (include_data={include_data})...")
    
    with zipfile.ZipFile(output_filename, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        # 1. readme.txt at root of master zip
        if os.path.exists('readme.txt'):
            z.write('readme.txt', 'readme.txt')
            print("  Added top-level: readme.txt")

        # 2. report (pdf) at root of master zip
        if os.path.exists('Report_Final.pdf'):
            z.write('Report_Final.pdf', 'Report_Final.pdf')
            z.write('Report_Final.pdf', 'report.pdf')
            print("  Added top-level: Report_Final.pdf and report.pdf")

        # 3. project folder: cloudProject/
        count = 0
        for root, dirs, files in os.walk('.'):
            # Exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'highD-dataset-v1.0']]
            
            if not include_data and 'data_corrupted' in root:
                continue

            for f in files:
                # Exclude zip archives and helper scripts from inside the project folder
                if f.endswith('.zip') or f in ['create_submission_zip.py']:
                    continue
                
                file_path = os.path.join(root, f)
                rel_path = os.path.relpath(file_path, '.')
                arcname = os.path.join('cloudProject', rel_path)
                z.write(file_path, arcname)
                count += 1
                
        print(f"  Added {count} project files inside cloudProject/")

    size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    print(f"Successfully created {output_filename} ({size_mb:.2f} MB)\n")

if __name__ == '__main__':
    # 1. Standard Moodle package (recommended: fits all Moodle limits)
    create_submission_zip('ujjwal_262IS036.zip', include_data=False)
    
    # 2. Full package with 108MB data_corrupted included
    create_submission_zip('ujjwal_262IS036_with_data.zip', include_data=True)
