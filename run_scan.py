from app.services import run_discovery_scan

result = run_discovery_scan(
    application="demo-app",
    root_dir="sample_app"
)

print("\n===== DISCOVERY SCAN RESULT =====\n")
print(result.model_dump_json(indent=2))