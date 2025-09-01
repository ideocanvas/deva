# Project Deva (Developer Agent)

Project Deva is a multi-tenant platform, orchestrated by a Master Control Program (MCP), that functions as an autonomous **Dev**eloper **A**gent. It can generate, deploy, test, and manage web applications based on high-level user prompts.

---

## Setup

1.  Clone the repository:
    `git clone <repository-url>`

2.  Create your local environment file from the example:
    `cp .env.example .env`

3.  Populate the `.env` file with your credentials (e.g., `OPENAI_API_KEY`).

4.  Build and start the platform services:
    `docker-compose up --build -d`

## Usage

*   **MCP Server API:** `http://localhost:8080/docs`
*   **Traefik Dashboard:** `http://localhost:8081`

The system is now running. You can begin assigning tasks to Jules, starting with **GEN-1**.