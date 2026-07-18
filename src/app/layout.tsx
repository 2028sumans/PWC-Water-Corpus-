import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PWC Water Atlas — Data Center Water Legibility",
  description:
    "How knowable is each Prince William County parcel's water relationship to data center infrastructure?",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} h-full antialiased dark`}
      suppressHydrationWarning
    >
      <body className="h-full bg-neutral-950 text-neutral-100" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
