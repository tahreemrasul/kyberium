import type { Metadata } from "next";
import { LooksView } from "@/components/looks/LooksView";

export const metadata: Metadata = { title: "My Looks · Rewear" };

export default function LooksPage() {
  return <LooksView />;
}
