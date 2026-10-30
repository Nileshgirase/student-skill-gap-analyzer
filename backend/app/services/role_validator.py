import re
import difflib

# Explicit non-IT professions and domains that are outside the scope of IT & technology analysis
NON_IT_PROFESSIONS = {
    # Engineering outside IT / Software
    "civil engineer",
    "civil engineering",
    "mechanical engineer",
    "mechanical engineering",
    "chemical engineer",
    "chemical engineering",
    "electrical power engineer",
    "structural engineer",
    "aerospace engineer",
    "petroleum engineer",
    "mining engineer",
    "marine engineer",
    "agricultural engineer",
    "environmental engineer",
    "biomedical engineer",
    "metallurgical engineer",
    # Healthcare & Medicine
    "medical doctor",
    "doctor",
    "physician",
    "surgeon",
    "nurse",
    "registered nurse",
    "dentist",
    "pharmacist",
    "veterinarian",
    "therapist",
    "physiotherapist",
    "paramedic",
    "radiologist",
    "optometrist",
    "psychologist",
    "psychiatrist",
    # Law & Public Safety
    "lawyer",
    "attorney",
    "judge",
    "paralegal",
    "police",
    "police officer",
    "firefighter",
    "security guard",
    # Hospitality & Food
    "chef",
    "cook",
    "baker",
    "waiter",
    "waitress",
    "bartender",
    # Trades & Construction
    "plumber",
    "electrician",
    "carpenter",
    "welder",
    "mason",
    "mechanic",
    "auto mechanic",
    "painter",
    # Transportation
    "driver",
    "truck driver",
    "bus driver",
    "taxi driver",
    "pilot",
    "flight attendant",
    "locomotive engineer",
    "train driver",
    # Education & Non-tech office
    "school teacher",
    "elementary teacher",
    "kindergarten teacher",
    "real estate agent",
    "realtor",
}

# Nonsensical or non-job keywords that flag invalid inputs
NONSENSICAL_WORDS = {
    "banana", "apple", "orange", "pizza", "burger", "potato", "monkey", "elephant",
    "alien", "dinosaur", "magic", "unicorn", "superhero", "nonsense", "dummy", "fake",
    "test123", "asdf", "qwerty", "foobar", "placeholder"
}

# Core IT domain terms indicating supported technology roles
IT_DOMAIN_KEYWORDS = {
    # Engineering & Development
    "software", "developer", "development", "programmer", "programming", "coder", "coding",
    "engineer", "engineering", "architect", "architecture", "lead", "sde", "swe",
    # Web & Application
    "frontend", "front end", "backend", "back end", "fullstack", "full stack", "web",
    "mobile", "android", "ios", "flutter", "react", "angular", "vue", "node", "django",
    "fastapi", "spring", "flask", "api", "microservices",
    # Data & Analytics
    "data", "analyst", "analytics", "bi", "business intelligence", "scientist", "science",
    "machine learning", "ml", "ai", "artificial intelligence", "deep learning", "nlp",
    "computer vision", "big data", "etl", "data warehouse", "statistician", "database",
    "dba", "sql",
    # Infrastructure, Cloud & DevOps
    "cloud", "devops", "sre", "site reliability", "platform", "infrastructure", "infra",
    "system", "systems", "sysadmin", "network", "networking", "server", "linux", "unix",
    "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform",
    # Security
    "cyber", "cybersecurity", "infosec", "information security", "security", "soc",
    "penetration", "pentest", "vulnerability",
    # Testing & Quality
    "qa", "quality assurance", "test", "testing", "sdet", "automation", "tester",
    # IT Product, Design & Technical Management
    "ui", "ux", "ui/ux", "designer", "product designer", "web designer", "ux designer", "ui designer",
    "technical product manager", "product manager", "it manager",
    "scrum master", "technical lead", "tech lead", "solutions architect", "it support",
    "help desk", "service desk", "it specialist", "technology consultant",
    # Programming Languages in title
    "python", "java", "c++", "c#", ".net", "golang", "go", "rust", "ruby", "php",
    "javascript", "typescript", "swift", "kotlin", "scala", "r"
}

ROLE_ERROR_MESSAGE = (
    "This job role is invalid or is not currently supported by our IT and technology "
    "job analysis system. Please enter a valid IT or technology-related job role."
)


def validate_it_role(role_title: str) -> tuple[bool, str | None]:
    """
    Validates that a free-text job role represents a legitimate IT or technology-related role.
    Rejects:
    1. Blank or nonsensical/gibberish input (e.g. '123456', 'asdfghjkl', 'Quantum Banana Analyst 987654').
    2. Explicit non-IT roles (e.g. 'Civil Engineer', 'Medical Doctor', 'Chef', 'Lawyer').
    3. Roles lacking recognizable technology / computing / digital engineering domain relevance.

    Returns:
        (True, None) if valid and supported.
        (False, error_message) if invalid or unsupported.
    """
    if not role_title or not role_title.strip():
        return False, "Job role cannot be empty."

    clean_role = role_title.strip()
    norm_role = re.sub(r"[^a-z0-9\s/+#\.-]", " ", clean_role.lower())
    tokens = [t.strip() for t in norm_role.split() if t.strip()]

    if not tokens:
        return False, ROLE_ERROR_MESSAGE

    # 1. Check for excessive digits or gibberish patterns (e.g. '987654', 'asdfghjkl')
    digit_chars = sum(c.isdigit() for c in clean_role)
    if digit_chars >= 4:
        # e.g., 'Quantum Banana Analyst 987654' or '123456'
        return False, ROLE_ERROR_MESSAGE

    # 2. Check for explicit nonsensical words
    for t in tokens:
        if t in NONSENSICAL_WORDS:
            return False, ROLE_ERROR_MESSAGE

    # 3. Check for exact or high-similarity non-IT professions
    for non_it in NON_IT_PROFESSIONS:
        if non_it in norm_role:
            # Exception: if clearly qualified by IT context (e.g. 'Software Engineer for Civil Engineering')
            it_qualifiers = {"software", "data", "developer", "programmer", "it", "systems"}
            if not any(q in tokens for q in it_qualifiers):
                return False, ROLE_ERROR_MESSAGE

        # Check token sequence similarity for phrases like 'civil engineer' or 'medical doctor'
        if len(tokens) >= 2:
            role_phrase = " ".join(tokens)
            if difflib.SequenceMatcher(None, role_phrase, non_it).ratio() >= 0.85:
                return False, ROLE_ERROR_MESSAGE

    # 4. Check for analyst without IT/Data qualification
    # E.g. 'Analyst' alone is fine if data/business/systems, but 'Banana Analyst' or 'Political Analyst' is not.
    if "analyst" in tokens and len(tokens) >= 2:
        non_it_analysts = {"political", "sports", "cricket", "football", "credit", "financial", "equity", "investment", "banana"}
        if any(t in non_it_analysts for t in tokens):
            it_analyst_terms = {"data", "bi", "business intelligence", "systems", "it", "security", "technical", "qa", "software"}
            if not any(term in norm_role for term in it_analyst_terms):
                return False, ROLE_ERROR_MESSAGE

    # 5. Must have at least one valid IT domain indicator (with typo tolerance for single words)
    has_it_indicator = False
    for keyword in IT_DOMAIN_KEYWORDS:
        if " " in keyword:
            if keyword in norm_role:
                has_it_indicator = True
                break
        else:
            if keyword in tokens:
                has_it_indicator = True
                break
            # Fuzzy typo tolerance for words >= 5 letters (e.g. 'anaylst' -> 'analyst', 'devloper' -> 'developer')
            if any(len(t) >= 5 and difflib.SequenceMatcher(None, t, keyword).ratio() >= 0.8 for t in tokens):
                has_it_indicator = True
                break

    if not has_it_indicator:
        return False, ROLE_ERROR_MESSAGE

    return True, None
