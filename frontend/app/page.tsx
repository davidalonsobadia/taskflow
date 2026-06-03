import Link from "next/link"
import { Button } from "@/components/ui/button"
import { CheckCircle2, ListTodo, Shield, Zap } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">TaskFlow</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" asChild>
              <Link href="/login">Sign in</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Get started</Link>
            </Button>
          </div>
        </div>
      </header>

      <main>
        <section className="container mx-auto px-4 py-20 text-center">
          <h1 className="text-5xl font-bold mb-6 text-balance">
            Organize your tasks with <span className="text-primary">TaskFlow</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto text-pretty">
            A modern, professional TODO platform that helps you manage your lists and tasks efficiently. Stay organized,
            stay productive.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button size="lg" asChild>
              <Link href="/register">Start for free</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">Sign in</Link>
            </Button>
          </div>
        </section>

        <section className="container mx-auto px-4 py-20">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 border rounded-lg bg-card">
              <ListTodo className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Organize Lists</h3>
              <p className="text-muted-foreground">
                Create multiple lists to organize your tasks by project, category, or priority.
              </p>
            </div>
            <div className="p-6 border rounded-lg bg-card">
              <Zap className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Fast & Efficient</h3>
              <p className="text-muted-foreground">
                Built with modern technology for a smooth, responsive experience on any device.
              </p>
            </div>
            <div className="p-6 border rounded-lg bg-card">
              <Shield className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Secure & Private</h3>
              <p className="text-muted-foreground">
                Your data is protected with email verification and secure authentication.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-muted-foreground">
          <p>© 2025 TaskFlow. Built with Next.js and modern web technologies.</p>
        </div>
      </footer>
    </div>
  )
}
