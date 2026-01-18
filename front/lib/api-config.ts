/**
 * Centralized API configuration for Property Investment Calculator
 * Handles backend URL configuration with environment variable support
 */

/**
 * Get the base API URL from environment variables
 * Falls back to localhost:8000 if not configured
 */
function getApiUrl(): string {
  // In Next.js, only env vars prefixed with NEXT_PUBLIC_ are available in the browser
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    console.warn('NEXT_PUBLIC_API_URL not set, using default localhost:8000');
    return 'http://localhost:8000';
  }

  // Remove trailing slash if present
  return apiUrl.replace(/\/$/, '');
}

/**
 * API endpoints configuration
 */
export const API_CONFIG = {
  baseUrl: getApiUrl(),
  endpoints: {
    simulate: '/simulate',
    strategyPresets: '/strategy-presets',
    validate: '/validate',
    health: '/health'
  }
} as const;

/**
 * Helper function to build full API URLs
 */
export function buildApiUrl(endpoint: keyof typeof API_CONFIG.endpoints): string {
  return `${API_CONFIG.baseUrl}${API_CONFIG.endpoints[endpoint]}`;
}

/**
 * Helper function for making API requests with proper error handling
 */
export async function apiRequest<T>(
  endpoint: keyof typeof API_CONFIG.endpoints,
  options: RequestInit = {}
): Promise<T> {
  const url = buildApiUrl(endpoint);

  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
