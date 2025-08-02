/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from Pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the Pydantic models and then re-run the script
*/

/**
 * Normalized ticket used internally by the application.
 */
export interface CleanTicketDTO {
  id: number;
  name?: string | null;
  status: string;
  /**
   * Priority as a human-readable label
   */
  priority?: string | null;
  date_creation?: string | null;
  assigned_to?: string;
  requester?: string | null;
  group?: string | null;
  [k: string]: unknown;
}
