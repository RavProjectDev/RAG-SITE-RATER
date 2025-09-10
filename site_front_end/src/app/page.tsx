"use client";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
      <Card className="w-full lg:max-w-3xl p-6 flex flex-col gap-6 shadow-lg">
        <h1 className="text-2xl font-bold text-center">Welcome to The Rav RAG Project</h1>
        <p className="text-base text-muted-foreground leading-relaxed">
          Explore our Retrieval-Augmented Generation project inspired by the teachings of Rabbi Joseph B. Soloveitchik ("The Rav").
          Choose one of the options below to continue:
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link href="/get_chunks">
            <Button>Get Chunks</Button>
          </Link>
          <Link href="/get_full_response">
            <Button variant="outline">Get Full Response</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}


