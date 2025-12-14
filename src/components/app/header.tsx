'use client';

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Menu, UserCircle } from "lucide-react";
import { AIVIDLogo } from "../icons";
import { ThemeSwitcher } from "../theme-switcher";

export function Header() {

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
       <div className="flex items-center gap-2">
            <AIVIDLogo className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-semibold tracking-tight">AI VID Studio</h1>
        </div>
      <div className="ml-auto flex items-center gap-2">
        <ThemeSwitcher />
        <Button variant="ghost" size="icon" className="rounded-full">
          <UserCircle className="h-5 w-5" />
          <span className="sr-only">Toggle user menu</span>
        </Button>
      </div>
    </header>
  );
}
