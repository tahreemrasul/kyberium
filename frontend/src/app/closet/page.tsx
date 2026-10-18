import type { Metadata } from "next";
import { ClosetView } from "@/components/closet/ClosetView";

export const metadata: Metadata = { title: "My Closet · Rewear" };

export default function ClosetPage() {
  return <ClosetView />;
}
