import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "partidos.json"

OPCIONES = {"1": "local", "2": "empate", "3": "visitante"}


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

    existente = next((p for p in data["participantes"] if p["nombre"].lower() == nombre.lower()), None)
    if existente:
        print(f"\nYa existe una entrada para '{existente['nombre']}'.")
        resp = input("¿Sobrescribir apuestas? (s/n): ").strip().lower()
        if resp != "s":
            print("Cancelado.")
            sys.exit(0)
        data["participantes"] = [p for p in data["participantes"] if p["nombre"].lower() != nombre.lower()]

    apuestas = []
    print("\nPara cada partido elige: 1=Local  2=Empate  3=Visitante\n")

    for partido in data["partidos"]:
        local = partido["local"]
        visitante = partido["visitante"]
        pid = partido["id"]
        print(f"  [{pid:2d}] {local} vs {visitante}  ({partido['fecha']})")
        while True:
            opcion = input("       Tu apuesta (1/2/3): ").strip()
            if opcion in OPCIONES:
                apuestas.append({"partido_id": pid, "ganador": OPCIONES[opcion]})
                break
            print("       Opción no válida. Escribe 1, 2 o 3.")

    data["participantes"].append({"nombre": nombre, "apuestas": apuestas})
    guardar(data)
    print(f"\n✓ Apuesta de '{nombre}' guardada correctamente.")
    print("Ejecuta 'python scripts/generar.py' para actualizar el sitio.\n")


if __name__ == "__main__":
    main()
