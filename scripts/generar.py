import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "partidos.json"
OUT_FILE = Path(__file__).parent.parent / "docs" / "index.html"

BANDERAS = {
    "México": "🇲🇽", "Sudáfrica": "🇿🇦", "Corea del Sur": "🇰🇷", "Chequia": "🇨🇿",
    "Canadá": "🇨🇦", "Bosnia-Herzegovina": "🇧🇦", "Qatar": "🇶🇦", "Suiza": "🇨🇭",
    "Brasil": "🇧🇷", "Marruecos": "🇲🇦", "Haití": "🇭🇹", "Escocia": "🏴",
    "Estados Unidos": "🇺🇸", "Paraguay": "🇵🇾", "Australia": "🇦🇺", "Turquía": "🇹🇷",
    "Alemania": "🇩🇪", "Curazao": "🇨🇼", "Costa de Marfil": "🇨🇮", "Ecuador": "🇪🇨",
    "Países Bajos": "🇳🇱", "Japón": "🇯🇵", "Suecia": "🇸🇪", "Túnez": "🇹🇳",
    "España": "🇪🇸", "Cabo Verde": "🇨🇻", "Arabia Saudita": "🇸🇦", "Uruguay": "🇺🇾",
    "Bélgica": "🇧🇪", "Egipto": "🇪🇬", "Irán": "🇮🇷", "Nueva Zelanda": "🇳🇿",
    "Francia": "🇫🇷", "Senegal": "🇸🇳", "Irak": "🇮🇶", "Noruega": "🇳🇴",
    "Argentina": "🇦🇷", "Argelia": "🇩🇿", "Austria": "🇦🇹", "Jordania": "🇯🇴",
    "Portugal": "🇵🇹", "RD Congo": "🇨🇩", "Uzbekistán": "🇺🇿", "Colombia": "🇨🇴",
    "Inglaterra": "🏴", "Croacia": "🇭🇷", "Ghana": "🇬🇭", "Panamá": "🇵🇦",
    "Por definir": "❓"
}

PUNTOS_ACIERTO = 1
PUNTOS_EMPATE_ACIERTO = 1

COLORES_GRUPO = {
    "A": "#FF5C4D", "B": "#FFB627", "C": "#1FAA59", "D": "#2EC4F1",
    "E": "#9B5DE5", "F": "#FF6FB5", "G": "#00B8A9", "H": "#F8C630",
    "I": "#4361EE", "J": "#F25C54", "K": "#5FBB63", "L": "#FF9F1C",
}


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
            if apuesta["ganador"] == ganador_real:
                pts = PUNTOS_ACIERTO if ganador_real != "empate" else PUNTOS_EMPATE_ACIERTO
                puntuaciones[nombre]["puntos"] += pts
                puntuaciones[nombre]["aciertos"] += 1

    return sorted(puntuaciones.items(), key=lambda x: -x[1]["puntos"])


def flag(equipo):
    return BANDERAS.get(equipo, "🏳")


def grupo_color(grupo):
    return COLORES_GRUPO.get(grupo, "#888")


def resultado_texto(partido):
    rl = partido["resultado_local"]
    rv = partido["resultado_visitante"]
    if rl is None:
        return '<span class="sin-resultado">vs</span>'
    return f'<span class="resultado">{rl} – {rv}</span>'


def apuesta_usuario_html(participante, partido_id, local, visitante, ganador_real):
    apuesta = next((a for a in participante.get("apuestas", []) if a["partido_id"] == partido_id), None)
    if apuesta is None:
        return '<span class="chip chip-vacio">sin apuesta</span>'
    g = apuesta["ganador"]
    etiquetas = {"local": local, "visitante": visitante, "empate": "Empate"}
    label = etiquetas.get(g, g)
    if ganador_real is None:
        return f'<span class="chip chip-pendiente">{label}</span>'
    acierto = g == ganador_real
    cls = "chip-acierto" if acierto else "chip-fallo"
    icono = "✓" if acierto else "✗"
    return f'<span class="chip {cls}">{label} {icono}</span>'


def build_clasificacion_html(ranking):
    if not ranking:
        return '<p class="empty-msg">¡Nadie ha apostado todavía! Sé el primero ⚡</p>'

    max_pts = max((s["puntos"] for _, s in ranking), default=0)
    if max_pts == 0:
        max_pts = 1

    medallas = ["🥇", "🥈", "🥉"]
    colores_pos = ["#FFD23F", "#C8D3DB", "#FFB36B"]

    html = '<div class="clasificacion">'
    for i, (nombre, stats) in enumerate(ranking):
        bar_fill = round((stats["puntos"] / max_pts) * 100)
        medalla = medallas[i] if i < 3 else None
        top3_cls = " top3" if i < 3 else ""
        borde = colores_pos[i] if i < 3 else "var(--marino-10)"
        inicial = nombre[0].upper()
        html += f"""
        <div class="jugador-row{top3_cls}" style="--borde-pos:{borde}">
            <div class="avatar">{medalla or inicial}</div>
            <div class="jugador-main">
                <div class="jugador-top">
                    <span class="nombre">{nombre}</span>
                    <span class="pts">{stats['puntos']} pts</span>
                </div>
                <div class="barra-wrap">
                    <div class="barra-fill" style="width: {bar_fill}%"></div>
                </div>
                <span class="stats">{stats['aciertos']} aciertos de {stats['jugados']} jugados</span>
            </div>
        </div>"""
    html += '</div>'
    return html


def build_partidos_html(data):
    fases = {}
    for p in data["partidos"]:
        key = p["fase"] + (" · Grupo " + p["grupo"] if p.get("grupo") else "")
        fases.setdefault(key, []).append(p)

    participantes = data["participantes"]
    html = ""

    for fase, partidos in fases.items():
        grupo = partidos[0].get("grupo")
        color = grupo_color(grupo) if grupo else "#16213E"
        html += f'<div class="fase-label" style="--c:{color}"><span>{fase}</span></div>'
        for partido in partidos:
            pid = partido["id"]
            local = partido["local"]
            visitante = partido["visitante"]
            rl = partido["resultado_local"]
            rv = partido["resultado_visitante"]
            ganador_real = calcular_ganador(rl, rv) if rl is not None else None

            chips_html = ""
            for part in participantes:
                chips_html += f"""
                <div class="apuesta-row">
                    <span class="part-nombre">{part['nombre']}</span>
                    {apuesta_usuario_html(part, pid, local, visitante, ganador_real)}
                </div>"""
            if not chips_html:
                chips_html = '<span class="chip chip-vacio">Sin apuestas aún</span>'

            html += f"""
            <div class="cromo" style="--c:{color}">
                <div class="cromo-top">
                    <div class="equipo">
                        <span class="bandera">{flag(local)}</span>
                        <span class="equipo-nombre">{local}</span>
                    </div>
                    <div class="marcador">{resultado_texto(partido)}</div>
                    <div class="equipo equipo-derecha">
                        <span class="equipo-nombre">{visitante}</span>
                        <span class="bandera">{flag(visitante)}</span>
                    </div>
                </div>
                <div class="cromo-fecha">{partido['fecha']}</div>
                <div class="apuestas-grid">
                    {chips_html}
                </div>
            </div>"""
    return html


def build_html(data):
    ranking = calcular_puntuaciones(data)
    total_partidos = len(data["partidos"])
    estado_apuestas = "ABIERTAS" if data.get("apuestas_abiertas") else "CERRADAS"
    badge_cls = "badge-open" if data.get("apuestas_abiertas") else "badge-closed"

    clasificacion_html = build_clasificacion_html(ranking)
    partidos_html = build_partidos_html(data)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data['torneo']} · Quiniela</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
    --crema: #FFF8EC;
    --marino: #16213E;
    --marino-10: rgba(22,33,62,0.1);
    --amarillo: #FFD23F;
    --coral: #FF5C4D;
    --azul: #2EC4F1;
    --verde: #1FAA59;
    --gris: #8D99AE;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: 'Inter', sans-serif;
    background: var(--crema);
    background-image:
        radial-gradient(circle at 8% 18%, rgba(46,196,241,0.12) 0, transparent 35%),
        radial-gradient(circle at 92% 12%, rgba(255,210,63,0.18) 0, transparent 35%),
        radial-gradient(circle at 85% 80%, rgba(255,92,77,0.10) 0, transparent 40%);
    color: var(--marino);
    min-height: 100vh;
}}
header {{
    position: relative;
    background: var(--marino);
    padding: 36px 24px 30px;
    text-align: center;
    overflow: hidden;
    border-bottom: 6px solid var(--amarillo);
}}
header::before, header::after {{
    content: "⚽";
    position: absolute;
    font-size: 4rem;
    opacity: 0.08;
}}
header::before {{ top: -10px; left: -10px; transform: rotate(-15deg); }}
header::after {{ bottom: -20px; right: -10px; transform: rotate(20deg); }}
.header-title {{
    font-family: 'Fredoka', sans-serif;
    font-size: clamp(1.8rem, 6vw, 2.8rem);
    font-weight: 700;
    color: var(--crema);
    letter-spacing: 0.02em;
}}
.header-title .accent {{ color: var(--amarillo); }}
.header-sub {{
    font-size: 0.9rem;
    color: var(--azul);
    margin-top: 6px;
    font-weight: 500;
}}
.badge {{
    display: inline-block;
    margin-top: 14px;
    font-family: 'Fredoka', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 6px 18px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
.badge-open {{ background: var(--amarillo); color: var(--marino); }}
.badge-closed {{ background: var(--coral); color: var(--crema); }}
main {{ max-width: 880px; margin: 0 auto; padding: 28px 16px 60px; }}
section {{ margin-bottom: 44px; }}
.section-title {{
    font-family: 'Fredoka', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--marino);
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.section-title .dot {{
    width: 14px; height: 14px;
    background: var(--coral);
    border-radius: 50%;
    display: inline-block;
}}

/* Clasificación */
.clasificacion {{ display: flex; flex-direction: column; gap: 10px; }}
.jugador-row {{
    display: flex;
    align-items: center;
    gap: 14px;
    background: #fff;
    border: 2px solid var(--marino-10);
    border-radius: 16px;
    padding: 12px 16px;
}}
.jugador-row.top3 {{ border-color: var(--borde-pos); border-width: 2.5px; }}
.avatar {{
    width: 42px; height: 42px;
    border-radius: 50%;
    background: var(--crema);
    border: 2px solid var(--borde-pos, var(--marino-10));
    display: flex; align-items: center; justify-content: center;
    font-family: 'Fredoka', sans-serif;
    font-weight: 600;
    font-size: 1.1rem;
    flex-shrink: 0;
}}
.jugador-main {{ flex: 1; min-width: 0; }}
.jugador-top {{
    display: flex; justify-content: space-between; align-items: baseline;
    margin-bottom: 6px; gap: 8px;
}}
.nombre {{ font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 1.02rem; }}
.pts {{ font-family: 'Fredoka', sans-serif; font-weight: 700; font-size: 1rem; color: var(--coral); white-space: nowrap; }}
.barra-wrap {{ width: 100%; height: 8px; background: var(--marino-10); border-radius: 999px; overflow: hidden; margin-bottom: 4px; }}
.barra-fill {{ height: 100%; background: linear-gradient(90deg, var(--azul), var(--verde)); border-radius: 999px; transition: width 0.6s ease; }}
.stats {{ font-size: 0.74rem; color: var(--gris); }}

/* Fase label */
.fase-label {{
    margin: 28px 0 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.fase-label span {{
    font-family: 'Fredoka', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    background: var(--c);
    color: #fff;
    padding: 5px 14px;
    border-radius: 999px;
}}
.fase-label::after {{
    content: "";
    flex: 1;
    height: 2px;
    background: repeating-linear-gradient(90deg, var(--c) 0 6px, transparent 6px 12px);
    opacity: 0.4;
}}

/* Cromo (match card) */
.cromo {{
    background: #fff;
    border-radius: 18px;
    border: 2.5px dashed var(--c);
    padding: 16px 18px;
    margin-bottom: 14px;
    position: relative;
}}
.cromo-top {{
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 8px;
}}
.equipo {{ display: flex; align-items: center; gap: 8px; min-width: 0; }}
.equipo-derecha {{ justify-content: flex-end; text-align: right; }}
.bandera {{ font-size: 1.6rem; flex-shrink: 0; }}
.equipo-nombre {{ font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 0.95rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.marcador {{ text-align: center; min-width: 60px; }}
.resultado {{ font-family: 'Fredoka', sans-serif; font-weight: 700; font-size: 1.3rem; color: var(--marino); }}
.sin-resultado {{ font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 1rem; color: var(--gris); }}
.cromo-fecha {{ text-align: center; font-size: 0.72rem; color: var(--gris); margin-top: 6px; letter-spacing: 0.05em; }}
.apuestas-grid {{
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px dashed var(--marino-10);
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}}
.apuesta-row {{ display: flex; align-items: center; gap: 6px; }}
.part-nombre {{ font-size: 0.76rem; color: var(--gris); font-weight: 500; }}
.chip {{
    font-family: 'Fredoka', sans-serif;
    font-size: 0.74rem; font-weight: 600;
    padding: 3px 10px; border-radius: 999px;
    background: var(--crema);
    border: 1.5px solid var(--marino-10);
}}
.chip-acierto {{ background: rgba(31,170,89,0.12); border-color: var(--verde); color: var(--verde); }}
.chip-fallo {{ background: rgba(255,92,77,0.10); border-color: var(--coral); color: var(--coral); }}
.chip-vacio {{ color: var(--gris); border-style: dashed; }}

.info-box {{
    background: #fff;
    border: 2px solid var(--marino-10);
    border-left: 5px solid var(--azul);
    border-radius: 14px;
    padding: 16px 20px;
    font-size: 0.88rem;
    color: var(--marino);
    line-height: 1.6;
}}
.info-box code {{
    background: var(--crema);
    padding: 2px 6px;
    border-radius: 6px;
    font-size: 0.82rem;
}}
.empty-msg {{ color: var(--gris); font-style: italic; font-size: 0.9rem; }}
footer {{
    text-align: center;
    padding: 28px;
    font-size: 0.76rem;
    color: var(--gris);
}}
@media (max-width: 480px) {{
    .equipo-nombre {{ font-size: 0.82rem; }}
    .bandera {{ font-size: 1.3rem; }}
}}
</style>
</head>
<body>
<header>
    <div class="header-title">⚽ {data['torneo']} <span class="accent">· Quiniela</span></div>
    <div class="header-sub">{total_partidos} partidos · ¿quién sabe más de fútbol?</div>
    <span class="badge {badge_cls}">Apuestas {estado_apuestas}</span>
</header>
<main>
    <section>
        <div class="section-title"><span class="dot"></span>Clasificación</div>
        {clasificacion_html}
    </section>
    <section>
        <div class="section-title"><span class="dot" style="background:var(--azul)"></span>Cómo apostar</div>
        <div class="info-box">
            <strong>Las apuestas están {estado_apuestas.lower()}.</strong><br>
            {"Ejecuta <code>python scripts/apostar.py</code> para registrar tu predicción de cada partido." if data.get("apuestas_abiertas") else "El plazo para apostar ha cerrado. Solo el admin puede actualizar resultados ahora."}
        </div>
    </section>
    <section>
        <div class="section-title"><span class="dot" style="background:var(--verde)"></span>Partidos</div>
        {partidos_html}
    </section>
</main>
<footer>Hecho con Python para el Mundial 2026 🌎</footer>
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