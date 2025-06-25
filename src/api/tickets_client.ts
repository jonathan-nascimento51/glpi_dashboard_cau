import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// --- DTOs (Data Transfer Objects) ---

/**
 * Represents a filter object for querying GLPI tickets.
 */
export interface TicketFilter {
  status?: number; // e.g., [1, 2] (GLPI status IDs)
  priority?: number; // e.g., [3, 4] (GLPI priority IDs)
  since?: Date; // created > since
  assigneeId?: number; // ID of the assigned user
  range?: { start: number; end: number }; // Pagination range, default 0-49
  lean?: boolean; // If true, only returns ticket IDs for optimization
}

/**
 * Represents a full GLPI Ticket object.
 * Note: This interface includes common fields based on GLPI API documentation snippets.
 * The actual fields returned depend on GLPI configuration and API version.
 * [5]
 */
export interface Ticket {
  id: number;
  name: string;
  date_creation: string; // ISO 8601 datetime string [6]
  status: number; // GLPI status ID (e.g., 1: New, 2: Processing (Assigned), 5: Solved, 6: Closed) [7]
  priority: number; // GLPI priority ID (e.g., 1: Very Low, 5: Very High) [7]
  content?: string; // [5]
  closedate?: string; // [5]
  date_mod?: string; // [5]
  impact?: number; // [5]
  itilcategories_id?: number; // [5]
  // Add other fields as needed based on GLPI.Ticket context output [5]
  [key: string]: any; // Allow for additional properties not explicitly defined
}

/**
 * Represents a lean GLPI Ticket object, containing only the ID.
 * Used when the `lean` filter option is true. [8]
 */
export interface LeanTicket {
  id: number;
}

// --- GLPI API Field IDs (Placeholders) ---
// These IDs are specific to your GLPI instance's search options.
// You would typically retrieve these from the /api/listSearchOptions/:itemtype endpoint. [9]
// For demonstration, we use common assumed IDs or placeholders.
const GLPI_FIELD_IDS = {
  TICKET_STATUS: 12, // Common placeholder for Ticket Status field ID (e.g., 'status')
  TICKET_PRIORITY: 10, // Common placeholder for Ticket Priority field ID (e.g., 'priority')
  TICKET_DATE_CREATION: 2, // Common placeholder for Ticket Creation Date field ID (e.g., 'date_creation') [6, 10]
  TICKET_ASSIGNED_TO: 4, // Common placeholder for Assigned To user field ID (e.g., 'users_id_assign' or similar) [11]
};

// --- API Client Configuration ---

const API_BASE_URL = process.env.GLPI_API_BASE_URL |
| 'https://your-glpi-instance/apirest.php';
const APP_TOKEN = process.env.GLPI_APP_TOKEN |
| 'YOUR_APP_TOKEN'; // Replace with your actual App-Token [12, 13]
const SESSION_TOKEN_KEY = 'glpi-session-token'; // Key for storing session token (e.g., in localStorage or a global state)

let currentSessionToken: string | null = null;

const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json', // [8]
    'App-Token': APP_TOKEN, // [8]
  },
  timeout: 10000, // 10 seconds timeout
});

// --- Axios Interceptors ---

// Request Interceptor: Inject Session-Token [8, 14]
axiosInstance.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    if (currentSessionToken) {
      config.headers = {
       ...config.headers,
        'Session-Token': currentSessionToken,
      };
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle 429 Too Many Requests with exponential back-off [15, 16]
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const { config, response } = error;
    const originalRequest = config;

    // Retry configuration
    const MAX_RETRIES = 3;
    const RETRY_DELAY_MS = 1000; // Base delay for exponential back-off

    if (response && response.status === 429) { // [15, 16]
      originalRequest!._retryCount = originalRequest!._retryCount |
| 0;

      if (originalRequest!._retryCount < MAX_RETRIES) {
        originalRequest!._retryCount += 1;
        const delay = RETRY_DELAY_MS * Math.pow(2, originalRequest!._retryCount - 1);
        console.warn(`Rate limit hit (429). Retrying in ${delay}ms (attempt ${originalRequest!._retryCount}/${MAX_RETRIES})...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return axiosInstance(originalRequest!); // Retry the original request
      } else {
        console.error(`Max retries (${MAX_RETRIES}) exceeded for 429 error.`);
      }
    }

    // For other errors, or if 429 retries are exhausted, re-throw the error
    return Promise.reject(error);
  }
);

// --- Session Management (Simplified for client-side) ---
// In a real application, session management might involve a dedicated authentication service
// or a more robust state management solution (e.g., Redux, Zustand).
// For this self-contained module, we'll use a simple global variable and localStorage.

/**
 * Initializes a GLPI session and stores the session token. [8, 7, 14]
 * In a real application, this would typically be called once on app startup or login.
 * @param userToken Optional user token for authentication. [14, 5]
 * @param username Optional username for authentication. [7, 14]
 * @param password Optional password for authentication. [7, 14]
 * @returns A Promise that resolves when the session is initiated.
 */
export async function initGLPISession(
  userToken?: string,
  username?: string,
  password?: string
): Promise<void> {
  const initSessionUrl = '/initSession'; // [8]
  let payload: { user_token?: string; login?: string; password?: string } = {};

  if (userToken) {
    payload.user_token = userToken;
  } else if (username && password) {
    payload.login = username;
    payload.password = password;
  } else {
    throw new Error('Either userToken or username/password must be provided for session initiation.');
  }

  try {
    const response = await axiosInstance.post(initSessionUrl, payload);
    currentSessionToken = response.data.session_token;
    if (currentSessionToken) {
      localStorage.setItem(SESSION_TOKEN_KEY, currentSessionToken);
      console.log('GLPI session initiated and token stored.');
    } else {
      console.error('Failed to get session_token from initSession response.');
      throw new Error('Session token not received.');
    }
  } catch (error) {
    console.error('Error initiating GLPI session:', error);
    throw error;
  }
}

/**
 * Kills the current GLPI session. [8]
 * In a real application, this would typically be called on logout.
 */
export async function killGLPISession(): Promise<void> {
  if (!currentSessionToken) {
    console.warn('No active GLPI session to kill.');
    return;
  }

  const killSessionUrl = '/killSession'; // [8]
  try {
    await axiosInstance.get(killSessionUrl);
    currentSessionToken = null;
    localStorage.removeItem(SESSION_TOKEN_KEY);
    console.log('GLPI session killed.');
  } catch (error) {
    console.error('Error killing GLPI session:', error);
    throw error;
  }
}

/**
 * Loads the session token from localStorage on module initialization.
 */
(function loadSessionTokenFromStorage() {
  const storedToken = localStorage.getItem(SESSION_TOKEN_KEY);
  if (storedToken) {
    currentSessionToken = storedToken;
    console.log('GLPI session token loaded from storage.');
  }
})();

// --- Helper to build GLPI criteria array ---

/**
 * Converts a TicketFilter object into GLPI API 'criteria' query parameters. [9, 10]
 * @param filter The filter object.
 * @returns An array of criterion objects for the GLPI API.
 */
function buildCriteria(filter: TicketFilter): any {
  const criteria: any =;
  let criterionIndex = 0;

  if (filter.status && filter.status.length > 0) {
    filter.status.forEach((statusId, index) => {
      criteria.push({
        link: index === 0? 'AND' : 'OR', // Use AND for first, OR for subsequent statuses [10]
        field: GLPI_FIELD_IDS.TICKET_STATUS,
        searchtype: 'equals', // [10]
        value: statusId.toString(),
      });
      criterionIndex++;
    });
  }

  if (filter.priority && filter.priority.length > 0) {
    filter.priority.forEach((priorityId, index) => {
      criteria.push({
        link: criterionIndex === 0? 'AND' : 'AND', // Always AND with other filter types
        field: GLPI_FIELD_IDS.TICKET_PRIORITY,
        searchtype: 'equals', // [10]
        value: priorityId.toString(),
      });
      criterionIndex++;
    });
  }

  if (filter.since) {
    // GLPI expects 'YYYY-MM-DD HH:MM:SS' format for datetime [6]
    const dateString = filter.since.toISOString().slice(0, 19).replace('T', ' ');
    criteria.push({
      link: criterionIndex === 0? 'AND' : 'AND',
      field: GLPI_FIELD_IDS.TICKET_DATE_CREATION,
      searchtype: 'morethan', // created > since [10]
      value: dateString,
    });
    criterionIndex++;
  }

  if (filter.assigneeId) {
    criteria.push({
      link: criterionIndex === 0? 'AND