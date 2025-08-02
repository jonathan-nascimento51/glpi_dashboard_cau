/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
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
