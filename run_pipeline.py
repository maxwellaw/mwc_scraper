import subprocess
import sys

# Force the correct Python interpreter from the virtual environment
python_exec = sys.executable  # This ensures the correct environment is used

scripts = ["mwc_list_companies.py", "mwc_fetch_details.py", "mwc_ai_categorization.py"]

for script in scripts:
    print(f"\n🚀 Running {script}...")
    try:
        result = subprocess.run([python_exec, script], check=True)
        print(f"✅ {script} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script}: {e}")
        break
