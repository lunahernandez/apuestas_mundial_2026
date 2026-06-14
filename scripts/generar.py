import json
import os
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "partidos.json"
OUT_FILE = Path(__file__).parent.parent / "docs" / "index.html"

BANDERAS = {
    "México": "🇲🇽", "Polonia": "🇵🇱", "Arabia Saudí": "🇸🇦", "Argentina": "🇦🇷",
    "Estados Unidos": "🇺🇸", "Gales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Irán": "🇮🇷",
    "Francia": "🇫🇷", "Australia": "🇦🇺", "Dinamarca": "🇩🇰", "Túnez": "🇹🇳",
    "España": "🇪🇸", "Costa Rica": "🇨🇷", "Alemania": "🇩🇪", "Japón": "🇯🇵",
    "Brasil": "🇧🇷", "Serbia": "🇷🇸", "Suiza": "🇨🇭", "Camerún": "🇨🇲",
    "Portugal": "🇵🇹", "Ghana": "🇬🇭", "Uruguay": "🇺🇾", "Corea del Sur": "🇰🇷"
}

PUNTOS_ACIERTO = 1
PUNTOS_EMPATE_ACIERTO = 1


def calcular_ganador(rl, rv):
    if rl > rv:
        return "local"
    if rv > rl:
        return "visitante"
    return "empate"


def calcular_puntuaciones(data):
    puntuaciones = {}
    for p in data["participantes"]:
        puntuaciones[p["nombre"]] = {"puntos": 0, "aciertos": 0, "jugados": 0}

    for partido in data["partidos"]:
        rl = partido["resultado_local"]
        rv = partido["resultado_visitante"]
        if rl is None or rv is None:
            continue
        ganador_real = calcular_ganador(rl, rv)
        pid = partido["id"]

        for participante in data["participantes"]:
            nombre = participante["nombre"]
            apuesta = next((a for a in participante.get("apuestas", []) if a["partido_id"] == pid), None)
            if apuesta is None:
                continue
            puntuaciones[nombre]["jugados"] += 1
            ganador_apostado = apuesta["ganador"]
            if ganador_apostado == ganador_real:
                pts = PUNTOS_ACIERTO if ganador_real != "empate" else PUNTOS_EMPATE_ACIERTO
                puntuaciones[nombre]["puntos"] += pts
                puntuaciones[nombre]["aciertos"] += 1

    return sorted(puntuaciones.items(), key=lambda x: -x[1]["puntos"])


def flag(equipo):
    return BANDERAS.get(equipo, "")


def resultado_texto(partido):
    rl = partido["resultado_local"]
    rv = partido["resultado_visitante"]
    if rl is None:
        return '<span class="sin-resultado">Pendiente</span>'
    return f'<span class="resultado">{rl} – {rv}</span>'


def apuesta_usuario_html(participante, partido_id, ganador_real):
    apuesta = next((a for a in participante.get("apuestas", []) if a["partido_id"] == partido_id), None)
    if apuesta is None:
        return '<span class="no-apuesta">—</span>'
    g = apuesta["ganador"]
    etiquetas = {"local": "Local", "visitante": "Visitante", "empate": "Empate"}
    label = etiquetas.get(g, g)
    if ganador_real is None:
        return f'<span class="apuesta">{label}</span>'
    acierto = g == ganador_real
    cls = "acierto" if acierto else "fallo"
    icono = "✓" if acierto else "✗"
    return f'<span class="apuesta {cls}">{label} {icono}</span>'


def build_clasificacion_html(ranking, total_partidos):
    if not ranking:
        return '<p class="empty-msg">Aún no hay participantes registrados.</p>'

    max_pts = ranking[0][1]["puntos"] if ranking else 1
    if max_pts == 0:
        max_pts = 1

    html = '<div class="clasificacion">'
    for i, (nombre, stats) in enumerate(ranking):
        pct = round((stats["puntos"] / (total_partidos * PUNTOS_ACIERTO)) * 100) if total_partidos > 0 else 0
        pct = min(pct, 100)
        bar_fill = round((stats["puntos"] / max_pts) * 100)
        medallas = ["🥇", "🥈", "🥉"]
        pos_icon = medallas[i] if i < 3 else f"{i+1}."
        html += f"""
        <div class="jugador-row">
            <div class="jugador-info">
                <span class="pos">{pos_icon}</span>
                <span class="nombre">{nombre}</span>
                <span class="stats">{stats['aciertos']} aciertos · {stats['jugados']} jugados</span>
            </div>
            <div class="barra-wrap">
                <div class="barra-fill" style="width: {bar_fill}%"></div>
            </div>
            <span class="pts">{stats['puntos']} pts</span>
        </div>"""
    html += '</div>'
    return html


def build_partidos_html(data):
    fases = {}
    for p in data["partidos"]:
        key = p["fase"] + (" – Grupo " + p["grupo"] if p.get("grupo") else "")
        fases.setdefault(key, []).append(p)

    participantes = data["participantes"]
    html = ""

    for fase, partidos in fases.items():
        html += f'<div class="fase-label">{fase}</div>'
        for partido in partidos:
            pid = partido["id"]
            rl = partido["resultado_local"]
            rv = partido["resultado_visitante"]
            ganador_real = calcular_ganador(rl, rv) if rl is not None else None

            apuestas_html = ""
            for part in participantes:
                apuestas_html += f"""
                <div class="apuesta-row">
                    <span class="part-nombre">{part['nombre']}</span>
                    {apuesta_usuario_html(part, pid, ganador_real)}
                </div>"""

            html += f"""
            <div class="partido-card">
                <div class="partido-header">
                    <div class="equipos">
                        <span>{flag(partido['local'])} {partido['local']}</span>
                        <span class="vs">vs</span>
                        <span>{partido['visitante']} {flag(partido['visitante'])}</span>
                    </div>
                    <div class="partido-meta">
                        <span class="fecha">{partido['fecha']}</span>
                        {resultado_texto(partido)}
                    </div>
                </div>
                <div class="apuestas-grid">
                    {apuestas_html if apuestas_html else '<span class="no-apuesta">Sin apuestas aún</span>'}
                </div>
            </div>"""
    return html


def build_html(data):
    ranking = calcular_puntuaciones(data)
    total_partidos_jugados = sum(
        1 for p in data["partidos"]
        if p["resultado_local"] is not None
    )
    total_partidos = len(data["partidos"])
    estado_apuestas = "abiertas" if data.get("apuestas_abiertas") else "cerradas"
    badge_cls = "badge-open" if data.get("apuestas_abiertas") else "badge-closed"

    clasificacion_html = build_clasificacion_html(ranking, total_partidos_jugados)
    partidos_html = build_partidos_html(data)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data['torneo']} · Apuestas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Barlow+Condensed:wght@600;800&display=swap" rel="stylesheet">
<style>
:root {{
    --verde: #00C46A;
    --verde-dark: #009950;
    --negro: #0D0D0D;
    --gris-oscuro: #1A1A1A;
    --gris-medio: #2A2A2A;
    --gris-borde: #333;
    --texto: #F0F0F0;
    --texto-suave: #888;
    --oro: #FFD060;
    --rojo: #FF4D4D;
    --accent: #00C46A;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: 'Space Grotesk', sans-serif;
    background: var(--negro);
    color: var(--texto);
    min-height: 100vh;
}}
header {{
    background: var(--gris-oscuro);
    border-bottom: 2px solid var(--verde);
    padding: 24px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}}
.header-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--verde);
}}
.header-sub {{
    font-size: 0.85rem;
    color: var(--texto-suave);
    margin-top: 2px;
}}
.badge {{
    font-size: 0.75rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.badge-open {{ background: var(--verde); color: #000; }}
.badge-closed {{ background: #444; color: var(--texto-suave); }}
main {{ max-width: 900px; margin: 0 auto; padding: 32px 16px; }}
section {{ margin-bottom: 48px; }}
.section-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--verde);
    border-left: 4px solid var(--verde);
    padding-left: 12px;
    margin-bottom: 20px;
}}
.clasificacion {{ display: flex; flex-direction: column; gap: 12px; }}
.jugador-row {{
    display: grid;
    grid-template-columns: 1fr auto auto;
    align-items: center;
    gap: 16px;
    background: var(--gris-oscuro);
    border: 1px solid var(--gris-borde);
    border-radius: 8px;
    padding: 14px 18px;
}}
.jugador-info {{ display: flex; align-items: center; gap: 10px; min-width: 0; }}
.pos {{ font-size: 1.2rem; flex-shrink: 0; }}
.nombre {{ font-weight: 700; font-size: 1rem; }}
.stats {{ font-size: 0.78rem; color: var(--texto-suave); white-space: nowrap; }}
.barra-wrap {{
    width: 120px;
    height: 8px;
    background: var(--gris-medio);
    border-radius: 4px;
    overflow: hidden;
    flex-shrink: 0;
}}
.barra-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--verde-dark), var(--verde));
    border-radius: 4px;
    transition: width 0.6s ease;
}}
.pts {{ font-weight: 700; font-size: 1rem; color: var(--oro); white-space: nowrap; }}
.fase-label {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--texto-suave);
    margin: 24px 0 10px;
}}
.partido-card {{
    background: var(--gris-oscuro);
    border: 1px solid var(--gris-borde);
    border-radius: 10px;
    margin-bottom: 12px;
    overflow: hidden;
}}
.partido-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 18px;
    border-bottom: 1px solid var(--gris-borde);
    flex-wrap: wrap;
    gap: 8px;
}}
.equipos {{ display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 0.95rem; }}
.vs {{ color: var(--texto-suave); font-size: 0.8rem; }}
.partido-meta {{ display: flex; align-items: center; gap: 12px; }}
.fecha {{ font-size: 0.78rem; color: var(--texto-suave); }}
.sin-resultado {{ font-size: 0.8rem; color: var(--texto-suave); font-style: italic; }}
.resultado {{ font-weight: 700; font-size: 1rem; color: var(--verde); }}
.apuestas-grid {{
    padding: 10px 18px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}}
.apuesta-row {{ display: flex; align-items: center; gap: 8px; }}
.part-nombre {{ font-size: 0.8rem; color: var(--texto-suave); }}
.apuesta {{ font-size: 0.78rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; background: var(--gris-medio); }}
.apuesta.acierto {{ background: rgba(0,196,106,0.2); color: var(--verde); }}
.apuesta.fallo {{ background: rgba(255,77,77,0.15); color: var(--rojo); }}
.no-apuesta {{ font-size: 0.78rem; color: #555; }}
.empty-msg {{ color: var(--texto-suave); font-style: italic; font-size: 0.9rem; }}
.info-box {{
    background: var(--gris-oscuro);
    border: 1px solid var(--gris-borde);
    border-left: 3px solid var(--verde);
    border-radius: 8px;
    padding: 16px 20px;
    font-size: 0.88rem;
    color: var(--texto-suave);
    line-height: 1.6;
}}
.info-box strong {{ color: var(--texto); }}
footer {{
    text-align: center;
    padding: 32px;
    font-size: 0.78rem;
    color: #444;
}}
@media (max-width: 600px) {{
    .barra-wrap {{ width: 70px; }}
    .jugador-row {{ grid-template-columns: 1fr auto; }}
    .barra-wrap {{ display: none; }}
}}
</style>
</head>
<body>
<header>
    <div>
        <div class="header-title">⚽ {data['torneo']} · Quiniela</div>
        <div class="header-sub">Predicción de ganadores · {total_partidos} partidos</div>
    </div>
    <span class="badge {badge_cls}">Apuestas {estado_apuestas}</span>
</header>
<main>
    <section>
        <div class="section-title">Clasificación</div>
        {clasificacion_html}
    </section>
    <section>
        <div class="section-title">Cómo apuntar tu apuesta</div>
        <div class="info-box">
            <strong>Las apuestas están {estado_apuestas}.</strong><br>
            {"Edita el archivo <code>data/partidos.json</code> y ejecuta <code>python scripts/generar.py</code> para registrar participantes y apuestas. Consulta el README para instrucciones detalladas." if data.get("apuestas_abiertas") else "El plazo para apostar ha cerrado. Solo el administrador puede actualizar resultados."}
        </div>
    </section>
    <section>
        <div class="section-title">Partidos</div>
        {partidos_html}
    </section>
</main>
<footer>Generado con Python · {data['torneo']}</footer>
</body>
</html>"""


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    OUT_FILE.parent.mkdir(exist_ok=True)
    html = build_html(data)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Sitio generado en {OUT_FILE}")


if __name__ == "__main__":
    main()