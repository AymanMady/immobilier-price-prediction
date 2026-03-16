"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell,
  PieChart as RePieChart,
  Pie
} from "recharts"
import { PieChart, TrendingUp, Info } from "lucide-react"
import { MarketStats } from "@/lib/types"
import { fetchApi } from "@/lib/api"

export default function AnalysisPage() {
  const [stats, setStats] = useState<MarketStats | null>(null)

  useEffect(() => {
    fetchApi<MarketStats>("/api/stats")
      .then(data => setStats(data))
      .catch(err => console.error("Error fetching stats:", err))
  }, [])

  const COLORS = ['#10b981', '#06b6d4', '#3b82f6', '#8b5cf6', '#d946ef', '#f43f5e']

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="flex items-center gap-3 mb-12">
        <div className="p-3 bg-cyan-500/10 rounded-2xl border border-cyan-500/20">
          <PieChart className="text-cyan-400" size={32} />
        </div>
        <div>
          <h1 className="text-4xl font-black">Market Insights</h1>
          <p className="text-zinc-500">Analyses approfondies du marché immobilier mauritanien.</p>
        </div>
      </div>

      {!stats ? (
        <div className="flex flex-col items-center justify-center h-64 opacity-50">
          <div className="animate-spin mb-4"><TrendingUp size={48} /></div>
          <p>Chargement des données du marché...</p>
        </div>
      ) : (
        <div className="space-y-12">
          {/* Main Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Neighborhood Price Comparison */}
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass-card p-8 rounded-3xl border border-white/5"
            >
              <h3 className="text-xl font-bold mb-8">Prix Médian par Quartier</h3>
              <div className="h-[400px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.top_neighborhoods} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
                    <XAxis type="number" hide />
                    <YAxis 
                      dataKey="name" 
                      type="category" 
                      stroke="#71717a" 
                      fontSize={12} 
                      width={100}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '12px' }}
                      itemStyle={{ color: '#10b981' }}
                    />
                    <Bar dataKey="price" radius={[0, 4, 4, 0]}>
                      {stats.top_neighborhoods.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* Distribution/Share */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass-card p-8 rounded-3xl border border-white/5"
            >
              <h3 className="text-xl font-bold mb-8">Part de l'Estimation</h3>
              <div className="h-[400px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart>
                    <Pie
                      data={stats.top_neighborhoods}
                      cx="50%"
                      cy="50%"
                      innerRadius={80}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="price"
                    >
                      {stats.top_neighborhoods.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '12px' }}
                    />
                  </RePieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                {stats.top_neighborhoods.slice(0, 4).map((q, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i] }} />
                    <span className="text-xs text-zinc-400 font-medium">{q.name}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Detailed Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
             <div className="p-8 bg-black/40 rounded-3xl border border-white/5 flex flex-col items-center">
                <Info className="text-zinc-700 mb-4" size={32} />
                <h4 className="text-zinc-500 text-xs font-black uppercase mb-2">Algorithme Principal</h4>
                <div className="text-2xl font-bold">Gradient Boosting</div>
             </div>
             <div className="p-8 bg-emerald-500/5 rounded-3xl border border-emerald-500/10 flex flex-col items-center">
                <div className="text-sm text-emerald-500 font-bold mb-2">Prix Moyen Global</div>
                <div className="text-3xl font-black">{stats.global_median.toLocaleString()} MRU</div>
                <div className="text-xs text-zinc-500 mt-2">Basé sur {stats.sample_size} zones</div>
             </div>
             <div className="p-8 bg-black/40 rounded-3xl border border-white/5 flex flex-col items-center">
                <TrendingUp className="text-zinc-700 mb-4" size={32} />
                <h4 className="text-zinc-500 text-xs font-black uppercase mb-2">Tendance 2026</h4>
                <div className="text-2xl font-bold">+4.2% / an</div>
             </div>
          </div>
        </div>
      )}
    </div>
  )
}
