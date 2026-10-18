import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import { Nav } from "@/components/Nav";
import { AppProvider } from "@/lib/store";
import "./globals.css";

const fraunces = Fraunces({ variable: "--font-fraunces", subsets: ["latin"], axes: ["opsz"] });
const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Rewear — restyle what you own",
  description: "Recreate the outfits you love using the clothes already in your wardrobe.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${fraunces.variable} ${inter.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <AppProvider>
          <Nav />
          <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col px-4 pb-20 sm:px-8">{children}</main>
          <footer className="border-t border-line/70 py-6 text-center text-xs text-muted">
            Rewear · Team Kyberium · The most sustainable outfit is the one you already own.
          </footer>
        </AppProvider>
      </body>
    </html>
  );
}
