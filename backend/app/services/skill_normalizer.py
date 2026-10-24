import re

COMMON_ALIASES = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "py": "python",
    "python": "python",
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "react.js": "react",
    "reactjs": "react",
    "react": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "vue": "vue",
    "node.js": "nodejs",
    "nodejs": "nodejs",
    "node": "nodejs",
    "golang": "go",
    "go lang": "go",
    "ms power bi": "power bi",
    "microsoft power bi": "power bi",
    "powerbi": "power bi",
    "power bi": "power bi",
    "k8s": "kubernetes",
    "docker containers": "docker",
    "amazon web services": "aws",
    "google cloud platform": "gcp",
}


def canonicalize_skill_name(raw_name: str) -> str:
    """
    Normalizes a skill name to its canonical lowercased comparison key.
    Preserves acronyms and multi-word terms while mapping known variants.
    """
    cleaned = re.sub(r"\s+", " ", raw_name.strip()).lower()
    return COMMON_ALIASES.get(cleaned, cleaned)
