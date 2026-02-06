"""Unit tests for ai_analysis.py pure functions. No LLM or network needed."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_analysis import (
    _normalize_analysis_keys,
    _validate_analysis_result,
    _build_failure_result,
    _lenient_parse,
    _regex_extract,
)

from tests.test_helpers import report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None, help="Path to test.config (ignored for unit tests)")
    parser.add_argument("--filter", default=None, help="Filter params (ignored for unit tests)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout (ignored for unit tests)")
    args = parser.parse_args()

    if args.dry_run:
        print("Would run: unit tests for _normalize_analysis_keys, _validate_analysis_result,")
        print("  _build_failure_result, _lenient_parse, _regex_extract")
        return 0

    failed = 0

    # _normalize_analysis_keys
    m = _normalize_analysis_keys({"Empfehlung": "Hold", "Genauigkeit": "Low"})
    if m.get("Recommendation") == "Hold" and m.get("Confidence") == "Low":
        report("normalize_german_keys", True, "OK")
    else:
        report("normalize_german_keys", False, f"Got {m}")
        failed += 1

    # _validate_analysis_result (a) complete valid
    valid, missing = _validate_analysis_result({
        "Recommendation": "Hold", "recommended_quantity": 0,
        "Reasoning": "x", "quantity_reasoning": "y", "Confidence": "Low"
    })
    if valid and not missing:
        report("validate_complete_valid_result", True, "OK")
    else:
        report("validate_complete_valid_result", False, f"valid={valid} missing={missing}")
        failed += 1

    # (b) missing Recommendation
    valid, missing = _validate_analysis_result({
        "recommended_quantity": 0, "Reasoning": "x", "quantity_reasoning": "y", "Confidence": "Low"
    })
    if not valid and "Recommendation" in missing:
        report("validate_missing_recommendation", True, "OK")
    else:
        report("validate_missing_recommendation", False, f"valid={valid} missing={missing}")
        failed += 1

    # (c) wrong type for recommended_quantity
    valid, missing = _validate_analysis_result({
        "Recommendation": "Hold", "recommended_quantity": "ten",
        "Reasoning": "x", "quantity_reasoning": "y", "Confidence": "Low"
    })
    if not valid and "recommended_quantity" in missing:
        report("validate_wrong_quantity_type", True, "OK")
    else:
        report("validate_wrong_quantity_type", False, f"valid={valid} missing={missing}")
        failed += 1

    # (d) invalid Confidence
    valid, missing = _validate_analysis_result({
        "Recommendation": "Hold", "recommended_quantity": 0,
        "Reasoning": "x", "quantity_reasoning": "y", "Confidence": "Invalid"
    })
    if not valid and "Confidence" in missing:
        report("validate_invalid_confidence", True, "OK")
    else:
        report("validate_invalid_confidence", False, f"valid={valid} missing={missing}")
        failed += 1

    # _build_failure_result
    r = _build_failure_result(["Recommendation"], "raw", "TestAsset")
    if (r.get("Recommendation") == "[Parse failed]" and r.get("_parse_failed") is True and
            r.get("recommended_quantity") == 0):
        report("build_failure_result", True, "OK")
    else:
        report("build_failure_result", False, f"Got {r}")
        failed += 1

    # _lenient_parse (a) complete valid
    out = _lenient_parse({"Recommendation": "Hold", "recommended_quantity": 5, "Reasoning": "a",
                         "quantity_reasoning": "b", "Confidence": "Medium"})
    if out.get("Recommendation") == "Hold" and out.get("recommended_quantity") == 5 and "_parse_failed" not in out:
        report("lenient_parse_complete_valid", True, "OK")
    else:
        report("lenient_parse_complete_valid", False, f"Got {out}")
        failed += 1

    # (b) missing fields
    out = _lenient_parse({"Recommendation": "Hold"})
    if (out.get("quantity_reasoning") == "[Missing]" and out.get("_parse_failed") is True):
        report("lenient_parse_missing_fields", True, "OK")
    else:
        report("lenient_parse_missing_fields", False, f"Got {out}")
        failed += 1

    # (c) invalid Recommendation
    out = _lenient_parse({"Recommendation": "Maybe", "recommended_quantity": 0, "Reasoning": "a",
                         "quantity_reasoning": "b", "Confidence": "Low"})
    if out.get("Recommendation") == "[Invalid]" and out.get("_parse_failed") is True:
        report("lenient_parse_invalid_recommendation", True, "OK")
    else:
        report("lenient_parse_invalid_recommendation", False, f"Got {out}")
        failed += 1

    # (d) non-int quantity coerced to 0
    out = _lenient_parse({"Recommendation": "Hold", "recommended_quantity": "x", "Reasoning": "a",
                         "quantity_reasoning": "b", "Confidence": "Low"})
    if out.get("recommended_quantity") == 0:
        report("lenient_parse_quantity_coerce", True, "OK")
    else:
        report("lenient_parse_quantity_coerce", False, f"Got {out}")
        failed += 1

    # (e) optional target_price, stop_loss
    out = _lenient_parse({"Recommendation": "Hold", "recommended_quantity": 0, "Reasoning": "a",
                         "quantity_reasoning": "b", "Confidence": "Low", "target_price": 10.5,
                         "stop_loss": None})
    if out.get("target_price") == 10.5 and out.get("stop_loss") is None:
        report("lenient_parse_optional_fields", True, "OK")
    else:
        report("lenient_parse_optional_fields", False, f"Got {out}")
        failed += 1

    # _regex_extract (a) Buy sentence
    r = _regex_extract("I recommend Buy 10 shares because of news")
    if r and r.get("Recommendation") == "Buy" and r.get("recommended_quantity") == 10:
        report("regex_extract_buy_sentence", True, "OK")
    else:
        report("regex_extract_buy_sentence", False, f"Got {r}")
        failed += 1

    # (b) empty string
    r = _regex_extract("")
    if r is None:
        report("regex_extract_empty", True, "OK")
    else:
        report("regex_extract_empty", False, f"Got {r}")
        failed += 1

    # (c) Hold confidence: Medium
    r = _regex_extract("Hold confidence: Medium")
    if r and r.get("Recommendation") == "Hold" and r.get("Confidence") == "Medium":
        report("regex_extract_hold_confidence", True, "OK")
    else:
        report("regex_extract_hold_confidence", False, f"Got {r}")
        failed += 1

    # (d) no recognizable fields
    r = _regex_extract("Some random text with no structure")
    if r is None:
        report("regex_extract_no_fields", True, "OK")
    else:
        report("regex_extract_no_fields", False, f"Got {r}")
        failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
