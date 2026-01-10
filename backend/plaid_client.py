"""
Plaid Client Setup for Fiscal Pilot
NOTE: This uses Plaid sandbox (demo only), not RBI Account Aggregator.
In production, this would be replaced with RBI Account Aggregator framework.

SECURITY: All Plaid secrets and access tokens stored server-side only.
"""
from plaid.api.plaid_api import PlaidApi
from plaid.configuration import Configuration, Environment
from plaid.api_client import ApiClient
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.products import Products
from datetime import datetime, timedelta, date
from .config import settings


def get_plaid_client():
    """
    Initialize and return Plaid API client
    
    SECURITY: Uses environment variables loaded from .env (not exposed to frontend)
    """
    # Determine environment host (use Environment.Sandbox for demo)
    # NOTE: This uses Plaid sandbox for demonstration purposes only
    if settings.PLAID_ENV == 'sandbox' or settings.PLAID_ENV == 'development':
        host = Environment.Sandbox  # Use Sandbox for both sandbox and development
    elif settings.PLAID_ENV == 'production':
        host = Environment.Production
    else:
        host = Environment.Sandbox  # Default to sandbox for demo
    
    configuration = Configuration(
        host=host,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET,
        }
    )
    
    api_client = ApiClient(configuration)
    return PlaidApi(api_client)


def create_link_token(user_id: int, client_name: str = "Fiscal Pilot") -> str:
    """
    Create a Plaid Link token for frontend integration
    
    Args:
        user_id: User ID for token association
        client_name: Application name shown in Plaid Link
        
    Returns:
        link_token: Token to pass to Plaid Link frontend component
        
    NOTE: This token is one-time use and expires quickly
    """
    client = get_plaid_client()
    
    request = LinkTokenCreateRequest(
        products=[Products('transactions')],  # Only request transactions product
        client_name=client_name,
        country_codes=[CountryCode('US')],  # Plaid sandbox uses US banks
        language='en',
        user=LinkTokenCreateRequestUser(
            client_user_id=str(user_id)  # Associate with user
        )
    )
    
    response = client.link_token_create(request)
    # Plaid SDK returns response object, access link_token attribute
    return response['link_token'] if isinstance(response, dict) else response.link_token


def exchange_public_token(public_token: str) -> dict:
    """
    Exchange public_token for access_token
    
    SECURITY: access_token must be stored server-side only, never exposed to frontend
    
    Args:
        public_token: One-time token from Plaid Link frontend
        
    Returns:
        dict with access_token and item_id
    """
    client = get_plaid_client()
    
    request = ItemPublicTokenExchangeRequest(
        public_token=public_token
    )
    
    response = client.item_public_token_exchange(request)
    
    # Plaid SDK returns response object or dict, handle both
    if isinstance(response, dict):
        access_token = response.get('access_token')
        item_id = response.get('item_id')
    else:
        access_token = getattr(response, 'access_token', None)
        item_id = getattr(response, 'item_id', None)
    
    return {
        'access_token': access_token,
        'item_id': item_id
    }


def get_institution_name(access_token: str) -> str:
    """
    Get institution name for a given access_token
    
    Args:
        access_token: Plaid access token
        
    Returns:
        Institution name
    """
    client = get_plaid_client()
    
    try:
        # Get item info
        from plaid.model.item_get_request import ItemGetRequest
        
        item_request = ItemGetRequest(access_token=access_token)
        item_response = client.item_get(item_request)
        
        # Access item object
        item = item_response.item if hasattr(item_response, 'item') else item_response['item']
        institution_id = item.institution_id if hasattr(item, 'institution_id') else (item.get('institution_id') if isinstance(item, dict) else None)
        
        if not institution_id:
            return "Unknown Bank"
        
        # Get institution details
        from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
        
        inst_request = InstitutionsGetByIdRequest(
            institution_id=institution_id,
            country_codes=[CountryCode('US')]
        )
        institution_response = client.institutions_get_by_id(inst_request)
        
        # Access institution object
        institution = institution_response.institution if hasattr(institution_response, 'institution') else institution_response['institution']
        return institution.name if hasattr(institution, 'name') else (institution.get('name', 'Unknown Bank') if isinstance(institution, dict) else 'Unknown Bank')
    except Exception as e:
        print(f"Error fetching institution name: {str(e)}")
        return "Unknown Bank"


def fetch_transactions(access_token: str, days: int = 30) -> list:
    """
    Fetch transactions from Plaid for the last N days
    
    SECURITY: access_token must come from server-side storage only
    
    Args:
        access_token: Plaid access token (server-side only)
        days: Number of days to fetch (default 30)
        
    Returns:
        List of transaction dictionaries with Plaid data
    """
    client = get_plaid_client()
    
    # Calculate date range - Plaid accepts Python date objects
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    
    try:
        response = client.transactions_get(request)
        
        # Access transactions list (handle both object and dict response)
        transactions = response.transactions if hasattr(response, 'transactions') else response.get('transactions', [])
        total_transactions = response.total_transactions if hasattr(response, 'total_transactions') else response.get('total_transactions', len(transactions))
        next_cursor = response.next_cursor if hasattr(response, 'next_cursor') else response.get('next_cursor')
        
        # Handle pagination if needed (Plaid returns up to 500 transactions per call)
        while next_cursor and len(transactions) < total_transactions:
            options = TransactionsGetRequestOptions(cursor=next_cursor)
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,  # Reuse same date objects
                end_date=end_date,
                options=options
            )
            paginated_response = client.transactions_get(request)
            
            paginated_txs = paginated_response.transactions if hasattr(paginated_response, 'transactions') else paginated_response.get('transactions', [])
            transactions.extend(paginated_txs)
            
            next_cursor = paginated_response.next_cursor if hasattr(paginated_response, 'next_cursor') else paginated_response.get('next_cursor')
            if not next_cursor:
                break
        
        return transactions
    except Exception as e:
        print(f"Error fetching transactions from Plaid: {str(e)}")
        raise
