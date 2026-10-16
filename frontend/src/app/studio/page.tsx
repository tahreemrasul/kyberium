import type { Metadata } from "next";
import { StudioView } from "@/components/studio/StudioView";

export const metadata: Metadata = { title: "Style Studio · Rewear" };

export default function StudioPage() {
  return <StudioView />;
}
