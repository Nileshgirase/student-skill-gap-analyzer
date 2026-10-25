import re
from dataclasses import dataclass
from typing import Literal

from app.services.skill_normalizer import canonicalize_skill_name

RequirementType = Literal["required", "preferred", "mentioned", "uncertain"]


@dataclass
class ExtractedSkill:
    skill_name: str
    canonical_skill: str
    requirement_type: RequirementType
    evidence_text: str
    extraction_method: str = "dictionary_phrase_match"
    confidence: float = 0.85


# Controlled vocabulary of technical skills: (Display Name, Regex pattern or aliases)
# Multi-word terms are listed and matched first to prevent partial substring matches.
SKILL_TAXONOMY = [
    # Multi-word platforms & frameworks
    ("Google Cloud Platform", r"\b(?:google cloud platform|gcp)\b"),
    ("Amazon Web Services", r"\b(?:amazon web services|aws)\b"),
    ("Microsoft Azure", r"\b(?:microsoft azure|azure cloud|azure)\b"),
    ("Power BI", r"\b(?:microsoft power bi|ms power bi|power bi|powerbi)\b"),
    ("Apache Spark", r"\b(?:apache spark|spark)\b"),
    ("Apache Kafka", r"\b(?:apache kafka|kafka)\b"),
    ("Apache Airflow", r"\b(?:apache airflow|airflow)\b"),
    ("Spring Boot", r"\b(?:spring boot|spring framework)\b"),
    ("REST API", r"\b(?:rest apis?|restful apis?|restful web services?)\b"),
    ("GraphQL", r"\bgraphql\b"),
    ("CI/CD", r"\b(?:ci/cd|continuous integration|continuous deployment)\b"),
    ("Machine Learning", r"\b(?:machine learning|ml)\b"),
    ("Deep Learning", r"\bdeep learning\b"),
    ("Scikit-Learn", r"\b(?:scikit-learn|sklearn)\b"),
    ("TensorFlow", r"\btensorflow\b"),
    ("PyTorch", r"\bpytorch\b"),
    ("Pandas", r"\bpandas\b"),
    ("NumPy", r"\bnumpy\b"),
    ("Next.js", r"\b(?:next\.js|nextjs)\b"),
    ("Vue.js", r"\b(?:vue\.js|vuejs|vue)\b"),
    ("Node.js", r"\b(?:node\.js|nodejs|node)\b"),
    ("React", r"\b(?:react\.js|reactjs|react native|react)\b"),
    ("Angular", r"\bangular(?:\.js)?\b"),
    ("FastAPI", r"\bfastapi\b"),
    ("Django", r"\bdjango\b"),
    ("Flask", r"\bflask\b"),
    (".NET", r"\b(?:\.net|dotnet|asp\.net)\b"),
    ("Terraform", r"\bterraform\b"),
    ("Kubernetes", r"\b(?:kubernetes|k8s)\b"),
    ("Docker", r"\bdocker(?:\s+containers)?\b"),
    ("Linux", r"\blinux\b"),
    ("Git", r"\bgit\b"),
    # Databases
    ("PostgreSQL", r"\b(?:postgresql|postgres)\b"),
    ("MySQL", r"\bmysql\b"),
    ("MongoDB", r"\bmongodb\b"),
    ("Redis", r"\bredis\b"),
    ("SQLite", r"\bsqlite\b"),
    ("Snowflake", r"\bsnowflake\b"),
    ("Elasticsearch", r"\belasticsearch\b"),
    ("SQL", r"\bsql\b"),
    ("NoSQL", r"\bnosql\b"),
    # Languages (special contextual word boundary rules)
    ("C++", r"\b[cC]\+\+(?!\w)"),
    ("C#", r"\b[cC]#(?!\w)"),
    ("TypeScript", r"\btypescript\b"),
    ("JavaScript", r"\bjavascript\b"),
    ("Python", r"\bpython\b"),
    ("Java", r"\bjava\b(?!\s*script)"),
    ("PHP", r"\bphp\b"),
    ("Ruby", r"\bruby\b(?!\s*on\s*rails)?"),
    ("Rust", r"\brust\b"),
    ("Kotlin", r"\bkotlin\b"),
    ("Swift", r"\bswift\b"),
    ("Scala", r"\bscala\b"),
    ("HTML", r"\bhtml(?:5)?\b"),
    ("CSS", r"\bcss(?:3)?\b"),
    ("Tableau", r"\btableau\b"),
    ("Excel", r"\b(?:microsoft excel|ms excel|excel)\b"),
    # Disambiguated short languages (R, Go, C)
    ("R", r"(?:\b[rR]\s+(?:programming|language|scripting|code)\b|\b(?:in|with|using)\s+[rR]\b|\b[rR]\s*[/,]\s*(?:python|sql)\b|\b(?:python|sql)\s*[/,]\s*[rR]\b)"),
    ("Go", r"(?:\b[gG]olang\b|\b[gG]o\s+(?:programming|language|developer|engineer|code)\b|\b(?:in|with|using)\s+[gG]o\b|\b(?:python|java|c\+\+)\s*,\s*[gG]o\b)"),
    ("C", r"(?:\b[cC]\s+(?:programming|language|developer|code)\b|\b[cC]\s*[/,]\s*C\+\+\b|\bC\+\+\s*[/,]\s*[cC]\b)"),
]

# Classification regex indicators
PREFERRED_PATTERN = re.compile(
    r"\b(?:preferred|nice to have|bonus|plus|desired|beneficial|ideal|optional|not required)\b",
    re.IGNORECASE,
)
REQUIRED_PATTERN = re.compile(
    r"\b(?:required|must have|requirements?|qualifications?|minimum qualifications?|proficiency in|experience with|strong understanding of|essential|proven track record)\b",
    re.IGNORECASE,
)


def extract_skills_from_text(description_text: str) -> list[ExtractedSkill]:
    """
    Scans a verified job description text, recognizes skills using controlled phrase matching,
    extracts the exact evidence sentence, and assigns a substantiated requirement type.
    """
    if not description_text:
        return []

    # Segment description into coherent sentence / bullet chunks
    raw_chunks = re.split(r"(?<=[.!?])\s+|\n+|•|\*|(?<=\n)-\s+", description_text)
    chunks = [c.strip() for c in raw_chunks if len(c.strip()) >= 5]

    extracted_map: dict[str, ExtractedSkill] = {}

    for chunk in chunks:
        # Determine chunk requirement context
        # Preferred keywords (e.g. 'is a plus', 'nice to have') designate optional qualifications
        has_preferred = bool(PREFERRED_PATTERN.search(chunk))
        has_required = bool(REQUIRED_PATTERN.search(chunk))

        if has_preferred:
            req_type: RequirementType = "preferred"
            conf = 0.90
        elif has_required:
            req_type = "required"
            conf = 0.90
        else:
            req_type = "mentioned"
            conf = 0.75

        # Check each skill pattern against the chunk
        for skill_name, pattern_str in SKILL_TAXONOMY:
            match = re.search(pattern_str, chunk, re.IGNORECASE)
            if match:
                canonical = canonicalize_skill_name(skill_name)

                # If already extracted, promote to 'required' if the new chunk is stronger
                if canonical in extracted_map:
                    existing = extracted_map[canonical]
                    if req_type == "required" and existing.requirement_type != "required":
                        extracted_map[canonical] = ExtractedSkill(
                            skill_name=skill_name,
                            canonical_skill=canonical,
                            requirement_type="required",
                            evidence_text=chunk,
                            confidence=conf,
                        )
                else:
                    extracted_map[canonical] = ExtractedSkill(
                        skill_name=skill_name,
                        canonical_skill=canonical,
                        requirement_type=req_type,
                        evidence_text=chunk,
                        confidence=conf,
                    )

    return list(extracted_map.values())
