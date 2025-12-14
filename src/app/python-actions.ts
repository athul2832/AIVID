'use server';

// Backend URL - defaults to localhost:8001 but can be overridden by environment variable
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';

type ActionResult<U> = { success: true; data: U } | { success: false; error: string };

async function handleBackendRequest<T, U>(endpoint: string, input: T): Promise<ActionResult<U>> {
  try {
    let response: Response;
    
    // For /generate-design endpoint, send as form data
    if (endpoint === '/generate-design') {
      const formData = new FormData();
      Object.entries(input as Record<string, any>).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          formData.append(key, value);
        }
      });
      
      response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });
    } else {
      // For other endpoints, send as JSON
      response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
      });
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend request failed with status ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    return { success: true, data: result };
  } catch (error) {
    console.error('An error occurred in handleBackendRequest:', error);
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
    return { success: false, error: errorMessage };
  }
}

// Define input/output types that match the Python backend
interface GenerateDesignInput {
  prompt: string;
  style: string;
  mode: string; // 'text', 'image', 'floorplan'
  baseImage?: string; // base64 encoded image
  floorPlan?: string; // base64 encoded image
}

interface GenerateDesignOutput {
  data: string[]; // array of image URLs
  prompt?: string;
  final_prompt?: string;
  image_ids?: string[];
}

interface ChatInput {
  query: string;
  session_id?: string;
}

interface ChatOutput {
  data: string;
}

interface SuggestEditsInput {
  baseImage?: string;
  designStyle?: string;
}

interface SuggestEditsOutput {
  data: string;
}

interface GeneratePromptInput {
  style: string;
  topic?: string;
}

interface GeneratePromptOutput {
  data: string;
}

// Flow interfaces
interface FlowGenerateImagePromptInput {
  topic: string;
}

interface FlowGenerateImagePromptOutput {
  generatedPrompt: string;
}

interface FlowGenerateInteriorDesignInput {
  prompt: string;
  designStyle: string;
}

interface FlowGenerateInteriorDesignOutput {
  imageUrls: string[];
}

interface FlowEditInteriorDesignInput {
  baseImage: string;
  editPrompt: string;
  designStyle?: string;
}

interface FlowEditInteriorDesignOutput {
  editedImages: string[];
}

interface FlowGetDesignSuggestionsInput {
  query: string;
}

interface FlowGetDesignSuggestionsOutput {
  suggestion: string;
}

interface FlowSummarizeDesignStylesInput {
  designStyles: string[];
}

interface FlowSummarizeDesignStylesOutput {
  summaries: string[];
}

interface FlowSuggestImageEditsInput {
  baseImage: string;
  designStyle?: string;
}

interface FlowSuggestImageEditsOutput {
  suggestion: string;
}

interface FlowGenerateImageFromCadFloorPlanInput {
  cadFloorPlanDataUri: string;
  designStyle: string;
  prompt?: string;
}

interface FlowGenerateImageFromCadFloorPlanOutput {
  generatedImageUrls: string[];
}

// Export the action functions
export async function generateDesignAction(input: GenerateDesignInput): Promise<ActionResult<GenerateDesignOutput>> {
  return handleBackendRequest<GenerateDesignInput, GenerateDesignOutput>('/generate-design', input);
}

export async function chatAction(input: ChatInput): Promise<ActionResult<ChatOutput>> {
  return handleBackendRequest<ChatInput, ChatOutput>('/chat', input);
}

export async function suggestEditsAction(input: SuggestEditsInput): Promise<ActionResult<SuggestEditsOutput>> {
  return handleBackendRequest<SuggestEditsInput, SuggestEditsOutput>('/suggest-edits', input);
}

export async function generatePromptAction(input: GeneratePromptInput): Promise<ActionResult<GeneratePromptOutput>> {
  return handleBackendRequest<GeneratePromptInput, GeneratePromptOutput>('/generate-new-prompt', input);
}

// Flow action functions
export async function flowGenerateImagePrompt(input: FlowGenerateImagePromptInput): Promise<ActionResult<FlowGenerateImagePromptOutput>> {
  return handleBackendRequest<FlowGenerateImagePromptInput, FlowGenerateImagePromptOutput>('/flow/generate-image-prompt', input);
}

export async function flowGenerateInteriorDesign(input: FlowGenerateInteriorDesignInput): Promise<ActionResult<FlowGenerateInteriorDesignOutput>> {
  return handleBackendRequest<FlowGenerateInteriorDesignInput, FlowGenerateInteriorDesignOutput>('/flow/generate-interior-design-from-prompt', input);
}

export async function flowEditInteriorDesign(input: FlowEditInteriorDesignInput): Promise<ActionResult<FlowEditInteriorDesignOutput>> {
  return handleBackendRequest<FlowEditInteriorDesignInput, FlowEditInteriorDesignOutput>('/flow/edit-interior-design-with-text', input);
}

export async function flowGetDesignSuggestions(input: FlowGetDesignSuggestionsInput): Promise<ActionResult<FlowGetDesignSuggestionsOutput>> {
  return handleBackendRequest<FlowGetDesignSuggestionsInput, FlowGetDesignSuggestionsOutput>('/flow/get-design-suggestions-from-chat', input);
}

export async function flowSummarizeDesignStyles(input: FlowSummarizeDesignStylesInput): Promise<ActionResult<FlowSummarizeDesignStylesOutput>> {
  return handleBackendRequest<FlowSummarizeDesignStylesInput, FlowSummarizeDesignStylesOutput>('/flow/summarize-design-styles', input);
}

export async function flowSuggestImageEdits(input: FlowSuggestImageEditsInput): Promise<ActionResult<FlowSuggestImageEditsOutput>> {
  return handleBackendRequest<FlowSuggestImageEditsInput, FlowSuggestImageEditsOutput>('/flow/suggest-image-edits', input);
}

export async function flowGenerateImageFromCadFloorPlan(input: FlowGenerateImageFromCadFloorPlanInput): Promise<ActionResult<FlowGenerateImageFromCadFloorPlanOutput>> {
  return handleBackendRequest<FlowGenerateImageFromCadFloorPlanInput, FlowGenerateImageFromCadFloorPlanOutput>('/flow/generate-image-from-cad-floor-plan', input);
}