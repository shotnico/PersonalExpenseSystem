# Personal Expense System

Programma da console in Python con database SQLite per registrare spese personali e confrontarle con un budget mensile.

## Requisiti

Python 3.8 o successivo, con i moduli standard `sqlite3`, `datetime`, `math` e `pathlib`. Non servono pacchetti esterni né compilazione.

## Avvio

```console
git clone https://github.com/shotnico/PersonalExpenseSystem.git
cd PersonalExpenseSystem
python src/main.py
```

Su macOS e Linux il comando può essere `python3 src/main.py`.

Al primo avvio il programma crea `spese.db` con le tabelle e i dati di esempio presi da `sql/database.sql`. Negli avvii successivi i dati inseriti restano.

## Uso

1. **Gestione Categorie**: aggiunge una categoria. Rifiuta nomi vuoti e duplicati.
2. **Inserisci Spesa**: chiede data nel formato `YYYY-MM-DD`, importo positivo e categoria già presente. La descrizione è facoltativa. Per i decimali vanno bene punto e virgola.
3. **Definisci Budget Mensile**: chiede mese `YYYY-MM`, categoria e importo positivo. Se il budget per quella coppia esiste già lo aggiorna.
4. **Visualizza Report**: totale per categoria, confronto mensile con il budget, oppure elenco delle spese per data.
5. **Esci**: chiude il programma.

Il confronto mensile mostra solo i mesi e le categorie che hanno un budget. Il totale per categoria mostra solo le categorie con almeno una spesa.

## File

- `src/main.py`: programma da console.
- `sql/database.sql`: tabelle, dati di esempio, prove dei vincoli e query dei report. Va eseguito su un database vuoto.
- `demo/`: video di funzionamento.

## Note di progetto

Le categorie sono confrontate senza distinguere maiuscole e minuscole (`COLLATE NOCASE`), quindi il controllo dei duplicati va fatto prima dell'inserimento. I mesi sono confrontati come stringhe `YYYY-MM`. Le date sono validate con `strptime` più un confronto sul testo, e restano comunque coperte dal vincolo nel database.