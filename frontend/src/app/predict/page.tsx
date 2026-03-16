"use client"

import { useState, useEffect } from "react"
import dynamic from "next/dynamic"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Building2, 
  Maximize, 
  Bed, 
  Bath, 
  MapPin, 
  ChevronRight, 
  Waves, 
  Warehouse, 
  Thermometer,
  Calculator,
  Loader2,
  Euro,
  Scale,
  Target
} from "lucide-react"
import { PredictionInput, PredictionResult } from "@/lib/types"
import { fetchApi } from "@/lib/api"

// Dynamic import for the map to avoid SSR issues
const InteractiveMap = dynamic(() => import("@/components/InteractiveMap"), { 
  ssr: false,
  loading: () => <div className="w-full h-[400px] bg-zinc-900 animate-pulse rounded-2xl" />
})

export default function PredictPage() {
  const [loading, setLoading] = useState(false)
  const [neighborhoods, setNeighborhoods] = useState<string[]>([])
  const [formData, setFormData] = useState<PredictionInput>({
    surface_m2: 150,
    nb_chambres: 3,
    nb_salons: 2,
    nb_sdb: 1,
    quartier: "Tevragh Zeina",
    has_piscine: false,
    has_garage: false,
    has_clim: false,
    taille_rue: 12,
    nb_balcons: 0
  })
  const [result, setResult] = useState<PredictionResult | null>(null)

  useEffect(() => {
    fetchApi<string[]>("/api/neighborhoods")
      .then(data => setNeighborhoods(data))
      .catch(err => console.error("Error fetching neighborhoods:", err))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await fetchApi<PredictionResult>("/api/predict", {
        method: "POST",
        body: JSON.stringify(formData)
      })
      setResult(data)
    } catch (err) {
      console.error("Prediction failed:", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="flex items-center gap-3 mb-12">
        <div className="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20">
          <Calculator className="text-emerald-500" size={32} />
        </div>
        <div>
          <h1 className="text-4xl font-black">Estimer mon Bien</h1>
          <p className="text-zinc-500">Remplissez les informations pour obtenir une estimation immédiate.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* Form Column */}
        <div className="lg:col-span-5">
          <form onSubmit={handleSubmit} className="space-y-8 glass-card p-8 rounded-3xl border border-white/5">
            <div className="space-y-6">
              {/* Quartier */}
              <div>
                <label className="block text-sm font-bold text-zinc-400 mb-2 flex items-center gap-2">
                  <MapPin size={16} /> Quartier
                </label>
                <select 
                  className="w-full bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500/50 transition-colors"
                  value={formData.quartier}
                  onChange={e => setFormData({...formData, quartier: e.target.value})}
                >
                  {neighborhoods.map(q => (
                    <option key={q} value={q}>{q}</option>
                  ))}
                </select>
              </div>

              {/* Surface */}
              <div>
                <label className="block text-sm font-bold text-zinc-400 mb-2 flex items-center justify-between">
                  <span className="flex items-center gap-2"><Maximize size={16} /> Surface (m²)</span>
                  <span className="text-emerald-500">{formData.surface_m2} m²</span>
                </label>
                <input 
                  type="range" min="20" max="1000" step="10"
                  className="w-full accent-emerald-500"
                  value={formData.surface_m2}
                  onChange={e => setFormData({...formData, surface_m2: parseInt(e.target.value)})}
                />
              </div>

              {/* Pieces Grid */}
              <div className="grid grid-cols-3 gap-4">
                <CounterInput 
                  label="Chambres" icon={<Bed size={16} />}
                  value={formData.nb_chambres}
                  onChange={val => setFormData({...formData, nb_chambres: val})}
                />
                <CounterInput 
                  label="Salons" icon={<Building2 size={16} />}
                  value={formData.nb_salons}
                  onChange={val => setFormData({...formData, nb_salons: val})}
                />
                <CounterInput 
                  label="Salles de bain" icon={<Bath size={16} />}
                  value={formData.nb_sdb}
                  onChange={val => setFormData({...formData, nb_sdb: val})}
                />
              </div>

              {/* Features (Checkboxes) */}
              <div className="space-y-4 pt-4 border-t border-white/5">
                <label className="block text-sm font-bold text-zinc-400">Équipements de Standing</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <FeatureToggle 
                    active={formData.has_garage} icon={<Warehouse size={18} />} label="Garage"
                    onClick={() => setFormData({...formData, has_garage: !formData.has_garage})}
                  />
                  <FeatureToggle 
                    active={formData.has_piscine} icon={<Waves size={18} />} label="Piscine"
                    onClick={() => setFormData({...formData, has_piscine: !formData.has_piscine})}
                  />
                   <FeatureToggle 
                    active={formData.has_clim} icon={<Thermometer size={18} />} label="Clim"
                    onClick={() => setFormData({...formData, has_clim: !formData.has_clim})}
                  />
                </div>
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-black py-4 rounded-2xl transition-all shadow-xl shadow-emerald-900/40 flex items-center justify-center gap-3"
            >
              {loading ? <Loader2 className="animate-spin" /> : <ChevronRight />}
              Obtenir l'Estimation IA
            </button>
          </form>
        </div>

        {/* Results/Map Column */}
        <div className="lg:col-span-7 space-y-8">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div 
                key="result"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="space-y-8"
              >
                {/* Result Card */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass-card rounded-[2rem] p-10 border border-emerald-500/30 relative overflow-hidden group shadow-[0_0_50px_-12px_rgba(16,185,129,0.3)]"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                  <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity duration-700 group-hover:scale-110 transform">
                    <Target size={180} className="text-emerald-500" />
                  </div>
                  
                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="h-px w-8 bg-emerald-500/50" />
                      <h3 className="text-emerald-500 font-black uppercase tracking-[0.2em] text-[10px]">
                        Estimation IA Terminée
                      </h3>
                    </div>

                    <div className="flex flex-col md:flex-row md:items-baseline gap-3 mb-10">
                      <motion.div 
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="text-7xl font-black text-white tracking-tighter"
                      >
                        {result.prediction.mru.toLocaleString()}
                      </motion.div>
                      <div className="text-2xl font-black text-zinc-600">MRU</div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-10 border-t border-white/5">
                      <div className="group/item flex items-center gap-5 p-4 rounded-2xl hover:bg-white/5 transition-colors">
                        <div className="p-3 bg-cyan-500/10 rounded-xl group-hover/item:scale-110 transition-transform"><Euro className="text-cyan-400" size={20} /></div>
                        <div>
                          <div className="text-xs text-zinc-500 font-black uppercase tracking-wider mb-1">Euros Govt.</div>
                          <div className="text-2xl font-bold text-white tracking-tight">{result.prediction.eur.toLocaleString()} €</div>
                        </div>
                      </div>
                      <div className="group/item flex items-center gap-5 p-4 rounded-2xl hover:bg-white/5 transition-colors">
                        <div className="p-3 bg-amber-500/10 rounded-xl group-hover/item:scale-110 transition-transform"><Scale className="text-amber-400" size={20} /></div>
                        <div>
                          <div className="text-xs text-zinc-500 font-black uppercase tracking-wider mb-1">Valeur au m²</div>
                          <div className="text-2xl font-bold text-white tracking-tight">{Math.round(result.stats.price_per_m2).toLocaleString()} <span className="text-xs font-normal text-zinc-500">MRU</span></div>
                        </div>
                      </div>
                    </div>

                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6 }}
                      className="mt-10 p-6 bg-zinc-950/50 rounded-2xl border border-white/5 flex flex-col md:flex-row items-center justify-between gap-4"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-xs text-zinc-400 font-bold uppercase tracking-widest">Gamme de Prix Estimée</span>
                      </div>
                      <span className="font-black text-emerald-400 text-lg">
                        {result.prediction.interval.min.toLocaleString()} — {result.prediction.interval.max.toLocaleString()} <span className="text-xs font-normal opacity-50">MRU</span>
                      </span>
                    </motion.div>
                  </div>
                </motion.div>

                {/* Neighborhood Comparison Card */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div className="p-6 bg-zinc-900/50 rounded-2xl border border-white/5">
                      <div className="text-sm text-zinc-500 mb-2 uppercase tracking-widest font-black text-[10px]">Moyenne Quartier</div>
                      <div className="text-2xl font-bold">{result.stats.neighborhood_median.toLocaleString()} MRU</div>
                   </div>
                   <div className="p-6 bg-zinc-900/50 rounded-2xl border border-white/5">
                      <div className="text-sm text-zinc-500 mb-2 uppercase tracking-widest font-black text-[10px]">Comparaison</div>
                      <div className={`text-2xl font-bold ${result.stats.comparison > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                        {result.stats.comparison > 0 ? '+' : ''}{result.stats.comparison}% 
                        <span className="text-xs ml-2 text-zinc-500 font-normal">vs moyenne</span>
                      </div>
                   </div>
                </div>
              </motion.div>
            ) : (
              <motion.div 
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="h-full flex flex-col items-center justify-center text-center p-12 glass-card rounded-3xl border border-dashed border-white/10 opacity-50"
              >
                <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mb-6">
                  <Calculator size={48} className="text-zinc-500" />
                </div>
                <h3 className="text-xl font-bold mb-2">Prêt pour l'estimation ?</h3>
                <p className="max-w-xs text-sm text-zinc-500">
                  Entrez les détails de votre bien et laissez notre modèle de Machine Learning faire le reste.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Map Section */}
          <div className="h-[400px]">
             <InteractiveMap selectedQuartier={formData.quartier} />
          </div>
        </div>
      </div>
    </div>
  )
}

function CounterInput({ label, icon, value, onChange }: { label: string, icon: React.ReactNode, value: number, onChange: (val: number) => void }) {
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="text-[10px] font-black uppercase text-zinc-500 tracking-tighter flex items-center gap-1">
        {icon} {label}
      </div>
      <div className="flex items-center bg-zinc-900 border border-white/10 rounded-xl overflow-hidden">
        <button 
          type="button"
          onClick={() => onChange(Math.max(0, value - 1))}
          className="px-3 py-2 hover:bg-white/5 text-zinc-400"
        >-</button>
        <span className="w-8 text-center font-bold text-sm">{value}</span>
        <button 
          type="button"
          onClick={() => onChange(value + 1)}
          className="px-3 py-2 hover:bg-white/5 text-zinc-400"
        >+</button>
      </div>
    </div>
  )
}

function FeatureToggle({ active, icon, label, onClick }: { active: boolean, icon: React.ReactNode, label: string, onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex flex-col items-center gap-2 p-4 rounded-2xl border transition-all ${
        active 
          ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400' 
          : 'bg-zinc-900 border-white/5 text-zinc-500 grayscale'
      }`}
    >
      {icon}
      <span className="text-[10px] font-bold uppercase">{label}</span>
    </button>
  )
}
