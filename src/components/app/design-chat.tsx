'use client';

import { useState, useRef, useEffect, useTransition } from 'react';
import { Bot, Loader2, Send, User, Sparkles } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { chatAction } from '@/app/python-actions';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export function DesignChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isPending, startTransition] = useTransition();
  const { toast } = useToast();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isPending) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    const query = input;
    setInput('');

    startTransition(async () => {
      const result = await chatAction({ query });
      if (result.success) {
        setMessages([...newMessages, { role: 'assistant', content: result.data.data }]);
      } else {
        toast({
          variant: 'destructive',
          title: 'Error',
          description: result.error,
        });
        setMessages(messages); // Revert to previous messages on error
      }
    });
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full" ref={scrollAreaRef}>
          <div className="p-4 space-y-4">
            {messages.length === 0 && (
                <div className="text-center text-sm text-sidebar-foreground/60 flex flex-col items-center gap-4 py-8">
                    <div className="p-3 rounded-full bg-sidebar-accent">
                        <Sparkles className="w-8 h-8 text-sidebar-primary" />
                    </div>
                    <p>Ask me anything about interior design! <br /> e.g., "What are some good color palettes for a small apartment?"</p>
                </div>
            )}
            {messages.map((message, index) => (
              <div
                key={index}
                className={cn(
                  'flex items-start gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.role === 'assistant' && (
                    <Avatar className="w-8 h-8 bg-sidebar-accent">
                        <AvatarFallback className='bg-sidebar-accent text-sidebar-primary'>
                            <Bot className="w-5 h-5" />
                        </AvatarFallback>
                    </Avatar>
                )}
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg p-3 text-sm',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-sidebar-accent text-sidebar-foreground'
                  )}
                >
                  <p className="font-code">{message.content}</p>
                </div>
                {message.role === 'user' && (
                    <Avatar className="w-8 h-8">
                        <AvatarFallback>
                            <User className="w-5 h-5" />
                        </AvatarFallback>
                    </Avatar>
                )}
              </div>
            ))}
            {isPending && (
                <div className="flex items-start gap-3 justify-start">
                    <Avatar className="w-8 h-8 bg-sidebar-accent">
                        <AvatarFallback className='bg-sidebar-accent text-sidebar-primary'>
                            <Loader2 className="w-5 h-5 animate-spin" />
                        </AvatarFallback>
                    </Avatar>
                    <div className="max-w-[80%] rounded-lg p-3 text-sm bg-sidebar-accent text-sidebar-foreground">
                        <p className="font-code">Thinking...</p>
                    </div>
                </div>
            )}
          </div>
        </ScrollArea>
      </div>
      <form onSubmit={handleSubmit} className="border-t border-sidebar-border p-2">
        <div className="relative">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a design question..."
            className="pr-12 bg-sidebar-accent border-0 focus-visible:ring-sidebar-ring"
          />
          <Button
            type="submit"
            size="icon"
            variant="ghost"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent"
            disabled={isPending || !input.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
}
