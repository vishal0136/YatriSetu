import json
import requests

from backend.app.ai.services.admin_db_reader import get_random_stop


stop = get_random_stop()

if not stop:
    raise RuntimeError("No stop was returned from DTMS_TEST.")


prompt = f"""
You are the YatriSetu Admin AI Agent.

An administrator asked:

"Give me the details of this randomly selected stop and confirm the
information from the database."

The following information was retrieved directly from the controlled
DTMS_TEST database using a read-only query.

DATABASE EVIDENCE:
{json.dumps(stop, indent=2, default=str)}

Instructions:

1. Use only the database evidence provided above.
2. Do not invent routes, trips, schedules, fares, or other information.
3. Clearly identify that the information comes from the database.
4. Report the stop ID, stop code, stop name, latitude, and longitude.
5. Do not modify the database.
6. If information was not retrieved, explicitly say it was not retrieved.
7. Return a concise factual response.
"""

response = requests.post(
    "http://127.0.0.1:8000/generate-recommendation",
    json={"prompt": prompt},
    timeout=180,
)

print("\n--- DATABASE EVIDENCE GIVEN TO AGENT ---")
print(json.dumps(stop, indent=2, default=str))

print("\n--- QWEN AGENT RESPONSE ---")

if response.ok:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print("HTTP status:", response.status_code)
    print(response.text)