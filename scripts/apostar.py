import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "partidos.json"

OPCIONES = {"1": "local", "2": "empate", "3": "visitante"}
ETIQUETAS = {"local": "Local", "empate": "Empate", "visitante": "Visitante"}


def cargar():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def guardar(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    data = cargar()

    if not data.get("apuestas_abiertas"):
        print("Las apuestas están cerradas. Ya no se pueden registrar predicciones.")
        sys.exit(1)

    print(f"\n=== {data['torneo']} · Registro de apuesta ===\n")
    nombre = input("Tu nombre: ").strip()
    if not nombre:
        print("Nombre inválido.")
        sys.exit(1)

    participante = next((p for p in data["participantes"] if p["nombre"].lower() == nombre.lower()), None)
    if participante is None:
        participante = {"nombre": nombre, "apuestas": []}
        data["participantes"].append(participante)
        print("\nNuevo participante. Vamos con tus apuestas.\n")
    else:
        print(f"\nYa tienes apuestas guardadas, '{participante['nombre']}'.")
        print("Pulsa Enter para mantener una apuesta existente, o escribe 1/2/3 para cambiarla.\n")

    apuestas_actuales = {a["partido_id"]: a["ganador"] for a in participante.get("apuestas", [])}

    print("1=Local  2=Empate  3=Visitante  Enter=mantener/saltar\n")

    for partido in data["partidos"]:
        local = partido["local"]
        visitante = partido["visitante"]
        pid = partido["id"]
        actual = apuestas_actuales.get(pid)
        sufijo = f"  (actual: {ETIQUETAS.get(actual, actual)})" if actual else ""
        print(f"  [{pid:2d}] {local} vs {visitante}  ({partido['fecha']}){sufijo}")
        while True:
            opcion = input("       Tu apuesta (1/2/3 o Enter): ").strip()
            if opcion == "":
                break
            if opcion in OPCIONES:
                apuestas_actuales[pid] = OPCIONES[opcion]
                break
            print("       Opción no válida. Escribe 1, 2, 3 o Enter.")

    participante["apuestas"] = [
        {"partido_id": pid, "ganador": ganador}
        for pid, ganador in apuestas_actuales.items()
    ]

    guardar(data)
    print(f"\n✓ Apuestas de '{participante['nombre']}' guardadas correctamente.")
    print("Ejecuta 'python scripts/generar.py' para actualizar el sitio.\n")


if __name__ == "__main__":
    main()