# Programming Project 2024 Erasmushogeschool Brussel
## Flask Applicatie voor de Uitleendienst van het Medialab
### Introductie
**Als eerstejaars studenten toegepaste informatica hebben we deze applicatie gebouwd die gebruikers toelaat om eenvoudig artikels te reserveren en beheren.**
Deze flask-applicatie heeft als doel om zowel beheerders als studenten/docenten van een duidelijk overzicht te voorzien waar men artikels kan reserveren, ophalen en terugbrengen.

Beheerders hebben de mogelijkheid om te zien wat er voor bepaalde data opgehaald/teruggebracht moet worden, gebruikers hebben de optie om gewenste items aan hun reserveringen toe te voegen en deze te annuleren/verlengen indien nodig.

Als framework voor de applicatie hebben we het Python Flask framework gebruikt vanwege zijn flexibiliteit, performance en eenvoud. 
Andere gebruikte modules zijn SQLAlchemy, Jinja2, Werkzeug en Pandas. Verderop in deze readme volgt een volledig overzicht van alle gebruikte technologieën.

### Instructies

1. Clone de repository naar je gewenste locatie

```typescript
git clone https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1
```

2. Open een terminal in de locatie waar de repository is opgeslagen, of navigeer er naartoe in je terminal

```typescript
cd ProgrammingProject_Groep1
```

3. Maak een python virtual environment aan in de repository

```typescript
python -m venv venv
```

Of, afhankelijk van je geïnstalleerde Python versie

```typescript
python3 -m venv venv
```

4. Activeer de virtual environment

**Windows**

```typescript
.\venv\Scripts\activate
```

**Mac**

```typescript
source venv/bin/activate
```

5. Eens de virtualenv geactiveerd is, installeer de requirements
(Afhankelijk van je Python versie)

```typescript
pip install -r requirements.txt
```

Of

```typescript
pip3 install -r requirements.txt
```

6. Maak een bestand aan in de "Website" folder (Waar views.py, auth.py,... staan) genaamd: config.py 

Hier zul je je Brevo API-Key moeten invullen (**Deze is om veiligheidsredenen niet meegegeven in de publieke Git Repository**)

**https://www.brevo.com/**

(**Zie teams voor API-Key**)

```typescript
api_key = "<Jouw-API-Key>"
```

7. Als alles geïnstalleerd is, kan je de applicatie starten door main.py te runnen, en naar localhost:5000 te navigeren in je browser

```typescript
python main.py
```

Of 

```typescript
python3 main.py
```

8. Voor testing zijn er 3 gebruikers toegevoegd:

 - Admin:
   - e-mail: admin@test
   - password: password
- Student:
   - e-mail: student@test
   - password: password
- Docent:
   - e-mail: docent@test
   - password: password
   

### Overzicht van gebruikte technologieën

- **Python Flask:** Flexibel en eenvoudig framework voor webapplicaties.
  
- **SQLAlchemy:** SQL toolkit en Object-Relational Mapping (ORM) library voor Python. Zorgt dat er geen nood is aan SQL-Queries.
  
- **Jinja2:** Template engine voor Python.
  
- **Werkzeug:** WSGI utility library voor Python. Onder andere gebruikt om password hashes met een salt te genereren en veilige filenames te genereren.
  
- **Pandas:** Data analysis en data manipulation tool voor Python. Gebruikt om berekeningen met data te maken.

- **Flask-Login:** Extensie voor Flask om gebruikerssessies en logins te beheren.

- **Flask-Mail:** Extensie voor Flask om emails te versturen vanuit de applicatie.

- **Bootstrap:** Front-end framework voor het ontwikkelen van responsive en gebruiksvriendelijke websites.

- **Jquery:** JavaScript library die het gemakkelijker maakt om met HTML documenten te werken, events te beheren en animaties toe te voegen.

- **Flatpickr:** Datetime picker.

- **Popper.js:** Library voor het beheren van poppers, die tooltips, popovers en dropdowns.

### Overzicht Functionaliteiten

- **Loginsysteem:** Gebruikers kunnen zich registreren en inloggen om toegang te krijgen tot de applicatie.
  
- **Catalogus:** Een uitgebreide catalogus waar gebruikers door items kunnen bladeren en door op ze te klikken hun beschrijving kunnen lezen.
    - **Zoekfunctie:** Gebruikers kunnen de catalogus doorzoeken met behulp van een zoekfunctie.
    - **Filterfunctie:**  Gebruikers kunnen de catalogus filteren op basis van verschillende criteria (categorie, merk, type en beschikbaarheid bepaalde datums)                             om snel specifieke items te vinden.
    - **Extra info:** Gebruikers kunnen klikken op een item om extra info te zien over het artikel.
    - **Carousels:**  Gebruikers kunnen door meerdere exemplaren van een specifiek item bladeren met een carrouselweergave.
    - **Reserveerfunctie:** Gebruikers kunnen een item reserveren door de gewenste datums aan te klikken op de kalender voor het ophalen en terugbrengen en vervolgens op de reserveerknop te klikken.
 
- **Overzicht reserveringen:** Gebruikers kunnen een overzicht van al hun reserveringen bekijken op een speciale reserveringspagina.
    -**Annuleerfunctie:** Gebruikers kunnen een reservering annuleren op de reserveringspagina, mits het item nog niet is opgehaald.
    -**Verlengfunctie:** Gebruikers kunnen een reservering verlengen met maximaal 1 week, mits het item in hun bezit is.
    -**Reserveringsdatums:** De start- en einddatums van elke reservering worden weergegeven.

- **Infopagina:** Een pagina waar gebruikers het reglement, de openingsuren, de contactgegevens en het adres van het MediaLab kunnen vinden.

- **Persoonlijke informatiepagina:** Gebruikers hebben toegang tot een pagina waar ze hun eigen persoonlijke informatie kunnen bekijken en mogelijk bewerken.                                           Hiervoor moeten ze op hun naam klikken rechtsbovenaan in de navigatiebalk.

- **Admin Dashboard:** Een pagina waar admins een overzicht hebben van de vorige/komende weken en de artikelen die opgehaald en teruggebracht moeten worden op de gekozen week.
    -** Artikelbeheer:** Admins kunnen direct op het admin dashboard ingeven wanneer een artikel is opgehaald of ingeleverd door op een van de artikels te klikken, of handmatig het artikel-id en user-id in te voeren. Bij het inleveren van een artikel kan ook aangeduid worden of er schade is aan het artikel, en een beschrijving + foto uploaden van de schade.                                          
    -** Artikelen over datum:** Admins kunnen op het admin dashboard direct zien welke artikels te laat zijn.

- **Historiekpagina:** In de historiekpagina kan de admin alle vorige reserveringen bekijken met gedetailleerde informatie over elke uitlening, inclusief titel, merk, artikel-ID, datums van de reservering, gebruiker en aanvullende informatie.
    
- **Artikelbeheerpagina:** Admins hebben toegang tot een speciale pagina voor het beheren van artikelen.
    - **Edit-functie:** Admins kunnen bestaande artikelen aanpassen, zoals bijvoorbeeld de naam, beschrijving of foto etc. door op het gewenste artikel te klikken.
    - **Add-functie:** Admins kunnen nieuwe artikelen toevoegen aan de catalogus door op de Add-knop te klikken.
    - **Filter-functie:** Admins kunnen gemakkelijk het gewenste artikel vinden door het op te zoeken in de zoekbalk, of een of meerdere filters toe te passen.
    
- **Blacklistpagina:** Op deze pagina wordt duidelijk aangegeven welke gebruikers geband zijn en welke niet.
  - **Banfunctie:** Admins hebben de mogelijkheid om gebruikers te bannen en daarmee hun recht om te reserveren weg te halen. Hierbij kan je ook een reden meegeven.
  - **Unbanfunctie:** Admins kunnen eerder verbannen gebruikers deblokkeren en hun toegang tot de reserveringfunctie herstellen.
  - **Filterfunctie:**  Admins kunnen de catalogus filteren op basis van verschillende criteria (banned, niet banned, naam en studentennummer) of zoeken op naam om snel specifieke gebruikers te vinden.
  - **Gebruikerstype veranderen:** Admins kunnen het type gebruiker en daarmee ook de rechten van de gebruikers aanpassen (Docent, Student, Admin).

- **Achterliggende functionaliteiten:**
  - Studenten kunnen max 14 dagen op voorhand reserveren. Datums na deze 14 dagen zijn niet selecteerbaar.
  - Docenten mogen items uitlenen zonder een limiet.
  - Gebruikers krijgen automatisch een mail als:
      - Een artikel gereserveerd wordt.
      - Een artikel verlengd wordt.
      - Een reservering geannuleerd wordt.
      - Ze een waarschuwing krijgen/ en of een reservering overtijd is.
      - Ze op de blacklist worden gezet/gehaald.
      - Als herinnering 1 dag voor het inleveren van het artikel.
      - Als een artikel dat zij hebben gereserveerd niet meer beschikbaar is.
  - Een artikel dat reeds gereserveerd is, wordt onselecteerbaar gemaakt voor de gereserveerde datums. Deze worden ook rood gekleurd in de kalender zodat het duidelijk is voor de gebruikers.
  - Het is onmogelijk een item te verlengen dat niet opgehaald is, of een reservering te annuleren die al opgehaald is.
  - Gebruikers die geen admin zijn worden de toegang geweigerd als ze op een pagina bestemd voor admins proberen te komen.
  - Gebruikers moeten ingelogd zijn om toegang te hebben tot alle pagina's (behalve de login-page).
  - Passwords worden beveiligd door middel van Hashing met de SHA-256 methode en een salt-length van 16 bytes.
  - Inputs die uit tekst bestaan worden in de backend gecontroleerd op verboden tekens om te beveiligen tegen verschillende vormen van injection.
  - File uploads mogen enkel fotobestanden zijn.
  - Bij het invoeren van een artikel-id of user-id in de admin dashboard, verschijnt automatisch de titel en de foto van het artikel of de naam van de gebruiker.
  - Als een gebruiker geblacklist is, kan hij nogsteeds zijn reserveringen bekijken maar geen nieuwe items reserveren.
  - Een artikel kan maximum 1 keer verlengd worden voor 1 week.
    

### Bronnenvermelding

- **Flask:**
    - https://flask.palletsprojects.com/en/3.0.x/#user-s-guide
    - https://www.youtube.com/watch?v=Z1RJmh_OqeA
    - https://www.youtube.com/watch?v=dam0GPOAvVI
    - https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
    - https://flask.palletsprojects.com/en/3.0.x/tutorial/layout/
    - https://flask.palletsprojects.com/en/2.1.x/security/
- **Flask-mail:**
    - https://developers.brevo.com/docs/send-a-transactional-email
- **Flask-login:**
    - https://flask-login.readthedocs.io/en/latest/
- **Python:** 
    - https://www.w3schools.com/python/
- **Bootstrap:**
    - https://getbootstrap.com/docs/4.1/getting-started/introduction/
- **jQuery:**
    - https://www.w3schools.com/jquery/default.asp
    - https://learn.jquery.com/ 
- **Flatpickr:** 
    - https://flatpickr.js.org/
- **css:**
    - https://www.w3schools.com/css/
- **ChatGPT:**
    - https://ehb-my.sharepoint.com/:w:/r/personal/haytham_tahere_student_ehb_be/Documents/chatgpt%20discussie.docx?  
      d=wfc741d26cc61488db7540b371653e2f4&csf=1&web=1&e=TbEDaT
      (chatgpt kan geen link genereren als er afbeeldingen of bestanden zijn in de discussie, dus hier is een word document met de   
      volledige discussie)
    - https://chatgpt.com/share/d6b79258-63d8-47a5-80a0-f93fce2de87b
    - https://chatgpt.com/share/9e4d1eac-5b48-4247-a983-9cdf888b7820
    - https://chatgpt.com/share/3b5e04ee-bfbf-4cc5-bd75-bd5fe1b374b4
    - https://chatgpt.com/share/91a53feb-fd8c-4e8e-a7fe-985af39c11eb
    - https://chatgpt.com/share/083b1eb6-e410-44c8-a5f5-c2a5c1d3b3ac
    - https://chatgpt.com/share/cdaab2a0-5cc8-4a26-8076-e7a931e0622c
    - https://chatgpt.com/share/415bdb5d-cc35-46c5-aff9-0b64fcbcec4e
    - https://chatgpt.com/share/aac02249-f0fd-427f-88e5-5b4bea24eff8
    - https://chatgpt.com/share/8d96fae1-985a-4300-b500-74f9ebb8131d
- **Github Copilot:**
    - Hulp bij javascript datepicker, mailsysteem, CSRF tokens en errors debuggen.

### Screenshots
- Login-page


<img width="1440" alt="Screen Shot 2024-06-04 at 17 03 01" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/49122ebc-a637-435d-8c1a-3f94c676c00a">


- Catalogus

  
<img width="1440" alt="Screen Shot 2024-06-04 at 17 04 12" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/4cec8c0f-19e3-4b31-a7e8-28e5d7e8dbfb">


<img width="1440" alt="Screen Shot 2024-06-04 at 17 04 02" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/93019019-3bf2-4772-9f20-ad305b2d0229">


<img width="1440" alt="Screen Shot 2024-06-04 at 17 04 59" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/214eaa59-ca55-4483-a694-11f6a3fa1882">


<img width="1440" alt="Screen Shot 2024-06-04 at 17 05 31" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/44fefdcc-9775-465c-9b5e-229b35e11547">


<img width="1440" alt="Screen Shot 2024-06-04 at 17 05 49" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/ae4df230-1c50-4c59-bbdf-d0238a1ffe14">


<img width="1440" alt="Screen Shot 2024-06-04 at 17 06 14" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/14c48c27-b5a5-4da0-9b31-c61c56563fe4">


- Reserveringen


<img width="1440" alt="Screen Shot 2024-06-04 at 17 07 09" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/439573b8-aad3-4bb9-83b2-097aafbaaebb">


- Infopagina
  

<img width="1440" alt="Screen Shot 2024-06-04 at 17 07 21" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/31cde829-7c02-476e-99d0-34115d21bdbb">


- User
  

<img width="1440" alt="Screen Shot 2024-06-04 at 17 07 30" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/d645198b-ea87-400c-b7be-f8faff23d300">


- Admin Dashboard


<img width="1440" alt="Screen Shot 2024-06-04 at 17 07 51" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/700e08f9-05bb-49b8-9b11-fe4e65f7199f">
  
  
<img width="1440" alt="Screen Shot 2024-06-04 at 17 08 03" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/c2606714-d336-4e34-a7a8-016899a2888b">


- Artikelbeheer


<img width="1440" alt="Screen Shot 2024-06-04 at 17 08 18" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/cb488650-1b81-47d8-a967-a96bb17480dd">
  

<img width="1439" alt="Screen Shot 2024-06-04 at 17 08 28" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/aa690145-045d-4f8e-843c-ae8d162201ea">


- Blacklist


<img width="1440" alt="Screen Shot 2024-06-04 at 17 08 43" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/72caf79f-a3b7-4731-b6e4-5c8337e3dcf0">


- Historiek


<img width="1440" alt="Screen Shot 2024-06-04 at 17 09 04" src="https://github.com/Programmingproject-Groep1/ProgrammingProject_Groep1/assets/145970333/6d34918a-de30-434c-8a72-6521ef55acb2">









