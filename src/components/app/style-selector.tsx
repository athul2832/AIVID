'use client';

import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { Label } from '../ui/label';
import { Palette } from 'lucide-react';

const designStyles = [
  'Modern',
  'Minimalist',
  'Scandinavian',
  'Bohemian',
  'Industrial',
  'Coastal',
];

type StyleSelectorProps = {
  selectedStyle: string;
  onStyleSelect: (style: string) => void;
};

export function StyleSelector({ selectedStyle, onStyleSelect }: StyleSelectorProps) {
  return (
    <div className="space-y-2">
      <Label className="flex items-center gap-2"><Palette className="h-4 w-4"/> Design Style</Label>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {designStyles.map((style) => (
          <div key={style} onClick={() => onStyleSelect(style)} className="cursor-pointer">
            <Card
              className={cn(
                'transition-all hover:shadow-md hover:-translate-y-0.5',
                selectedStyle === style
                  ? 'ring-2 ring-primary bg-primary/10'
                  : 'bg-muted/50 hover:bg-muted'
              )}
            >
              <CardContent className="p-3 flex items-center justify-center">
                <h3 className="text-sm font-semibold">{style}</h3>
              </CardContent>
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
}
