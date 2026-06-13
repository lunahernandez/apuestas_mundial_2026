# ⚽ Mundial 2026 · Quiniela entre amigos

Visor de apuestas para el Mundial con clasificación en tiempo real, desplegado en **GitHub Pages**.

## Cómo funciona

| Quién | Qué hace |
|-------|----------|
| Cualquier amigo | Ejecuta `apostar.py` para registrar sus predicciones |
| Admin | Ejecuta `admin.py` para meter resultados y cerrar apuestas |
| Todos | Ven el marcador en `https://TU_USUARIO.github.io/TU_REPO/` |

**Sistema de puntos**
- Aciertas el ganador → **3 puntos**
- Aciertas que hay empate → **1 punto**
- Fallas → 0 puntos

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
```

No necesitas instalar ninguna librería. Solo Python 3.8+.

### 2. Activar GitHub Pages

En tu repositorio de GitHub:
- Ir a **Settings → Pages**
- Source: **Deploy from a branch**
- Branch: `main` / carpeta: `/docs`
- Guardar

El sitio estará en `https://TU_USUARIO.github.io/TU_REPO/`

### 3. Cambiar la contraseña de admin (opcional pero recomendado)

La contraseña por defecto es `mundial2026`. Para cambiarla:

```bash
python scripts/admin.py
# Introduce la contraseña actual y ve a la opción 4
```

---

## Flujo del primer día (período de apuestas)

### Cada participante registra sus apuestas:

```bash
python scripts/apostar.py
```

El script pregunta partido por partido. Las respuestas se guardan en `data/partidos.json`.

### Después de que todos apuesten, el admin cierra el período:

```bash
python scripts/admin.py
# Opción 2 → Cerrar período de apuestas
```

### Regenerar el sitio y subir a GitHub:

```bash
python scripts/generar.py
git add .
git commit -m "Apuestas cerradas"
git push
```

---

## Durante el torneo

Cuando haya un resultado, el admin lo introduce:

```bash
python scripts/admin.py
# Opción 1 → Actualizar resultado
# El script pregunta si quieres regenerar el sitio
```

Después:

```bash
git add .
git commit -m "Resultado: España 2-0 Costa Rica"
git push
```

GitHub Pages actualiza automáticamente en ~1 minuto.

---

## Estructura del proyecto

```
mundial-apuestas/
├── data/
│   └── partidos.json        ← base de datos (apuestas + resultados)
├── docs/
│   └── index.html           ← sitio generado (GitHub Pages sirve esto)
├── scripts/
│   ├── apostar.py           ← los amigos registran apuestas
│   ├── admin.py             ← el admin actualiza resultados
│   └── generar.py           ← genera el HTML estático
└── README.md
```

---

## Personalizar los partidos

Edita `data/partidos.json` para añadir, quitar o cambiar partidos. Formato de cada partido:

```json
{
  "id": 1,
  "fase": "Grupos",
  "grupo": "A",
  "local": "España",
  "visitante": "Costa Rica",
  "fecha": "2026-06-12",
  "resultado_local": null,
  "resultado_visitante": null
}
```

Cuando el resultado esté disponible, pon los goles en vez de `null`.

---

## Seguridad

- La contraseña de admin se guarda como hash SHA-1 en `partidos.json`. No es criptografía de producción, pero es suficiente para una quiniela entre amigos.
- Las apuestas son visibles para todos una vez que se genera el HTML.
