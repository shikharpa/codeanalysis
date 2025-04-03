# Repository Analysis System (Alpha version)

## Overview
This project provides an API-based system for analyzing GitHub repositories using LLM-based insights. It allows users to submit repository links, process them asynchronously, and retrieve detailed analysis reports.

## Features
- **User Authentication** (JWT-based login/logout)
- **Repository Submission** (Submit GitHub repo URL for analysis)
- **LLM-Based Analysis** (Extract insights and summarize codebase structure)
- **Asynchronous Processing** (Background tasks for repo cloning and analysis)
- **Dockerized Deployment** (Backend, Database, and Redis setup using Docker Compose)

## Tech Stack
- **Backend:** FastAPI, PostgreSQL, Redis
- **Task Queue:** RQ (Redis Queue)
- **LLM Integration:** OpenAI API
- **Deployment:** Docker, GCP

---

## Backend Setup
### Prerequisites
- Install [Docker](https://docs.docker.com/get-docker/)
- Install [Docker Compose](https://docs.docker.com/compose/install/)

### Run Backend and frontend using Docker Compose
```sh
docker-compose up --build
```

This will start the FastAPI backend, PostgreSQL database, and Redis instance and frontend.

---

## API Endpoints
### Authentication
```plaintext
POST /auth/login  - Authenticate user
POST /auth/sigin  - Add user
```

### Repository Management
```plaintext
POST /repo/submit_repo  - Submit a GitHub repo for analysis
GET /analysis/get_repo/{repo_id}  - Get submitted repository details in very detail and strctures response
```

### Analysis
```plaintext
GET /analysis/{repo_id}  - Retrieve LLM-based analysis of the repository code , method by method
```

---

## Environment Variables
Create a `.env` file in the backend directory:
```ini
DATABASE_URL=postgresql://user:password@db:5432/dbname
REDIS_URL=redis://redis:6379
OPENAI_API_KEY=your_openai_api_key
```

---

## Contributing
1. Fork the repo
2. Create a new branch (`feature-branch`)
3. Commit your changes
4. Push to your fork and submit a PR

---

## Developed BY (Beta version)
Shikhar Pandey
