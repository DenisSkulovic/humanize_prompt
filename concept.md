# Humanization System Design

## Overview
This document outlines the design and architecture of the text humanization system, including API structure, worker architecture, feedback collection, and scalability considerations.

## Architecture
The system is designed with modularity, scalability, and future adaptability in mind. It consists of:
- **API Service**: Handles RESTful requests for text humanization and feedback submission.
- **Worker Service**: Processes humanization tasks asynchronously via RabbitMQ.
- **RabbitMQ**: Message queue for decoupling API requests from processing.
- **PostgreSQL Database**: Stores humanization requests, responses, and feedback.
- **Redis Cache**: Stores explanation versions for fast retrieval.

### Folder Structure
```
backend/
│
├── api/                  # FastAPI application
│   ├── endpoints/        # API route handlers
│   │   ├── humanize.py   # Endpoint for text humanization
│   │   ├── feedback.py   # Endpoint for feedback submission
│   │   ├── __init__.py
│   ├── main.py           # FastAPI entry point
│   ├── dependencies.py   # Dependency injection setup
│   ├── __init__.py
│
├── worker/               # RabbitMQ consumer (worker)
│   ├── consumer.py       # Consumes tasks from queue
│   ├── __init__.py
│
├── rabbitmq/             # RabbitMQ-related logic
│   ├── producer.py       # Publishes messages to queue
│   ├── connection.py     # Manages RabbitMQ connection
│   ├── __init__.py
│
├── database/             # Postgres & SQLAlchemy setup
│   ├── models.py         # ORM models (Feedback, etc.)
│   ├── session.py        # Database session management
│   ├── migrations/       # Alembic migration scripts
│   ├── __init__.py
│
├── dto/                  # Data Transfer Objects (DTOs)
│   ├── humanize_dto.py   # DTO for humanization request
│   ├── feedback_dto.py   # DTO for feedback submission
│   ├── __init__.py
│
├── services/             # Business logic layer
│   ├── humanizer.py      # Handles text transformation logic
│   ├── feedback.py       # Handles feedback processing
│   ├── __init__.py
│
├── core/                 # Core utilities & settings
│   ├── config.py         # Configuration settings (env vars, OpenAI key, etc.)
│   ├── logger.py         # Logging setup
│   ├── __init__.py
│
├── tests/                # Unit & integration tests
│   ├── test_humanizer.py # Tests for humanization logic
│   ├── test_feedback.py  # Tests for feedback processing
│   ├── __init__.py
│
├── .env                  # Environment variables (excluded from git)
├── Pipfile               # Pipenv dependencies
├── Pipfile.lock          # Locked dependencies
├── Dockerfile            # Dockerfile
├── docker-compose.yml    # Docker Compose setup
```

## System Components

### API Service
- Implements FastAPI.
- Exposes endpoints for:
  - Humanizing text.
  - Submitting feedback.
- Relies on RabbitMQ for job delegation.

### Worker Service
- Listens to RabbitMQ queue.
- Processes text humanization requests asynchronously.
- Uses OpenAI API for text transformation.

### Database
PostgreSQL is used to store:
1. **Humanization Requests**
   - Stores original text, humanized output, parameters, and explanation versions.
2. **Explanation Versions**
   - Maintains records of instruction versions.
3. **Feedback**
   - Tracks user ratings on a scale from `-2` (AI-like) to `2` (Human-like).

#### Tables
**`humanization_requests`**
| id | original_text | humanized_text | parameters_json | explanation_version_id | created_at |
|----|--------------|---------------|----------------|-----------------------|------------|
| 1  | "Hello!"     | "Hey there!"   | `{casual: 5}`  | 1                     | timestamp  |
| 2  | "How are you?" | "How's it going?" | `{casual: 7, humor: 2}` | 2 | timestamp |

**`explanation_versions`**
| id | version_number | explanation_text | created_at |
|----|---------------|-----------------|------------|
| 1  | 1.0           | "Make it more casual." | timestamp  |
| 2  | 2.0           | "Make it casual, but not slangy." | timestamp  |

**`feedback`**
| id | request_id | feedback_score (-2 to 2) | created_at |
|----|-----------|--------------------------|------------|
| 1  | 1         | 1                        | timestamp  |
| 2  | 2         | -2                       | timestamp  |

## Scalability Considerations
- **Caching Explanation Versions**: Storing in Redis reduces DB load.
- **Feedback-driven Model Tweaks**: Parameters and explanation versions can be adjusted based on user ratings.
- **Database Pruning Strategies**:
  - Auto-delete unreviewed entries after a set period.
  - Retain only relevant data with feedback.
  - Store hashed inputs to avoid duplicate storage.

## Deployment
### **Docker Compose Setup**
```yaml
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - ./backend/api.env
    command: [ "python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      - rabbitmq
      - postgres
  
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - ./backend/worker.env
    command: [ "python3", "worker.py" ]
    depends_on:
      - rabbitmq
      - postgres

  rabbitmq:
    image: rabbitmq:3-management
    env_file:
      - ./backend/rabbitmq.env
    ports:
      - "5672:5672"
      - "15672:15672"

  postgres:
    image: postgres:latest
    env_file:
      - ./backend/postgres.env
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data"

volumes:
  postgres-data:
```

## Future Enhancements
- **More granular feedback tracking** (breaking feedback into multiple dimensions instead of one score).
- **Fine-tuning model parameters dynamically** based on data trends.
- **Adding a UI for internal analysis** (optional).