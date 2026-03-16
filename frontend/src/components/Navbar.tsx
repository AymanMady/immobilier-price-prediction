"use client"

import Link from "next/link"
import { Building2, PieChart, Home, Info } from "lucide-react"

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-black/50 backdrop-blur-xl">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 font-bold text-xl text-white group">
          <div className="w-10 h-10 rounded-xl overflow-hidden border border-emerald-500/20 group-hover:scale-110 transition-transform">
            <img src="/icon.png" alt="RIM Immo Logo" className="w-full h-full object-cover" />
          </div>
          <span>RIM <span className="text-emerald-500">Immo</span></span>
        </Link>
        
        <div className="hidden md:flex items-center gap-8">
          <Link href="/" className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-1">
            <Home size={16} /> Home
          </Link>
          <Link href="/predict" className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-1">
            <Building2 size={16} /> Prédire
          </Link>
          <Link href="/analysis" className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-1">
            <PieChart size={16} /> Analyse
          </Link>
        </div>

        <Link 
          href="/predict" 
          className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-full text-sm font-bold transition-all transform hover:scale-105"
        >
          Estimation Gratuite
        </Link>
      </div>
    </nav>
  )
}
