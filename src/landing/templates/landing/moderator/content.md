{% load landing_links %}
{% load landing_tags %}

Version du 15/05/2019.

## Catégories

### Paramédical
	AS, ambu, diét, ergo, psychomot, manip, orthophoniste/ptiste, podo

 * Aide-soigant
 * Diététicien
 * Ergothérapeute
 * Psychomotricien
 * Manipulateur radiologie
 * Orthophoniste
 * Orthoptiste
 * Podologue

### Chirurgien-dentiste	

### Étudiant en médecine
### Sage-femme
### IDE
 * IDE (Infirmier Diplomé d'Etat)
 * IDE/IPA (Infirmier de Pratique Avancée)

### Non pro(fessionnel de santé)

Anciennement: '*Patient*'

N'est pas 1 pro de santé et ne rentre dans aucune autre catégorie.

Si vous avez 1 doute et que vous n'arrivez pas à trouver une catégorie pour l'auteur d'1 question, le mieux est de choisir cette catégorie.

### Pharmacien

### Préparateur en pharmacie
    Préparateur en pharmacie, physicien médical

### Kinésithérapeute

### Médecin

A partir du statut d'interne ou FFI (période entre l'examen ECN et le début de l'internat).

### Spam
Compte faisant la promotion d'1 produit ou d'1 service.

### Collectifs
    ordre, asso, société savante...

Compte collectif représentant un Ordre professionnel, une association de professionnels de santé ou une société savante.

## DM Quick Reply

<div><a href="/static/landing/images/quick-reply.png"><img class="img-fluid" src="/static/landing/images/quick-reply.png" alt="Quick Reply DM"></a></div>

Pour voir apparaître les boutons correspondant aux différents choix, le DM Quick Reply doit être le dernier message dans votre liste de DM. Si le bot vous envoie plusieurs modérations à la suite, il suffit de répondre à la dernière (chronologiquement) puis d'effacer votre réponse (elle est enregistrée par Twitter dès qu'une marque "check" apparaît: vous pouvez l'effacer sans crainte une seconde ou deux après l'avoir envoyée) et les DM du bot jusqu'au DM QuickReply correspondant à la modération précédente. Les boutons apparaitront et vous pourrez modérer.

Remarque: quand vous sélectionnez le bouton "Médecin", votre réponse semble n'être qu'une chaîne de caractères "Médecin". En réalité, dans les coulisses, des métadonnées (notamment une chaîne unique identifiant la modération) est transmise au bot. Si vous écrivez vous même "Médecin", le bot ne saura pas à quelle modération cette réponse est déstinée et ne pourra pas prendre en compte votre réponse. Il est nécessaire de passer par les boutons Quick Reply.

A l'avenir, nous mettrons en place une page sur le site pour chaque modération avec davantage d'informations. Vous aurez le choix de modérer via DM Quick Reply ou via cette page (un lien vers la page sera indiqué dans chaque DM).

## Liens vers 1 recherche Twitter
Des liens vers 1 recherche Twitter sur des mots clefs seront bientôt ajoutés au contenu du DM.

 * médecin
 * patient
 * pharmacien
 * sage-femme
 * kiné
 * IDE

Ils permettront d'avoir rapidement des informations sur la profession du twitto.
Vous pouvez dès maintenant effectuer une recherche parmi tous les tweets passés d'1 compte en entrant par exemple ceci dans la recherche:

```from:@nomducompte médecin```

@nomducompte ici est le login Twitter (exemple: @doctoctocbot). Ce n'est pas le nom de fantaisie (exemple: "#DocTocToc?") qui s'affiche en grands caractères dans le profil.
Souvent un twitto dit lui-même quelle est ou quelle n'est pas sa profession: "je ne suis pas médecin mais (insérer le contenu de la recherche Google)", "je suis kiné", etc.

## Liens sociaux
Nous vous fournissons un graphique qui rend compte de l'analyse du réseau social de l'auteur d'un tweet {% hashtag_lst %}.

### Followers

<div><a href="/static/landing/images/doctoctocbot.jpeg"><img class="img-fluid" src="/static/landing/doctoctocbot.jpeg" alt="followers of @DocTocTocBot"></a></div>

Vous connaitrez le nombre et le pourcentage de followers (abonné·e·s) qui sont des utilisateurs vérifiés, et leur répartition parmi les différentes catégories de professionnels de santé. Ca vous donnera une bonne orientation sur sa profession.

### Friends

Nous fournirons bientôt une analyse comparable pour les abonnements (friends) du compte à modérer.

Notez que les personnes qui suivent beaucoup de médecins mais qui ne sont pas suivies par beaucoup de médecins sont souvent des personnes intéressées par la médecine (ou par les conseils médicaux gratuits) mais ne sont pas forcément des médecins.

## Je passe
Un bouton "Je passe" sera ajouté. Utilisez le pour indiquer que vous ne pensez pas avoir de temps à consacrer à cette modération dans l'heure qui suit. Nous transmettrons à un autre modérateur.

En attendant merci d'écrire "Je passe". Les DM Twitter ont une fonctionnalité anti-spam peu connnue: si votre interlocuteur envoie 5 messages et que vous ne répondez pas, il ne peut plus envoyer de message supplémentaire tant que vous n'avez pas répondu. Il suffit d'envoyer au moins 1 caractère ou 1 emoji au hasard, n'importe lequel, mais il faut 1 réponse, sinon {% bot_screen_name %} ne peut plus vous envoyer de modération et la modération reste en suspens. Merci.

## Pause

### Via DM QuickReply

Nous ajouterons des boutons "Pause" (1 jour, 1 semaine) pour indiquer que vous ne serez pas disponible pendant ce laps de temps.

### Via le site

Disponible dès maintenant dans l'onglet *Modération* de l'espace utilisateur du site, un interrupteur pour suspendre et reprendre la modération collective quand vous le souhaitez. Vous devez vous connecter via Twitter pour vous authentifier et accéder à votre espace utilisateur.

<div><a href="/static/landing/images/moderation-switch.png"><img class="img-fluid" src="/static/landing/images/moderation-switch.png" alt="moderation switch"></a></div>

Dans le futur il sera possible de choisir votre planning de modération à la carte via l'espace utilisateur du site web.

## Doute
En cas de doute, posez votre question dans le DM collectif des modérateurs.

## Urgence
En cas de tweet ou de conversation qui vous semble très problématique, en plus d'en parler sur le DM collectif, merci de prévenir @medecinelibre par DM ou via le formulaire de contact du site. Nous vous fournirons des outils de modération des tweets (annulation d'1 RT) dès que possible.