/**
 * Creates a stable string from an object, suitable for use in React Query keys.
 * It sorts keys to ensure that objects with the same keys and values produce the same string.
 * Note: This is a simplified version and does not handle nested objects.
 * @param obj The object to stringify.
 * @returns A stable string representation of the object.
 */
export const stableStringify = (obj: Record<string, unknown> | undefined | null): string => {
  if (!obj) {
    return '';
  }
  const sortedObj = Object.keys(obj)
    .sort((a, b) => a.localeCompare(b))
    .reduce<Record<string, unknown>>((acc, key) => {
      acc[key] = obj[key];
      return acc;
    }, {});
  return JSON.stringify(sortedObj);
};
