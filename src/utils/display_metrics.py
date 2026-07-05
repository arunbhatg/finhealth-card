"""Small display helpers with no heavy scoring imports."""


def court_case_count(profile: dict) -> int:
    courts = profile["courts"]
    return courts["civil_cases"] + courts["criminal_cases"] + courts["insolvency_petitions"]


def active_litigation_label(profile: dict) -> str:
    count = court_case_count(profile)
    if count == 0:
        return "None"
    outstanding = profile["courts"].get("total_outstanding_litigation_lakhs", 0)
    return f"Yes — {count} case(s), ₹{outstanding:.1f}L"


def bill_pay_on_time_pct(features: dict) -> float:
    return (features["electricity_payment_regularity"] + features["aa_emi_on_time_rate"]) / 2 * 100
