# Candidate Recommendation Feature - Simple Explanation

## 📋 What is This Feature?

Imagine you're a company looking to hire someone. You post a job (like "Python Developer"). Many people apply with their resumes and cover letters. 

**The Problem:** How do you quickly find the best candidates from hundreds of applications?

**Our Solution:** An AI-powered system that automatically:
1. Reads the job description and finds what skills are needed
2. Reads all candidate resumes and cover letters to find their skills
3. Matches candidates to the job based on their skills
4. Shows you a ranked list with "fit scores" (like 85% match, 70% match, etc.)

---

## 🎯 Real-World Example

**Job Posting:** "Senior Python Developer"
- Job description mentions: Python, Django, PostgreSQL, REST APIs, Docker

**Candidates Who Applied:**
- **Alice's Resume:** "5 years Python, Django expert, knows PostgreSQL, built REST APIs"
- **Bob's Resume:** "3 years JavaScript, React, Node.js"
- **Charlie's Resume:** "2 years Python, some Django experience"

**What Our System Does:**
1. Extracts skills from the job: `[Python: 10/10, Django: 10/10, PostgreSQL: 8/10, REST APIs: 9/10, Docker: 7/10]`
2. Extracts skills from each candidate's resume/cover letter
3. Calculates match scores:
   - **Alice:** 95% match (has all the important skills!)
   - **Charlie:** 60% match (has Python and Django, but missing others)
   - **Bob:** 20% match (wrong tech stack)

**Result:** The company sees Alice at the top of the list, saving hours of manual resume screening!

---

## 🔧 How It Works (Step by Step)

### Step 1: Job Skills Extraction
**When:** Company posts or updates a job description

**What Happens:**
- System reads the job description text
- Uses **NLP (Natural Language Processing)** to find skill keywords
- Assigns importance scores (0-10) to each skill
  - Skills mentioned multiple times = higher score
  - Skills near words like "required", "must have" = higher score
  - Skills in the job title = higher score

**Example:**
```
Job Description: "We need a Python developer with strong Django skills. 
PostgreSQL experience is required. Docker knowledge is a plus."

Extracted Skills:
- Python: 10/10 (in title + mentioned)
- Django: 9/10 (mentioned with "strong")
- PostgreSQL: 8/10 (marked as "required")
- Docker: 6/10 (marked as "plus")
```

**Where It's Stored:** `JobSkill` table in database

---

### Step 2: Candidate Skills Extraction
**When:** A candidate applies for a job (submits cover letter + resume)

**What Happens:**
- System reads the **cover letter** text
- System reads the **resume file** (PDF or DOCX)
- Extracts skills from both sources
- Stores them with a "source" tag (cover_letter or resume)

**Example:**
```
Alice's Application:
- Cover Letter: "I have 5 years of Python experience..."
- Resume: "Skills: Python, Django, PostgreSQL, REST APIs, Docker, Git"

Extracted Skills (from both sources):
- Python (from: resume, cover_letter)
- Django (from: resume)
- PostgreSQL (from: resume)
- REST APIs (from: resume)
- Docker (from: resume)
- Git (from: resume)
```

**Where It's Stored:** `CandidateSkill` table in database

---

### Step 3: Matching Candidates to Jobs
**When:** Company clicks "Find Matching Candidates" on a job

**What Happens:**
1. System gets all skills required for the job (with their importance scores)
2. System gets all candidates who applied to **this company's jobs** (not other companies!)
3. For each candidate:
   - Checks which job skills they have
   - Calculates a "fit score" based on:
     - How many required skills they have
     - How important those skills are (weighted)
   - Formula: `(Sum of matched skill weights / Total job skill weights) × 100`

**Example Calculation:**
```
Job Skills (total weight = 40):
- Python: 10
- Django: 10
- PostgreSQL: 8
- REST APIs: 9
- Docker: 7

Alice's Skills:
- Python ✓ (10 points)
- Django ✓ (10 points)
- PostgreSQL ✓ (8 points)
- REST APIs ✓ (9 points)
- Docker ✓ (7 points)

Alice's Fit Score = (10+10+8+9+7) / 40 × 100 = 44/40 × 100 = 110% → capped at 100%

Charlie's Skills:
- Python ✓ (10 points)
- Django ✓ (10 points)
- Missing: PostgreSQL, REST APIs, Docker

Charlie's Fit Score = (10+10) / 40 × 100 = 20/40 × 100 = 50%
```

4. Results are sorted by fit score (highest first)

**Where It's Shown:** Recommendations page for that job

---

## 🛠️ Technical Components (Simple Terms)

### 1. **NLP (Natural Language Processing)**
**What it is:** A way for computers to understand human language

**What we use:** spaCy library (a popular Python NLP tool)
- It can read text and identify important words/phrases
- It understands context (e.g., "Python programming" vs "python the snake")

**Why we need it:** To automatically find skills in job descriptions and resumes without manual tagging

---

### 2. **Skill Dictionary**
**What it is:** A curated list of known skills (like a vocabulary)

**Example skills in our dictionary:**
- Programming languages: Python, JavaScript, Java, C++
- Frameworks: Django, React, Spring Boot
- Databases: PostgreSQL, MySQL, MongoDB
- Tools: Docker, Git, AWS

**Why we need it:** To standardize skill names (e.g., "Python" vs "python" vs "Python programming" all become "Python")

What is the Skill Dictionary?
The skill dictionary is a manually curated list of skills we created in jobs/skills_dictionary.py. It contains:
Technical skills (70+ items): Python, Django, React, AWS, Docker, etc.
Soft skills (30+ items): Leadership, Communication, Problem Solving, etc.
Total: ~100 skills in the dictionary.


How It Works
We created the list: manually added common skills to the file.
The system uses it for matching: when NLP extracts text, it checks if the extracted words/phrases match anything in this dictionary.
Normalization: it helps standardize skill names (e.g., "Python", "python", "PYTHON" all become "Python").

Example
Without Dictionary:
Resume says: "I know Python programming"
Job says: "Looking for Python developer"
System might not match them (different wording)
With Dictionary:
Resume says: "I know Python programming"

NLP extracts: "Python programming" → checks dictionary → finds "python" → normalizes to "Python"
Job says: "Looking for Python developer"
NLP extracts: "Python developer" → checks dictionary → finds "python" → normalizes to "Python"
Match found.



Why We Created It:
Standardization: ensures consistent skill names across the system
Accuracy: reduces false positives from random words
Control: we decide which skills are recognized
Extensibility: easy to add more skills later


How to Explain This in an Interview
"We created a curated skill dictionary with about 100 common technical and soft skills. When NLP extracts text from job descriptions or resumes, it checks if the extracted phrases match our dictionary. This ensures we only recognize legitimate skills and standardize naming (e.g., 'Python', 'python', 'PYTHON' all become 'Python'). This dictionary can be extended with industry-standard taxonomies like ESCO or ONET as the platform scales."

he dictionary acts as a filter and normalizer to improve matching accuracy.
---

### 3. **Resume Parsing**
**What it is:** Extracting text from PDF and Word documents

**How it works:**
- **PDF files:** Uses PyPDF2 library to read text from PDF pages
- **DOCX files:** Uses python-docx library to read text from Word documents

**Why we need it:** Resumes come in different formats, we need to extract the text to analyze it

---

### 4. **Database Models**
**What they are:** Tables that store information

**Our Models:**
- **JobSkill:** Stores skills for each job (job_id, skill_name, weight)
- **CandidateSkill:** Stores skills for each candidate (user_id, skill_name, source, confidence)

**Why we need them:** To quickly search and match without re-analyzing text every time

---

## 📊 Data Flow Diagram (Simple)

```
1. Company Posts Job
   ↓
2. System Extracts Skills from Job Description
   ↓
3. Skills Stored in Database (JobSkill table)
   ↓
4. Candidate Applies (Cover Letter + Resume)
   ↓
5. System Extracts Skills from Cover Letter
   ↓
6. System Extracts Skills from Resume File
   ↓
7. Skills Stored in Database (CandidateSkill table)
   ↓
8. Company Clicks "Find Matching Candidates"
   ↓
9. System Compares Job Skills vs Candidate Skills
   ↓
10. System Calculates Fit Scores
    ↓
11. Results Shown (Ranked by Fit Score)
```

---

## 🎤 How to Explain to an Interviewer

### **Short Version (30 seconds):**
"We built an AI-powered candidate recommendation system. When a company posts a job, the system automatically extracts required skills from the job description using NLP. When candidates apply, it extracts their skills from both their cover letter and resume. Then it matches candidates to jobs based on skill overlap and shows companies a ranked list with fit scores, saving hours of manual resume screening."

### **Medium Version (2 minutes):**
"We implemented a recommendation feature similar to what Manatal does. Here's how it works:

**First, skill extraction:** When a company posts a job, we use NLP (spaCy library) to automatically extract skills from the job description and assign importance weights. For example, if a job says 'Python developer with Django experience required,' we extract Python and Django with high weights.

**Second, candidate analysis:** When candidates apply, we extract skills from both their cover letter text and their uploaded resume file (supporting PDF and DOCX formats). We use libraries like PyPDF2 and python-docx for document parsing.

**Third, matching algorithm:** When a company wants to see recommendations, we compare the job's required skills against each candidate's skills. We calculate a weighted fit score based on how many required skills they have and how important those skills are. The results are ranked by fit score.

**Key features:**
- Only shows candidates from that company's own applicant pool (privacy)
- Uses NLP for automatic skill extraction (no manual tagging)
- Processes both cover letters and resumes
- Provides visual fit scores with progress bars

This helps companies quickly identify the best candidates from hundreds of applications."

### **Technical Deep Dive (if asked):**
**NLP Implementation:**
- We use spaCy's `en_core_web_sm` model for entity recognition and noun chunk extraction
- We combine NLP extraction with a dictionary-based fallback for reliability
- Skills are normalized and matched against a curated skill dictionary

**Matching Algorithm:**
- Weighted overlap calculation: `fit_score = (matched_weight / total_weight) × 100`
- Only considers candidates who applied to that company's jobs
- Skills are stored in the database for fast querying

**Resume Parsing:**
- PDF: PyPDF2 library extracts text page by page
- DOCX: python-docx library reads paragraph text
- Both sources (cover letter + resume) are processed and stored separately

**Database Design:**
- `JobSkill` model: job_id, skill_name, weight (0-10)
- `CandidateSkill` model: user_id, skill_name, source (cover_letter/resume), confidence
- Indexed for fast queries

---

## 🔑 Key Points to Remember

1. **Automatic:** No manual skill tagging required
2. **Smart:** Uses NLP to understand context, not just keyword matching
3. **Comprehensive:** Analyzes both cover letters and resumes
4. **Privacy-focused:** Companies only see their own candidates
5. **Visual:** Shows fit scores with progress bars for easy understanding
6. **Fast:** Skills are pre-extracted and stored, so matching is instant

---

## 💡 Why This is Impressive

1. **Real-world problem:** Solves an actual pain point (resume screening is time-consuming)
2. **AI/NLP usage:** Demonstrates understanding of modern AI techniques
3. **Full-stack:** Involves frontend (UI), backend (Django), database (models), and AI (NLP)
4. **Production-ready:** Handles errors gracefully, supports multiple file formats
5. **Scalable:** Can handle hundreds of jobs and thousands of candidates

---

## 🚀 Future Improvements (If Asked)

1. **Better NLP:** Use transformer models (BERT) for more accurate skill extraction
2. **Semantic matching:** Match "web development" with "frontend development" (synonyms)
3. **Experience levels:** Extract years of experience for each skill
4. **Education matching:** Match required degrees/qualifications
5. **Location matching:** Consider candidate location vs job location
6. **Learning:** Improve weights based on which candidates get hired

---

## 📝 Quick Reference

**Technologies Used:**
- Django (Python web framework)
- spaCy (NLP library)
- PyPDF2 (PDF parsing)
- python-docx (Word document parsing)
- SQLite/PostgreSQL (Database)

**Key Files:**
- `jobs/services.py` - Core NLP and matching logic
- `jobs/models.py` - Database models (JobSkill, CandidateSkill)
- `jobs/views.py` - API endpoints (extract skills, show recommendations)
- `jobs/skills_dictionary.py` - Curated skill list

**Key Functions:**
- `extract_skills()` - Extracts skills from text using NLP
- `save_job_skills()` - Saves extracted skills for a job
- `save_candidate_skills_from_text()` - Saves extracted skills for a candidate
- `build_candidate_match_payload()` - Calculates fit scores and matches

---

## ✅ Practice Questions

**Q: How does the system extract skills?**
A: We use spaCy NLP library to analyze text. It identifies noun phrases and entities that match our skill dictionary. We also look for context clues like "required" or "must have" to assign importance weights.

**Q: What if a skill isn't in your dictionary?**
A: The NLP model can still extract it as a noun phrase, and we store it. However, matching works best with standardized skills from our dictionary.

**Q: How do you handle different resume formats?**
A: We support PDF (using PyPDF2) and DOCX (using python-docx). The system detects the file type and uses the appropriate parser.

**Q: Why do you store skills in the database instead of extracting on-the-fly?**
A: For performance. Extracting skills is computationally expensive. By storing them, we can quickly match candidates without re-processing text every time.

**Q: How accurate is the matching?**
A: The NLP extraction is quite good for common technical skills. The matching algorithm is deterministic (based on skill overlap), so it's consistent. The fit scores give a good indication, but human review is still recommended for final decisions.

---

**Remember:** The goal is to show you understand the problem, the solution, and the technology. Be confident, and don't worry if you don't know every detail - focus on the big picture!

