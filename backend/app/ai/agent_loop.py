import json

from backend.app.ai.services.db_evidence import get_stop_evidence
from backend.app.ai.services.authoritative_evidence import (
    get_authoritative_correction,
)
from backend.app.ai.recommendation_validator import validate_recommendation


def generate_response(tokenizer, model, prompt, max_new_tokens=400):
    import torch

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    inputs = tokenizer(
        text,
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

    generated_tokens = outputs[0][
        inputs["input_ids"].shape[-1]:
    ]

    return tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    ).strip()


def extract_affected_record(validation_report):
    """
    Extract the affected record and field from the validation report.

    Currently supports the controlled R011 invalid-latitude experiment.
    """

    for issue in validation_report.get("issues", []):
        if issue.get("rule_id") != "R011":
            continue

        if issue.get("description") != "Invalid latitude values detected.":
            continue

        # Controlled R011 experiment currently targets stop_id=1.
        # The actual record is obtained from DB evidence rather than
        # being supplied to the LLM.
        return {
            "table": "stops",
            "record_id": "1",
            "field": "stop_lat",
        }

    return None


def build_correction_prompt(
    validation_report,
    db_evidence,
    authoritative_evidence,
):
    return f"""
You are the YatriSetu Transit Operations Intelligence System.

Your task is to formulate a database correction proposal from
ALREADY VERIFIED evidence.

IMPORTANT SAFETY RULES:

1. Do not invent any value.
2. Do not infer a replacement value.
3. Use authoritative_value exactly as provided.
4. Do not propose changes to fields absent from authoritative evidence.
5. The current database value must remain old_value.
6. Database modification requires explicit administrator approval.
7. Return JSON only.
8. requires_admin_approval must always be true.

VALIDATION REPORT:
{json.dumps(validation_report, indent=2)}

DATABASE EVIDENCE:
{json.dumps(db_evidence, indent=2)}

VERIFIED AUTHORITATIVE EVIDENCE:
{json.dumps(authoritative_evidence, indent=2)}

Return exactly this structure:

{{
  "issue_summary": "...",
  "primary_issue": "...",
  "related_issues": [],
  "evidence": [],
  "unknowns": [],
  "recommended_action": "...",
  "risk_level": "HIGH",
  "confidence": 0.0,
  "proposed_changes": [
    {{
      "table": "stops",
      "record_id": "...",
      "field": "...",
      "old_value": 0,
      "proposed_value": 0,
      "evidence_source": "..."
    }}
  ],
  "requires_admin_approval": true
}}
"""


def run_correction_agent(
    tokenizer,
    model,
    validation_report,
):
    """
    Run the Admin Agent only when deterministic evidence
    establishes a verified correction.
    """

    affected_record = extract_affected_record(validation_report)

    if affected_record is None:
        return {
            "status": "BLOCKED",
            "reason": "No supported affected record was identified.",
        }

    if affected_record["table"] != "stops":
        return {
            "status": "BLOCKED",
            "reason": "Unsupported table.",
        }

    db_evidence = get_stop_evidence(
        stop_id=affected_record["record_id"]
    )

    if db_evidence is None:
        return {
            "status": "BLOCKED",
            "reason": "Database evidence could not be obtained.",
        }

    current_value = db_evidence.get(
        affected_record["field"]
    )

    authoritative_evidence = get_authoritative_correction(
        stop_id=affected_record["record_id"],
        field=affected_record["field"],
        current_value=current_value,
    )

    if authoritative_evidence is None:
        return {
            "status": "BLOCKED",
            "reason": "No matching authoritative evidence was found.",
        }

    prompt = build_correction_prompt(
        validation_report=validation_report,
        db_evidence=db_evidence,
        authoritative_evidence=authoritative_evidence,
    )

    raw_response = generate_response(
        tokenizer,
        model,
        prompt,
    )

    try:
        recommendation = json.loads(raw_response)
    except json.JSONDecodeError:
        return {
            "status": "REJECT",
            "reason": "Admin Agent returned invalid JSON.",
            "raw_response": raw_response,
        }

    safety_validation = validate_recommendation(
        recommendation,
        validation_report,
    )

    return {
        "status": safety_validation["validation_status"],
        "recommendation": recommendation,
        "safety_validation": safety_validation,
        "authoritative_evidence": authoritative_evidence,
    }