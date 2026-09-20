from backend.app.ai.services.authoritative_evidence import (
    get_authoritative_correction,
)


def main():

    print("=== AUTHORITATIVE EVIDENCE TEST ===")

    result = get_authoritative_correction(
        stop_id="1",
        field="stop_lat",
        current_value=999.0,
    )

    print("\nMATCHING EVIDENCE:")
    print(result)

    if result and result["verified"] is True:
        print("\nRESULT: PASS")
    else:
        print("\nRESULT: FAIL")


if __name__ == "__main__":
    main()