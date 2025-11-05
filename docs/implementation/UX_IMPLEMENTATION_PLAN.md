# 🎨 SIGRAA - Plan de Implementación UX/UI de Clase Mundial

**Fecha**: Octubre 24, 2025
**Objetivo**: Transformación visual radical basada en referencias de diseño moderno
**Duración Estimada**: 4-6 días
**Prioridad**: ALTA

---

## 📋 Análisis de Referencias UX

### Características Identificadas en las Imágenes de Referencia

#### **Imagen 1 - My Library (Biblioteca)**
✅ **Diseño Observado**:
- Tabla limpia con separadores sutiles
- Columnas: Title, Author, Year, Actions
- Iconos de acción (ver, descargar, favorito) en azul
- Filtros dropdown (Subject, Year, Author) + botón Sort
- Búsqueda con placeholder claro
- Paginación simple (Previous/Next)
- Header con navegación horizontal
- Avatar de usuario en esquina superior derecha
- Background blanco/gris muy claro

#### **Imagen 2 - Upload Articles**
✅ **Diseño Observado**:
- Drag & drop zone con borde punteado
- Ícono de upload central
- Botón "Browse Files" secundario
- Opción de URL upload
- Progress bars con porcentaje
- Estados: En progreso, Completo (con checkmark)
- Formulario de metadata manual
- Campos: Title, Authors, Journal/Conference, Year, Abstract
- Botón primario "Save Metadata"
- Layout en dos secciones (upload + metadata)

#### **Imagen 3 - Article Details**
✅ **Diseño Observado**:
- Breadcrumb navigation (Home / Article Details)
- Título grande del artículo
- Metadata: Journal, Date, Authors
- Abstract completo y legible
- Botones de acción primarios (Read PDF, Generate Citation)
- Sección "Related Articles" con cards visuales
- Cards con imágenes artísticas/abstractas
- Cada card: Imagen + Título + Descripción corta
- Layout en grid de 3 columnas

#### **Imagen 4 - Recommendations**
✅ **Diseño Observado**:
- Filtros por categoría (All, Computer Science, AI, ML, Data Science)
- Pills/badges estilo tags
- Cards de recomendación con:
  - Título destacado
  - Descripción del paper
  - Imagen artística/representativa a la derecha
  - Botones "Add to Library" y "View Details"
- Espaciado generoso entre cards
- Imágenes con estilo artístico/abstracto

#### **Imagen 5 - Bibliography Generator**
✅ **Diseño Observado**:
- Layout de dos paneles (izquierda: settings, derecha: output)
- Selector de estilo de citación (APA 7th Edition dropdown)
- Lista de artículos con checkboxes
- Búsqueda dentro de la biblioteca
- Preview de bibliografía generada
- Botón "Copy" prominente
- Información del artículo: Autores, año, journal

#### **Imagen 6 - Dashboard**
✅ **Diseño Observado**:
- Mensaje de bienvenida personalizado
- Búsqueda global destacada
- Cards de estadísticas (Total Articles, Articles Read, Citations)
- Números grandes y legibles
- Sección "Recent Recommendations" con carousel
- Cards visuales con imágenes artísticas
- Botones de "Quick Actions"
- Background limpio

---

## 🎨 Sistema de Diseño (Design System)

### 1. Paleta de Colores

```css
/* Colores Primarios */
--primary-blue: #2563EB;        /* Azul principal (botones, links) */
--primary-blue-hover: #1D4ED8;  /* Hover state */
--primary-blue-light: #DBEAFE; /* Backgrounds sutiles */

/* Colores Neutros */
--white: #FFFFFF;
--gray-50: #F9FAFB;    /* Background principal */
--gray-100: #F3F4F6;   /* Cards, inputs */
--gray-200: #E5E7EB;   /* Borders */
--gray-300: #D1D5DB;   /* Borders hover */
--gray-400: #9CA3AF;   /* Placeholder text */
--gray-500: #6B7280;   /* Secondary text */
--gray-600: #4B5563;   /* Body text */
--gray-700: #374151;   /* Headings */
--gray-900: #111827;   /* Primary text */

/* Colores de Acento */
--accent-beige: #F5EBE0;        /* Para cards artísticas */
--accent-coral: #FFB4A2;        /* Variaciones */
--accent-sage: #B7C4A1;         /* Variaciones */
--accent-sky: #C9E4F0;          /* Variaciones */

/* Colores de Estado */
--success: #10B981;
--error: #EF4444;
--warning: #F59E0B;
--info: #3B82F6;
```

### 2. Tipografía

```css
/* Font Families */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-headings: 'Inter', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;     /* 12px */
--text-sm: 0.875rem;    /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--text-xl: 1.25rem;     /* 20px */
--text-2xl: 1.5rem;     /* 24px */
--text-3xl: 1.875rem;   /* 30px */
--text-4xl: 2.25rem;    /* 36px */
--text-5xl: 3rem;       /* 48px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

### 3. Espaciado y Layout

```css
/* Spacing Scale (Tailwind-style) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */

/* Border Radius */
--radius-sm: 0.25rem;   /* 4px */
--radius-md: 0.375rem;  /* 6px */
--radius-lg: 0.5rem;    /* 8px */
--radius-xl: 0.75rem;   /* 12px */
--radius-2xl: 1rem;     /* 16px */
--radius-full: 9999px;  /* Circular */

/* Shadows */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
```

### 4. Componentes Base

#### Botones
```
Primary Button:
- Background: --primary-blue
- Text: white
- Padding: 12px 24px
- Border-radius: --radius-lg
- Font-weight: --font-medium
- Shadow: --shadow-sm
- Hover: --primary-blue-hover + --shadow-md

Secondary Button:
- Background: transparent
- Border: 1px solid --gray-300
- Text: --gray-700
- Padding: 12px 24px
- Hover: --gray-100

Icon Button:
- Size: 40x40px
- Border-radius: --radius-md
- Color: --primary-blue
- Hover: --primary-blue-light background
```

#### Cards
```
Standard Card:
- Background: white
- Border: 1px solid --gray-200
- Border-radius: --radius-xl
- Padding: 24px
- Shadow: --shadow-sm
- Hover: --shadow-md (transition)

Recommendation Card:
- Background: white
- Border-radius: --radius-2xl
- Padding: 32px
- Image: Artistic/abstract on right side
- Shadow: --shadow-lg
```

#### Inputs
```
Text Input:
- Border: 1px solid --gray-300
- Border-radius: --radius-lg
- Padding: 12px 16px
- Font-size: --text-base
- Focus: border --primary-blue, ring 2px --primary-blue-light

Search Input:
- Icon: Search icon on left
- Border: 1px solid --gray-200
- Border-radius: --radius-full
- Padding: 12px 20px 12px 48px
- Background: --gray-50
```

---

## 🏗️ Plan de Implementación por Páginas

### **Fase 1: Setup y Configuración (Día 1)**

#### 1.1 Instalación de Dependencias UI
```bash
npm install @headlessui/react @heroicons/react clsx
npm install -D @tailwindcss/forms @tailwindcss/typography
```

#### 1.2 Configuración de Tailwind Extendida
**Archivo**: `frontend/tailwind.config.js`
- Agregar colores personalizados
- Configurar tipografía
- Extender spacing
- Configurar shadows

#### 1.3 Fuente Inter de Google Fonts
**Archivo**: `frontend/index.html`
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

#### 1.4 Archivo de Tokens CSS
**Archivo**: `frontend/src/styles/tokens.css`
- Definir CSS custom properties
- Variables de color, spacing, typography

---

### **Fase 2: Componentes Base (Día 2)**

#### 2.1 Crear Sistema de Componentes Reutilizables

**Archivos a Crear**:
```
frontend/src/components/ui/
├── Button.tsx           # Botones primarios, secundarios, iconos
├── Card.tsx             # Cards base, recommendation cards
├── Input.tsx            # Inputs, search, textareas
├── Badge.tsx            # Pills para categorías
├── Avatar.tsx           # Avatar de usuario
├── Dropdown.tsx         # Dropdowns para filtros
├── Modal.tsx            # Modales
├── Table.tsx            # Tabla estilizada
├── Progress.tsx         # Barras de progreso
└── index.ts             # Barrel export
```

#### 2.2 Íconos (Heroicons)
- Usar @heroicons/react para íconos consistentes
- Crear componente wrapper si es necesario

---

### **Fase 3: Layout y Navegación (Día 2-3)**

#### 3.1 Rediseñar Navigation Component
**Archivo**: `frontend/src/components/common/Navigation.tsx`

**Características**:
- Logo SIGRAA a la izquierda con ícono
- Links horizontales: My Library, Explore, Recommendations
- Search bar centrado/derecha
- Notificaciones (icono campana)
- Avatar usuario con dropdown
- Background blanco, border-bottom sutil
- Sticky top

#### 3.2 Rediseñar Layout Component
**Archivo**: `frontend/src/components/common/Layout.tsx`

**Características**:
- Container con max-width
- Padding consistente
- Background --gray-50
- Navegación fija arriba

---

### **Fase 4: Páginas - Implementación Detallada**

### **Página 1: Dashboard (Día 3)**
**Archivo**: `frontend/src/pages/Dashboard.tsx`
**Referencia**: Imagen 6

**Secciones**:
1. **Header**
   - Título: "Dashboard"
   - Subtítulo: "Welcome back, [Username]"
   
2. **Search Bar**
   - Grande y centrado
   - Placeholder: "Search your library for articles, authors, or topics..."
   - Ícono de búsqueda
   
3. **Stats Cards** (Grid 3 columnas)
   ```tsx
   <div className="grid grid-cols-3 gap-6">
     <StatCard title="Total Articles" value="235" />
     <StatCard title="Articles Read" value="150" />
     <StatCard title="Citations" value="450" />
   </div>
   ```

4. **Recent Recommendations**
   - Carousel horizontal de cards
   - Cards con imágenes artísticas
   - Botón "View All"

5. **Quick Actions**
   - Botones: "Upload Article", "Create Collection"

**Componentes Nuevos**:
- `StatCard.tsx` - Card de estadística
- `RecommendationCarousel.tsx` - Carousel de recomendaciones

---

### **Página 2: Library (Día 3-4)**
**Archivo**: `frontend/src/pages/Library.tsx`
**Referencia**: Imagen 1

**Secciones**:
1. **Header**
   - Título: "My Library"
   - Subtítulo: "Manage your collection of academic articles"

2. **Filtros y Búsqueda**
   ```tsx
   <div className="flex gap-4">
     <SearchInput placeholder="Search articles in your library..." />
     <Dropdown label="Subject" options={...} />
     <Dropdown label="Year" options={...} />
     <Dropdown label="Author" options={...} />
     <Button variant="primary" icon={SortIcon}>Sort</Button>
   </div>
   ```

3. **Tabla de Artículos**
   ```tsx
   <Table>
     <TableHeader>
       <TableColumn>Title</TableColumn>
       <TableColumn>Author</TableColumn>
       <TableColumn>Year</TableColumn>
       <TableColumn>Actions</TableColumn>
     </TableHeader>
     <TableBody>
       {articles.map(article => (
         <TableRow key={article.id}>
           <TableCell>{article.title}</TableCell>
           <TableCell>{article.author}</TableCell>
           <TableCell>{article.year}</TableCell>
           <TableCell>
             <IconButton icon={EyeIcon} />
             <IconButton icon={DownloadIcon} />
             <IconButton icon={HeartIcon} />
           </TableCell>
         </TableRow>
       ))}
     </TableBody>
   </Table>
   ```

4. **Paginación**
   - "Showing 1-5 of 20 articles"
   - Botones Previous/Next

**Componentes Nuevos**:
- `Table.tsx` - Sistema de tabla completo
- `Pagination.tsx` - Paginación

---

### **Página 3: Upload (Día 4)**
**Archivo**: `frontend/src/pages/Upload.tsx`
**Referencia**: Imagen 2

**Secciones**:
1. **Header**
   - Título: "Upload Articles"

2. **Upload Zone**
   ```tsx
   <DropZone>
     <UploadIcon />
     <p>Drag and drop PDF files here</p>
     <p>or</p>
     <Button variant="secondary">Browse Files</Button>
   </DropZone>
   ```

3. **URL Upload Option**
   ```tsx
   <div>
     <label>Article URL</label>
     <Input placeholder="https://example.com/article.pdf" />
     <Button>Upload</Button>
   </div>
   ```

4. **Upload Progress**
   ```tsx
   <div className="space-y-4">
     <ProgressItem 
       filename="Quantum_Computing_Review.pdf" 
       progress={25} 
     />
     <ProgressItem 
       filename="AI_Ethics_in_Healthcare.pdf" 
       progress={75} 
     />
     <ProgressItem 
       filename="Deep_Learning_for_Genomics.pdf" 
       progress={100} 
       complete 
     />
   </div>
   ```

5. **Manual Metadata Entry**
   ```tsx
   <Card>
     <h3>Manual Metadata Entry</h3>
     <p>For files that couldn't be parsed automatically...</p>
     <Form>
       <Input label="Title" />
       <Input label="Authors" />
       <Input label="Journal/Conference" />
       <Input label="Year" />
       <Textarea label="Abstract" rows={5} />
       <Button>Save Metadata</Button>
     </Form>
   </Card>
   ```

**Componentes Nuevos**:
- `DropZone.tsx` - Drag & drop zone
- `ProgressItem.tsx` - Upload progress bar

---

### **Página 4: Article Details (Día 4)**
**Archivo**: `frontend/src/pages/ArticleDetails.tsx`
**Referencia**: Imagen 3

**Secciones**:
1. **Breadcrumb**
   ```tsx
   <Breadcrumb>
     <BreadcrumbItem href="/">Home</BreadcrumbItem>
     <BreadcrumbItem>Article Details</BreadcrumbItem>
   </Breadcrumb>
   ```

2. **Article Header**
   ```tsx
   <div>
     <h1 className="text-4xl font-bold">
       The Impact of AI on Creative Industries: A Comprehensive Analysis
     </h1>
     <div className="metadata">
       <span>Journal of Creative Technologies</span>
       <span>Date: January 15, 2024</span>
       <span>Authors: Dr. Anya Sharma, Prof. Ben Carter</span>
     </div>
   </div>
   ```

3. **Abstract**
   ```tsx
   <Card>
     <h3>Abstract</h3>
     <p className="text-gray-600 leading-relaxed">
       {article.abstract}
     </p>
   </Card>
   ```

4. **Action Buttons**
   ```tsx
   <div className="flex gap-4">
     <Button icon={DocumentIcon}>Read PDF</Button>
     <Button variant="secondary" icon={QuoteIcon}>
       Generate Citation
     </Button>
   </div>
   ```

5. **Related Articles**
   ```tsx
   <section>
     <h2>Related Articles</h2>
     <div className="grid grid-cols-3 gap-6">
       {relatedArticles.map(article => (
         <RelatedArticleCard 
           key={article.id}
           image={article.image}
           title={article.title}
           description={article.description}
         />
       ))}
     </div>
   </section>
   ```

**Componentes Nuevos**:
- `Breadcrumb.tsx` - Navegación breadcrumb
- `RelatedArticleCard.tsx` - Card con imagen artística

---

### **Página 5: Recommendations (Día 5)**
**Archivo**: `frontend/src/pages/Recommendations.tsx`
**Referencia**: Imagen 4

**Secciones**:
1. **Header**
   - Título: "Recommendations"
   - Subtítulo: "Explore articles tailored to your interests and library content"

2. **Category Filters**
   ```tsx
   <div className="flex gap-3">
     <Badge active>All</Badge>
     <Badge>Computer Science</Badge>
     <Badge>Artificial Intelligence</Badge>
     <Badge>Machine Learning</Badge>
     <Badge>Data Science</Badge>
   </div>
   ```

3. **Recommendation Cards**
   ```tsx
   <div className="space-y-6">
     {recommendations.map(rec => (
       <RecommendationCard
         key={rec.id}
         title={rec.title}
         description={rec.description}
         image={rec.image}
         actions={
           <>
             <Button>Add to Library</Button>
             <Button variant="secondary">View Details</Button>
           </>
         }
       />
     ))}
   </div>
   ```

**Características de Recommendation Card**:
- Layout horizontal (texto izquierda, imagen derecha)
- Imagen artística/abstracta
- Título destacado
- Descripción del paper
- Botones de acción

**Componentes Nuevos**:
- `RecommendationCard.tsx` - Card horizontal con imagen

---

### **Página 6: Bibliography Generator (Día 5)**
**Archivo**: `frontend/src/pages/Bibliography.tsx`
**Referencia**: Imagen 5

**Layout de 2 Paneles**:
```tsx
<div className="grid grid-cols-2 gap-8">
  {/* Panel Izquierdo: Settings */}
  <div>
    <Card>
      <h3>Bibliography Settings</h3>
      <Dropdown 
        label="Citation Style"
        value="APA 7th Edition"
        options={['APA 7th', 'MLA', 'Chicago', 'BibTeX', 'RIS']}
      />
    </Card>
    
    <Card>
      <h3>Select Articles</h3>
      <SearchInput placeholder="Search your library" />
      <div className="space-y-2">
        {articles.map(article => (
          <ArticleCheckbox
            key={article.id}
            title={article.title}
            authors={article.authors}
            year={article.year}
            journal={article.journal}
          />
        ))}
      </div>
    </Card>
  </div>
  
  {/* Panel Derecho: Generated Bibliography */}
  <div>
    <Card>
      <div className="flex justify-between items-center">
        <h3>Generated Bibliography</h3>
        <Button icon={ClipboardIcon}>Copy</Button>
      </div>
      <div className="bibliography-output">
        {generatedBibliography.map(citation => (
          <p key={citation.id} className="citation">
            {citation.formatted}
          </p>
        ))}
      </div>
      <p className="text-center text-gray-500">
        Select articles from your library to generate a bibliography
      </p>
    </Card>
  </div>
</div>
```

**Componentes Nuevos**:
- `ArticleCheckbox.tsx` - Checkbox con metadata del artículo

---

### **Página 7: Login & Register (Día 5-6)**
**Actualizar para modernizar**

#### Login.tsx
```tsx
<div className="min-h-screen flex items-center justify-center bg-gray-50">
  <Card className="w-full max-w-md">
    <div className="text-center mb-8">
      <Logo size="large" />
      <h1 className="text-3xl font-bold mt-4">Welcome back</h1>
      <p className="text-gray-500 mt-2">Sign in to your account</p>
    </div>
    
    <Form>
      <Input label="Email" type="email" />
      <Input label="Password" type="password" />
      <Button fullWidth>Sign In</Button>
    </Form>
    
    <p className="text-center mt-4">
      Don't have an account? <Link>Sign up</Link>
    </p>
  </Card>
</div>
```

---

## 📦 Assets y Recursos

### Imágenes Artísticas para Cards
**Fuentes recomendadas**:
1. **Unsplash** - https://unsplash.com/
   - Buscar: abstract art, minimalist art, geometric shapes
   
2. **MidJourney/DALL-E** - Generar arte abstracto personalizado
   - Prompts sugeridos:
     - "minimalist abstract art, pastel colors, geometric shapes"
     - "organic shapes, beige and coral tones, modern art"
     - "3D rendered abstract sculpture, soft lighting"

3. **Placeholder inicial**: Usar gradientes CSS
   ```css
   background: linear-gradient(135deg, #F5EBE0 0%, #FFB4A2 100%);
   ```

### Íconos
- **Heroicons** (ya compatible con Tailwind)
- Consistencia en: outline vs solid style

---

## 🎯 Métricas de Éxito

### Performance
- Lighthouse Score > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3s

### Visual
- Consistencia en spacing (usar scale de 4px)
- Jerarquía visual clara
- Accesibilidad WCAG AA
- Responsive en mobile, tablet, desktop

### UX
- Feedback inmediato en interacciones
- Loading states en todas las acciones
- Error handling claro
- Animaciones sutiles (transitions 200-300ms)

---

## 📅 Cronograma de Implementación

### **Día 1: Setup**
- ✅ Configurar Tailwind extendido
- ✅ Agregar fuente Inter
- ✅ Crear archivo de tokens CSS
- ✅ Instalar dependencias UI

### **Día 2: Componentes Base**
- ✅ Crear componentes UI base (Button, Card, Input, etc.)
- ✅ Rediseñar Navigation
- ✅ Rediseñar Layout

### **Día 3: Dashboard + Library**
- ✅ Implementar Dashboard completo
- ✅ Implementar Library (tabla + filtros)

### **Día 4: Upload + Article Details**
- ✅ Implementar Upload con drag & drop
- ✅ Implementar Article Details

### **Día 5: Recommendations + Bibliography**
- ✅ Implementar Recommendations
- ✅ Implementar Bibliography Generator

### **Día 6: Polish + Login/Register**
- ✅ Refinar Login y Register
- ✅ Agregar animaciones
- ✅ Testing responsive
- ✅ Ajustes finales

---

## 🚀 Siguiente Paso

**Comenzar con Día 1**: Setup y Configuración

```bash
# 1. Instalar dependencias
cd frontend
npm install @headlessui/react @heroicons/react clsx
npm install -D @tailwindcss/forms @tailwindcss/typography

# 2. Crear estructura de carpetas
mkdir -p src/components/ui
mkdir -p src/styles

# 3. Actualizar tailwind.config.js
# 4. Crear tokens.css
# 5. Comenzar con componentes base
```

**¿Comenzamos con la implementación?** 🚀

---

**Documentado por**: UX Implementation Team
**Fecha**: Octubre 24, 2025
**Estado**: Listo para implementación
**Nivel de Calidad**: Mundial 🌍
