# Zones de potentiel IRVE en Île-de-France

> Où implanter les prochaines bornes de recharge rapides (≥ 150 kW) ? Ce projet croise open data, SIG réseau et BI pour hiérarchiser les **1 266 communes d'Île-de-France** selon leur potentiel d'accueil d'infrastructures de recharge pour véhicules électriques.

** Projet personnel réalisé en parallèle du Master 2 Géographies numériques (Université Lyon 2, Lyon 3 et Jean Monnet), en lien avec une candidature au CS27 « RGE-D / Renault » — référentiel géospatial et analyse des usages de la mobilité.**

##  La question

La recharge rapide est le maillon critique de l'électrification : un automobiliste sans borne ≥ 150 kW à moins de 15 minutes de chez lui ne passera pas à l'électrique. Ce projet identifie les communes où le besoin est le plus criant, en combinant trois dimensions :

- **la demande** : population et densité (Insee) ;
- **l'éloignement** : temps de trajet routier jusqu'à la borne rapide la plus proche ;
- **l'offre existante** : points de charge pour 1 000 habitants

##  Résultats en un coup d'œil


| Livrable                                                                                | Accès                                                                                         |
| --------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
|  **Carte de synthèse A3** (choroplèthe communale, 5 classes)                         | [`docs/AMC_IRVE.pdf`](docs/AMC_IRVE.pdf)                                                      |
|  **Dashboard interactif** (KPI, filtre département, seuil d'éloignement paramétrable) | [Looker Studio](https://datastudio.google.com/reporting/8da5f0e4-b1c3-4bf1-a26c-6cc4834aef5c) |
|  **Scripts** (acquisition, score composite, export)                                   | [`scripts/`](scripts/)                                                                        |



