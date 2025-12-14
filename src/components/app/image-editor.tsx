'use client';

import * as React from 'react';
import Image from 'next/image';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, Loader2, Send, X } from 'lucide-react';
import { Skeleton } from '../ui/skeleton';
import { Input } from '../ui/input';
import { useState } from 'react';
import { cn } from '@/lib/utils';

type ImageEditorProps = {
  generatedImages: string[] | null;
  setSelectedIndex: (index: number) => void;
  selectedIndex: number;
  isLoading: boolean;
  onEdit: (editPrompt: string) => void;
  isEditing: boolean;
  onClear: () => void;
};

export function ImageEditor({ 
  generatedImages, 
  setSelectedIndex,
  selectedIndex,
  isLoading, 
  onEdit, 
  isEditing,
  onClear
}: ImageEditorProps) {
  const [editPrompt, setEditPrompt] = useState('');
  const selectedImage = generatedImages ? generatedImages[selectedIndex] : null;

  const handleDownload = () => {
    if (selectedImage) {
      const link = document.createElement('a');
      link.href = selectedImage;
      link.download = `aivid-design-${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editPrompt.trim()) {
      onEdit(editPrompt);
      setEditPrompt('');
    }
  };
  
  const showLoading = isLoading || isEditing;
  const loadingText = isLoading ? 'Generating your designs...' : 'Applying your edits...';
  
  // Debug: Log the selected image to see what we're getting
  React.useEffect(() => {
    if (selectedImage) {
      console.log('Selected image data:', selectedImage.substring(0, 100) + '...');
      console.log('Is valid data URI?', selectedImage.startsWith('data:image/'));
    }
  }, [selectedImage]);
  
  return (
    <Card className="h-full flex flex-col relative overflow-hidden">
      <CardContent className="flex-1 p-2 flex items-center justify-center bg-muted/30 relative">
          {showLoading && (
            <div className="absolute inset-0 bg-background/50 backdrop-blur-sm flex flex-col items-center justify-center z-20">
                <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
                <p className="text-foreground/80 font-medium">{loadingText}</p>
                <p className="text-foreground/60 text-sm">This can take a few moments.</p>
            </div>
          )}

          {!selectedImage ? (
             <Skeleton className="w-full h-full max-w-full max-h-full" />
          ) : (
            <div className="w-full h-full relative flex items-center justify-center">
              {/* Debug: Show image URL in a tooltip or console */}
              <Image
                src={selectedImage}
                alt={`Generated interior design ${selectedIndex + 1}`}
                fill
                className="object-contain"
                data-ai-hint="interior design"
                key={selectedImage}
                onError={(e) => {
                  console.error('Image failed to load:', e);
                  console.log('Failed image src:', selectedImage?.substring(0, 100) + '...');
                }}
              />
            </div>
          )}
      </CardContent>
      <CardFooter className="p-2 border-t bg-background/80 backdrop-blur-sm flex-col gap-2">
        {generatedImages && generatedImages.length > 1 && !showLoading && (
            <div className="flex w-full gap-2 p-2 justify-center">
            {generatedImages.map((image, index) => (
              <button 
                key={index}
                onClick={() => setSelectedIndex(index)}
                className={cn(
                  'w-20 h-16 rounded-md overflow-hidden relative transition-all duration-200 ring-offset-background focus-visible:ring-2 focus-visible:ring-ring',
                  selectedIndex === index ? 'ring-2 ring-primary' : 'ring-1 ring-border hover:ring-primary/50'
                )}
              >
                <Image
                  src={image}
                  alt={`Thumbnail ${index + 1}`}
                  fill
                  className="object-cover"
                  onError={(e) => {
                    console.error('Thumbnail failed to load:', e);
                    console.log('Failed thumbnail src:', image?.substring(0, 100) + '...');
                  }}
                />
              </button>
            ))}
          </div>
        )}

        {selectedImage && !showLoading && (
          <div className="w-full flex items-center gap-2">
              <form onSubmit={handleEditSubmit} className="flex-1 relative">
                  <Input 
                      placeholder="Describe your edits... (e.g., 'make the sofa blue')"
                      value={editPrompt}
                      onChange={(e) => setEditPrompt(e.target.value)}
                      className="pr-24 bg-card"
                  />
                  <div className="absolute right-1 top-1/2 -translate-y-1/2 flex items-center">
                    <Button 
                        type="submit" 
                        size="icon" 
                        variant="ghost" 
                        className="h-8 w-8"
                        disabled={!editPrompt.trim()}
                    >
                        <Send className="h-4 w-4"/>
                    </Button>
                     <Button variant="ghost" size="icon" onClick={onClear} className="h-8 w-8">
                        <X className="h-4 w-4" />
                    </Button>
                  </div>
              </form>
              <Button variant="outline" size="icon" onClick={handleDownload}>
                <Download className="h-4 w-4" />
              </Button>
          </div>
        )}
      </CardFooter>
    </Card>
  );
}