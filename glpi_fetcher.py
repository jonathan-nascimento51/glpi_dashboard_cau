import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from glpi_session import GLPISession, Credentials
from glpi_errors import GLPIAPIError, GLPINotFoundError
from config import GLPI_BASE_URL, GLPI_APP_TOKEN, GLPI_USERNAME, GLPI_PASSWORD, GLPI_USER_TOKEN, FETCH_PAGE_SIZE

logger = logging.getLogger(__name__)

class GLPIFetcher:
    """
    Fetches ticket data from the GLPI API, implementing pagination and filtering.
    Wraps the GLPISession for API interactions.
    """
    def __init__(self):
        self.credentials = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD
        )
        self.glpi_session = GLPISession(GLPI_BASE_URL, self.credentials)

    async def fetch_tickets(self, since_date: Optional[datetime] = None) -> List]:
        """
        Fetches tickets from GLPI API, handling pagination.
        Applies 'since' filter for date_creation.
        [5, 9, 10]
        """
        all_tickets: List] =
        offset = 0
        has_more_data = True

        async with self.glpi_session as session:
            while has_more_data:
                params: Dict]]] = {
                    "range": f"{offset}-{offset + FETCH_PAGE_SIZE - 1}", # GLPI range is inclusive [5]
                    "expand_dropdowns": True, # Get human-readable names [5]
                    "only_id": False, # We need full data for the dashboard [5]
                    "is_deleted": False # Only active tickets
                }

                criteria =
                if since_date:
                    # GLPI expects 'YYYY-MM-DD HH:MM:SS' format for datetime
                    date_str = since_date.strftime("%Y-%m-%d %H:%M:%S")
                    # Assuming field ID for date_creation is 2
                    criteria.append({
                        "link": "AND",
                        "field": 2, # Placeholder for GLPI 'date_creation' field ID
                        "searchtype": "morethan", # created > since
                        "value": date_str
                    })
                
                if criteria:
                    params["criteria"] = criteria

                logger.info(f"Fetching tickets from GLPI: range={params['range']}, since={since_date}")
                try:
                    # Use the /search/Ticket endpoint as requested [9, 11, 10]
                    response_data = await session.get("search/Ticket", params=params)
                    
                    # GLPI search endpoint typically returns a list of dictionaries [11]
                    tickets_page = response_data if isinstance(response_data, list) else response_data.get('data',)

                    if not tickets_page:
                        has_more_data = False
                        logger.info("No more tickets to fetch from GLPI.")
                        break

                    all_tickets.extend(tickets_page)
                    logger.info(f"Fetched {len(tickets_page)} tickets. Total fetched: {len(all_tickets)}")

                    # Check if the number of items returned is less than the page size,
                    # indicating it's the last page.
                    if len(tickets_page) < FETCH_PAGE_SIZE:
                        has_more_data = False
                    else:
                        offset += FETCH_PAGE_SIZE

                except GLPINotFoundError:
                    logger.info("GLPI search endpoint returned 404, likely no more data or invalid query.")
                    has_more_data = False
                except GLPIAPIError as e:
                    logger.error(f"Error fetching tickets from GLPI API: {e.status_code} - {e.message}")
                    has_more_data = False # Stop on API errors
                except Exception as e:
                    logger.error(f"An unexpected error occurred during GLPI ticket fetch: {e}")
                    has_more_data = False # Stop on unexpected errors
        
        logger.info(f"Finished fetching all tickets. Total: {len(all_tickets)}")
        return all_tickets