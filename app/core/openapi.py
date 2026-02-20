OPENAPI_TAGS = [
    {"name": "Welcome", "description": "Bienvenida"},
    {
        "name": "Subtopic",
        "description": "Gestion de subtemas vinculados a cada area temática.",
    },
    {
        "name": "Topic",
        "description": "Gestion de areas temáticas para clasificar preguntas.",
    },
    {
        "name": "Institution",
        "description": "Gestion de instituciones asociadas al banco de preguntas.",
    },
    {
        "name": "Source",
        "description": "Gestion de fuentes y referencias del contenido académico.",
    },
    {
        "name": "Image",
        "description": "Gestion de imágenes relacionadas con preguntas y contenido.",
    },
    {
        "name": "Question",
        "description": "Gestion de preguntas académicas, alternativas, dificultad y soluciones.",
    },
]

FASTAPI_METADATA = {
    "title": "Question Bank",
    "summary": "API para gestion estructurada de preguntas academicas.",
    "description": (
        "API REST para la gestion de un banco de preguntas academicas.\n"
        "Permite administrar preguntas, contenidos (texto e imagen), alternativas, "
        "soluciones, dificultad y categorizacion por areas y subtemas.\n"
        "Construida con FastAPI, SQLAlchemy 2.0 y PostgreSQL, siguiendo una "
        "arquitectura por capas con validaciones de dominio y manejo estructurado "
        "de excepciones."
    ),
    "version": "0.1.0",
    "contact": {
        "name": "Jancarlos",
        "email": "jancarlosmanuel03@gmail.com",
        "url": "https://github.com/Jancarlos042003",
    },
    "openapi_tags": OPENAPI_TAGS,
}
