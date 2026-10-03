import geopandas as gpd
import pyogrio
import pandas as pd

# ── 0. Paramètres & lecture ─────────────────────────────────────────
GDB    = r"C:/Users/Benjamin/Documents/ArcGIS/Projects/Stage_Renault/Stage_Renault.gdb"
COUCHE = "commune_access_v2"        # ← "communes_access_v2" si vous avez refait la jointure

# print(pyogrio.list_layers(GDB))  # décommentez pour vérifier les noms de couches

df = gpd.read_file(GDB, layer=COUCHE)
print(df.columns.tolist())

# ── 0bis. Champ temps : on harmonise le nom (jointures Pro = noms fluctuants) ──
if "Total_temps" not in df.columns and "Total_Minutes" in df.columns:
    df = df.rename(columns={"Total_Minutes": "Total_temps"})
assert "Total_temps" in df.columns, "champ temps introuvable — voir df.columns ci-dessus"

# ── 1. Population : jointure si elle manque ─────────────────────────
if "population" not in df.columns:
    fond = gpd.read_file("communes_idf.geojson")
    df = df.merge(fond[["code", "population"]], on="code", how="left")
    assert df["population"].isna().sum() == 0, "des communes sans population !"

# ── 1bis. nb_irve : jointure depuis votre couche IRVE par commune ────
if "nb_irve" not in df.columns:
    df_irve = gpd.read_file(GDB, layer="irve_par_commu_JSONToFeature")
    print(df_irve.columns.tolist())                     # vérifiez le nom de la clé : "code" ?
    df = df.merge(
        df_irve[["code", "nb_irve"]].drop_duplicates("code"),
        on="code", how="left",
    )
    assert len(df) == 1266, f"la fusion a créé des doublons : {len(df)} lignes !"
    df["nb_irve"] = df["nb_irve"].fillna(0)             # commune absente = 0 borne

# ── 2bis. Communes valides / non calculées ──────────────────────────
mask  = df["Total_temps"].isna()
valid = ~mask
print(f"Communes valides : {valid.sum()}, non calculées : {mask.sum()}")

# ── 3. Densité — surface calculée en Lambert-93, quel que soit le CRS ──
if "dens_pop" not in df.columns:
    area_km2 = df.geometry.to_crs(2154).area / 1e6       # km², projection légale France
    df["dens_pop"] = df["population"] / area_km2

# ── 4. Équipement relatif : PDC pour 1 000 habitants ─────────────────
df["pdc_1000hab"] = (df["nb_irve"] / df["population"] * 1000).fillna(0)

# ── 5. Score composite — uniquement sur les communes valides ─────────
r_pop   = df["dens_pop"].rank(pct=True)
r_temps = df["Total_temps"].rank(pct=True)
r_equip = df["pdc_1000hab"].rank(pct=True)

df.loc[valid, "score_potentiel"] = (
    (r_pop + r_temps + (1 - r_equip)) / 3 * 100
).round(1)[valid]

# ── 5bis. Classe cartographique : 5 quintiles + « Non calculé » ──────
df["classe_potentiel"] = pd.qcut(
    df.loc[valid, "score_potentiel"], 5,
    labels=["Très faible", "Faible", "Moyen", "Fort", "Très fort"],
)
df["classe_potentiel"] = df["classe_potentiel"].astype(object)
df.loc[mask, "classe_potentiel"] = "Non calculé"

# ── 6. Contrôles ─────────────────────────────────────────────────────
print(df["classe_potentiel"].value_counts())
print(df.loc[valid, "score_potentiel"].describe())
print(df.nlargest(10, "score_potentiel")[["code", "score_potentiel"]])

# ── 7. Export en GPKG ────────────────────────────────────────────────
df.to_file("communes_score.gpkg", driver="GPKG")