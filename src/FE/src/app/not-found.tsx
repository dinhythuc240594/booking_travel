import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex flex-col flex-1 items-center justify-center gap-16 py-24 px-8 dark:bg-black">
      <div className="flex flex-col items-center gap-6 max-w-lg text-center">
        <div className="flex flex-col items-center gap-2">
          <h1 className="text-9xl font-bold tracking-tight text-black dark:text-zinc-50">
            404
          </h1>
          <p className="text-lg text-zinc-500 dark:text-zinc-400">
            Page Not Found
          </p>
        </div>
        <p className="text-base text-zinc-600 dark:text-zinc-400">
          The page you are looking for doesn&apos;t exist or has been moved.
        </p>
        <Link href="/">
          <Button size="lg">Back to Home</Button>
        </Link>
      </div>
    </main>
  );
}
