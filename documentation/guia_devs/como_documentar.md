# Guía para Devs e IA — Cómo Documentar

Reglas para mantener la carpeta `documentation/` coherente y navegable.

---

## Principios

- **Una responsabilidad por archivo.** Cada `.md` cubre un tema concreto y acotado.
  Si un archivo necesita dos secciones de nivel 2 que no tienen relación directa, son dos archivos.
- **Máximo 150 líneas por archivo.** Si se supera, dividir en dos archivos del mismo directorio.
- **Agrupar por tema en subdirectorios.** Los archivos relacionados van juntos en una carpeta con nombre descriptivo.
- **Todo archivo nuevo se registra en `README.md`.** El README raíz es el único índice; no crear índices locales por directorio.

---

## Estructura de directorios actual

```
documentation/
├── README.md                        # Índice raíz — registrar todo archivo nuevo aquí
├── arquitectura.md
├── reglas_de_codigo.md
├── config/                          # Configuración del sistema en tiempo de ejecución
│   ├── logging.md
│   ├── scripts.md
│   └── yaml_comandos.md
├── guia_devs/                       # Guías de proceso para devs e IA
│   ├── como_documentar.md           # Este archivo
│   ├── integraciones.md
│   ├── onboarding.md
│   └── patrones_y_checklist.md
├── herramientas/                    # Tooling de desarrollo
│   ├── tests.md
│   └── tooling.md
└── piezas_clave/                    # Módulos del sistema
    ├── config.md
    ├── core_y_dtos.md
    ├── handlers_y_helpers.md
    └── services.md
```

---

## Cuándo crear un archivo nuevo

Crear un archivo nuevo cuando:
- El tema no encaja en ningún archivo existente sin romper su responsabilidad única
- Una sección de un archivo existente crece hasta acercarse a las 150 líneas
- Surge un tema transversal que varios archivos necesitarían referenciar

No crear un archivo nuevo cuando:
- El tema es una subsección natural de un archivo existente
- La información cabe en menos de 10 líneas y no tiene vida propia

---

## Cuándo crear un directorio nuevo

Crear un subdirectorio cuando hay 3 o más archivos sobre el mismo tema.
Dos archivos relacionados pueden convivir en la raíz de `documentation/`; a partir del tercero, moverlos a un directorio.

Nombre del directorio: sustantivo en plural, minúsculas, sin espacios (`guia_devs/`, `herramientas/`, `piezas_clave/`).

---

## Cómo registrar un archivo nuevo en README.md

Agregar una fila a la tabla de la sección que corresponda:

```markdown
| [directorio/nuevo.md](directorio/nuevo.md) | Qué cubre en una línea |
```

Si el archivo no encaja en ninguna sección existente del README, crear una sección nueva con `## Nombre` antes de agregarla.

---

## Formato interno de cada archivo

```markdown
# Título — Subtítulo si aplica

Descripción de una o dos líneas de qué cubre este archivo.

---

## Sección 1

...

---

## Sección 2

...
```

- Título principal: `#` — uno solo por archivo
- Secciones: `##` — máximo 6 por archivo antes de considerar dividir
- Separador `---` entre secciones para facilitar la lectura
- Sin tablas de contenido (TOC) — el README raíz cumple esa función

---

## Checklist antes de agregar documentación

1. ¿El tema ya está cubierto en algún archivo existente?
2. ¿El archivo nuevo tiene una sola responsabilidad?
3. ¿Tiene menos de 150 líneas?
4. ¿Está registrado en `README.md` con descripción de una línea?
5. ¿Está en el directorio correcto según su tema?
