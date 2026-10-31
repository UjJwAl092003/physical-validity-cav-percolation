import os
import shutil
import zipfile

def main():
    print("Building clean, focused submission package...")
    
    # Define submission directory
    sub_dir = "submission_package"
    proj_dir = os.path.join(sub_dir, "cloudProject")
    fig_dir = os.path.join(proj_dir, "figures")
    
    # Clean previous build if any
    if os.path.exists(sub_dir):
        shutil.rmtree(sub_dir)
        
    os.makedirs(fig_dir, exist_ok=True)
    print(f"Created directory structure: {proj_dir}")

    # 1. Copy top-level submission items
    shutil.copy2("readme.txt", os.path.join(sub_dir, "readme.txt"))
    shutil.copy2("Report_Final.pdf", os.path.join(sub_dir, "Report_Final.pdf"))
    shutil.copy2("Report_Final.pdf", os.path.join(sub_dir, "report.pdf"))
    print("Copied top-level items: readme.txt, Report_Final.pdf, report.pdf")

    # 2. Copy core project files into cloudProject/
    shutil.copy2("Objective_1_Infeasible_Rate.ipynb", os.path.join(proj_dir, "Objective_1_Infeasible_Rate.ipynb"))
    shutil.copy2("Objective_2_Percolation_Sweep.ipynb", os.path.join(proj_dir, "Objective_2_Percolation_Sweep.ipynb"))
    shutil.copy2("run_objective_2.py", os.path.join(proj_dir, "run_objective_2.py"))
    shutil.copy2(os.path.join("results", "results.xlsx"), os.path.join(proj_dir, "results.xlsx"))
    shutil.copy2("README.md", os.path.join(proj_dir, "README.md"))
    print("Copied core code and results: notebooks, run script, results.xlsx, README.md")

    # 3. Copy figures into cloudProject/figures/
    for fig_file in os.listdir("figures"):
        if fig_file.endswith(".png"):
            src = os.path.join("figures", fig_file)
            dst = os.path.join(fig_dir, fig_file)
            shutil.copy2(src, dst)
            print(f"  Copied figure: {fig_file}")

    # 4. Create the focused zip file: ujjwal_262IS036.zip
    zip_name = "ujjwal_262IS036.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
        
    with zipfile.ZipFile(zip_name, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(sub_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, sub_dir)
                z.write(full_path, rel_path)
                
    zip_size_mb = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"\nSuccessfully generated {zip_name} ({zip_size_mb:.2f} MB)")

    # Clean up the large 112MB zip if present
    if os.path.exists("ujjwal_262IS036_with_data.zip"):
        os.remove("ujjwal_262IS036_with_data.zip")
        print("Removed bulky test zip: ujjwal_262IS036_with_data.zip")

    print("\n--- SUBMISSION VERIFICATION ---")
    with zipfile.ZipFile(zip_name, 'r') as z:
        for item in sorted(z.namelist()):
            print(f"  [ZIP ITEM] {item}")

if __name__ == '__main__':
    main()
