import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "RIM Immo - Prédiction de Prix Immobiliers Mauritanie",
  description: "Estimez le prix de votre bien immobilier en Mauritanie grâce à l'intelligence artificielle.",
  icons: {
    icon: '/icon.png',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className="dark">
      <body className={`${inter.className} bg-zinc-950 text-zinc-100 min-h-screen selection:bg-emerald-500/30 selection:text-emerald-200`}>
        <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-900/20 via-zinc-950 to-zinc-950 opacity-100" />
        <Navbar />
        {children}
        <footer className="border-t border-white/5 py-12 mt-20">
          <div className="container mx-auto px-4 text-center text-zinc-500 text-sm">
            <p>© 2026 RIM Immo - Projet ML SupNum Mauritanie. Données basées sur Voursa.com</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
