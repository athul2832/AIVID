import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarInset,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@/components/ui/sidebar';
import { Button } from '@/components/ui/button';
import { AIVIDLogo } from '../icons';
import { Bot, LayoutGrid, Settings, UserCircle } from 'lucide-react';
import { Header } from './header';
import Studio from './studio';
import { DesignChat } from './design-chat';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../ui/accordion';

export default function MainLayout() {
  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
            <div className="flex items-center gap-2">
                <AIVIDLogo className="size-7 text-sidebar-primary" />
                <span className="text-lg font-semibold">AIVID</span>
            </div>
        </SidebarHeader>
        <SidebarContent className='p-0'>
          <SidebarGroup className='p-2'>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton isActive>
                  <LayoutGrid />
                  <span>AI Studio</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroup>
          <div className="flex-1 flex flex-col min-h-0">
             <Accordion type="single" collapsible defaultValue="chat" className="flex flex-col flex-1">
                <AccordionItem value="chat" className="border-b-0 flex flex-col flex-1">
                    <div className="p-2">
                        <AccordionTrigger className="text-xs font-medium uppercase text-sidebar-foreground/70 p-2 hover:no-underline hover:bg-sidebar-accent rounded-md">
                            <div className="flex items-center gap-2">
                                <Bot className="h-4 w-4" />
                                <span>Design AI Chat</span>
                            </div>
                        </AccordionTrigger>
                    </div>
                    <AccordionContent className="flex-1 data-[state=closed]:flex-grow-0 overflow-hidden">
                        <DesignChat />
                    </AccordionContent>
                </AccordionItem>
            </Accordion>
          </div>
        </SidebarContent>
        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton>
                <Settings />
                <span>Settings</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton>
                <UserCircle />
                <span>Sign in</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>
      <SidebarInset className="flex flex-col">
        <Header />
        <main className="flex-1 p-4 sm:px-6 sm:py-0 md:gap-8 overflow-auto">
          <Studio />
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
