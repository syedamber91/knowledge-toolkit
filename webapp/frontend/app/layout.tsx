import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { GeistMono } from "geist/font/mono";
import "@/styles/globals.css";
import Topbar from "@/components/Topbar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = { title: "Knowledge Toolkit" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${GeistMono.variable}`}>
      <body className="bg-[var(--gray-97)] font-[family-name:var(--font-inter)] text-[var(--gray-10)]">
        <Topbar />
        <main className="pt-14">{children}</main>
      </body>
    </html>
  );
}
