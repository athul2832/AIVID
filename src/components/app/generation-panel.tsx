
'use client';

import { Image as ImageIcon, Loader2, ScanLine, Sparkles, Upload, Wand2, Lightbulb } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { StyleSelector } from './style-selector';
import type { Dispatch, SetStateAction } from 'react';
import { Card, CardContent } from '../ui/card';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { useState, useTransition } from 'react';
import { generatePromptAction, suggestEditsAction } from '@/app/python-actions';
import { useToast } from '@/hooks/use-toast';

const fileToDataUri = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

type GenerationPanelProps = {
  prompt: string;
  setPrompt: Dispatch<SetStateAction<string>>;
  style: string;
  setStyle: Dispatch<SetStateAction<string>>;
  setSourceImage: Dispatch<SetStateAction<File | null>>;
  sourceImage: File | null;
  setFloorPlan: Dispatch<SetStateAction<File | null>>;
  floorPlan: File | null;
  handleSubmit: (mode: 'text' | 'image' | 'floorplan') => void;
  isLoading: boolean;
  activeTab: string;
  setActiveTab: Dispatch<SetStateAction<string>>;
};

const FileUpload = ({ file, setFile, label, id }: { file: File | null; setFile: (file: File | null) => void; label: string, id: string }) => (
  <div className="space-y-2">
    <Label htmlFor={id}>{label}</Label>
    <Card className="border-2 border-dashed bg-muted hover:border-muted-foreground/50 hover:bg-muted/80 transition-colors">
      <CardContent className="p-4">
        <label htmlFor={id} className="cursor-pointer">
          <div className="flex flex-col items-center justify-center space-y-2 text-muted-foreground">
            <Upload className="h-8 w-8" />
            <p className="text-sm">
              {file ? (
                <span className="font-medium text-foreground">{file.name}</span>
              ) : (
                <>
                  <span className="font-semibold text-primary">Click to upload</span> or drag and drop
                </>
              )}
            </p>
            <p className="text-xs">PNG, JPG, or WEBP</p>
          </div>
          <Input id={id} type="file" className="sr-only" onChange={(e) => setFile(e.target.files?.[0] ?? null)} accept="image/png, image/jpeg, image/webp" />
        </label>
      </CardContent>
    </Card>
  </div>
);

function AutoPromptGenerator({ setPrompt, style }: { setPrompt: (prompt: string) => void; style: string }) {
  const [topic, setTopic] = useState('');
  const [isGenerating, startTransition] = useTransition();
  const { toast } = useToast();

  const handleGenerate = () => {
    if (!topic.trim()) {
      toast({ variant: 'destructive', title: 'Topic is empty', description: 'Please enter a topic to generate a prompt.' });
      return;
    }
    startTransition(async () => {
      if (!style) {
        toast({
          variant: 'destructive',
          title: 'Style not defined',
          description: 'Please select a design style first.',
        });
        return;
      }
      const result = await generatePromptAction({ topic, style });
      if (result.success) {
        setPrompt(result.data.data);
      } else {
        toast({
          variant: 'destructive',
          title: 'Failed to generate prompt',
          description: result.error,
        });
      }
    });
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-2">
          <Wand2 />
          Auto-generate prompt
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="grid gap-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">Generate a detailed prompt</h4>
            <p className="text-sm text-muted-foreground">
              Enter a simple topic (e.g., "a cozy living room") and let AI create a rich prompt for you.
            </p>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="topic">Topic</Label>
            <Input
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., modern kitchen"
              disabled={isGenerating}
            />
          </div>
          <Button onClick={handleGenerate} disabled={isGenerating}>
            {isGenerating ? 'Generating...' : 'Generate'}
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}

export function GenerationPanel({
  prompt,
  setPrompt,
  style,
  setStyle,
  setSourceImage,
  sourceImage,
  setFloorPlan,
  floorPlan,
  handleSubmit,
  isLoading,
  activeTab,
  setActiveTab
}: GenerationPanelProps) {
  const [isSuggesting, startSuggestTransition] = useTransition();
  const { toast } = useToast();

  const handleSuggestEdits = () => {
    const imageToSuggest = activeTab === 'image' ? sourceImage : floorPlan;
    const toastTitle = activeTab === 'image' ? 'No image uploaded' : 'No floor plan uploaded';
    const toastDescription = activeTab === 'image' ? 'Please upload an image to get suggestions.' : 'Please upload a floor plan to get suggestions.';

    if (!imageToSuggest) {
      toast({ variant: 'destructive', title: toastTitle, description: toastDescription });
      return;
    }
    startSuggestTransition(async () => {
      try {
        const baseImage = await fileToDataUri(imageToSuggest);
        const result = await suggestEditsAction({ baseImage, designStyle: style });
        if (result.success) {
          setPrompt(result.data.data);
          toast({ title: "Suggestion applied!", description: "The AI's suggestion has been added to the prompt." });
        } else {
          throw new Error(result.error);
        }
      } catch (e: any) {
        toast({
          variant: 'destructive',
          title: 'Failed to get suggestion',
          description: e.message || 'An unknown error occurred.',
        });
      }
    });
  };

  const canSubmit = (mode: 'text' | 'image' | 'floorplan') => {
    if (isLoading) return false;
    if (mode === 'text') return prompt.trim().length > 0 && style.length > 0;
    if (mode === 'image') return sourceImage !== null && prompt.trim().length > 0;
    if (mode === 'floorplan') return floorPlan !== null && style.length > 0;
    return false;
  }

  return (
    <Card className="h-full flex flex-col">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="p-4 border-b">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="text"><ImageIcon className="mr-2" />Text</TabsTrigger>
            <TabsTrigger value="image"><Upload className="mr-2"/>Image</TabsTrigger>
            <TabsTrigger value="floorplan"><ScanLine className="mr-2"/>Plan</TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <TabsContent value="text" className="mt-0 space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="prompt-text">Prompt</Label>
                <AutoPromptGenerator setPrompt={setPrompt} style={style} />
              </div>
              <Textarea
                id="prompt-text"
                placeholder="e.g., A cozy living room with a fireplace and a large bookshelf"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
              />
            </div>
            <StyleSelector selectedStyle={style} onStyleSelect={setStyle} />
          </TabsContent>

          <TabsContent value="image" className="mt-0 space-y-4">
            <FileUpload file={sourceImage} setFile={setSourceImage} label="Base Image / Virtual Staging" id="source-image-upload" />
            <StyleSelector selectedStyle={style} onStyleSelect={setStyle} />
            <div className="space-y-2">
               <div className="flex justify-between items-center">
                <Label htmlFor="prompt-image">Edit Prompt</Label>
                <Button variant="ghost" size="sm" className="gap-2" onClick={handleSuggestEdits} disabled={!sourceImage || isSuggesting}>
                  {isSuggesting ? <Loader2 className="animate-spin" /> : <Lightbulb />}
                  Suggest edits
                </Button>
              </div>
              <Textarea
                id="prompt-image"
                placeholder="e.g., Add a red sofa, make the walls light blue"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={3}
              />
            </div>
          </TabsContent>

          <TabsContent value="floorplan" className="mt-0 space-y-4">
             <FileUpload file={floorPlan} setFile={setFloorPlan} label="Floor Plan" id="floor-plan-upload" />
            <StyleSelector selectedStyle={style} onStyleSelect={setStyle} />
             <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="prompt-floorplan">Additional Details</Label>
                 <Button variant="ghost" size="sm" className="gap-2" onClick={handleSuggestEdits} disabled={!floorPlan || isSuggesting}>
                  {isSuggesting ? <Loader2 className="animate-spin" /> : <Lightbulb />}
                  Suggest edits
                </Button>
              </div>
              <Textarea
                id="prompt-floorplan"
                placeholder="e.g., Use light wood flooring, add plenty of plants"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={3}
              />
            </div>
          </TabsContent>
        </div>
        
        <div className="p-4 border-t mt-auto">
          <Button 
            className="w-full" 
            size="lg" 
            onClick={() => handleSubmit(activeTab as any)} 
            disabled={!canSubmit(activeTab as any)}
          >
            {isLoading ? <Sparkles className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
            Generate
          </Button>
        </div>
      </Tabs>
    </Card>
  );
}
