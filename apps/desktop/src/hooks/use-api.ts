import { useState, useCallback, useEffect, useRef } from "react";
import { api, ApiError } from "@/lib/api-client";

interface UseApiOptions<T> {
  /** Fetch data on mount */
  immediate?: boolean;
  /** Initial data */
  initialData?: T;
  /** Transform response */
  transform?: (data: unknown) => T;
}

interface UseApiReturn<T> {
  data: T | undefined;
  error: string | null;
  isLoading: boolean;
  refetch: () => Promise<void>;
}

export function useApi<T>(
  endpoint: string,
  options: UseApiOptions<T> = {}
): UseApiReturn<T> {
  const { immediate = true, initialData, transform } = options;
  const [data, setData] = useState<T | undefined>(initialData);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(immediate);
  const mountedRef = useRef(true);

  const refetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.get<T>(endpoint);
      if (mountedRef.current) {
        setData(transform ? transform(result) : result);
      }
    } catch (err) {
      if (mountedRef.current) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Ocorreu um erro inesperado.");
        }
      }
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [endpoint, transform]);

  useEffect(() => {
    mountedRef.current = true;
    if (immediate) {
      refetch();
    }
    return () => {
      mountedRef.current = false;
    };
  }, [immediate, refetch]);

  return { data, error, isLoading, refetch };
}
