from backend.app.ai.services.admin_db_reader import get_random_stop


result = get_random_stop()

print("\n--- ADMIN AGENT READ-ONLY DB TEST ---")

if result:
    for key, value in result.items():
        print(f"{key}: {value}")
else:
    print("No stop found.")