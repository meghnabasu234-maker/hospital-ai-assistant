EMERGENCY_KEYWORDS = [
    "chest pain",
    "heart attack",
    "stroke",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "unconscious",
    "fainted",
    "seizure",
    "poisoning",
    "overdose",
    "suicide",
    "self harm",
    "severe injury"
]


MEDICAL_ADVICE_KEYWORDS = [
    "what medicine",
    "which medicine",
    "should i take",
    "what should i take",
    "how to treat",
    "how can i treat",
    "diagnose me",
    "do i have",
    "is this cancer",
    "is this serious",
    "treatment for",
    "dosage",
    "dose",
    "prescription"
]


def is_emergency_question(question: str) -> bool:
    question = question.lower()

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in question:
            return True

    return False


def is_medical_advice_question(question: str) -> bool:
    question = question.lower()

    for keyword in MEDICAL_ADVICE_KEYWORDS:
        if keyword in question:
            return True

    return False