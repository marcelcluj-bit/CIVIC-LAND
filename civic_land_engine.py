import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any

class CivicLandFinancialModel:
    """
    Model de analiză economico-financiară și fiscală pentru proiectul municipal CIVIC-LAND.
    """
    def __init__(self, total_hectares: float, plots_per_hectare: int, monthly_lease_eur: float):
        self.total_hectares = total_hectares
        self.plots_per_hectare = plots_per_hectare
        self.total_plots = int(total_hectares * plots_per_hectare)
        self.monthly_lease_eur = monthly_lease_eur

    def calculate_municipal_revenues(self, occupancy_rate: float = 1.0) -> Dict[str, Any]:
        """
        Calculează proiecția veniturilor la bugetul local pe bază de chirie și impozite.
        """
        active_plots = int(self.total_plots * occupancy_rate)
        monthly_income = active_plots * self.monthly_lease_eur
        annual_lease_income = monthly_income * 12
        
        # Estimare impozit pe clădiri/proprietate după finalizarea construcțiilor (medie 150 EUR/an/locuință)
        estimated_annual_property_tax = active_plots * 150.0

        return {
            "total_plots_generated": self.total_plots,
            "active_plots": active_plots,
            "monthly_lease_revenue_eur": monthly_income,
            "annual_lease_revenue_eur": annual_lease_income,
            "estimated_annual_property_tax_eur": estimated_annual_property_tax,
            "total_annual_municipal_inflow_eur": annual_lease_income + estimated_annual_property_tax
        }

    def estimate_utility_phase_transition(self, cost_per_septic_unit: float = 1500.0, cost_centralized_sewer_per_plot: float = 2500.0) -> Dict[str, float]:
        """
        Calculează tranziția de la fose septice ecologice la sistemul centralizat de canalizare.
        """
        phase_1_septic_total = self.total_plots * cost_per_septic_unit
        phase_2_centralized_total = self.total_plots * cost_centralized_sewer_per_plot
        
        return {
            "phase_1_decentralized_septic_capex_eur": phase_1_septic_total,
            "phase_2_centralized_sewer_capex_eur": phase_2_centralized_total,
            "total_infrastructure_investment_eur": phase_1_septic_total + phase_2_centralized_total
        }


class CivicLandGISGenerator:
    """
    Generator open-source de metadate spațiale (GeoJSON) pentru integrarea cu QGIS și hărți Web3.
    """
    def __init__(self, base_latitude: float, base_longitude: float):
        self.base_lat = base_latitude
        self.base_lon = base_longitude

    def generate_geojson_grid(self, num_plots: int, plot_size_meters: float = 20.0) -> Dict[str, Any]:
        """
        Generează o rețea de parcele de 500 mp (20m x 25m) formatată GeoJSON.
        """
        features = []
        delta_lat = plot_size_meters / 111000.0  # Aproximație grade latitudine
        delta_lon = plot_size_meters / 78000.0   # Aproximație grade longitudine (pentru latitudini medii)

        cols = 50  # 50 parcele pe rând
        for i in range(num_plots):
            row = i // cols
            col = i % cols

            min_lon = self.base_lon + (col * delta_lon)
            max_lon = min_lon + delta_lon
            min_lat = self.base_lat + (row * delta_lat)
            max_lat = min_lat + delta_lat

            plot_id = f"PARCEL-{i+1:04d}"
            
            # Structură poligonală GeoJSON
            feature = {
                "type": "Feature",
                "properties": {
                    "parcel_id": plot_id,
                    "area_sqm": 500,
                    "monthly_lease_eur": 200,
                    "status": "AVAILABLE",
                    "building_covenant_years": 5,
                    "utilities": ["ROADS", "POWER", "WATER", "ECO_SEPTIC"]
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat]
                    ]]
                }
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "metadata": {
                "project": "CIVIC-LAND Municipal Blueprint",
                "generated_at": datetime.utcnow().isoformat(),
                "total_features": len(features)
            },
            "features": features
        }


# ==========================================
# TESTARE ȘI EXECUTARE COD OPEN-SOURCE
# ==========================================
if __name__ == "__main__":
    print("=" * 70)
    print("      CIVIC-LAND MUNICIPAL OPEN-SOURCE PYTHON ENGINE")
    print("=" * 70)

    # 1. Rularea analizei financiare pentru 100 Hectare (2.000 parcele)
    model = CivicLandFinancialModel(total_hectares=100, plots_per_hectare=20, monthly_lease_eur=200)
    financials = model.calculate_municipal_revenues(occupancy_rate=0.85)  # grad de ocupare 85%
    utilities = model.estimate_utility_phase_transition()

    print("\n[1] PROIECȚIE FINANCIARĂ MUNICIPALĂ (100 Ha / 2.000 Parcele):")
    print(f" • Parcele Totale Generat: {financials['total_plots_generated']} loturi")
    print(f" • Parcele Active (85% Ocupare): {financials['active_plots']} loturi")
    print(f" • Încasări Lunare Chirii: €{financials['monthly_lease_revenue_eur']:,.2f}")
    print(f" • Încasări Anuale Chirii: €{financials['annual_lease_revenue_eur']:,.2f}")
    print(f" • Impozite Anuale Estimate pe Clădiri: €{financials['estimated_annual_property_tax_eur']:,.2f}")
    print(f" • TOTAL VENIT ANUAL LA BUGETUL LOCAL: €{financials['total_annual_municipal_inflow_eur']:,.2f}")

    print("\n[2] TRANZIȚIE INFRASTRUCTURĂ CANALIZARE:")
    print(f" • Etapa 1 (Fose Ecologice Decentralizate): €{utilities['phase_1_decentralized_septic_capex_eur']:,.2f}")
    print(f" • Etapa 2 (Canalizare Centralizată): €{utilities['phase_2_centralized_sewer_capex_eur']:,.2f}")

    # 2. Generarea fișierului GeoJSON
    gis_gen = CivicLandGISGenerator(base_latitude=46.7712, base_longitude=23.6236)
    geojson_data = gis_gen.generate_geojson_grid(num_plots=10)  # Exemplu pentru primele 10 parcele

    print("\n[3] EȘANTION EXPORT GIS GEOJSON (Gata de import în QGIS / Hărți):")
    print(json.dumps(geojson_data, indent=2)[:600] + "\n... [restul datelor trunchiate]")

    # Salvare în fișier local
    with open("civic_land_parcels.geojson", "w") as f:
        json.dump(geojson_data, f, indent=2)
    print("\n -> Fișierul 'civic_land_parcels.geojson' a fost salvat cu succes!")
