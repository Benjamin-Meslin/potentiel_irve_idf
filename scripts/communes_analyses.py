import geopandas as gpd

df = gpd.read_file("communes_score.gpkg")

# colonne département (pour les filtres du dashboard) — dérivée du code INSEE
df["departement"] = df["code"].str[:2]

# centroïde en WGS84 → colonnes lat/lon pour une carte à points dans Looker
pts = df.geometry.to_crs(4326).representative_point()   # point garanti DANS la commune
df["lon"] = pts.x.round(5)
df["lat"] = pts.y.round(5)

assert df["population"].isna().sum() == 0, "des communes sans population !"
df["population"] = df["population"].round().astype("int64")

# même soin pour nb_irve si besoin (souvent float après le fillna) :
df["nb_irve"] = df["nb_irve"].round().astype("int64")
# export SANS géométrie — c'est ça qui part dans BigQuery
df.drop(columns="geometry").to_csv("communes_analyse.csv", index=False)

# option : les bornes rapides (même principe, depuis votre gdb ou votre CSV d'origine)
# b = gpd.read_file(GDB, layer="irve_idf_rapides")
# b.drop(columns="geometry").to_csv("bornes_rapides.csv", index=False)