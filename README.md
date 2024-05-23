# Programming Project 2024 Erasmushogeschool Brussel
## Flask Applicatie voor de Uitleendienst van het Medialab
### Introductie
**Als eerstejaars studenten toegepaste informatica hebben we deze applicatie gebouwd die gebruikers toelaat om eenvoudig artikels te reserveren en beheren.**
Deze flask-applicatie heeft als doel om zowel beheerders als studenten/docenten van een duidelijk overzicht te voorzien waar men artikels kan reserveren, ophalen en terugbrengen.

Beheerders hebben de mogelijkheid om te zien wat er voor bepaalde data opgehaald/teruggebracht moet worden, gebruikers hebben de optie om gewenste items aan hun reserveringen toe te
voegen en deze te annuleren/verlengen indien nodig.

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

Hier zul je je Sendgrid API-Key moeten invullen (**Deze is om veiligheidsredenen niet meegegeven in de publieke Git Repository**)

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












