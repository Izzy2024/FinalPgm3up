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
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## Documentation

See [docs/](./docs/) for detailed documentation.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
