## Composición completa del proyecto SIGRAA

Este documento resume la **estructura**, **tecnologías**, **APIs** y **flujo general** del proyecto SIGRAA (Sistema de Gestión y Recomendación de Artículos Académicos) para que cualquier integrante del equipo pueda explicar cómo está construido el sistema.

---

## 1. Arquitectura general

El sistema está dividido en tres capas principales:

```text
┌───────────────────────────┐
│        Frontend           │
│ React 18 + TypeScript     │
│ Vite + Tailwind CSS       │
└────────────▲──────────────┘
             │ HTTP/JSON (REST)
             ▼
┌───────────────────────────┐
│         Backend           │
│ FastAPI (Python)         │
│ Servicios de NLP/ML      │
└────────────▲──────────────┘
             │ SQLAlchemy (ORM)
             ▼
┌───────────────────────────┐
│       Base de Datos       │
│ PostgreSQL                │
└───────────────────────────┘
```

* El **frontend** es una SPA en React que consume APIs REST.
* El **backend** expone endpoints con FastAPI, aplica lógica de negocio (clasificación, resúmenes, recomendaciones, anotaciones, etc.).
* La **base de datos** almacena usuarios, artículos, biblioteca personal, anotaciones y metadatos.

---

## 2. Tecnologías principales

### 2.1 Backend (carpeta `backend/`)

- **Lenguaje**: Python 3.9
- **Framework web**: FastAPI (`fastapi`, `uvicorn`)
- **Configuración y settings**: `pydantic`, `pydantic-settings`, `python-dotenv`
- **Base de datos**:
  - ORM: `sqlalchemy`, `sqlalchemy-utils`
  - Migraciones: `alembic`
  - Driver PostgreSQL: `psycopg2-binary`
- **Autenticación y seguridad**:
  - JWT: `python-jose[cryptography]`
  - Hashing de contraseñas: `passlib[bcrypt]`, `bcrypt`
  - Manejo de formularios: `python-multipart`
- **Procesamiento de PDFs**:
  - `PyPDF2`, `pypdf`, `pdfplumber` para leer y extraer texto y metadatos
- **NLP / Machine Learning**:
  - `scikit-learn`, `nltk`, `textstat`, `numpy`, `pandas`
  - Se usan para clasificar artículos, calcular temas, niveles de resumen y análisis de texto.
- **Utilidades**: `requests`, `beautifulsoup4` (scrapeo de páginas para obtener PDFs), `python-slugify`, `validators`.
- **Testing y calidad**: `pytest`, `pytest-asyncio`, `httpx`, `black`, `flake8`, `isort`, `mypy`.

### 2.2 Frontend (carpeta `frontend/`)

- **Lenguaje**: TypeScript
- **Framework**: React 18
- **Bundler / Dev server**: Vite
- **Estilos**:
  - `tailwindcss` + `@tailwindcss/forms` + `@tailwindcss/typography`
- **Gestión de estado y datos remotos**:
  - Store de autenticación: `zustand`
  - Fetching/caché de datos: `@tanstack/react-query`
  - Cliente HTTP: `axios` (con interceptor para token JWT)
- **Ruteo**: `react-router-dom`
- **Componentes UI**:
  - `@headlessui/react` (componentes accesibles) y `@heroicons/react` (iconos)
- **Testing**:
  - `vitest` + `@testing-library/react` + `@testing-library/user-event` + `jsdom`

---

## 3. Estructura de carpetas a alto nivel

En la raíz del proyecto:

```text
backend/   → API FastAPI + lógica de negocio + modelos + migraciones
frontend/  → Aplicación React + TypeScript
data/      → Archivos de datos y uploads (PDFs)
docs/      → Documentación interna del proyecto
scripts/   → Scripts de utilidad (arranque, etc.)
uxreference/ → Material de referencia de UX
```

### 3.1 Backend (`backend/app`)

```text
app/
  main.py          → Punto de entrada FastAPI y configuración global
  core/            → Configuración, seguridad, esquemas Pydantic, DB
  api/routes/      → Rutas/routers de la API (auth, users, articles, ...)
  models/          → Modelos SQLAlchemy (User, Article, Category, ...)
  services/        → Servicios de dominio (resúmenes, clasificación, etc.)
  utils/           → Utilidades varias
```

### 3.2 Frontend (`frontend/src`)

```text
src/
  main.tsx         → Arranque de React, monta `<App />`
  App.tsx          → Definición de rutas con React Router
  pages/           → Páginas principales (Dashboard, Library, Upload, ...)
  components/      → Componentes reutilizables (`common/`, `ui/`)
  context/         → Stores de estado (p.ej. `authStore` con Zustand)
  services/        → Clientes API (`api.ts`) y servicios auxiliares
  styles/          → Estilos adicionales
  tests/           → Pruebas de frontend
```

---

## 4. Backend en detalle

### 4.1 Archivo principal: `app/main.py`

- Crea la instancia de `FastAPI` con el título **"SIGRAA API"**.
- Configura CORS leyendo `CORS_ORIGINS` desde las variables de entorno.
- Incluye todos los routers:
  - `auth`, `users`, `articles`, `recommendations`, `annotations`.
- En el evento de `startup` ejecuta `run_database_migrations()` para aplicar las migraciones de Alembic automáticamente.
- Expone endpoints básicos:
  - `GET /` → información básica de la API.
  - `GET /health` → health check (para saber si el backend está vivo).

### 4.2 Modelos principales (`app/models/*.py`)

Algunos modelos importantes (via SQLAlchemy):

- `User`: usuarios del sistema (username, email, password_hash, institución, campo de estudio, etc.).
- `Article`: artículos académicos (título, autores, abstract, keywords, año, journal, DOI, ruta del archivo PDF, hash de archivo, categoría, topics automáticos, etc.).
- `Category`: categorías temáticas generales.
- `UserLibrary`: relación "usuario ↔ artículo" con estado de lectura, rating, notas, topics personalizados.
- `Recommendation`: almacena o soporta el sistema de recomendaciones.
- `Annotation`: resaltados/anotaciones sobre artículos (texto, página, color, notas, tags, posición en el PDF).
- `UserIndex`: índices o perfiles de búsqueda (listas de keywords por usuario).

### 4.3 Servicios (`app/services/*.py`)

La lógica de negocio compleja se organiza en servicios:

- `metadata_extractor.py`: extrae metadatos y texto de PDFs (título, autores, abstract, keywords, año, etc.).
- `classifier.py`: clasificador de artículos (sugerir categoría, scores por categoría usando ML).
- `topic_classifier.py`: detecta temas (topics) a partir de título/abstract/keywords/texto.
- `bibliography_generator.py`: genera citas en múltiples formatos (APA, MLA, Chicago, BibTeX, RIS).
- `summarizer.py` y `chunked_summarizer.py`: resumen de textos con diferentes niveles (ejecutivo, detallado, exhaustivo) y métodos (local, Groq, etc.).
- `multi_document_summarizer.py`: genera resúmenes combinados de varios artículos (síntesis, comparación, identificación de vacíos/gaps).
- `recommender.py`: recomendaciones de artículos según el historial, biblioteca y temas del usuario.
- `document_structure_extractor.py`: identificación de secciones/estructura interna de un documento.

### 4.4 Autenticación y seguridad (`app/core/security.py`)

- Login basado en **JWT**:
  - Se genera un access token con `python-jose`.
  - Se almacena el hash de la contraseña usando `passlib[bcrypt]`.
- `get_current_user` se usa como dependencia en las rutas protegidas para recuperar el usuario autenticado a partir del token.

### 4.5 Esquemas y validación (`app/core/schemas.py`)

- Se definen modelos Pydantic para validar entrada/salida de la API:
  - `UserCreate`, `UserResponse`, `Token`.
  - `ArticleCreate`, `ArticleUpdate`, `ArticleResponse`.
  - `BatchSummaryRequest`, `BatchSummaryResponse`, `SummaryResult`.
  - `MultiDocumentSummaryRequest`, `MultiDocumentSummaryResponse`.
  - `AnnotationCreate`, `AnnotationUpdate`, `AnnotationResponse`.

### 4.6 APIs principales (routers)

#### 4.6.1 Autenticación (`/api/auth`)

- `POST /api/auth/register` → registro de usuario nuevo.
- `POST /api/auth/token` → login (form-urlencoded), devuelve `access_token` (JWT).
- `GET /api/auth/me` → devuelve los datos del usuario autenticado.

#### 4.6.2 Usuarios y biblioteca (`/api/users`)

- `GET /api/users/{user_id}` → obtener información de un usuario por ID.
- `PUT /api/users/profile` → actualizar perfil del usuario logueado.
- Gestión de biblioteca personal (`/api/users/library/...`):
  - `POST /api/users/library/{article_id}` → añadir artículo a la biblioteca.
  - `DELETE /api/users/library/{article_id}` → eliminar de la biblioteca.
  - `GET /api/users/library/` → listar biblioteca con filtros (estado, topic, búsqueda, índice, orden).
  - `PUT /api/users/library/{article_id}` → actualizar entrada de biblioteca (status: unread/reading/read, rating 0–5, notas, topics personalizados).
  - `GET /api/users/library/stats` → estadísticas de lectura (totales, distribuciones por estado y topic).
- Gestión de índices de usuario (`/api/users/library/indexes`):
  - `GET /api/users/library/indexes` → listar índices.
  - `POST /api/users/library/indexes` → crear índice (nombre, keywords, color).
  - `DELETE /api/users/library/indexes/{index_id}` → eliminar índice.

#### 4.6.3 Artículos y resúmenes (`/api/articles`)

- Ingesta de artículos:
  - `POST /api/articles/upload` → subir archivo (`PDF` o `TXT`) del usuario.
  - `POST /api/articles/upload-url` → subir artículo a partir de una URL (Google Scholar, ResearchGate, ArXiv, etc.), usando `requests` + `beautifulsoup4` para localizar el PDF.
- Gestión básica:
  - `GET /api/articles/` → listar artículos con filtros (categoría, palabra clave, fechas, etc.).
  - `GET /api/articles/{article_id}` → obtener detalle de un artículo.
  - `PUT /api/articles/{article_id}` → actualizar metadatos del artículo.
  - `DELETE /api/articles/{article_id}` → eliminar un artículo.
- Funciones avanzadas:
  - `GET /api/articles/{article_id}/bibliography/{format}` → generar cita en formato `apa`, `mla`, `chicago`, `bibtex`, `ris`.
  - `GET /api/articles/{article_id}/classify` → clasificar el artículo (sugerir categoría y scores por categoría).
  - `POST /api/articles/summaries/batch` → generar resúmenes por lote (batch) de varios artículos:
    - Parámetros: `article_ids`, `method` (`auto`, `local`, `groq`), `level` (`executive`, `detailed`, `exhaustive`), longitud máxima, etc.
  - `POST /api/articles/summaries/multi-document` → resumen conjunto de varios artículos:
    - Modos: `synthesis`, `comparison`, `gaps` (vacíos en la literatura).

#### 4.6.4 Recomendaciones (`/api/recommendations`)

- `GET /api/recommendations/` → devuelve una lista de artículos recomendados para el usuario actual (lógica implementada en `ArticleRecommender`).

#### 4.6.5 Anotaciones (`/api/annotations`)

- `POST /api/annotations/` → crear nueva anotación o resaltado en un artículo.
- `GET /api/annotations/article/{article_id}` → listar anotaciones del usuario actual para un artículo; se puede filtrar por color o tag.
- `GET /api/annotations/my-annotations` → listar todas las anotaciones del usuario (con filtros y paginación).
- `GET /api/annotations/{annotation_id}` → obtener detalle de una anotación específica.
- `PUT /api/annotations/{annotation_id}` → actualizar anotación (texto, nota, color, tags, posición).
- `DELETE /api/annotations/{annotation_id}` → eliminar anotación.
- `GET /api/annotations/article/{article_id}/stats` → estadísticas de anotaciones por color, número total, tags únicos, etc.

---

## 5. Frontend en detalle

### 5.1 Configuración general

- Punto de entrada: `src/main.tsx`, que monta `<App />` dentro del `BrowserRouter` de `react-router-dom`.
- `App.tsx` define las rutas principales y envuelve la app en `QueryClientProvider` (React Query).
- Se usa un componente `ProtectedRoute` para proteger las secciones que requieren login.

### 5.2 Rutas principales (React Router)

En `App.tsx` se definen:

- `/login` → página de Login.
- `/register` → página de registro.
- `/` (protegida) → layout principal con las siguientes subrutas:
  - `index` ("/") → `Dashboard`.
  - `/library` → `Library` (biblioteca personal).
  - `/articles` → `Articles` (exploración general de artículos).
  - `/upload` → `Upload` (subir PDF o URL).
  - `/recommendations` → `Recommendations` (recomendaciones personalizadas).
- Cualquier otra ruta redirige a `/`.

### 5.3 Estado de autenticación (`src/context/authStore.ts`)

- Implementado con **Zustand**:
  - Guarda `token`, `user` e `isAuthenticated`.
  - Lee el token inicial de `localStorage` (`access_token`).
  - Métodos: `setToken`, `setUser`, `logout` (borra el token del almacenamiento local).
- Este store es consumido por `ProtectedRoute` y por los componentes que necesitan datos del usuario.

### 5.4 Cliente de APIs (`src/services/api.ts`)

- Usa `axios` con un `baseURL` configurable vía `VITE_API_URL` (`.env` del frontend; por defecto `http://localhost:8000`).
- Interceptor de requests: añade el header `Authorization: Bearer <token>` si hay token en `localStorage`.
- Agrupa las llamadas en objetos por dominio:

#### authAPI

- `register(data)` → `POST /api/auth/register`.
- `login(username, password)` → `POST /api/auth/token` (form-urlencoded).
- `getCurrentUser()` → `GET /api/auth/me`.

#### articlesAPI

- `list(filters)` → `GET /api/articles/`.
- `get(id)` → `GET /api/articles/{id}`.
- `upload(file, categoryId?)` → `POST /api/articles/upload` (form-data).
- `uploadFromUrl(url, categoryId?)` → `POST /api/articles/upload-url`.
- `update(id, data)` → `PUT /api/articles/{id}`.
- `delete(id)` → `DELETE /api/articles/{id}`.
- `classify(id)` → `GET /api/articles/{id}/classify`.
- `getBibliography(id, format)` → `GET /api/articles/{id}/bibliography/{format}`.
- `summarize(payload)` → `POST /api/articles/summaries/batch`.
- `multiDocumentSummarize(payload)` → `POST /api/articles/summaries/multi-document`.

#### libraryAPI

- `list(params)` → `GET /api/users/library/`.
- `add(articleId)` → `POST /api/users/library/{articleId}`.
- `remove(articleId)` → `DELETE /api/users/library/{articleId}`.
- `update(articleId, status?, rating?, notes?, topics?)` → `PUT /api/users/library/{articleId}`.
- `getStats()` → `GET /api/users/library/stats`.
- `listIndexes()` → `GET /api/users/library/indexes`.
- `createIndex(data)` → `POST /api/users/library/indexes`.
- `deleteIndex(indexId)` → `DELETE /api/users/library/indexes/{indexId}`.

#### usersAPI

- `getProfile(userId)` → `GET /api/users/{userId}`.
- `updateProfile(data)` → `PUT /api/users/profile`.

#### recommendationsAPI

- `get(limit?)` → `GET /api/recommendations/`.

#### annotationsAPI

- `create(data)` → `POST /api/annotations/`.
- `getByArticle(articleId, color?, tag?)` → `GET /api/annotations/article/{articleId}`.
- `getMyAnnotations(skip?, limit?, articleId?, color?)` → `GET /api/annotations/my-annotations`.
- `get(annotationId)` → `GET /api/annotations/{annotationId}`.
- `update(annotationId, data)` → `PUT /api/annotations/{annotationId}`.
- `delete(annotationId)` → `DELETE /api/annotations/{annotationId}`.
- `getStats(articleId)` → `GET /api/annotations/article/{articleId}/stats`.

### 5.5 Páginas principales (`src/pages`)

- `Dashboard.tsx`:
  - Vista general del usuario: resumen de biblioteca, estadísticas, atajos a secciones claves.
- `Library.tsx`:
  - Tabla/lista de artículos de la biblioteca del usuario.
  - Filtros por estado, topic, índices personalizados y búsqueda.
  - Uso de componentes como `AdvancedFilter`, `ArticleDetailModal`, `BatchSummaryModal`, `AnnotationPanel`, etc.
- `Upload.tsx`:
  - Subida de artículos vía archivo (drag & drop) o vía URL.
  - Muestra progreso de upload y resultados de clasificación automática.
  - Genera bibliografía en múltiples formatos y la muestra en `BibliographyModal`.
- `Articles.tsx`:
  - Listado general de artículos, filtros, búsqueda y acciones para añadir a la biblioteca.
- `Recommendations.tsx`:
  - Lista artículos recomendados consumiendo `recommendationsAPI`.
- `Login.tsx` y `Register.tsx`:
  - Formularios para autenticación y creación de cuenta; integrados con `authAPI` y `authStore`.

### 5.6 Componentes UI destacados (`src/components/ui`)

- `AdvancedFilter.tsx` → filtros avanzados para la biblioteca y artículos.
- `AnnotationPanel.tsx` → panel lateral para ver/crear/editar anotaciones sobre el PDF.
- `BatchSummaryModal.tsx` → modal para lanzar resúmenes en lote y mostrar resultados.
- `BibliographyModal.tsx` → muestra las citas generadas en diferentes estilos.
- Componentes básicos reutilizables: `Button`, `Card`, `Input`, `Table`, `Progress`, `Dropdown`, `Avatar`, `Badge`, `ClassificationResult`, `ArticleDetailModal`, etc.

### 5.7 Estilos y diseño

- Se usa **Tailwind CSS** como sistema de estilos utilitario.
- Configuración en `tailwind.config.js` con integración para formularios y tipografía.
- El diseño se basa en componentes reutilizables y un layout principal (`Layout` en `components/common`).

---

## 6. Flujo típico de uso (de extremo a extremo)

1. **Registro y Login**
   - El usuario se registra desde `/register` → `authAPI.register` → `POST /api/auth/register`.
   - Luego hace login en `/login` → `authAPI.login` → `POST /api/auth/token`.
   - El frontend guarda el token en `authStore` y en `localStorage`.

2. **Subir artículos**
   - Desde la página `Upload`, el usuario:
     - Sube un PDF (`/api/articles/upload`), o
     - Proporciona una URL (`/api/articles/upload-url`).
   - El backend guarda el archivo en `backend/data/uploads`, extrae metadatos y texto, calcula hash, detecta topics y crea el registro `Article`.

3. **Clasificación, topics y bibliografía**
   - Después del upload, el frontend llama a:
     - `articlesAPI.classify` → `GET /api/articles/{id}/classify`.
     - `articlesAPI.getBibliography` para cada formato → `GET /api/articles/{id}/bibliography/{format}`.
   - Estos datos se muestran en la UI para que el usuario confirme o edite.

4. **Gestión de biblioteca personal**
   - Los artículos pueden agregarse a la biblioteca del usuario (`POST /api/users/library/{article_id}`).
   - En `Library` se pueden cambiar estados (unread/reading/read), ratings, notas y topics.
   - Se pueden crear índices de estudio personalizados (palabras clave agrupadas).

5. **Resúmenes y análisis multi-documento**
   - Desde la biblioteca o vista de artículos, el usuario puede seleccionar múltiples artículos y abrir `BatchSummaryModal`.
   - El frontend envía un `BatchSummaryPayload` o `MultiDocumentSummaryPayload` a `/api/articles/summaries/batch` o `/api/articles/summaries/multi-document`.
   - El backend usa los servicios de `summarizer` y `multi_document_summarizer` para devolver los resúmenes.

6. **Recomendaciones**
   - El usuario puede ir a `Recommendations` para obtener artículos sugeridos (`GET /api/recommendations/`).

7. **Anotaciones sobre artículos**
   - Desde el `AnnotationPanel`, el usuario crea y gestiona anotaciones:
     - `POST /api/annotations/` para crear.
     - `GET /api/annotations/article/{article_id}` para listar.
     - `PUT`/`DELETE` para actualizar o borrar anotaciones.
   - Se pueden ver estadísticas de anotaciones por color y tags (`/stats`).

---

## 7. Variables de entorno (visión general)

Sin entrar en credenciales específicas, a nivel conceptual se usan:

- **Backend (`backend/.env`)**:
  - `DATABASE_URL` → conexión a PostgreSQL.
  - `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` → configuración de JWT.
  - `CORS_ORIGINS` → orígenes permitidos (normalmente `http://localhost:5173`).
  - `BACKEND_HOST`, `BACKEND_PORT` → host y puerto para Uvicorn.

- **Frontend (`frontend/.env`)**:
  - `VITE_API_URL` → URL base del backend (por defecto `http://localhost:8000`).

---

## 8. Resumen para exposición oral

Al presentar el proyecto, cada estudiante debería poder explicar al menos:

1. **Qué hace SIGRAA**: gestiona artículos académicos, genera recomendaciones, resúmenes automáticos, bibliografía en varios formatos y permite anotaciones.
2. **Arquitectura**: frontend en React+TS (Vite, Tailwind) que consume una API REST en FastAPI, con PostgreSQL como base de datos.
3. **APIs clave**: `auth`, `users/library`, `articles` (upload, summary, bibliography), `recommendations`, `annotations`.
4. **Librerías principales**: FastAPI, SQLAlchemy, Alembic, scikit-learn, NLTK, React, React Query, Axios, Zustand, Tailwind.
5. **Flujo completo**: desde el registro y subida de PDFs hasta la obtención de resúmenes, recomendaciones y gestión de anotaciones dentro de la biblioteca personal.
