import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PWC Water Atlas — Data Center Scope 1/2/3 Water Footprint",
  description:
    "What is the defensible Scope 1/2/3 water footprint of every named data-center building and campus in Prince William County?",
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
