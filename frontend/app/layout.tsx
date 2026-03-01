import type { Metadata } from "next";
import { Lora, Lobster_Two } from "next/font/google";
import "./globals.css";

const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
});

const lobsterTwo = Lobster_Two({
  variable: "--font-lobster-two",
  subsets: ["latin"],
  weight: ["700"],
  style: ["italic"],
});

export const metadata: Metadata = {
  title: "Remy — AI Sous Chef",
  description: "Your hands-free AI cooking assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${lora.variable} ${lobsterTwo.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
