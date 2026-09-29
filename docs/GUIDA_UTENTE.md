# Guida Utente — Agenda Parrocchiale

Guida passo-passo per installare, configurare e utilizzare il generatore
di agende liturgiche su **Windows**.

**Destinatari:** il frate responsabile del santuario/parrocchia,
con supporto tecnico da remoto se necessario.

---

## Indice

1. [Cos'è questo programma](#1-cosè-questo-programma)
2. [Cosa ti serve](#2-cosa-ti-serve)
3. [Prima installazione](#3-prima-installazione)
4. [Primo avvio — Genera la configurazione](#4-primo-avvio--genera-la-configurazione)
5. [Compilare l'agenda (Excel)](#5-compilare-lagenda-excel)
6. [Generare il PDF](#6-generare-il-pdf)
7. [Problemi comuni](#7-problemi-comuni)
8. [Privacy e backup](#8-privacy-e-backup)

---

## 1. Cos'è questo programma

Il programma genera **l'agenda annuale delle Messe** del santuario in
formato PDF, pronto per essere mandato in tipografia.

**Cosa fa automaticamente:**
- Calcola il calendario liturgico dell'anno (Pasqua, feste mobili)
- Applica gli orari stagionali (inverno, estate, maggio)
- Rispetta i divieti pomeridiani (Assunta, San Nicola, Corpus Domini)
- Inserisce le ricorrenze proprie (Triduo San Salvatore, Nove Mercoledì)
- Compila il registro delle intenzioni di Messa
- - Aggiunge in fondo una pagina dedicata alle prenotazioni dei matrimoni degli anni successivi

**Cosa devi fare tu:**
- Compilare un file Excel con gli orari, le intenzioni, i matrimoni
- Lanciare lo script che genera il PDF
- Controllare il PDF e mandarlo in tipografia

---

## 2. Cosa ti serve

### Requisiti minimi

| Cosa | Dettaglio |
|---|---|
| **Sistema operativo** | Windows 10 o 11 |
| **Spazio disco** | Almeno 500 MB liberi |
| **Connessione Internet** | Solo per la prima installazione |
| **Programma per Excel** | Microsoft Excel o LibreOffice Calc (gratuito) |

### Software da installare

1. **Python 3.13** (linguaggio di programmazione)
2. **Git** (per scaricare il progetto)
3. **LibreOffice** (se non hai Excel)
4. **Adobe Acrobat Reader** (per leggere i PDF)

---

## 3. Prima installazione

### 3.1 — Scaricare Python 3.13

1. Apri il browser e vai su: **https://www.python.org/downloads/**
2. Clicca sul pulsante giallo **"Download Python 3.13.x"**
3. Salva il file `python-3.13.x-amd64.exe` sul Desktop
4. **Doppio clic** sul file scaricato

**⚠️ IMPORTANTE:** nella prima schermata dell'installer, **spunta la casella** in basso:
**☑ Add python.exe to PATH**

Questo passaggio è **fondamentale**. Se non lo spunti, il programma non funzionerà.

5. Clicca **"Install Now"**
6. Attendi la fine dell'installazione (2-3 minuti)
7. Clicca **"Close"**

**Verifica:** apri il Prompt dei comandi (tasto Windows → digita `cmd` → Invio) e scrivi:
```cmd
python --version
```
**Deve rispondere qualcosa tipo Python 3.13.5.**
Se dà errore, Python non è installato correttamente → reinstalla spuntando "Add to PATH".

### 3.2 — Scaricare Git
1. Vai su: https://git-scm.com/download/win
2. Il download parte automaticamente
3. Doppio clic sul file .exe
4. Clicca "Next" su tutte le schermate (le impostazioni predefinite vanno bene)
5. Clicca "Install"
6. Al termine, clicca "Finish"

Verifica: apri il Prompt dei comandi e scrivi:
```cmd
git --version
```
**Deve rispondere git version 2.xx.x.**

### 3.3 — Scaricare il progetto
1. Apri il Prompt dei comandi (tasto Windows → cmd → Invio)
2. Digita:
```cmd
cd %USERPROFILE%\Documents
git clone https://github.com/hac114/agenda-parrocchiale.git 
```
3. Attendi il download (~10 MB, 30 secondi)
4. Verifica che sia presente la cartella C:\Users\<NomeUtente>\Documents\agenda-parrocchiale\

### 3.4 — Installare le dipendenze
Sempre dal Prompt dei comandi:
```cmd
cd %USERPROFILE%\Documents\agenda-parrocchiale
python -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```
#### Cosa fa ogni comando:
| Comando | Cosa fa |
|---|---|
| `cd ...` | Entra nella cartella del progetto |
| `python -m venv .venv` | Crea un "ambiente virtuale" isolato |
| `.venv\Scripts\activate.bat` | Attiva l'ambiente |
| `pip install ...` | Scarica le librerie necessarie |

**L'installazione dura 3-5 minuti. Se compaiono molte righe di testo, è normale.**

#### Verifica finale:
dopo l'installazione, il prompt mostra (.venv) all'inizio:

```cmd
(.venv) C:\Users\...\agenda-parrocchiale>
```
### 3.5 — Installare LibreOffice (se non hai Excel)
1. Vai su: https://it.libreoffice.org/download/download/
2. Clicca "Scarica"
3. Installa come un qualsiasi programma Windows
4. Avvia LibreOffice Calc una volta per completare la configurazione

## 4. Primo avvio — Genera la configurazione
1. Apri Esplora File e vai in:
C:\Users\<NomeUtente>\Documents\agenda-parrocchiale\scripts\
2. Doppio clic su genera_agenda.bat
3. Si apre una finestra nera (Prompt dei comandi) con questo output:
```text
======================================================================
  GENERAZIONE AGENDA
  Profilo: san_pietro_in_silki
  Anno:    2027
======================================================================

>>> STEP 1/3: Generazione config.xlsx
✅ Template generato: ...
📦 Backup creato: ...
✅ Profilo generato: ...

>>> STEP 2/3: Generazione PDF
PDF generato: ...output\Agenda_2027.pdf

>>> STEP 3/3: Riepilogo
✅ Fatto! PDF generato:
   ...\output\Agenda_2027.pdf
======================================================================
```
4. Premi un tasto per chiudere
Cosa è stato creato:
- configs\san_pietro_in_silki\config.xlsx → file Excel da compilare
- output\Agenda_2027.pdf → PDF (ancora vuoto, con dati di base)

## 5. Compilare l'agenda (Excel)
### 5.1 — Aprire il file Excel
- Vai in:

C:\Users\<NomeUtente>\Documents\agenda-parrocchiale\configs\san_pietro_in_silki\

- Doppio clic su config.xlsx.
- Si apre con Excel o LibreOffice Calc.

### 5.2 — Compilare il foglio "Impostazioni"
| Campo | Cosa scrivere |
|---|---|
| **Anno** | L'anno dell'agenda (es. 2027) |
| **Nome parrocchia** | Es. "San Pietro in Silki" |
| **Città** | Es. "Sassari" |
| **Periodi e orari** | Verifica che siano corretti per l'anno. Se cambiano, modifica |

**⚠️ Le celle GIALLE sono compilabili. Le altre sono protette.**

### 5.3 — Compilare il foglio "Intenzioni"
Per ogni intenzione di Messa:

| Colonna | Cosa scrivere |
|---|---|
| **Data consegna** | Quando il fedele ha consegnato l'intenzione |
| **Intenzione** | Il testo dell'intenzione (es. "Per la pace") |
| **Offerta (€)** | Solo per uso interno (non appare nel PDF) |
| **Data applicazione** | Quando la Messa sarà celebrata |
| **Note** | Eventuali annotazioni |

**Nota: la colonna N. si numera automaticamente.**

### 5.4 — Compilare il foglio "Matrimoni"

Qui puoi inserire **tutti i matrimoni che vuoi**, sia dell'anno corrente
dell'agenda, sia degli anni successivi.

**Come vengono usati nel PDF:**

| Data del matrimonio | Dove appare nel PDF |
|---|---|
| Nell'anno dell'agenda (es. 2027) | Nel **giorno specifico** del calendario |
| Negli anni successivi (es. 2028, 2029) | Nella **pagina finale** "Prenotazioni Matrimoni" |

**Esempio:** se stai facendo l'agenda 2027 e inserisci un matrimonio
del 15/06/2027, apparirà nel giorno 15 giugno 2027.
Se inserisci un matrimonio del 10/09/2028, apparirà nella pagina finale
dedicata alle prenotazioni future.

| Colonna | Cosa scrivere |
|---|---|
| **Data** | Data del matrimonio (gg/mm/aaaa) |
| **Ora** | Es. 15:30 |
| **Nome sposi** | Nomi completi |
| **Contatti** | Telefono o email |
| **Note** | Eventuali annotazioni |

**Nota:** nella pagina finale "Prenotazioni Matrimoni" compaiono solo
**data, ora e nome sposi** (i contatti e le note restano interni).

### 5.5 — Compilare il foglio "Note"
Annotazioni libere, per esempio:
- Programma del mese mariano (maggio)
- Iniziative del Triduo di San Salvatore
- Eventi speciali

| Colonna | Cosa scrivere |
|---|---|
| **Dal** | Data di inizio (gg/mm/aaaa) |
| **Al** | Data di fine (lascia vuoto se è un giorno solo) |
| **Nota** | Il testo |

5.6 — Salvare e chiudere
Salva il file (Ctrl+S) e chiudi Excel/LibreOffice.

**⚠️ IMPORTANTE: chiudi completamente Excel/LibreOffice prima di
generare il PDF. Altrimenti il PDF avrà i dati vecchi.**

## 6. Generare il PDF
1. Vai in: C:\Users\<NomeUtente>\Documents\agenda-parrocchiale\scripts\
2. Doppio clic su genera_agenda.bat
3. Attendi 30-60 secondi
4. Il PDF aggiornato appare in:

C:\Users\<NomeUtente>\Documents\agenda-parrocchiale\output\Agenda_2027.pdf

5. Apri il PDF con doppio clic per verificare che sia tutto a posto

**Cosa contiene il PDF (in ordine):**
1. **Copertina** (nome parrocchia, città, anno)
2. **365 pagine giorno** (una per ogni giorno dell'anno)
3. **Registro intenzioni** (elenco di tutte le intenzioni)
4. **Prenotazioni Matrimoni** (pagina finale con i matrimoni degli anni successivi)

5. Se ci sono errori, il programma mostra un riepilogo tipo:
```text
⚠️  ATTENZIONE: 3 problemi rilevati durante la lettura
...
Vuoi comunque procedere? [y/N]:
```
- Digita n per correggere gli errori in Excel
- Digita y per procedere (il PDF avrà dei buchi)

## 7. Problemi comuni
### 7.1 Il nome della parrocchia non si aggiorna
Causa:
Excel/LibreOffice tiene in memoria una versione vecchia.

Soluzione:
1. Chiudi completamente Excel/LibreOffice
2. Verifica che non ci siano processi attivi (Ctrl+Shift+Esc → Task Manager)
3. Riapri il file

### 7.2 Python non è riconosciuto come comando
Causa:
Python non è stato aggiunto al PATH durante l'installazione.

Soluzione:
1. Disinstalla Python dal Pannello di Controllo
2. Reinstalla spuntando "Add python.exe to PATH"

### 7.3 WeasyPrint non funziona o errori strani
Soluzione:
reinstalla le dipendenze.
```cmd
cd %USERPROFILE%\Documents\agenda-parrocchiale
.venv\Scripts\activate.bat
pip install --upgrade -r requirements.txt
```
### 7.4 Il PDF non si genera
Possibili cause:
- Excel/LibreOffice è ancora aperto → chiudilo
- config.xlsx non è compilato bene → controlla
- Manca qualche cella obbligatoria (Anno, Nome, Città)

**Come vedere i dettagli:** il .bat lascia la finestra aperta.
Leggi l'ultimo errore e mandalo al supporto tecnico.

### 7.5 Ho fatto casino e voglio ricominciare
Non ti preoccupare, ci sono i **backup automatici.**

Vai in: configs\san_pietro_in_silki\.backup\
Trovi tutti i backup con data e ora.
Basta copiare il file desiderato e rinominarlo in config.xlsx.

## 8. Privacy e backup
### ⚠️ Dati personali
Il file config.xlsx contiene dati personali:
- Nomi di defunti (intenzioni di Messa)
- Nomi degli sposi (matrimoni)
- Offerte ricevute

Queste informazioni NON devono essere condivise con nessuno.

### ⚠️ Il PC è condiviso con altri frati:

- Non lasciare config.xlsx aperto quando ti allontani
- Considera di mettere una password al PC
- Il file è in C:\Users\<TuoUtente>\Documents\ — visibile solo al tuo utente Windows

### Backup
Il programma fa backup automatici ogni volta che rigeneri la configurazione.
Li trovi in:

```text
configs\san_pietro_in_silki\.backup\config_<data>_<ora>.xlsx
```
**Consiglio:** una volta al mese, copia la cartella agenda-parrocchiale
su una **chiavetta USB** o su **Google Drive**.

### Cosa NON mandare mai in tipografia
- ❌ config.xlsx (contiene dati personali)
- ❌ Cartella configs\
- ✅ Solo il PDF in output\Agenda_2027.pdf

## Supporto
Per problemi tecnici, contatta Maurizio Chieruzzi con:
- Screenshot dell'errore
- Cosa stavi facendo
- Che giorno/ora era