# Season Review 2025 — U8

## Résumé chiffré

- Matches analysés: **12**
- Victoires: **10**, Nuls: **0**, Défaites: **2**
- Buts pour: **139** (11.6 / match)
- Buts contre: **59** (4.9 / match)
- Tirs pour: **246** (20.5 / match)
- Tirs contre: **106** (8.8 / match)
## Top buteurs

| Rang | Joueur | Buts | Tirs | Efficacité |
|---:|---|---:|---:|---:|
| 1 | Nestor | 46 | 71 | 64.8% |
| 2 | Maxence Jonckheere | 27 | 36 | 75.0% |
| 3 | Tiago | 18 | 22 | 81.8% |
| 4 | Auguste Robinet | 17 | 28 | 60.7% |
| 5 | Nathan | 12 | 17 | 70.6% |
| 6 | Lilou | 10 | 19 | 52.6% |
| 7 | Hugo | 5 | 10 | 50.0% |
| 8 | Robin | 4 | 4 | 100.0% |

## Par match (synthèse)

| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |
|---|---:|---:|---:|
| 2025-08-30 | 12 - 1 | 24 | 5 |
| 2025-09-06 | 16 - 3 | 28 | 6 |
| 2025-09-13 | 12 - 5 | 27 | 12 |
| 2025-09-17 | 4 - 11 | 6 | 17 |
| 2025-09-27 | 19 - 4 | 33 | 7 |
| 2025-10-08 | 8 - 6 | 13 | 9 |
| 2025-10-11 | 25 - 0 | 43 | 1 |
| 2025-10-16 | 7 - 3 | 11 | 6 |
| 2025-10-18 | 7 - 5 | 7 | 5 |
| 2025-11-01 | 12 - 4 | 21 | 5 |
| 2025-11-08 | 16 - 3 | 29 | 8 |
| 2025-11-19 | 1 - 14 | 4 | 25 |
## Observations & Recommandations

- Synthèse principale : l'équipe produit beaucoup d'occasions et convertit un grand nombre d'entre elles (moyenne de tirs élevée et buteur principal performant). L'effort doit être concentré sur la stabilité défensive et la gestion des phases de transition.
- Offensif : consolider la diversité offensive — travailler les combinaisons courtes dans les 18m et encourager des permutations de position pour éviter de dépendre d'un seul point d'appui. Maintenir les exercices de finition qui portent leurs fruits.
- Défensif : mettre en place des repères simples de replacement (points de référence pour les joueurs), travailler la réactivité après perte de balle et organiser des mini-séances sur les duels et les replis.
- Gestion du groupe : attention aux phases d'entrée de match (quelques buts encaissés tôt sur certains matchs). Instaurer une routine d'activation pré-match et un micro-briefing collectif à la mi-temps quand l'équipe est menée.
- Individuel : valoriser la polyvalence constatée (Nestor, Maxence, Tiago, Auguste) en proposant des rotations planifiées pour conserver de l'énergie et multiplier les solutions.
- Données & suivi : utiliser la table `Par match` comme source de vérité pour les totaux ; pour les attributions individuelles, privilégier les JSON `YYYY-MM-DD.json` quand ils contiennent `players_present` et `events`.

## Caveats

- Sources hétérogènes : les chiffres proviennent de deux sources différentes : les fichiers Markdown `YYYY-MM-DD.md` (totaux d'équipe) et les JSON `YYYY-MM-DD.json` (attributions individuelles). J'ai appliqué une logique hybride (MD pour les totaux, JSON pour les joueurs) — vérifiez si vous préférez une seule source prioritaire.
- Tirs manquants : certains JSON ne contiennent pas le champ `shots`; j'ai backfillé les tirs depuis les JSON disponibles et le tableau `Par match`. Les lignes où `shots` manquaient ont été laissées à 0 avant le backfill — demandez si vous voulez un signalement détaillé des matchs manquants.
- Attributions incomplètes : si un événement dans un JSON a `player: null`, l'événement reste non attribué ; je n'ai pas deviné d'attribution. Pour améliorer les attributions, fournissez des orthographes stables dans `completed-tasks/roster/U8.md`.
- Canonicalisation des noms : j'ai appliqué une normalisation automatique à partir du roster local — certaines correspondances heuristiques peuvent être imparfaites ; je peux fournir la table d'appariement (observé → canonique) pour vérification.
- Changements manuels : vous avez demandé une correction manuelle (ex. `2025-11-19` : `Tirs Eux = 25`) — such overrides are kept as-is and may differ from original JSONs.
- Reproductibilité : tous les scripts sont dans `tools/` (ex: `aggregate_matches.py`, `update_shots_md.py`, `regenerate_season_review.py`). Relancer ces scripts reproduit le processus et mettra à jour les fichiers si de nouvelles données arrivent.


## Répartition par niveau d'adversaire

### Adversaire faible

- Matchs: **5**
- Buts pour: **84**
- Buts contre: **12**
- Tirs pour: **149**
- Tirs contre: **24**

| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |
|---|---:|---:|---:|
| 2025-08-30 | 12 - 1 | 24 | 5 |
| 2025-09-06 | 16 - 3 | 28 | 6 |
| 2025-09-27 | 19 - 4 | 33 | 7 |
| 2025-10-11 | 25 - 0 | 43 | 1 |
| 2025-11-01 | 12 - 4 | 21 | 5 |


### Adversaire moyen

- Matchs: **4**
- Buts pour: **42**
- Buts contre: **16**
- Tirs pour: **74**
- Tirs contre: **31**

| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |
|---|---:|---:|---:|
| 2025-09-13 | 12 - 5 | 27 | 12 |
| 2025-11-08 | 16 - 3 | 29 | 8 |
| 2025-10-16 | 7 - 3 | 11 | 6 |
| 2025-10-18 | 7 - 5 | 7 | 5 |


### Adversaire fort

- Matchs: **3**
- Buts pour: **13**
- Buts contre: **31**
- Tirs pour: **23**
- Tirs contre: **51**

| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |
|---|---:|---:|---:|
| 2025-09-17 | 4 - 11 | 6 | 17 |
| 2025-10-08 | 8 - 6 | 13 | 9 |
| 2025-11-19 | 1 - 14 | 4 | 25 |

