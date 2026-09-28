<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1b27,100:3d59a1&height=190&section=header&text=Mohammed%20Faraz%20Kabbo&fontSize=46&fontColor=ffffff&fontAlignY=36&desc=AI%20%26%20Software%20Engineer%20%C2%B7%20Co-Founder%20%40%20Clarus&descSize=18&descAlignY=58" width="100%" alt="Mohammed Faraz Kabbo" />

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=20&duration=3200&pause=900&color=7AA2F7&center=true&vCenter=true&width=640&lines=I+build+AI+systems+that+hold+up+in+production;RAG+pipelines+%C2%B7+AI+agents+%C2%B7+APIs+%C2%B7+data+layers;13+hackathon+projects+%C2%B7+3+wins+%C2%B7+funded+startup" alt="Typing intro" />

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohammed-faraz-kabbo/)
[![Portfolio](https://img.shields.io/badge/Portfolio-1a1b27?style=for-the-badge&logo=githubpages&logoColor=white)](https://farazkabbo.github.io/Portfolio/)
[![Email](https://img.shields.io/badge/Email-7AA2F7?style=for-the-badge&logo=maildotru&logoColor=white)](mailto:faraz18@my.yorku.ca)
[![Devpost](https://img.shields.io/badge/Devpost-003E54?style=for-the-badge&logo=devpost&logoColor=white)](https://devpost.com/farazkabbo)

<br/>

![Hackathon projects](https://img.shields.io/badge/Hackathon_Projects-13-e0af68?style=flat-square)
![Hackathon wins](https://img.shields.io/badge/Hackathon_Wins-3-f7768e?style=flat-square)
![Startup](https://img.shields.io/badge/Clarus-Funded_%C2%B7_NSU_Cohort_4-9ece6a?style=flat-square)
![Co-ops](https://img.shields.io/badge/Gov_Co--ops-2-7aa2f7?style=flat-square)
![Status](https://img.shields.io/badge/Open_to-Spring%2FFall_2027_%C2%B7_New_Grad-bb9af7?style=flat-square)

</div>

---

## About Me

I'm a Computer Science student at **York University** who likes the unglamorous half of AI: making it fast, measurable, and trustworthy once real users depend on it.

- Co-founding **[Clarus](https://devpost.com/software/clarus-7werym)**, an AI workflow automation startup that won **Hack Canada 2026** and is now funded through **NSU Cohort 4**
- Previously **AI Engineer** and **Software Developer** co-op at the **Ontario Government**
- Looking for **Spring / Fall 2027 internships** and **new grad** roles in AI, backend, and full-stack engineering

---

## Impact at a Glance

<div align="center">

| Metric | Where |
|:---|:---|
| **35%** lower inference latency on a production RAG system | Ontario Government, AI Engineer |
| **33%** faster incident response through monitoring and alerting | Ontario Government, Software Developer |
| **30 datasets** from **20 systems** consolidated into one data layer | Ontario Government, Software Developer |
| **60%+** of questions answered automatically by a multi-agent system | Numen, GenAI Genesis 2026 |
| **5 systems**, **0 manual handoffs** in an automated AI workflow | Clarus, Hack Canada 2026 Winner |
| **85%** classifier accuracy with **30%** faster inference | Mimicoo, HackTheValley 2025 Winner |

</div>

---

## Featured Projects

### [Clarus](https://devpost.com/software/clarus-7werym) &nbsp; ![Winner](https://img.shields.io/badge/Hack_Canada_2026-Winner-f7768e?style=flat-square) ![Funded](https://img.shields.io/badge/NSU_Cohort_4-Funded-9ece6a?style=flat-square)

A production **AI agent** that automates a business workflow end to end across five integrated systems.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![AI Agents](https://img.shields.io/badge/AI_Agents-Tool_Use-bb9af7?style=flat-square)

```mermaid
flowchart LR
    A[Business event] -->|webhook| B[FastAPI service]
    A -.->|polling fallback| B
    B --> C{Agent<br/>runtime tool selection}
    C -->|branch| D[Extract structured data<br/>from documents]
    C -->|branch| E[Act across<br/>5 integrated systems]
    D --> F[(Per-run audit trail)]
    E --> F
```

- Runtime **tool selection** and conditional branching, taken from prototype to production
- Added a **polling fallback** after diagnosing a silent webhook failure, so no event is lost
- Every agent action is logged to a **per-run audit trail** for reliability review

---

### [Numen](https://devpost.com/software/numen-9l43wx) &nbsp; ![GenAI Genesis](https://img.shields.io/badge/GenAI_Genesis-2026-7aa2f7?style=flat-square)

A **multi-agent** knowledge platform that answers engineering and sales questions, and knows when *not* to answer.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white)

```mermaid
flowchart LR
    Q[Question] --> K{Classify<br/>question type}
    K -->|code| V[Vector search over<br/>indexed pull requests]
    K -->|knowledge| G[768-dim embedding graph<br/>with staleness decay]
    V --> S{Confidence score}
    G --> S
    S -->|high| H[Answer directly]
    S -->|medium| M[Answer with caveats]
    S -->|low| X[Route to human expert<br/>with packaged context]
```

- **60%+ auto-answer rate** across engineering, sales, and custom agents
- **Hybrid search** routes each question to the retrieval path that fits it
- **Confidence gating** keeps uncertain answers away from users

---

<table>
<tr>
<td width="33%" valign="top">

### [Vroomi](https://devpost.com/software/vroomi)
![Winner](https://img.shields.io/badge/SpurHacks_2025-Winner-f7768e?style=flat-square)

Full-stack web app with third-party **REST API** and **Stripe** payment integrations, deployed to production.

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![Stripe](https://img.shields.io/badge/Stripe-635BFF?style=flat-square&logo=stripe&logoColor=white)

</td>
<td width="33%" valign="top">

### [Mimicoo](https://devpost.com/software/mimicoo)
![Winner](https://img.shields.io/badge/HackTheValley_2025-Winner-f7768e?style=flat-square)

Feature-engineered classifier trained to **85% accuracy**, served from a Python inference API with **30%** faster inference.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![ML](https://img.shields.io/badge/Machine_Learning-e0af68?style=flat-square)

</td>
<td width="33%" valign="top">

### [Troupe](https://troupeapp.vercel.app/)
![Android](https://img.shields.io/badge/Android-Social_Platform-9ece6a?style=flat-square)

Android app with feeds, matching, and media uploads on a **Spring Boot REST** back end, with **Redis** caching and rate limiting.

![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)

</td>
</tr>
</table>

---

## Experience

```mermaid
timeline
    title Journey
    2023 : Started B.Sc. Computer Science at York University
    2025 : SpurHacks winner (Vroomi)
         : HackTheValley winner (Mimicoo)
         : Software Developer co-op, Ontario Government
    2026 : Hack Canada winner, co-founded Clarus
         : GenAI Genesis (Numen)
         : AI Engineer co-op, Ontario Government
         : Clarus funded through NSU Cohort 4
```

**AI Engineer, Co-op** &nbsp;·&nbsp; Ontario Government &nbsp;·&nbsp; *May 2026 – Aug 2026*
Shipped a production **RAG application** over 20 curriculum documents with **LangChain** and **Pinecone**, and cut inference latency **35%** through chunk tuning and embedding caching.

**Software Developer, Co-op** &nbsp;·&nbsp; Ontario Government &nbsp;·&nbsp; *Sept 2025 – May 2026*
Built **Python** pipelines and **REST APIs** consolidating **30 datasets from 20 systems**, deployed on **AWS** with **Docker** and **CI/CD**, and built monitoring that cut incident response **33%**.

---

## Tech Stack

<div align="center">

**AI & Machine Learning**
<br/>
<img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
<img src="https://img.shields.io/badge/Pinecone-000000?style=for-the-badge&logo=pinecone&logoColor=white" />
<img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" />
<img src="https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" />
<img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" />
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />

**Languages**
<br/>
<img src="https://skillicons.dev/icons?i=python,ts,js,java,cs,kotlin,html,css&theme=dark" />

**Frameworks**
<br/>
<img src="https://skillicons.dev/icons?i=fastapi,spring,nodejs,react,nextjs,tailwind&theme=dark" />

**Data & Infrastructure**
<br/>
<img src="https://skillicons.dev/icons?i=postgres,mongodb,redis,supabase,aws,docker,kubernetes,kafka,git,linux&theme=dark" />

</div>

---

## GitHub Activity

<div align="center">

<img src="https://github-readme-stats.vercel.app/api?username=farazkabbo&show_icons=true&include_all_commits=true&count_private=true&theme=tokyonight&hide_border=true&bg_color=1a1b27" height="165" alt="GitHub stats" />
<img src="https://github-readme-stats.vercel.app/api/top-langs?username=farazkabbo&layout=compact&langs_count=6&theme=tokyonight&hide_border=true&bg_color=1a1b27" height="165" alt="Top languages" />

<img src="https://streak-stats.demolab.com?user=farazkabbo&theme=tokyonight&hide_border=true&background=1a1b27" height="165" alt="GitHub streak" />

<img src="https://github-readme-activity-graph.vercel.app/graph?username=farazkabbo&theme=tokyo-night&hide_border=true&area=true&bg_color=1a1b27" width="100%" alt="Contribution graph" />

<img src="https://raw.githubusercontent.com/farazkabbo/farazkabbo/output/github-snake-dark.svg" width="100%" alt="Contribution snake" />

</div>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:3d59a1,100:1a1b27&height=110&section=footer" width="100%" />
