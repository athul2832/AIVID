'use server';

import {
  generateInteriorDesignFromPrompt,
  GenerateInteriorDesignFromPromptInput,
  GenerateInteriorDesignFromPromptOutput,
} from '@/ai/flows/generate-interior-design-from-prompt';
import {
  editInteriorDesignWithText,
  EditInteriorDesignWithTextInput,
  EditInteriorDesignWithTextOutput,
} from '@/ai/flows/edit-interior-design-with-text';
import {
  generateImageFromCadFloorPlan,
  GenerateImageFromCadFloorPlanInput,
  GenerateImageFromCadFloorPlanOutput,
} from '@/ai/flows/generate-image-from-cad-floor-plan';
import {
  getDesignSuggestionsFromChat,
  GetDesignSuggestionsInput,
  GetDesignSuggestionsOutput,
} from '@/ai/flows/get-design-suggestions-from-chat';
import {
  summarizeDesignStyles,
  SummarizeDesignStylesInput,
  SummarizeDesignStylesOutput,
} from '@/ai/flows/summarize-design-styles';
import {
  generateImagePrompt,
  GenerateImagePromptInput,
  GenerateImagePromptOutput,
} from '@/ai/flows/generate-image-prompt';
import {
  suggestImageEdits,
  SuggestImageEditsInput,
  SuggestImageEditsOutput,
} from '@/ai/flows/suggest-image-edits';

type ActionResult<U> = { success: true; data: U } | { success: false; error: string };

async function handleAction<T, U>(input: T, action: (input: T) => Promise<U>): Promise<ActionResult<U>> {
  try {
    const result = await action(input);
    return { success: true, data: result };
  } catch (error) {
    console.error('An error occurred in handleAction:', error);
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
    return { success: false, error: errorMessage };
  }
}

export async function generateDesignAction(input: GenerateInteriorDesignFromPromptInput): Promise<ActionResult<GenerateInteriorDesignFromPromptOutput>> {
  return handleAction(input, generateInteriorDesignFromPrompt);
}

export async function editDesignAction(input: EditInteriorDesignWithTextInput): Promise<ActionResult<EditInteriorDesignWithTextOutput>> {
  return handleAction(input, editInteriorDesignWithText);
}

export async function generateFromFloorPlanAction(input: GenerateImageFromCadFloorPlanInput): Promise<ActionResult<GenerateImageFromCadFloorPlanOutput>> {
  return handleAction(input, generateImageFromCadFloorPlan);
}

export async function getChatSuggestionAction(input: GetDesignSuggestionsInput): Promise<ActionResult<GetDesignSuggestionsOutput>> {
  return handleAction(input, getDesignSuggestionsFromChat);
}

export async function summarizeStylesAction(input: SummarizeDesignStylesInput): Promise<ActionResult<SummarizeDesignStylesOutput>> {
  return handleAction(input, summarizeDesignStyles);
}

export async function generatePromptAction(input: GenerateImagePromptInput): Promise<ActionResult<GenerateImagePromptOutput>> {
  return handleAction(input, generateImagePrompt);
}

export async function suggestEditsAction(input: SuggestImageEditsInput): Promise<ActionResult<SuggestImageEditsOutput>> {
  return handleAction(input, suggestImageEdits);
}
