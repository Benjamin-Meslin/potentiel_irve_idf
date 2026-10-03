import pandas as pd
import geopandas as gpd
import requests

df_irve = pd.read_csv('IRVE.csv')


df_irve[['lon', 'lat']] = df_irve['coordonneesXY'].str.strip("[], ").str.split(",", expand = True).astype(float)
print (df_irve.head())

df_irve_filtre = df_irve[(df_irve['puissance_nominale']>0)]

gdf_irve = gpd.GeoDataFrame(df_irve_filtre, 
                                geometry=gpd.points_from_xy(
                                    x=df_irve_filtre['lon'],
                                    y=df_irve_filtre['lat']),
                                crs='EPSG:4326')
gdf_irve.info()

gdf_irve= gdf_irve.to_crs("EPSG:2154")

gdf_irve.to_file('irve.gpkg')



reponse = requests.get("https://geo.api.gouv.fr/departements").json()
departements = []
for d in reponse:
    departements.append(d["code"])


# url_communes = "https://geo.api.gouv.fr/departements/{}/communes?fields=code,population&format=geojson&geometry=contour"

# communes = pd.concat(
#     [gpd.read_file(url_communes.format(code)) for code in departements],
#     ignore_index=True
# )
# print(len(communes), "communes")                 
# print(communes["population"].isna().sum())      
# print(communes.crs)

# communes.to_crs(epsg=2154)

# communes.to_file("communes.geojson", driver="GeoJSON")



url_idf = "https://geo.api.gouv.fr/communes?codeRegion=11&fields=code,population&format=geojson&geometry=contour"
communes_idf = gpd.read_file(url_idf)         
print(len(communes_idf), "communes")     

communes_idf = communes_idf.to_crs("EPSG:2154")

communes_idf.to_file("communes_idf.geojson", driver="GeoJSON")


gdf_irve = gpd.read_file("irve.gpkg")

jointure_irve_idf = gpd.sjoin(gdf_irve, communes_idf  , how = 'inner', predicate= 'within')

print (jointure_irve_idf.head())

jointure_irve_idf.to_file('jointure_irve_idf.geojson', driver='GeoJSON')

irve_par_commune = jointure_irve_idf.groupby("code").size().rename("nb_irve").reset_index()
irve_communes_idf = communes_idf.merge(irve_par_commune, on="code", how="left")
irve_communes_idf["nb_irve"] = irve_communes_idf ["nb_irve"].fillna(0)
irve_communes_idf.to_file("irve_commune_idf.geojson", driver='GeoJSON')

complet_communes_idf = gpd.read_file("irve_commune_idf.geojson")
complet_communes_idf ['aire_km2'] = irve_communes_idf.geometry.area / 1_000_000
print (complet_communes_idf['aire_km2'])
complet_communes_idf["dens_pop"] = complet_communes_idf["population"] / complet_communes_idf["aire_km2"]
complet_communes_idf.to_file('dens_pop_idf.geojson', driver='GeoJSON')

centres = communes_idf.copy()
centres["geometry"] = centres.geometry.centroid
centres.to_file('centres_idf.geojson', driver='GeoJSON')

bornes_rapides = gdf_irve[gdf_irve["puissance_nominale"] >= 150].copy()
print(len(bornes_rapides), "bornes rapides sur", len(jointure_irve_idf), "bornes IDF")

