# Progetto di programmazione - gestione delle spese personali e del budget
# Python + SQLite, programma da console. Avvio: python src/main.py

import sqlite3
from datetime import datetime
from math import isfinite
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "spese.db"
SQL_PATH = BASE_DIR / "sql" / "database.sql"


def connetti_database():
    nuovo_db = not DB_PATH.exists()
    conn = sqlite3.connect(DB_PATH)
    # se no le foreign key non vengono controllate
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        if nuovo_db:
            conn.executescript(SQL_PATH.read_text(encoding="utf-8"))
            conn.commit()
            print("Database creato e popolato con i dati di esempio.")
    except sqlite3.Error:
        conn.close()
        if nuovo_db:
            DB_PATH.unlink()
        raise
    return conn


def data_valida(testo, formato):
    try:
        data = datetime.strptime(testo, formato)
    except ValueError:
        return False
    return testo == data.strftime(formato)


def leggi_importo(messaggio):
    # accetto anche la virgola e poi converto
    testo = input(messaggio).strip().replace(",", ".")
    try:
        importo = float(testo)
    except ValueError:
        return None
    return importo if isfinite(importo) else None


def trova_categoria(conn, nome):
    riga = conn.execute(
        "SELECT id_categoria FROM categorie WHERE nome = ?;", (nome,)
    ).fetchone()
    return riga[0] if riga else None


def gestione_categorie(conn):
    print("\n--- GESTIONE CATEGORIE ---")
    nome = input("Nome della categoria: ").strip()

    if nome == "":
        print("Errore: il nome della categoria non può essere vuoto.")
        return

    if trova_categoria(conn, nome) is not None:
        print("La categoria esiste già.")
        return

    conn.execute("INSERT INTO categorie (nome) VALUES (?);", (nome,))
    conn.commit()
    print("Categoria inserita correttamente.")


def inserisci_spesa(conn):
    print("\n--- INSERISCI SPESA ---")
    data = input("Data (YYYY-MM-DD): ").strip()
    importo = leggi_importo("Importo: ")
    categoria = input("Nome della categoria: ").strip()
    descrizione = input("Descrizione (facoltativa): ").strip()

    if not data_valida(data, "%Y-%m-%d"):
        print("Errore: data non valida (formato YYYY-MM-DD).")
        return

    if importo is None:
        print("Errore: l'importo deve essere un numero.")
        return

    if importo <= 0:
        print("Errore: l'importo deve essere maggiore di zero.")
        return

    id_categoria = trova_categoria(conn, categoria)
    if id_categoria is None:
        print("Errore: la categoria non esiste.")
        return

    conn.execute(
        "INSERT INTO spese (data, importo, id_categoria, descrizione) "
        "VALUES (?, ?, ?, ?);",
        (data, importo, id_categoria, descrizione if descrizione else None),
    )
    conn.commit()
    print("Spesa inserita correttamente.")


def definisci_budget(conn):
    print("\n--- DEFINISCI BUDGET MENSILE ---")
    mese = input("Mese (YYYY-MM): ").strip()
    categoria = input("Nome della categoria: ").strip()
    importo = leggi_importo("Importo del budget: ")

    if not data_valida(mese, "%Y-%m"):
        print("Errore: mese non valido (formato YYYY-MM).")
        return

    if importo is None or importo <= 0:
        print("Errore: il budget deve essere maggiore di zero.")
        return

    id_categoria = trova_categoria(conn, categoria)
    if id_categoria is None:
        print("Errore: la categoria non esiste.")
        return

    budget_esistente = conn.execute(
        "SELECT id_budget FROM budget WHERE mese = ? AND id_categoria = ?;",
        (mese, id_categoria),
    ).fetchone()

    # stessa coppia mese/categoria: aggiorno
    if budget_esistente:
        conn.execute(
            "UPDATE budget SET importo = ? WHERE id_budget = ?;",
            (importo, budget_esistente[0]),
        )
    else:
        conn.execute(
            "INSERT INTO budget (mese, id_categoria, importo) VALUES (?, ?, ?);",
            (mese, id_categoria, importo),
        )
    conn.commit()
    print("Budget mensile salvato correttamente.")


def report_totale_per_categoria(conn):
    righe = conn.execute(
        "SELECT c.nome, SUM(s.importo) AS totale "
        "FROM categorie c JOIN spese s ON s.id_categoria = c.id_categoria "
        "GROUP BY c.id_categoria, c.nome "
        "ORDER BY totale DESC;"
    ).fetchall()

    print("\n" + "Categoria".ljust(20, ".") + "Totale Speso")
    if not righe:
        print("Nessuna spesa registrata.")
    for nome, tot in righe:
        print(nome.ljust(20, ".") + f" {tot:.2f}")


def report_spese_vs_budget(conn):
    righe = conn.execute(
        "SELECT b.mese, c.nome, b.importo, ROUND(COALESCE(SUM(s.importo), 0), 2) AS speso "
        "FROM budget b "
        "JOIN categorie c ON c.id_categoria = b.id_categoria "
        "LEFT JOIN spese s ON s.id_categoria = b.id_categoria "
        "                 AND substr(s.data, 1, 7) = b.mese "
        "GROUP BY b.mese, c.nome, b.importo "
        "ORDER BY b.mese, c.nome;"
    ).fetchall()

    if not righe:
        print("\nNessun budget definito.")
    for mese, categoria, budget, speso in righe:
        if speso > budget:
            stato = "SUPERAMENTO BUDGET"
        elif speso == budget:
            stato = "BUDGET RAGGIUNTO"
        else:
            stato = "NEI LIMITI"
        print(f"\nMese: {mese}")
        print(f"Categoria: {categoria}")
        print(f"Budget: {budget:.2f}")
        print(f"Speso: {speso:.2f}")
        print(f"Stato: {stato}")


def report_elenco_spese(conn):
    righe = conn.execute(
        "SELECT s.data, c.nome, s.importo, COALESCE(s.descrizione, '') "
        "FROM spese s JOIN categorie c ON c.id_categoria = s.id_categoria "
        "ORDER BY s.data, s.id_spesa;"
    ).fetchall()

    print(f"\n{'Data':<12}{'Categoria':<14}{'Importo':>10}  Descrizione")
    print("-" * 62)
    if not righe:
        print("Nessuna spesa registrata.")
    for data, categoria, importo, descrizione in righe:
        print(f"{data:<12}{categoria:<14}{importo:>10.2f}  {descrizione}")


def visualizza_report(conn):
    while True:
        print("\n-------------------------")
        print("       MENU REPORT")
        print("-------------------------")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese ordinate per data")
        print("4. Ritorna al menu principale")
        print("-------------------------")
        scelta = input("Inserisci la tua scelta: ").strip()

        if scelta == "1":
            report_totale_per_categoria(conn)
        elif scelta == "2":
            report_spese_vs_budget(conn)
        elif scelta == "3":
            report_elenco_spese(conn)
        elif scelta == "4":
            return
        else:
            print("Scelta non valida. Riprovare.")


def ciclo_principale(conn):
    while True:
        print("\n-------------------------")
        print(" SISTEMA SPESE PERSONALI")
        print("-------------------------")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        print("-------------------------")
        scelta = input("Inserisci la tua scelta: ").strip()

        if scelta == "1":
            gestione_categorie(conn)
        elif scelta == "2":
            inserisci_spesa(conn)
        elif scelta == "3":
            definisci_budget(conn)
        elif scelta == "4":
            visualizza_report(conn)
        elif scelta == "5":
            print("Arrivederci!")
            return
        else:
            print("Scelta non valida. Riprovare.")


def main():
    print("Benvenuto nel Sistema di Gestione delle Spese Personali!")
    try:
        conn = connetti_database()
        ciclo_principale(conn)
    except sqlite3.Error as errore:
        print(f"Errore del database: {errore}")
        return
    finally:
        try:
            conn.close()
        except UnboundLocalError:
            pass


if __name__ == "__main__":
    main()