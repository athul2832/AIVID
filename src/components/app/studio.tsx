'use client';

import { useState, useTransition } from 'react';
import { GenerationPanel } from './generation-panel';
import { ImageEditor } from './image-editor';
import { useToast } from '@/hooks/use-toast';
import { generateDesignAction } from '@/app/python-actions';
import { chatAction as editDesignAction } from '@/app/python-actions';
import { generatePromptAction as generateFromFloorPlanAction } from '@/app/python-actions';

const fileToDataUri = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

export default function Studio() {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('Modern');
  const [activeTab, setActiveTab] = useState('text');
  
  const [sourceImageFile, setSourceImageFile] = useState<File | null>(null);
  const [floorPlanFile, setFloorPlanFile] = useState<File | null>(null);
  
  const [generatedImages, setGeneratedImages] = useState<string[] | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  const [isLoading, startGenerationTransition] = useTransition();
  const [isEditing, startEditTransition] = useTransition();
  const { toast } = useToast();
  
  const resetInputs = () => {
    setPrompt('');
  }

  const handleClear = () => {
    setGeneratedImages(null);
    setSelectedImageIndex(0);
  }

  const handleGenerationSubmit = (mode: 'text' | 'image' | 'floorplan') => {
    startGenerationTransition(async () => {
      setGeneratedImages(null); 
      
      try {
        let result;
        if (mode === 'text') {
            if (!prompt || !style) {
                toast({ variant: "destructive", title: "Missing fields", description: "Please provide a prompt and select a style." });
                return;
            }
            result = await generateDesignAction({ prompt, style, mode: 'text' });
            if (result.success) {
              setGeneratedImages(result.data.data);
            }
        } else if (mode === 'image') {
            if (!sourceImageFile || !prompt) {
                toast({ variant: "destructive", title: "Missing fields", description: "Please upload a base image and provide an edit prompt." });
                return;
            }
            const baseImage = await fileToDataUri(sourceImageFile);
            result = await generateDesignAction({ prompt, style, mode: 'image', baseImage });
             if (result.success) {
                setGeneratedImages(result.data.data);
             }
        } else if (mode === 'floorplan') {
            if (!floorPlanFile || !style) {
                 toast({ variant: "destructive", title: "Missing fields", description: "Please upload a floor plan and select a style." });
                return;
            }
            const floorPlan = await fileToDataUri(floorPlanFile);
            result = await generateDesignAction({ prompt, style, mode: 'floorplan', floorPlan });
            if (result.success) {
              setGeneratedImages(result.data.data);
            }
        } else {
            return;
        }

        if (result && result.success) {
          setSelectedImageIndex(0);
          resetInputs();
        } else {
          throw new Error(result?.error || 'An unexpected error occurred.');
        }

      } catch (error) {
        toast({
          variant: 'destructive',
          title: 'Generation Failed',
          description: error instanceof Error ? error.message : 'Please try again later.',
        });
      }
    });
  };

  const handleEditSubmit = (editPrompt: string) => {
    if (!generatedImages || generatedImages.length === 0) {
        toast({ variant: "destructive", title: "No image to edit", description: "Please generate an image first." });
        return;
    }

    startEditTransition(async () => {
        try {
            const baseImage = generatedImages[selectedImageIndex];
            const result = await editDesignAction({ query: `Edit this image with the following prompt: ${editPrompt}` });

            if (result && result.success) {
                setGeneratedImages([result.data.data]);
                setSelectedImageIndex(0); 
            } else {
                throw new Error(result?.error || 'An unexpected error occurred.');
            }
        } catch (error) {
             toast({
                variant: 'destructive',
                title: 'Edit Failed',
                description: error instanceof Error ? error.message : 'Please try again later.',
            });
        }
    });
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 h-full max-h-[calc(100vh-5rem)]">
        <div className="lg:col-span-3 h-full">
            <GenerationPanel
                prompt={prompt}
                setPrompt={setPrompt}
                style={style}
                setStyle={setStyle}
                setSourceImage={setSourceImageFile}
                sourceImage={sourceImageFile}
                setFloorPlan={setFloorPlanFile}
                floorPlan={floorPlanFile}
                handleSubmit={handleGenerationSubmit}
                isLoading={isLoading}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
            />
        </div>
        <div className="lg:col-span-4 h-full">
            <ImageEditor 
                generatedImages={generatedImages} 
                setSelectedIndex={setSelectedImageIndex}
                selectedIndex={selectedImageIndex}
                isLoading={isLoading}
                onEdit={handleEditSubmit}
                isEditing={isEditing}
                onClear={handleClear}
            />
        </div>
    </div>
  );
}