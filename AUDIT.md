# ProviderKit — suivi de l’audit

**Mis à jour le 19 novembre 2026.** Ce document ne liste que les actions restantes. Les correctifs P1–P3 déjà validés localement ont été retirés de la liste de travail.

**Point de départ vérifié :** Python 3.12, 50 tests côté cœur et 8 côté Django 5.2.17 ; Ruff (lint et formatage) et Xenon au seuil B passent. Avant le dernier test de régression, la couverture du cœur était de 63 % des instructions. La matrice GitHub Actions complète reste à valider sur une PR.

## Lot 1 — Sécuriser la publication

Inspiré du contrôle de version et des tests avant publication de `django-boosted`, et de la vérification d’installation non éditable de `django-importexport-flow`.

- [ ] **Vérifier le tag et tester le commit à publier.** Le [workflow de publication](.github/workflows/release.yml#L9-L58) construit et vérifie les distributions, mais ne relance pas les tests du commit tagué. Comparer le tag à la version des deux distributions ([cœur](python-providerkit/pyproject.toml#L5-L10), [Django](django-providerkit/pyproject.toml#L5-L13)) avec une comparaison PEP 440, après retrait du préfixe `v`. Valider au minimum un tag stable, un tag RC et un tag incohérent. Lancer les deux suites sur le commit tagué et bloquer la publication si l’un des contrôles échoue. Préserver la destination actuelle : RC vers TestPyPI, versions stables vers PyPI.
- [ ] **Installer les deux wheels construits, ensemble et hors du checkout.** Le [build CI](.github/workflows/ci.yml#L179-L223) vérifie déjà la licence. Ajouter un test d’installation dans un environnement vierge, sans mode éditable ni `PYTHONPATH` vers les sources. Exécuter `pip check`, vérifier `providerkit version` et lancer un contrôle Django minimal avec les modules installés. En release, tester les mêmes artefacts que ceux transmis à la publication, sans les reconstruire après validation. Conserver les attestations et le contrôle de licence ; réutiliser ce dernier en release si possible.
- [ ] **Ouvrir une PR et attendre la CI complète.** Inclure les nouveaux tests, le profil Ruff et la licence du cœur s’ils sont encore non suivis. Vérifier la matrice Python 3.11–3.12 et Django 5.2 (plancher et dernier correctif). Aucun tag ni publication pour valider la PR ; tester les cas du contrôle de version localement ou via un mode sans publication.

**Critère de clôture :** une version incohérente, des tests en échec ou un wheel non installable empêchent la publication ; les deux wheels validés sont ceux utilisés par le job de publication.

## Lot 2 — Ajouter des garde-fous CI

- [ ] **Couverture des branches et Xenon.** Comme dans `django-importexport-flow`, publier un rapport de couverture des branches pour les deux paquets sur une seule configuration Python, d’abord sans seuil bloquant. Ajouter Xenon sur les deux répertoires source avec les seuils déjà vérifiés localement : maximum B par bloc et module, moyenne A. Garder [le job Ruff existant](.github/workflows/ci.yml#L71-L92) ; si les jobs de qualité doivent conditionner un autre job, déclarer explicitement la dépendance correspondante.
- [ ] **Bandit sur les sources et audit de toutes les dépendances résolues.** `django-boosted` et `django-importexport-flow` font les deux. Compléter, sans remplacer, [l’audit ciblé du plancher et du dernier Django 5.2](.github/workflows/ci.yml#L94-L153). Scanner les dépendances tierces des deux paquets dans un environnement séparé des outils d’audit. Pour Bandit, commencer par les sources au niveau de sévérité moyen ou supérieur ; documenter les exceptions au cas par cas, sans ignorer des familles entières de règles.
- [ ] **Durcir les références des actions de publication.** Épingler les actions de publication et d’attestation à des SHA vérifiés et prévoir leur mise à jour automatique. Conserver les permissions OIDC actuelles et ne pas ajouter de secret PyPI statique.

CodeQL existe chez `django-importexport-flow`, mais n’est pas requis pour ce lot. Ne pas rendre MyPy ou Vulture bloquants tant que les résultats liés aux champs Django dynamiques, aux réexports et à la découverte de fournisseurs n’ont pas été triés.

## Autres points ouverts

- [ ] **Tests du cœur :** cibler l’[exécution des fournisseurs](python-providerkit/src/providerkit/providers/base/execute.py) et le [filtrage](python-providerkit/src/providerkit/providers/base/filter.py), notamment les chemins vides et les erreurs. Mesurer la couverture après ajout des tests avant de fixer un seuil.
- [ ] **Démarrage Django :** revérifier l’import automatique par le shell des [modèles générés](django-providerkit/src/django_providerkit/models/__init__.py). L’audit initial a signalé sept modèles non importés automatiquement sous Django 5.2.19 ; ce point est distinct de `manage.py check`.
- [ ] **Erreurs silencieuses :** revoir les exceptions ignorées dans les [champs Django](django-providerkit/src/django_providerkit/fields.py). Ne limiter les exceptions interceptées que si des tests décrivent les cas attendus.
- [ ] **Métadonnées PyPI :** corriger les URL Documentation du [cœur](python-providerkit/pyproject.toml#L50-L54) et de [Django](django-providerkit/pyproject.toml#L49-L54) pour qu’elles pointent chacune vers le bon sous-projet.

Les deux clones jscpd restant côté Django (filtres/admin et managers) ne bloquent pas la PR. Ne les factoriser que si leur comportement doit réellement évoluer ensemble.