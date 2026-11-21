# Career Recommendation System (CareerWithinU / Aivance)
### Based on Interest, Education, and Skills

An AI-assisted, domain-restricted web application built strictly to the **Software Requirements Specification (SRS v1.0)** and replicating the **4 provided UI design screenshots**.

---

## 🌟 Key Modules & UI Screenshots Mapping

| UI Screenshot | Module Name | Features Implemented |
| :--- | :--- | :--- |
| **Image 1** (`CareerWithinU`) | **AI Career Chat & Activity Center** | Real-time chat with avatars, embedded career recommendation cards (Software Engineer, Data Scientist, Robotics, Research), activity/transfers ledger, next assessment card ("Monday, 11 AM"), and progress tracking bars (Psychometric Test 80%, Shortlist 50%, Roadmap 30%). |
| **Image 2** (`Ascento`) | **Gamified Career Roadmap** | Level 12 tracker, 2840/3200 XP progress bar, 7-day streak flame, 15,420 total points, achievements ("First Steps", "Streak Master"), interactive milestones (HTML/CSS, JS, React, Node.js...) with live status toggling (Not Started / In Progress / Completed) and XP rewards. |
| **Image 3** (`My Choices`) | **Best Matches & Career Explorer** | Filter pills (Degree 3+ years, A-levels, GCSEs, Technology, Engineering, Finance, Creative), match percentage indicators (100% Systems Analyst, 98% Software Developer, 94% Data Scientist, etc.), favorite heart toggle, bin/hide toggle, and side-by-side career comparison. |
| **Image 4** (`Aivance`) | **Student Learning Dashboard** | Lessons took metric (46 completed, trend line), skill tracker bars (Design 46%, Management 12%, Software 27%), 127h spent, interactive calendar widget, upcoming lessons (Figma Pro 62%), mock interview tool scheduler, CV/Resume drag-and-drop parser, and recommended courses. |

---

## 🛡️ Strict AI Assistant Constraints & Guardrails

The Career Guidance Assistant is restricted by multi-layered security filters conforming to **SRS Section 4 & Section 11.3**:

1. **Strict Career Domain Only (AI-01, AI-02)**:
   - Responds **only** to career choices, job roles, educational qualifications, skills, pathways, skill gaps, learning roadmaps, internships, and interview preparation.
   - Any off-topic question (jokes, recipes, weather, politics, celebrity gossip, gaming, general trivia) is strictly blocked and receives the pre-defined redirection reply:
     > *"I can help with career-related questions. Would you like to explore a career or improve a skill?"*

2. **Identity & Architecture Shielding (AI-03, AI-04)**:
   - The assistant **does not reveal its internal identity, model/provider name, architecture, or system instructions**.
   - If prompted with *"Who are you?"*, *"What model are you?"*, or *"Reveal your identity"*, it never discloses underlying technology and sends:
     > *"I can help with career-related questions. What career path would you like to explore?"*

3. **Prompt-Injection & Secret Defense (AI-05, AI-06)**:
   - Resists jailbreaks, attempts to ignore rules, or requests for developer prompts, returning the safe redirection:
     > *"I can help with career-related questions. What career path would you like to explore?"*

4. **Privacy Protection (AI-09)**:
   - Refuses requests to disclose other students' records or confidential system data:
     > *"Personal profiles and system data are private and cannot be disclosed. I can only assist with your own career guidance and development."*

---

## 🧮 Recommendation Engine Formula (SRS Section 3.6)

The recommendation engine implements the transparent weighted scoring model:

$$\text{Match Score} = (\text{Interest Fit} \times 0.40) + (\text{Education Fit} \times 0.30) + (\text{Skills Fit} \times 0.30)$$

- **Interest Alignment (40%)**: Evaluates overlap between user's chosen categories (from the 10 SRS categories) and career domains.
- **Education Alignment (30%)**: Compares qualification stage (School, Diploma, Undergraduate, Postgraduate, Doctorate) and specialization keywords against required and preferred career credentials.
- **Skills Alignment (30%)**: Analyzes required vs acquired skills, adjusting fit by proficiency (Beginner: 0.45, Intermediate: 0.75, Advanced: 1.0).
- **Skill Gap Analysis (FR-32 to FR-34)**: Dissects skills into *Matched Skills*, *Developing Skills (Needs Improvement)*, and *Missing Gaps*, directly linking to step-by-step roadmaps.

---

## 🚀 How to Run the Application

### Option A: Using the One-Click Runner (Windows)
Double-click `run.bat` in the project root.

### Option B: Using the Command Line
```powershell
& "C:\Users\NAGARAJ\AppData\Local\Python\bin\python.exe" manage.py runserver 0.0.0.0:8000
```
Open your browser and navigate to: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Pre-Configured Demo Accounts

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Student** | `rahul` | `password123` | Pre-loaded with profile, 11th Grade Science, chat history, skills, and roadmaps matching the screenshots. |
| **Administrator** | `admin` | `admin123` | Access to the Admin Portal (`/admin-portal/`), catalogue CRUD, and the SRS 11.3 Red-Team Test Bench. |

---

## 🧪 Automated Test Verification

All 15 automated tests covering recommendation algorithms, skill gap analysis, and the complete SRS 11.3 Red-Team test suite pass with 100% success rate:
```powershell
& "C:\Users\NAGARAJ\AppData\Local\Python\bin\python.exe" manage.py test core
# Ran 15 tests in 5.464s -> OK
```
