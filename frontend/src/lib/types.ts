export interface PredictionInput {
  surface_m2: number;
  nb_chambres: number;
  nb_salons: number;
  nb_sdb: number;
  quartier: string;
  has_piscine: boolean;
  has_garage: boolean;
  has_clim: boolean;
  taille_rue: number;
  nb_balcons: number;
}

export interface PredictionResult {
  prediction: {
    mru: number;
    eur: number;
    interval: {
      min: number;
      max: number;
    };
  };
  stats: {
    price_per_m2: number;
    neighborhood_median: number;
    comparison: number;
  };
}

export interface MarketStats {
  top_neighborhoods: { name: string; price: number }[];
  global_median: number;
  sample_size: number;
}
