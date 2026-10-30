# Ma revue quotidienne

Flux RSS public de cinq articles sélectionnés quotidiennement par IA, avec résumés en français.

## Activation

1. Créer un secret GitHub Actions nommé `OPENAI_API_KEY` dans **Settings → Secrets and variables → Actions**. Ne jamais publier la clé dans un fichier.
2. Dans **Settings → Pages**, sélectionner **Deploy from a branch**, branche **main**, dossier **/docs**, puis enregistrer.
3. Lancer une première exécution via **Actions → Revue quotidienne → Run workflow**.
4. Ajouter l'URL `https://tesorus.github.io/daily-curiosity-feed/feed.xml` dans le widget RSS de Start.me.

La planification vise **5 h Europe/Paris** (GitHub Actions peut démarrer avec du retard). Le coût de l'API OpenAI est indépendant de l'abonnement ChatGPT. En cas d'erreur, le dernier flux généré reste en place.

Les résumés sont rédigés à partir des titres et métadonnées RSS, sans garantie d'accès au contenu complet. Aucune donnée personnelle n'est utilisée ou publiée.
