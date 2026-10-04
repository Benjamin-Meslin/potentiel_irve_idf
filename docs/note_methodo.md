# 📐 Note méthodologique — Zones de potentiel IRVE en Île-de-France

**Millésime des données IRVE : extraction du 28/09/2026** · Benjamin Meslin · version 1.0

Cette note documente la chaîne de traitement, les choix méthodologiques et les contrôles qualité du projet. Elle accompagne le [README](../README.md) du dépôt.

## 1. Objectif et périmètre

Hiérarchiser les **1 266 communes d'Île-de-France** selon leur potentiel d'accueil de bornes de recharge rapides (**puissance ≥ 150 kW**), en croisant demande (population), offre existante (points de charge) et éloignement (temps de trajet routier à la borne la plus proche).

## 2. Sources et millésimes

| Source | Producteur | Version / date | Usage |
| --- | --- | --- | --- |
| Base IRVE consolidée (schéma statique v2.3.1) | Etalab / data.gouv.fr | **extraction du 28/09/2026** | localisation et puissance des points de charge |
| API Géo (communes, population, contours) | Insee / IGN | appel du **28/09/2026** | fond communal, population, densités |
| BD TOPO® (réseau routier) | IGN | édition du **15/06/2026** | jeu de données réseau pour l'analyse d'accessibilité |

⚠️ La base IRVE est **actualisée en continu** : tout comptage de points de charge n'a de sens que rapporté à sa date d'extraction. Ce millésime est indiqué dans le dashboard interactif.

## 3. Chaîne de traitement

**Étape 1 — Acquisition et préparation** (`scripts/main.py`, Python / pandas / GeoPandas)

- Téléchargement de la base IRVE consolidée et du fond communal via l'API Géo ;
- Filtre sur la puissance : ne sont retenues que les bornes **≥ 150 kW** ;
- Jointures spatiales (points dans les polygones) : nombre de points de charge par commune, densités, équipement pour 1 000 habitants.

**Étape 2 — Accessibilité routière** (ArcGIS Pro, jeu de données réseau)

- Construction du jeu de données réseau sur le réseau routier de la **BD TOPO® (IGN)** ;
- Analyse **Closest Facility** : pour chaque commune (point de départ), temps de trajet routier jusqu'à la borne rapide la plus proche ;
- Le temps de trajet par commune (`Total_temps`) est rattaché à la table communale par jointure spatiale sur les points de départ des itinéraires.

**Étape 3 — Score composite** (`scripts/score_composite.py`)

```
score = ( rang(densité) + rang(temps de trajet) + (1 − rang(équipement)) ) / 3 × 100
```

- Chaque dimension est transformée en **rang percentile** : le score est insensible aux unités et robuste aux valeurs extrêmes — décisif face aux hubs (voir § 5) ;
- Discrétisation en **5 classes** par la méthode de **Jenks** (ruptures naturelles) pour la carte de synthèse A3 : les classes suivent les discontinuités de la distribution du score plutôt que des effectifs équilibrés.

**Étape 4 — Diffusion** (`scripts/communes_analyses.py`)

- Export CSV chargé dans **BigQuery**, dashboard **Looker Studio** (KPI, filtre département, seuil d'éloignement paramétrable) ;
- Carte de synthèse A3 mise en page dans ArcGIS Pro (`docs/AMC_IRVE.pdf`).

## 4. Contrôles qualité

- **Effectifs à chaque étape** : chaque script vérifie par `assert` que la chaîne manipule bien **1 266 communes** — jointures spatiales, appariement des itinéraires et exports peuvent perdre ou dupliquer des entités en silence, ce qui fausserait tous les KPI en aval ;
- Les communes sans itinéraire calculable sont **étiquetées « Non calculé »** plutôt que supprimées : elles restent visibles dans les livrables.

## 5. Points de vigilance documentés

1. **Dater son extraction** — la base IRVE évolue en continu ; le millésime (28/09/2026) est affiché dans le dashboard.
2. **L'effet hub** — Coupvray (3 066 habitants) concentre **518 points de charge** (~170 pour 1 000 habitants, record régional, porté par l'A4 et les parkings de Disneyland Paris). Un tel hub écrase toute moyenne brute : c'est le raison d'être des scores par rangs percentiles.
3. **Compter à chaque étape** — les `assert` d'effectifs protègent chaque maillon de la chaîne.

## 6. Limites

- Le **temps de trajet** est un temps théorique (réseau, sans trafic réel) : proxy d'accessibilité, pas de mesure de terrain ;
- La **puissance** retenue est la puissance installée, sans information de disponibilité réelle des bornes ;
- Les données IRVE sont **déclaratives** (fiabilité dépendante des opérateurs) ;
- Le score agrège trois dimensions d'importance égale : une pondération différente peut être testée dans `scripts/score_composite.py` ;
- Périmètre communal : les hétérogénéités intra-urbaines (besoins de quartier) ne sont pas visibles.

## 7. Reproduire

```bash
pip install -r requirements.txt
python scripts/main.py              # acquisition IRVE + communes, jointures, densités
# … analyse réseau dans ArcGIS Pro (Closest Facility, bornes ≥ 150 kW) …
python scripts/score_composite.py   # score + classes
python scripts/communes_analyses.py # export CSV pour BigQuery
```

Les données sources sont publiques (licences : Etalab v2, licences ouvertes Insee/IGN). Ce projet est sous licence MIT.