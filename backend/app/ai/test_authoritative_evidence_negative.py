from backend.app.ai.services.authoritative_evidence import (
    get_authoritative_correction,
)


def main():

    print("=== NEGATIVE AUTHORITATIVE EVIDENCE TEST ===")

    result = get_authoritative_correction(
        stop_id="1",
        field="stop_lat",
        current_value=998.0,
    )

    print("\nMATCHING EVIDENCE:")
    print(result)

    if result is None:
        print("\nEXPECTED REJECTION: PASS")
    else:
        print("\nEXPECTED REJECTION: FAIL")


if __name__ == "__main__":
    main()
