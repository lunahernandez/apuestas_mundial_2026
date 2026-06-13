import json
import hashlib
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "partidos.json"

DEFAULT_PASSWORD = "mundial2026"


def cargar():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def guardar(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_pwd(pwd):
    return hashlib.sha1(pwd.encode()).hexdigest()


def verificar_admin(data):
    pwd = input("Contraseña de administrador: ").strip()
    stored = data.get("admin_hash", hash_pwd(DEFAULT_PASSWORD))
    if hash_pwd(pwd) != stored:
        print("Contraseña incorrecta.")
        sys.exit(1)


def menu_principal(data):
    print(f"\n=== Admin · {data['torneo']} ===")
    apuestas_str = "ABIERTAS" if data.get("apuestas_abiertas") else "CERRADAS"
    print(f"Apuestas: {apuestas_str} | Participantes: {len(data['participantes'])} | Partidos: {len(data['partidos'])}\n")
    print("1. Actualizar resultado de un partido")
    print("2. Cerrar período de apuestas")
    print("3. Reabrir período de apuestas")
    print("4. Cambiar contraseña de administrador")
    print("5. Ver estado de los partidos")
    print("6. Eliminar participante")
    print("0. Salir")
    return input("\nOpción: ").strip()


def actualizar_resultado(data):
    print("\nPartidos disponibles:\n")
    for p in data["partidos"]:
        rl = p["resultado_local"]
        rv = p["resultado_visitante"]
        estado = f"{rl}–{rv}" if rl is not None else "Pendiente"
        print(f"  [{p['id']:2d}] {p['local']} vs {p['visitante']}  ({p['fecha']})  →  {estado}")

    try:
        pid = int(input("\nID del partido a actualizar: ").strip())
    except ValueError:
        print("ID inválido.")
        return

    partido = next((p for p in data["partidos"] if p["id"] == pid), None)
    if partido is None:
        print("Partido no encontrado.")
        return

    print(f"\n{partido['local']} vs {partido['visitante']}")
    try:
        rl = int(input(f"Goles {partido['local']}: ").strip())
        rv = int(input(f"Goles {partido['visitante']}: ").strip())
    except ValueError:
        print("Valor inválido.")
        return

    partido["resultado_local"] = rl
    partido["resultado_visitante"] = rv
    guardar(data)
    print(f"✓ Resultado guardado: {partido['local']} {rl} – {rv} {partido['visitante']}")


def ver_partidos(data):
    print("\nEstado de todos los partidos:\n")
    for p in data["partidos"]:
        rl = p["resultado_local"]
        rv = p["resultado_visitante"]
        estado = f"{rl}–{rv}" if rl is not None else "Pendiente"
        print(f"  [{p['id']:2d}] {p['local']} vs {p['visitante']}  ({p['fecha']})  →  {estado}")
    input("\nPulsa Enter para continuar.")


def eliminar_participante(data):
    if not data["participantes"]:
        print("No hay participantes.")
        return
    print("\nParticipantes:")
    for i, p in enumerate(data["participantes"]):
        print(f"  {i+1}. {p['nombre']}")
    nombre = input("\nNombre a eliminar: ").strip()
    antes = len(data["participantes"])
    data["participantes"] = [p for p in data["participantes"] if p["nombre"].lower() != nombre.lower()]
    if len(data["participantes"]) < antes:
        guardar(data)
        print(f"✓ '{nombre}' eliminado.")
    else:
        print("Nombre no encontrado.")


def cambiar_password(data):
    nueva = input("Nueva contraseña: ").strip()
    if len(nueva) < 4:
        print("La contraseña debe tener al menos 4 caracteres.")
        return
    data["admin_hash"] = hash_pwd(nueva)
    guardar(data)
    print("✓ Contraseña actualizada.")


def main():
    data = cargar()
    verificar_admin(data)

    while True:
        data = cargar()
        opcion = menu_principal(data)

        if opcion == "1":
            actualizar_resultado(data)
        elif opcion == "2":
            data["apuestas_abiertas"] = False
            guardar(data)
            print("✓ Apuestas cerradas.")
        elif opcion == "3":
            data["apuestas_abiertas"] = True
            guardar(data)
            print("✓ Apuestas reabiertas.")
        elif opcion == "4":
            cambiar_password(data)
        elif opcion == "5":
            ver_partidos(data)
        elif opcion == "6":
            eliminar_participante(data)
        elif opcion == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción no válida.")

        if opcion in ("1", "2", "3", "4", "6"):
            regen = input("\n¿Regenerar el sitio web ahora? (s/n): ").strip().lower()
            if regen == "s":
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / "generar.py")],
                    capture_output=True, text=True
                )
                print(result.stdout or result.stderr)


if __name__ == "__main__":
    main()
