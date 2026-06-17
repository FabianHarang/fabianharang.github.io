# Fabian Nøst Harang - personlig hjemmeside

Dette er en statisk, publiseringsklar hjemmeside i AMOR-stilen. Den trenger
ingen build tools: `index.html`, `assets/`, `css/` og `ai/` er nok.

## Se siden lokalt

Åpne `index.html` direkte i nettleseren, eller kjør en enkel lokal server:

```bash
python3 -m http.server 8080
```

Gå deretter til `http://localhost:8080`.

## Hva som er klart

- Forside i AMOR-profilen.
- Portrettbilde i `assets/Fabian-Harang.jpg`.
- Google Scholar-lenke: `https://scholar.google.com/citations?user=BgOf4TgAAAAJ&hl=no`
- SURE-AI-lenke: `https://www.simula.no/sure-ai`
- GitHub-lenke til tensordev: `https://github.com/hagerpa/tensordev`
- Full publikasjonliste hentet fra arXiv per 17. juni 2026.
- Egne seksjoner for AI Notes og news.
- Statisk KI-fondet-artikkel på `ai/blog/ai-fondet.html`.
- Kontaktfelt med `fabian.harang@bi.no`.

## Det jeg trenger fra deg senere

- CV som PDF hvis du vil ha en direkte CV-knapp. Legg den for eksempel i
  `assets/Fabian-Harang-CV.pdf`.
- AI-notater, offentlige dokumenter eller korte refleksjoner som PDF eller Word.
  Når de ligger i prosjektmappen, kan de lenkes fra `#ai-notes`.
- News-lenker eller korte tekster fra AMOR/SURE-AI. De kan legges inn som nye
  `<article class="news-item">...</article>` i `#news`.
- Riktig offentlig AMOR-URL. Jeg fant ikke en verifiserbar AMOR-hjemmeside
  offentlig, så AMOR-lenken peker foreløpig til AMOR-seksjonen på egen side.

## Lansering med GitHub Pages og eget domene

Dette er den anbefalte veien hvis du vil ha en ryddig akademisk hjemmeside som
er lett å oppdatere videre.

### 1. Test siden lokalt først

Kjør dette fra prosjektmappen:

```bash
cd "/Users/fabianharang/Documents/Fabian Hjemmeside"
python3 -m http.server 8080
```

Åpne `http://localhost:8080`. Sjekk forsiden, menyen, bildet, publikasjoner,
AI Notes, KI-fondet-artikkelen, news og kontakt.

Viktig: KI-fondet-artikkelen lastes som statisk innhold via nettleseren. Test
den derfor via lokal server eller GitHub Pages, ikke ved å dobbeltklikke direkte
på `ai/blog/ai-fondet.html`.

Stopp lokal server etterpå med `Ctrl+C` i terminalen.

### 2. Opprett GitHub-konto

1. Gå til `https://github.com`.
2. Opprett konto eller logg inn.
3. Velg et kort brukernavn du er komfortabel med at står i URL-en. Eksempel:
   `fabianharang`.

Hvis brukernavnet ditt er `fabianharang`, blir GitHub Pages-adressen:

```text
https://fabianharang.github.io
```

### 3. Opprett riktig repository

1. På GitHub: klikk `+` øverst til høyre.
2. Velg `New repository`.
3. Repository name må være nøyaktig:

```text
DITT-GITHUB-BRUKERNAVN.github.io
```

Eksempel:

```text
fabianharang.github.io
```

4. Velg `Public`.
5. Ikke velg en komplisert template.
6. Det er greit å huke av `Add a README file`, men ikke nødvendig siden vi har
   en lokal `README.md`.
7. Klikk `Create repository`.

### 4. Last opp filene

I repositoryet:

1. Klikk `Add file`.
2. Velg `Upload files`.
3. Dra inn disse fra prosjektmappen:

```text
index.html
README.md
assets/
css/
ai/
```

Viktig: `assets/`, `css/` og `ai/` må være mapper på toppnivå, ikke inni en
ekstra mappe.
Riktig struktur på GitHub skal være:

```text
fabianharang.github.io/
├── index.html
├── README.md
├── assets/
│   ├── Fabian-Harang.jpg
│   ├── amor-icon-dark.png
│   ├── amor-logo-white.png
│   └── ...
├── css/
│   └── post.css
└── ai/
    └── blog/
        ├── ai-fondet.html
        └── ai-fondet.content.html
```

Ikke last opp `KI-fondet-nettside/` som del av den offentlige nettsiden. Den er
en arbeids-/kildemappe med originalinstruksene. GitHub Pages trenger bare den
ferdige `ai/`-mappen og `css/`-mappen som ligger på toppnivå.

4. Skriv commit-melding, for eksempel `Initial website`.
5. Klikk `Commit changes`.

### 5. Aktiver GitHub Pages

1. Gå til repositoryet på GitHub.
2. Klikk `Settings`.
3. I venstremenyen: klikk `Pages`.
4. Under `Build and deployment`:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/ (root)`
5. Klikk `Save`.
6. Vent 1-10 minutter.
7. Besøk:

```text
https://DITT-GITHUB-BRUKERNAVN.github.io
```

Eksempel:

```text
https://fabianharang.github.io
```

### 6. Kjøp domene

Du trenger ikke webhotell. Du trenger bare et domene, fordi GitHub Pages hoster
selve nettsiden gratis.

Jeg ville valgt slik:

- `Domeneshop`: best hvis du vil ha norsk leverandør, norsk grensesnitt,
  norsk support og eventuelt `.no`.
- `Cloudflare Registrar`: fint for `.com`, teknisk ryddig og ofte billig på
  fornyelse, men litt mer teknisk.
- `Namecheap`: greit og brukervennlig for `.com`, men sjekk alltid
  fornyelsespris før du kjøper.

Forslag til domener:

```text
fabianharang.com
fabianharang.no
fabian-nost-harang.com
fabianharang.ai
```

Jeg ville startet med `fabianharang.com` hvis det er ledig. Hvis du vil ha norsk
preg, kjøp også `fabianharang.no` og la ett av dem redirecte til hoveddomenet.

### 7. Legg domenet inn i GitHub Pages

Etter at domenet er kjøpt:

1. Gå til GitHub-repositoryet.
2. Klikk `Settings`.
3. Klikk `Pages`.
4. Under `Custom domain`, skriv domenet du vil bruke.

Jeg anbefaler å bruke `www` som hovedadresse:

```text
www.fabianharang.com
```

5. Klikk `Save`.

GitHub lager da normalt en `CNAME`-fil i repositoryet. Den skal inneholde:

```text
www.fabianharang.com
```

### 8. Sett DNS hos domeneforhandleren

Gå til DNS-innstillingene der du kjøpte domenet.

Hvis hovedadressen skal være `www.fabianharang.com`, legg inn:

```text
Type: CNAME
Name/Host: www
Value/Target: DITT-GITHUB-BRUKERNAVN.github.io
TTL: Auto eller 3600
```

Eksempel:

```text
Type: CNAME
Name/Host: www
Value/Target: fabianharang.github.io
TTL: Auto eller 3600
```

For at `fabianharang.com` uten `www` også skal virke, legg inn disse fire
`A`-recordene:

```text
Type: A
Name/Host: @
Value: 185.199.108.153

Type: A
Name/Host: @
Value: 185.199.109.153

Type: A
Name/Host: @
Value: 185.199.110.153

Type: A
Name/Host: @
Value: 185.199.111.153
```

Hvis DNS-panelet også støtter IPv6, kan du i tillegg legge inn disse
`AAAA`-recordene:

```text
Type: AAAA
Name/Host: @
Value: 2606:50c0:8000::153

Type: AAAA
Name/Host: @
Value: 2606:50c0:8001::153

Type: AAAA
Name/Host: @
Value: 2606:50c0:8002::153

Type: AAAA
Name/Host: @
Value: 2606:50c0:8003::153
```

Ikke legg inn wildcard-records som `*.fabianharang.com`.

### 9. Aktiver HTTPS

1. Gå tilbake til GitHub -> repository -> `Settings` -> `Pages`.
2. Vent til GitHub har funnet domenet og utstedt sertifikat.
3. Huk av `Enforce HTTPS`.

Det kan ta opptil 24 timer før HTTPS-valget blir tilgjengelig etter DNS-endring.

### 10. Sjekk at alt virker

Test disse adressene:

```text
https://www.fabianharang.com
https://fabianharang.com
https://DITT-GITHUB-BRUKERNAVN.github.io
https://www.fabianharang.com/ai/blog/ai-fondet.html
```

Hvis `www` virker, men domenet uten `www` ikke virker, er det nesten alltid
`A`-recordene som mangler eller ikke har propagert ennå.

Du kan sjekke DNS i terminalen:

```bash
dig www.fabianharang.com +nostats +nocomments +nocmd
dig fabianharang.com +noall +answer -t A
```

### 11. Oppdater nettsiden senere

For små endringer:

1. Åpne `index.html` lokalt.
2. Endre tekst eller lenker.
3. Gå til GitHub-repositoryet.
4. Klikk filen du vil endre.
5. Klikk blyant-ikonet.
6. Lim inn/endre innhold.
7. Klikk `Commit changes`.

For større endringer kan vi senere sette opp GitHub Desktop eller `git` lokalt,
slik at du bare kan pushe endringer fra Mac-en.

- Nye AI-notater eller dokumenter legges i `assets/` og lenkes fra AI Notes-seksjonen.
- Nye lengre AI-notater kan legges som egne HTML-sider i `ai/blog/`.
- Nye nyheter legges inn i `#news` som nye `news-item`-artikler.

## Vedlikehold

Dette er en ren HTML-side. Nye publikasjoner kan legges inn ved å kopiere et
nytt `<article class="pub">...</article>` i publikasjonslisten.
