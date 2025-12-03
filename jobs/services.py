"""
NLP-powered utilities for extracting and matching skills.

This module centralizes all skill intelligence so both jobs and candidates
can share the same extraction pipeline. The implementation uses spaCy when
available and falls back to a lightweight dictionary-based approach when the
NLP model is not installed (e.g., on constrained hosting environments).
"""

from __future__ import annotations

import re
from collections import defaultdict
from functools import lru_cache
from typing import Dict, List, Optional
import logging

try:
    import spacy
except ImportError:  # pragma: no cover - spaCy might be missing in some envs
    spacy = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Prefetch

from .skills_dictionary import ALL_SKILLS
from .models import Application, CandidateSkill, Job, JobSkill

logger = logging.getLogger(__name__)

# --- Configuration ----------------------------------------------------------------

DEFAULT_SPACY_MODEL = "en_core_web_sm"
MAX_RETURNED_SKILLS = 15
CONTEXT_KEYWORDS = {
    "required",
    "requirement",
    "must",
    "mandatory",
    "key",
    "essential",
    "preferred",
    "expert",
    "experience",
    "proven",
    "strong",
}

SKILL_LOOKUP: Dict[str, str] = {skill.lower(): skill for skill in ALL_SKILLS}


# --- spaCy helpers -----------------------------------------------------------------

@lru_cache(maxsize=2)
def get_nlp(model_name: str = DEFAULT_SPACY_MODEL):
    """Lazily load and cache the spaCy model."""
    if not spacy:
        return None
    try:
        return spacy.load(model_name)
    except Exception:
        return None


# --- Normalization helpers ---------------------------------------------------------

def normalize_phrase(phrase: str) -> str:
    if not phrase:
        return ""
    return re.sub(r"\s+", " ", phrase.strip().lower())


def find_canonical_skill(phrase: str) -> Optional[str]:
    """
    Map a free-form phrase to our canonical skill dictionary.

    We attempt exact matches first, followed by substring and token overlaps.
    """
    normalized = normalize_phrase(phrase)
    if not normalized:
        return None
    if normalized in SKILL_LOOKUP:
        return SKILL_LOOKUP[normalized]
    # Check if the phrase contains a known skill term or vice versa.
    for skill_key, canonical in SKILL_LOOKUP.items():
        if skill_key in normalized or normalized in skill_key:
            return canonical
    return None


def sentence_has_context(sentence: str) -> bool:
    normalized = normalize_phrase(sentence)
    return any(keyword in normalized for keyword in CONTEXT_KEYWORDS)


# --- Extraction logic --------------------------------------------------------------

def _update_skill_stats(stats: Dict[str, Dict], skill: str, position: int, sentence: str):
    entry = stats.setdefault(
        skill,
        {
            "count": 0,
            "positions": [],
            "context_hits": 0,
        },
    )
    entry["count"] += 1
    entry["positions"].append(position)
    if sentence_has_context(sentence):
        entry["context_hits"] += 1


def _calculate_weight(
    skill: str,
    data: Dict,
    total_tokens: int,
    job_title: str,
) -> Dict[str, int]:
    base_score = 5
    frequency_bonus = min(data.get("count", 0) * 0.75, 3)
    earliest_position = min(data.get("positions", [])) if data.get("positions") else 0
    relative_position = earliest_position / total_tokens if total_tokens else 0
    position_bonus = 1 if relative_position <= 0.2 else 0
    context_bonus = min(data.get("context_hits", 0), 2)
    title_bonus = 2 if skill.lower() in normalize_phrase(job_title) else 0

    weight = base_score + frequency_bonus + position_bonus + context_bonus + title_bonus
    weight = min(int(round(weight)), 10)
    confidence = min(10, weight + context_bonus)

    return {
        "skill": skill,
        "weight": weight,
        "confidence": confidence,
    }


def extract_skills_with_nlp(
    text: str,
    job_title: str = "",
    max_skills: int = MAX_RETURNED_SKILLS,
) -> List[Dict[str, int]]:
    """
    Extract skills using spaCy noun chunks, entities, and keywords.
    Falls back to dictionary-only matching when spaCy is unavailable.
    """
    if not text:
        return []
    nlp = get_nlp()
    if not nlp:
        return extract_skills_dictionary(text, job_title, max_skills)

    doc = nlp(text)
    total_tokens = len(doc)
    stats: Dict[str, Dict] = {}

    # 1) Named entities
    for ent in doc.ents:
        skill = find_canonical_skill(ent.text)
        if skill:
            _update_skill_stats(stats, skill, ent.start, ent.sent.text)

    # 2) Noun chunks
    for chunk in doc.noun_chunks:
        skill = find_canonical_skill(chunk.text)
        if skill:
            _update_skill_stats(stats, skill, chunk.start, chunk.sent.text)

    # 3) Important tokens
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN"}:
            skill = find_canonical_skill(token.lemma_)
            if skill:
                _update_skill_stats(stats, skill, token.i, token.sent.text)

    # If no matches, fallback to dictionary scanning.
    if not stats:
        return extract_skills_dictionary(text, job_title, max_skills)

    scored = [
        _calculate_weight(skill, data, total_tokens, job_title)
        for skill, data in stats.items()
    ]
    scored.sort(key=lambda item: item["weight"], reverse=True)
    return scored[:max_skills]


def extract_skills_dictionary(
    text: str,
    job_title: str = "",
    max_skills: int = MAX_RETURNED_SKILLS,
) -> List[Dict[str, int]]:
    """
    Lightweight extractor that simply scans for dictionary matches.
    Acts as a fallback when spaCy cannot be used.
    """
    if not text:
        return []
    normalized_text = normalize_phrase(text)
    stats: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "positions": [], "context_hits": 0})

    for skill_key, canonical in SKILL_LOOKUP.items():
        occurrences = [m.start() for m in re.finditer(re.escape(skill_key), normalized_text)]
        if occurrences:
            stats[canonical]["count"] = len(occurrences)
            stats[canonical]["positions"] = occurrences
            # Check for context keywords near the skill
            for pos in occurrences:
                start = max(0, pos - 50)
                end = min(len(normalized_text), pos + len(skill_key) + 50)
                context_text = normalized_text[start:end]
                if any(keyword in context_text for keyword in ["required", "essential", "must", "need", "important"]):
                    stats[canonical]["context_hits"] += 1

    if not stats:
        return []

    total_tokens = len(normalized_text.split())
    scored = [
        _calculate_weight(skill, data, total_tokens, job_title)
        for skill, data in stats.items()
    ]
    scored.sort(key=lambda item: item["weight"], reverse=True)
    return scored[:max_skills]


def extract_skills(
    text: str,
    job_title: str = "",
    max_skills: int = MAX_RETURNED_SKILLS,
    force_dictionary: bool = False,
) -> List[Dict[str, int]]:
    """
    Public API that chooses the best extraction strategy automatically.
    """
    if force_dictionary:
        return extract_skills_dictionary(text, job_title, max_skills)
    return extract_skills_with_nlp(text, job_title, max_skills)


def extract_candidate_skills(
    text: str,
    max_skills: int = MAX_RETURNED_SKILLS,
) -> List[Dict[str, int]]:
    """
    Convenience wrapper for candidate materials where the job title context
    is less important. We still leverage the main extractor for consistency.
    """
    return extract_skills(text, job_title="", max_skills=max_skills)


def extract_text_from_pdf(file) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file: Django UploadedFile or file-like object
        
    Returns:
        Extracted text as string, or empty string if extraction fails
    """
    if not PyPDF2:
        logger.warning("PyPDF2 not installed, cannot extract text from PDF")
        return ""
    
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.warning(f"Failed to extract text from PDF: {e}")
        return ""


def extract_text_from_docx(file) -> str:
    """
    Extract text content from a DOCX file.
    
    Args:
        file: Django UploadedFile or file-like object
        
    Returns:
        Extracted text as string, or empty string if extraction fails
    """
    if not Document:
        logger.warning("python-docx not installed, cannot extract text from DOCX")
        return ""
    
    try:
        # Reset file pointer to beginning
        file.seek(0)
        doc = Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.warning(f"Failed to extract text from DOCX: {e}")
        return ""


def extract_text_from_resume(resume_file) -> str:
    """
    Extract text from a resume file (PDF, DOC, or DOCX).
    
    Args:
        resume_file: Django UploadedFile
        
    Returns:
        Extracted text as string
    """
    if not resume_file:
        return ""
    
    filename = resume_file.name.lower()
    
    # Reset file pointer to beginning
    resume_file.seek(0)
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(resume_file)
    elif filename.endswith(('.docx', '.doc')):
        return extract_text_from_docx(resume_file)
    else:
        logger.warning(f"Unsupported file type for resume: {filename}")
        return ""


def save_candidate_skills_from_text(
    user,
    text: str,
    source: str = "cover_letter",
    max_skills: int = MAX_RETURNED_SKILLS,
    min_weight: int = 5,
):
    """
    Persist candidate skills derived from free-form text.

    Args:
        user: Django auth user (must be a candidate profile).
        text: Source text (cover letter, resume excerpt, etc.).
        source: Tag describing where the skill came from.
        max_skills: Limit for extracted skills.
        min_weight: Minimum weight required before saving.
    """
    if not text:
        return []

    skills_payload = extract_candidate_skills(text, max_skills=max_skills)
    saved_skills = []

    with transaction.atomic():
        for payload in skills_payload:
            if payload["weight"] < min_weight:
                continue
            obj, _ = CandidateSkill.objects.update_or_create(
                user=user,
                skill_name=payload["skill"],
                source=source,
                defaults={"confidence": payload["confidence"]},
            )
            saved_skills.append(obj)
    return saved_skills


def save_job_skills(
    job: Job,
    force_dictionary: bool = False,
    max_skills: int = MAX_RETURNED_SKILLS,
):
    """
    Extract and persist skills for a Job instance.
    """
    if not job.description:
        job.skills_extracted = False
        job.save(update_fields=["skills_extracted"])
        return []

    skills_payload = extract_skills(
        job.description,
        job_title=job.title,
        max_skills=max_skills,
        force_dictionary=force_dictionary,
    )

    with transaction.atomic():
        job.job_skills.all().delete()
        for payload in skills_payload:
            JobSkill.objects.create(
                job=job,
                skill_name=payload["skill"],
                weight=payload["weight"],
            )
        job.skills_extracted = bool(skills_payload)
        job.save(update_fields=["skills_extracted"])

    return skills_payload


def get_company_candidate_queryset(job: Job):
    """
    Return a queryset of candidate users who have applied to this company's jobs.
    """
    company_job_ids = Job.objects.filter(company=job.company).values_list("id", flat=True)
    applicant_ids = (
        Application.objects.filter(job_id__in=company_job_ids)
        .order_by()
        .values_list("applicant_id", flat=True)
        .distinct()
    )
    User = get_user_model()
    return User.objects.filter(id__in=applicant_ids).prefetch_related(
        Prefetch("candidate_skills", queryset=CandidateSkill.objects.all())
    )


def build_candidate_match_payload(job: Job, min_match_weight: int = 1):
    """
    Build a list of candidate matches with fit scores for the given job.
    """
    job_skills = list(job.job_skills.all())
    if not job_skills:
        return []

    total_weight = sum(skill.weight for skill in job_skills) or 1
    job_skill_lookup = {skill.skill_name.lower(): skill.weight for skill in job_skills}

    candidates = []
    for candidate in get_company_candidate_queryset(job):
        candidate_skills = list(candidate.candidate_skills.all())
        if not candidate_skills:
            continue

        matched_weight = 0
        matched_skill_names = []
        candidate_skill_lookup = {cs.skill_name.lower(): cs for cs in candidate_skills}

        for skill_name, weight in job_skill_lookup.items():
            if skill_name in candidate_skill_lookup:
                matched_weight += weight
                matched_skill_names.append(candidate_skill_lookup[skill_name].skill_name)

        if matched_weight < min_match_weight:
            continue

        fit_score = round((matched_weight / total_weight) * 100, 1)
        candidates.append(
            {
                "candidate": candidate,
                "fit_score": fit_score,
                "matched_weight": matched_weight,
                "total_weight": total_weight,
                "matched_skills": matched_skill_names,
            }
        )

    candidates.sort(key=lambda item: item["fit_score"], reverse=True)
    return candidates

