{% load landing_links %}
{% load landing_tags %}
{% load moderator %}

## Pourquoi modérer?
La communauté {% hashtag_lst %} est composée de professionnels de santé qui souhaitent s'entraider en se posant des questions. Parmi ces professionnels, une immense majorité ne souhaite pas répondre aux demandes de conseils médicaux en provenance de non professionnels de santé et ne souhaite pas lire de tweets promotionnels ou publicitaires utilisant le hashtag {% hashtag_lst %} ou répondant à 1 thread initié par une question {% hashtag_lst %}.
Un des objectifs du projet {% bot_screen_name %} est de filtrer ces messages hors-sujet ou indésirables.

## Qu'est-ce qui fait l'objet d'une modération?
Les modérateurs de {% bot_screen_name %} modère les comptes Twitter, pas le contenu du message. Nous faisons confiance aux professionnels que nous retweetons pour suivre nos [suggestions d'utilisation du hashtag][guidelines] pour leur plus grand bénéfice et celui de toute la communauté.

## Quels comptes font l'objet d'une modération?
Seuls les comptes qui suivent {% bot_screen_name %} peuvent faire l'objet d'une modération puis être retweetés s'ils exercent une des professions admises. Ainsi, nous respectons mieux le choix des twittos: celles et ceux qui souhaitent être retweetés par le bot suivent le bot et nous laissons les autres tranquilles. Nous pourrons mieux communiquer nos recommandations en envoyant un DM avec un lien vers les [recommandations de bonne pratique][guidelines] à chaque nouveau follower.

## Quels sont les règles suivies pour la modération?
Les règles sont décidées collectivement par l'équipe des modérateurs. Voir nos [recommandations][guidelines] de bonne pratique et les [règles][rules] du bot.

## Comment se déroule la modération?

La modération est effectuée collectivement par une équipe de modérateurs bénévoles, tous professionnels de santé.
Un logiciel libre et open source a été spécifiquement développé pour la modération par @medecinelibre. Le bot détecte 1 question {% hashtag_lst %} envoyée par un utilisateur de Twitter qui n'a jamais été modéré. Il envoie un DM spécial (QuickReply) à 1 modérateur disponible. Le modérateur tente de déterminer si l'utilisateur est un professionnel de santé et si sa profession fait partie de celles qui sont retweetées par le bot. Le modérateur répond au DM en cliquant sur le bouton correspondant à sa modération. Le bot détecte la réponse et, en fonction des règles en vigueur, retweete ou pas le tweet initial.

## Puis-je vous aider à modérer les questions {% hashtag_lst %}?
Oui! Volontiers! Si vous êtes {% membership_category_or %}, et que avez pris part à des conversations {% hashtag_lst %} depuis quelques mois, vous pouvez rejoindre l'équipe de modération. Il suffit de suivre {% bot_screen_name %} et de lui envoyer 1 DM indiquant "Je souhaite participer à la modération collective". Il est possible de faire une pause à tout moment et de reprendre la modération quand vous le souhaitez. Si vous avez un peu l'habitude de Twitter et des conversations {% hashtag_lst %}, ça reste simple et rapide. Nous sommes {% moderator_count %} et il y a rarement plus de 3 ou 4 modérations par jour. La "charge de travail de modération" est donc plutôt légère.


[guidelines]: /guidelines/ "Recommandations de bonnes pratiques"
[rules]: /rules/ "Règles du bot"