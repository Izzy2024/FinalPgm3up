# SIGRAA - Sistema de Gestión y Recomendación de Artículos Académicos

Un sistema completo para organizar, clasificar y recibir recomendaciones de artículos académicos.

## Características

- 📚 Gestión completa de artículos académicos
- 🤖 Clasificación automática de papers
- 💡 Recomendaciones personalizadas
- 📖 Generador de bibliografías (APA, MLA, Chicago)
- 👥 Autenticación y perfiles de usuario
- 🔍 Búsqueda avanzada y filtros

## Tech Stack

### Backend
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy ORM
- JWT Authentication

### Frontend
- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Query

## Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from .env.example
cp .env.example .env

# Setup database
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Run development server
npm run dev
```

## Project Structure

```
sigraa/
├── backend/           # FastAPI application
├── frontend/          # React application
├── data/             # Uploaded files and data
├── docs/             # Documentation (organized by category)
│   ├── setup/        # Installation and setup guides
│   ├── phases/       # Phase-specific documentation
│   ├── implementation/ # Implementation details and plans
│   ├── tracking/     # Project tracking and status
│   ├── testing/      # Testing guides
│   └── system-diagrams/ # System architecture and diagrams
├── scripts/          # Utility scripts
└── uxreference/      # UX reference materials
```

## Documentation

### Quick Links
- **Getting Started**: [docs/setup/START_HERE.md](./docs/setup/START_HERE.md)
- **Setup Guide**: [docs/setup/GETTING_STARTED.md](./docs/setup/GETTING_STARTED.md)
- **Running the Project**: [docs/setup/RUN_PROJECT.md](./docs/setup/RUN_PROJECT.md)
- **Commands Reference**: [CLAUDE.md](./CLAUDE.md)

### Documentation Structure
- **Setup & Installation** - `docs/setup/`
  - Initial setup guides
  - Configuration instructions
  - Running the project

- **Phase Documentation** - `docs/phases/`
  - Phase 2 status and setup
  - Phase 3 planning, status, and completion
  - Quick start guides for each phase

- **Implementation** - `docs/implementation/`
  - UX implementation plans
  - Component documentation
  - Implementation summaries

- **Project Tracking** - `docs/tracking/`
  - Current status
  - Roadmap
  - Change tracking

- **Testing** - `docs/testing/`
  - Testing guides
  - Test procedures

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
