# Guida Rapida — Agenda Parrocchiale

**Cheat sheet** per l'uso annuale del programma.
Da tenere stampato accanto al PC.

> Per l'installazione completa, vedi la [Guida Utente](GUIDA_UTENTE.md).

---

## ⚠️ Requisito importante (Windows)

Su **Windows** è obbligatorio installare **GTK 3 Runtime** per generare il PDF.
Senza di esso, il launcher fallirà con un errore tipo
`cannot load library 'libgobject-2.0-0'`.

**Download:** https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

Vedi la [Guida Utente](GUIDA_UTENTE.md#32-bis--installare-gtk-3-runtime-obbligatorio-per-windows) per le istruzioni dettagliate.

---

## I 3 passi annuali

| # | Cosa fare | Dove |
|---|---|---|
| **1** | Compila il file Excel (solo celle gialle) | `configs/<profilo>/config.xlsx` |
| **2** | Salva e **chiudi** Excel/LibreOffice | — |
| **3** | Doppio clic sul launcher → PDF | `scripts/genera_agenda.bat` |

Il PDF appare in: `output/Agenda_<anno>.pdf`

---

## Aggiornare il programma (quando serve)

Quando vuoi scaricare le novità dal programma:

1. Doppio clic su `scripts/aggiorna.bat`
2. Attendi 30 secondi

Poi rigenera il PDF con `scripts/genera_agenda.bat`.

**I tuoi dati non vengono toccati.**

---

## Cosa scrivere nei 4 fogli

### 📋 Foglio "Impostazioni"

| Campo | Cosa scrivere |
|---|---|
| **Anno** | L'anno dell'agenda (es. 2027) |
| **Nome parrocchia** | Es. "San Pietro in Silki" |
| **Città** | Es. "Sassari" |
| **Periodi e orari** | Verifica che siano corretti per l'anno |

### 📋 Foglio "Intenzioni"

| Colonna | Cosa scrivere |
|---|---|
| **Data consegna** | Quando il fedele ha consegnato l'intenzione |
| **Intenzione** | Il testo (es. "Per la pace") |
| **Offerta (€)** | Solo uso interno (non appare nel PDF) |
| **Data applicazione** | Quando la Messa sarà celebrata |
| **Note** | Eventuali annotazioni |

**Nota:** la colonna `N.` si numera da sola.

### 📋 Foglio "Matrimoni"

| Colonna | Cosa scrivere |
|---|---|
| **Data** | gg/mm/aaaa (anno corrente o futuri) |
| **Ora** | Es. 15:30 |
| **Nome sposi** | Nomi completi |
| **Contatti** | Telefono o email |
| **Note** | Eventuali annotazioni |

**Dove appaiono nel PDF:**

| Data matrimonio | Posizione nel PDF |
|---|---|
| Nell'anno dell'agenda | Nel giorno specifico + tabella "MATRIMONI \<anno\>" in coda |
| Negli anni successivi | Solo nella tabella "MATRIMONI \<anno\>" in coda |

### 📋 Foglio "Note"

| Colonna | Cosa scrivere |
|---|---|
| **Dal** | Data di inizio |
| **Al** | Data di fine (vuoto se un giorno solo) |
| **Nota** | Il testo |

---

## Le 5 regole d'oro

1. ✅ Modifica **solo le celle GIALLE**
2. ✅ **Chiudi Excel** prima di generare il PDF
3. ✅ **Un giorno = una riga** nel foglio Intenzioni
4. ✅ La **data matrimonio** decide in quali tabelle annuali appare in coda al PDF (il giorno specifico è automatico)
5. ❌ Non cancellare colonne, non rinominare fogli

---

## Cosa contiene il PDF

1. **Copertina**
2. **10 pagine "Intenzioni libere"** (subito dopo la copertina, da compilare a mano)
3. **365 pagine giorno** (una per giorno, con tabella Messe + tabella Intenzioni + spazio iniziative)
4. **Registro intenzioni**
5. **Tabelle matrimoni annuali** in coda: "MATRIMONI 2027", "MATRIMONI 2028"
   (una riga per ogni sabato disponibile, escluso maggio)

Ogni pagina giorno contiene:
- Data, giorno settimana, festività
- Note liturgiche (se presenti)
- Tabella Messe (Ora / Intenzioni / Firma, 3 sub-righe per Messa)
- Tabella Intenzioni di applicazione (Luogo / Intenzione / Firma)
- Spazio "Altre iniziative / Note"

Il PDF ha **margini di rilegatura di 30 mm** su entrambi i lati.

---

## Cosa fare se qualcosa va storto

### ❌ Il nome della parrocchia non si aggiorna in Excel

**Causa:** Excel/LibreOffice tiene in memoria la versione vecchia, anche dopo aver chiuso il file.

#### Procedura rapida

**Windows:**
1. Chiudi **tutte** le finestre di Excel/LibreOffice
2. `Ctrl+Shift+Esc` → Task Manager → cerca `EXCEL.EXE` o `soffice` → Termina attività
3. Riapri il file

**Linux:**
```bash
pkill soffice
libreoffice --norestore configs/san_pietro_in_silki/config.xlsx
```

#### Se il problema persiste — verifica il file

Il file su disco contiene il nome corretto? Apri il Prompt dei comandi (o il terminale):

**Windows:**
```cmd
cd %USERPROFILE%\Documents\agenda-parrocchiale
python -c "from openpyxl import load_workbook; wb = load_workbook('configs/san_pietro_in_silki/config.xlsx'); ws = wb['Impostazioni']; print('Nome:', ws['B6'].value)"
```

**Linux:**
```bash
cd ~/Developer/Python/progetti/agenda-parrocchiale
python -c "from openpyxl import load_workbook; wb = load_workbook('configs/san_pietro_in_silki/config.xlsx'); ws = wb['Impostazioni']; print('Nome:', ws['B6'].value)"
```

**Cosa aspettarti:**
- Se stampa `Nome: San Pietro in Silki` → il file è OK, era solo la cache dell'editor
- Se stampa un nome vuoto o sbagliato → il problema è nel file o nel codice, contatta il supporto

#### Soluzione definitiva per LibreOffice (Linux)

Se anche cancellare la cache non funziona, apri il file con:

```bash
libreoffice --norestore configs/san_pietro_in_silki/config.xlsx
```

L'opzione `--norestore` impedisce a LibreOffice di ricaricare l'ultima
sessione e **forza la lettura pulita dal disco**.

#### Altri comandi utili

Cancella la cache di LibreOffice:

```bash
rm -rf ~/.config/libreoffice/4/user/backup
rm -rf ~/.config/libreoffice/4/user/registrymodifications.xcu
```

Verifica che il file su disco contenga il nome corretto:

```bash
python -c "
from openpyxl import load_workbook
wb = load_workbook('configs/san_pietro_in_silki/config.xlsx')
ws = wb['Impostazioni']
print('Nome:', ws['B6'].value)
"
```

Poi riapri il file.

### ❌ Il PDF non si genera

**Possibili cause:**
- Excel è ancora aperto → chiudilo
- Manca Anno, Nome o Città → controlla
- Errore nel launcher → leggi l'ultima riga della finestra nera

### ❌ Ho fatto casino, voglio ricominciare

**Soluzione:** usa i **backup automatici**.

Vai in: `configs/<profilo>/.backup/`
Trovi file con data e ora.
Copia quello desiderato e rinominalo in `config.xlsx`.

---

## Contatti

**Maurizio Chieruzzi** — maurizio.chieruzzi@gmail.com

Quando chiedi aiuto invia:
- Screenshot dell'errore
- Cosa stavi facendo
- Che giorno/ora era