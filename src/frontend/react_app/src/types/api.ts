/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

/**
 * Status
 */
export type TicketStatus = 0 | 1 | 2 | 3 | 4 | 5 | 6;
/**
 * Urgency
 */
export type Urgency = 0 | 1 | 2 | 3 | 4 | 5 | 6;
/**
 * Impact
 */
export type Impact = 0 | 1 | 2 | 3 | 4 | 5 | 6;
/**
 * Ticket type
 */
export type TicketType = 0 | 1 | 2;

/**
 * Subset of ticket fields exposed to the frontend.
 */
export interface CleanTicketDTO {
  /**
   * Ticket identifier
   */
  id: number;
  /**
   * Short summary
   */
  name?: string;
  /**
   * Detailed description
   */
  content?: string | null;
  status?: TicketStatus;
  /**
   * Priority
   */
  priority?: string | null;
  urgency?: Urgency;
  impact?: Impact;
  type?: TicketType;
  /**
   * Creation timestamp
   */
  date_creation?: string | null;
}
