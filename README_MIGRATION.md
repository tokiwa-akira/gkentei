# Project Structure Migration Guide

## Overview

This project has been restructured to follow modern development practices with clear separation of concerns, improved maintainability, and better organization.

## New Directory Structure

```
.
├── backend/                    # Backend application
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── v1/            # API version 1
│   │   │   └── endpoints/     # Route definitions
│   │   ├── core/              # Core configuration
│   │   ├── models/            # Database models & schemas
│   │   ├── services/          # Business logic
│   │   │   ├── embedding/     # Vector search service
│   │   │   ├── llm/           # LLM service
│   │   │   ├── scraper/       # Web scraping service
│   │   │   ├── exam/          # Exam generation service
│   │   │   └── problem/       # Problem CRUD service
│   │   ├── utils/             # Utility functions
│   │   └── scripts/           # Management scripts
│   ├── tests/                 # Backend tests
│   ├── alembic/               # Database migrations
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React PWA application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API clients
│   │   ├── types/             # TypeScript definitions
│   │   ├── utils/             # Utility functions
│   │   └── styles/            # Styling
│   ├── public/                # Static assets
│   └── package.json           # Node.js dependencies
│
├── docker/                     # Docker configurations
├── scripts/                    # Setup and utility scripts
├── data/                       # Data storage
├── cache/                      # Model cache
├── models/                     # ML models
└── config/                     # Configuration files
```

## Migration Status

### ✅ Completed
- Modern backend structure with FastAPI
- Frontend structure with React + Vite + TypeScript
- Docker configuration for containerization
- Service layer architecture
- API versioning structure
- Configuration management
- Legacy file migration

### 🔄 In Progress
- Legacy code integration
- Database migration scripts
- Test migration
- Service implementations

### 📋 TODO
- Complete service implementations
- Frontend component development
- PWA configuration
- Documentation updates

## Key Changes

### Backend Changes
1. **Modular Architecture**: Services are now separated by domain
2. **FastAPI Structure**: Modern async API with automatic documentation
3. **Configuration Management**: Centralized settings with environment variables
4. **Database Layer**: Proper ORM models with Alembic migrations
5. **Dependency Injection**: Clean service dependencies

### Frontend Changes
1. **Modern React**: Using React 18 with TypeScript
2. **Vite Build Tool**: Fast development and build process
3. **Mantine UI**: Modern component library with dark mode
4. **PWA Ready**: Service worker and offline capabilities
5. **State Management**: Zustand for global state

### DevOps Changes
1. **Docker Compose**: Multi-service development environment
2. **Separate Dockerfiles**: Optimized for development and production
3. **Scripts**: Automated setup and maintenance scripts
4. **Environment Variables**: Proper configuration management

## Migration Guide for Developers

### For Backend Development
1. Navigate to `backend/` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Start development server: `uvicorn app.main:app --reload`
4. Legacy files are in `app/services/*/legacy/` for reference

### For Frontend Development
1. Navigate to `frontend/` directory
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`
4. Access at `http://localhost:3000`

### For Full Stack Development
1. Use Docker Compose: `docker compose -f docker-compose.new.yml up --build`
2. Backend API: `http://localhost:8000`
3. Frontend App: `http://localhost:3000`
4. API Documentation: `http://localhost:8000/docs`

## Legacy File Mapping

| Legacy File | New Location |
|-------------|--------------|
| `main.py` | `backend/app/legacy_main.py` |
| `search_api.py` | `backend/app/services/embedding/legacy_search_api.py` |
| `models.py` | `backend/app/models/legacy_models.py` |
| `router_llm.py` | `backend/app/services/llm/legacy_router.py` |
| `ingest_embedding.py` | `backend/app/scripts/init_embeddings.py` |
| `scraper.py` | `backend/app/services/scraper/scraper.py` |
| `parser.py` | `backend/app/services/scraper/parser.py` |
| `exam/` | `backend/app/services/exam/legacy/` |
| `test/` | `backend/tests/legacy/` |

## Next Steps

1. **Review the new structure** and understand the organization
2. **Update import paths** when working with migrated code
3. **Implement missing services** using the new structure
4. **Migrate tests** to the new test structure
5. **Update CI/CD** configurations if applicable

## Support

For questions about the new structure:
- Check `CLAUDE.md` for development commands
- Review service files for implementation patterns
- Refer to FastAPI and React documentation for best practices