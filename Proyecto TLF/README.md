# Motor de Patrones — Autómatas Finitos

Aplicación de escritorio para detección, validación y extracción de patrones en texto
mediante un **motor propio de expresiones regulares** implementado con autómatas finitos
(AFND/AFD). No utiliza la librería `re` ni ninguna otra librería de expresiones regulares.

## Características

- **Motor de regex propio**: Lexer → Parser → AST → Thompson (AFND) → Subconjuntos (AFD) → Simulador
- **Validación en tiempo real**: Formularios con retroalimentación visual inmediata (<150 ms)
- **Búsqueda en texto**: Carga de archivos hasta 10 MB con resaltado de coincidencias
- **Gestión de reglas**: Crear, editar, activar/desactivar patrones persistidos en JSON
- **Validación semántica**: Fechas (años bisiestos), correos (TLD), teléfonos, URLs, placas
- **Exportación**: Resultados en CSV y JSON
- **Casos de prueba**: Panel integrado con ejecución automática

## Patrones soportados

| Patrón | Formato | Estrategia |
|--------|---------|------------|
| Correo electrónico | local@dominio.tld | AFD + validación semántica |
| Teléfono | +57 3001234567 | AFD + normalización |
| Fecha ISO | YYYY-MM-DD | AFD + validación de rango |
| Fecha | DD/MM/YYYY | AFD + validación de rango |
| Placa vehicular | ABC-123 | AFD simple |
| Identificador | letras + dígitos | AFD configurable |

## Requisitos

- Python 3.10 o superior
- Sistema operativo: Windows o Linux

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

## Ejecución de pruebas

```bash
python -m pytest tests/ -v
```

## Estructura del proyecto

```
├── main.py                        # Punto de entrada
├── pattern_engine/                # Motor de patrones (core)
│   ├── lexer.py                   # Tokenizador del mini-DSL
│   ├── parser.py                  # Parser → AST
│   ├── ast_nodes.py               # Nodos del AST
│   ├── thompson.py                # Construcción de Thompson → AFND
│   ├── nfa.py                     # Definición de AFND
│   ├── subset_construction.py     # AFND → AFD (subconjuntos)
│   ├── dfa.py                     # Definición de AFD
│   ├── dfa_simulator.py           # Simulador del AFD
│   ├── pattern_engine.py          # Fachada principal
│   └── semantic_validator.py      # Validación semántica
├── ui/                            # Interfaz gráfica (tkinter)
│   ├── app.py                     # Ventana principal
│   ├── form_panel.py              # Formulario con validación
│   ├── search_panel.py            # Búsqueda en texto/archivo
│   ├── rules_panel.py             # Gestión de reglas
│   ├── results_panel.py           # Resultados detallados
│   ├── test_panel.py              # Casos de prueba
│   └── styles.py                  # Tema y estilos
├── rules/                         # Reglas en JSON
│   └── default_rules.json
├── tests/                         # Pruebas automatizadas
└── requirements.txt
```

## Mini-DSL para patrones

Ejemplo de expresión:

```
(letra|digito|"."|"_")+ "@" (letra|digito)+ "." letra{2,4}
```

### Sintaxis

| Elemento | Descripción |
|----------|-------------|
| `"texto"` | Literales entre comillas |
| `letra` | Cualquier letra (a-z, A-Z) |
| `digito` | Cualquier dígito (0-9) |
| `espacio` | Espacio en blanco |
| `cualquier` | Cualquier carácter |
| `[a-z]` | Rango de caracteres |
| `\|` | Alternancia |
| `*` | Cero o más |
| `+` | Uno o más |
| `?` | Opcional |
| `{n}` | Exactamente n veces |
| `{n,m}` | Entre n y m veces |
| `{n,}` | Al menos n veces |

## Pipeline de procesamiento

```
Expresión DSL → Lexer → Tokens → Parser → AST → Thompson → AFND → Subconjuntos → AFD → Simulador
```

## Licencia

Proyecto académico — Teoría de Lenguajes Formales.
