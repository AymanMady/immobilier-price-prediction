"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, Building2, MapPin, TrendingUp, ShieldCheck, Zap } from "lucide-react"
import { MarketStats } from "@/lib/types"
import { fetchApi } from "@/lib/api"

export default function Home() {
  const [stats, setStats] = useState<MarketStats | null>(null)

  useEffect(() => {
    fetchApi<MarketStats>("/api/stats")
      .then(data => setStats(data))
      .catch(err => console.error("Error fetching stats:", err))
  }, [])

  return (
    <main className="container mx-auto px-4 py-20 overflow-hidden">
      {/* Background Blobs */}
      <div className="fixed top-0 left-1/4 w-[500px] h-[500px] bg-emerald-600/10 blur-[120px] rounded-full -z-10 animate-pulse-soft" />
      <div className="fixed bottom-0 right-1/4 w-[600px] h-[600px] bg-cyan-600/10 blur-[120px] rounded-full -z-10 animate-float" />

      {/* Hero Section */}
      <section className="text-center mb-32 relative">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.span
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-block py-1 px-4 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-black tracking-[0.2em] mb-8 border border-emerald-500/20 uppercase"
          >
            Intelligence Artificielle en Immobilier
          </motion.span>
          <h1 className="text-5xl md:text-7xl font-extrabold mb-8 tracking-tight">
            Estimez votre bien en <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
              un seul clic.
            </span>
          </h1>
          <p className="text-zinc-400 text-lg md:text-xl max-w-2xl mx-auto mb-12 leading-relaxed">
            Utilisez notre puissant modèle de Machine Learning entraîné sur plus de 1,000 annonces
            pour obtenir une estimation précise du marché mauritanien.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/predict"
              className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-500 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-2 group shadow-lg shadow-emerald-900/20"
            >
              Lancer l'estimation <ArrowRight className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/analysis"
              className="w-full sm:w-auto bg-white/5 hover:bg-white/10 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-2 border border-white/10"
            >
              Voir les analyses
            </Link>
          </div>
        </motion.div>

        {/* Decorative elements */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10 w-full h-[500px] bg-emerald-500/5 blur-[120px] rounded-full" />
      </section>

      {/* Features Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-40 relative">
        {[
          { icon: <Zap className="text-amber-400" />, title: "Instantanné", desc: "Obtenez un prix estimé en moins d'une seconde grâce à nos algorithmes optimisés." },
          { icon: <ShieldCheck className="text-emerald-400" />, title: "Précis", desc: "Entraîné sur des données réelles de Nouakchott et du reste de la Mauritanie pour coller au marché." },
          { icon: <TrendingUp className="text-cyan-400" />, title: "Analytique", desc: "Visualisez comment votre bien se situe par rapport à la moyenne de son quartier." }
        ].map((feat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.15, duration: 0.6 }}
          >
            <FeatureCard
              icon={feat.icon}
              title={feat.title}
              description={feat.desc}
            />
          </motion.div>
        ))}
      </section>

      {/* Market Stats Quick Look */}
      {stats && (
        <section className="glass-card rounded-3xl p-8 md:p-12 mb-32 relative overflow-hidden">
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-12">
            <div className="md:w-1/2">
              <h2 className="text-3xl font-bold mb-6">Tendances du Marché</h2>
              <p className="text-zinc-400 mb-8 max-w-lg">
                Le marché immobilier mauritanien est en constante évolution. Nos données montrent que
                le prix médian à Nouakchott est actuellement de <span className="text-emerald-400 font-bold">{stats.global_median.toLocaleString()} MRU</span>.
              </p>

              <div className="space-y-4">
                {stats.top_neighborhoods.map((q, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                    <span className="font-semibold flex items-center gap-2">
                      <MapPin size={16} className="text-emerald-500" /> {q.name}
                    </span>
                    <span className="text-emerald-400 font-bold">{q.price.toLocaleString()} MRU</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="md:w-1/2 grid grid-cols-2 gap-4">
              <div className="p-8 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 text-center">
                <div className="text-4xl font-black text-emerald-400 mb-2">{stats.sample_size}</div>
                <div className="text-xs text-emerald-500 font-bold uppercase tracking-wider">Zones Analysées</div>
              </div>
              <div className="p-8 bg-cyan-500/10 rounded-2xl border border-cyan-500/20 text-center">
                <div className="text-4xl font-black text-cyan-400 mb-2">5,000+</div>
                <div className="text-xs text-cyan-500 font-bold uppercase tracking-wider">Total Annonces</div>
              </div>
              <div className="col-span-2 p-8 bg-zinc-900 rounded-2xl border border-white/5 flex items-center justify-center gap-4">
                <TrendingUp size={48} className="text-zinc-700" />
                <div className="text-left">
                  <div className="text-xl font-bold">XGBoost & LightGBM</div>
                  <div className="text-zinc-500 text-sm">Précision de modélisation avancée</div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* About Section */}
      <section className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl font-bold mb-8 italic">"Transformer les données en décisions"</h2>
        <p className="text-zinc-400 leading-relaxed mb-12">
          Ce projet a été développé dans le cadre d'une recherche sur le Machine Learning appliqué au
          contexte local. Nous collectons des données en temps réel pour affiner sans cesse nos prédictions
          et aider les acheteurs et vendeurs à naviguer sur le marché immobilier avec confiance.
        </p>
        <div className="flex items-center justify-center gap-8 opacity-50 grayscale hover:grayscale-0 transition-all cursor-not-allowed">
          <div className="text-2xl font-black text-white">SupNum</div>
          <div className="text-2xl font-black text-white">Voursa</div>
          <div className="text-2xl font-black text-white">Python</div>
        </div>
      </section>
    </main>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="p-8 glass-card rounded-2xl border border-white/5 hover:border-emerald-500/30 transition-all"
    >
      <div className="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center mb-6 text-2xl">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-4">{title}</h3>
      <p className="text-zinc-400 text-sm leading-relaxed">
        {description}
      </p>
    </motion.div>
  )
}
