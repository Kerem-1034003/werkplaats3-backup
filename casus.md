![alt_text](images/image1.jpg "image_tooltip")


# **Werkplaats 3: Actiontypes**


# **Inhaalopdracht 2023**

Versies

| Versie | Datum | Auteur | Opmerkingen |
| --- | --- | --- | --- |
| 1.0 | 14-09-2023 | Mark Otting | Eerste versie |

# Inleiding

Op de opleiding “software development” zijn de docenten van het vak “persoonlijke vorming” verantwoordelijk voor de teamindeling van het praktijkvak. Een goed team bestaat uit leden met verschillende soorten persoonlijkheden, maar hoe bepaal je die? Daar gebruiken ze de zogenaamde “[action types](https://www.actiontype.nl/actiontype-benadering/)”, ook wel bekend als de “Myers-Briggs persoonlijkheidstypes" . Kort door de bocht deelt deze methode je in op basis van 4 kenmerken, waarbij elk kenmerk aan één van twee keuzes de voorkeur geeft. Met alle verschillende combinaties heb je 16 types in totaal. Om die keuzes te bepalen wordt je een set met stellingen aangeboden. Iedere stelling leunt naar één van de kenmerken. 

Nu gebeurt dat met een zelf gebouwd webformulier, waar de docent vervolgens met de hand alsnog de action types moet uitrekenen. Dat kan natuurlijk handiger - en dat is dan ook precies wat wij gaan maken in deze opdracht. 


## Vereisten

We verwachten dat voordat je aan deze opdracht begint je tenminste basale kennis hebt van de volgende technische zaken:  



* De python “Flask” module
* REST API ontwerp
* Javascript / jQuery en AJAX 
* Database ontwerp en bewerking


# Case

We willen in deze opdracht een webapplicatie die een lijst met stellingen aan biedt en aan de hand van de antwoorden het “action type” van de geïnterviewde student bepaald. Daarnaast kan de docent via een overzicht zien welke studenten bij welk type horen en ze zo indelen in klas en team. 

De action types web applicatie bevat een aantal onderdelen: 
* Een frontend waarin een student zijn studentnummer opgeeft. Vervolgens moet de student uit twee stellingen kiezen - en dat 20x herhalen. Om het ophalen van deze stellingen snel te houden willen we hier gebruik maken van **javascript** om met het **AJAX** patroon na ieder antwoord de volgende stelling op te halen. 
* De vragen willen we aanbieden via een REST API. We zijn namelijk van plan om later een mobiele app op de telefoon aan te bieden om deze vragen mee te maken. 
* CRUD pagina’s voor de docent om nieuwe studentnummers op te voeren, te zien welke er al zijn ingevuld en daar vervolgens een klas en/of team aan toe te voegen. De antwoorden, de studenten en de stellingen willen we opslaan in een SQL gebaseerde database. Je zult hier zelf een ontwerp voor moeten maken met tabellen voor de **studentnummers**, **stellingen** en **gegeven antwoorden**. 
* Je krijgt JSON bestanden met daarin alle stellingen en een initiëel set studenten, deze willen we met een python script kunnen inladen in de database.  


## Requirements


### Frontend

Er is geen login nodig, maar er zijn wel een paar uitgangspunten om de privacy van studenten te bewaken: 


* Er wordt eerst gevraagd om een studentnummer. 
* Als het studentnummer niet bekend is wordt dat in een melding getoond. 
* Als er voor deze student al een compleet ingevulde lijst is wordt er een melding getoond dat opnieuw invullen (of opvragen van een action type) niet mogelijk is. 
* Als er nog geen compleet ingevulde lijst met stellingen is, wordt de naam van de student, de klas en de eerstvolgende stelling getoond. Dat zal meestal stelling 1 zijn!

![WP3 - Actiontypes stelling.png](images%2FWP3%20-%20Actiontypes%20stelling.png)

<sup>Dit is een voorbeeld van hoe de stellingen eruit zouden kunnen zien. Het staat je geheel vrij om een ander ontwerp te kiezen.</sup>


Bij iedere stelling dient de student één van twee stellingen te kiezen. Na de keuze wordt dit antwoord meteen opgeslagen (via javascript) en wordt de volgende stelling getoond, of, als er geen stellingen meer zijn, wordt de lijst afgesloten en de student bedankt. 

Je hebt nu alle gegevens om het “action type” van een student te bepalen. De berekening is simpel. Iedere stelling verwijst naar één van twee gekozen kenmerken en er zijn een oneven aantal stellingen per kenmerk. Tel het aantal keer dat een kenmerk is gekozen en je hebt het resultaat. Voeg de vier kenmerken bij elkaar en je hebt het “actiontype”. 

Een rekenvoorbeeld: stel dat we 20 vragen hebben, dat zijn er 5 per kenmerk. Stel dat de student bij de “Extravert of Intravert” stellingen 3x voor de stelling koos die “introvert” vertegenwoordigt en 2x voor de stelling die “extrovert” aangeeft. Het eerste kenmerk is dan “introvert”, ofwel de I. 

Let op, op geen manier mag een student het actiontype van andere studenten kunnen inzien!


### REST API

Om de stellingen op te halen willen we een REST gebaseerde API aanbieden. Zo kunnen we in de toekomst ook een mobiele app of andere applicatie aansluiten. Deze API zal maar twee URLs hebben, genoeg om de stellingen op te halen en op te slaan. 

|  | Stelling ophalen                                                                                                          | Stelling opslaan                                                                                            | 
| --- |---------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| **Method** | GET                                                                                                                       | POST                                                                                                        |
| **Omschrijving** | Geeft de eerstvolgende ongekozen stelling terug voor deze student, of een foutmelding als er geen stellingen (meer) zijn. | Verwacht in de body van het verzoek een stelling keuze. Slaat deze op en stuurt een {“result”: “ok”} terug. |
| **URL** | /api/student/<student_number>/statement                                                                                   | /api/student/<student_number>/statement/<statement_number>                                              |
| **Body** | -                                                                                                                         | { “statement_choice”: 1 }                                                                                   |
| **Response** | (zie onder)                                                                                                               | { “result”: “ok” }                                                                                          |

De response op verzoeken naar het "Stelling ophalen" endpoint: 
```json
{
   "statement_number":1,
   "statement_choices":[
      {
         "choice_number":1,
         "choice_text":"Stelling 1"
      },
      {
         "choice_number":2,
         "choice_text":"Stelling 2"
      }
   ]
}
```
In het repository is ook een OpenAPI bestand meegegeven (“openapi.yaml”). Dit bestand is een referentie en beschrijft de requests en responses. Je hoeft dit bestand niet te gebruiken, maar je zou het in bijvoorbeeld Postman kunnen importeren om de API te testen. 


### Beheer

Voor de docent maken we een aantal pagina’s om beheer op de studenten en resultaten te kunnen uitvoeren. Deze pagina's mogen alleen toegankelijk zijn voor docenten, dus afgesloten met een usernaam / wachtwoord combinatie. 

Op deze pagina’s: 
* Kun je een nieuw studentnummer toevoegen, met daarbij de naam van de student en de klas.
* Een docent kan een "admin" zijn. In dat geval mag deze nieuwe docenten toevoegen (en verwijderen) met een naam, gebruikersnaam en wachtwoord en via een vink of de nieuwe docent ook "admin" rechten heeft.
* Krijg je een overzicht met alle studentnummers. Per studentnummer: 
    * Zie je het bijbehorende “actiontype”, indien ingevuld.
    * Zie je de datum waarop de student de antwoorden heeft gegeven. Neem hier de datum van de laatste keer dat een student een stelling heeft beantwoord. 
    * Kun je het studentnummer (en alle gegeven antwoorden) verwijderen. Het studentnummer is dan weer bruikbaar om opnieuw de stellingen te beoordelen. 
    * Kun je de details van een studentnummer bekijken. 
* Het detailscherm van een student bevat de studentgegevens en de stellingen die deze student heeft gekozen. Hier kun je een team selecten voor deze student. Indien de student al een team heeft wordt weergegeven wie de student aan het team heeft toegevoegd.
* Vanuit het detailscherm moet de gebruiker een "wijzigbaar" scherm kunnen openen. Buiten aanpassen van de gegevens en klas van de student kan hier ook een ander team worden geselecteerd. 
 
    
![WP3 - Actiontypes.png](images%2FWP3%20-%20Actiontypes.png)

<sup>Dit is een voorbeeld van hoe de beheerpagina eruit zou kunnen zien. Het staat je geheel vrij om een ander ontwerp te kiezen.</sup> 

* Kun je de lijst met studentnummers filteren op klas en op teamnaam. 

* Optioneel: het zou ook wenselijk zijn om deze resultaten in een Excel bestand of CSV te kunnen exporteren. Je zou een export knop onder een (gefilterde) lijst kunnen toevoegen. Als we daarop drukken willen we dat er een CSV bestand wordt gedownload met daarin alle informatie bij de studentnummers: studentnummer, naam, actiontype, datum, klas en team.

### Database

We leveren een voorbeeld JSON bestand met 20 stellingen en bijbehorende antwoorden. Daarnaast is er een json bestand met de initiële lijst met studenten. We willen graag dat je een python script maakt dat deze gegevens in de database importeert. 

Optioneel: indien mogelijk zouden we graag later nieuwe versies van deze bestanden importeren. We willen de bestaande stellingen wel bewaren, zodat we per student kunnen zien welke stellingen deze heeft gekozen. Studenten die niet in een nieuwere lijst staan mogen worden verwijderd (inclusief hun antwoorden). 


## Technische eisen



* We verwachten dat de pagina’s gestyled zijn. Dit heeft een lagere prioriteit dan de werking van het systeem en het vervullen van de requirements. 
* We verwachten een back-end in python met Flask of een alternatief python web framework. Zowel de webpagina’s als de APIs worden via het framework aangeboden. Als data opslag raden we SQLite aan, maar een andere database variant is ook toegestaan. De code moet voldoen aan de eisen zoals in de introductie is uitgelegd (MVC, PEP8, etcetera).
* De lijst met stellingen moet gebruikmaken van het AJAX patroon om nieuwe stellingen op te halen en antwoorden per student op te slaan. Je mag AJAX ook toepassen op andere plaatsen zoals de beheerpagina's.  


## Oplevering

Als oplevering verwachten we de volgende zaken, vóór de inleverdatum:



* Een commit in het repository van de opdracht getagd met een “v1.0” release. Als je voor de einddatum inlevert mag je je werk nog herstellen met een nieuwe tag met goedkeuring van de docent.


# Beoordeling

Voor de beoordeling volgen we de regels zoals die in de modulehandleiding staan. Kort samengevat komt dat op het volgende neer: 



* We verwachten een investering qua tijd en moeite in je code terug te zien. Daarbij moet je gebruik maken van alle technologie genoemd onder “oplevering”. 

* Deze inhaalopdracht is beperkt qua requirements. We verwachten daarom de hele applicatie (frontend en backend) te zien voor een beoordeling met een “voldoende”. 

* De code voldoet aan de standaarden zoals uitgelegd in de WP1 en WP2 presentaties: de naamgeving in de code is in het Engels, de code uitgelijnd volgens de PEP8 standaard, et cetera. Code van het backend moet in MVC stijl gesplitst zijn. 

* We beoordelen een werkend product met een “voldoende”. We beoordelen met een “goed” als alle requirements zijn ingevuld en de code begrip van javascript en REST laat zien. Een “uitstekend” wordt gegeven als je buiten voorstaande ook extra zaken oplevert die niet in de opdrachtomschrijving staan. Denk daarbij aan een login voor de docenten of de mogelijkheid om door de applicatie de teams te laten samenstellen. 

Bij vragen over of onduidelijkheden in de requirements, neem contact op. Ook als je technisch vast komt te zitten geef het aan, we helpen je graag verder!
