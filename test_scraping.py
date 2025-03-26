from src.data_scraping import get_elo_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_elo_scraping():
    """Test the ELO data scraping functionality"""
    try:
        # Get ELO data
        df_elo = get_elo_data()
        
        if df_elo is None:
            logger.error("Failed to get ELO data")
            return False
            
        # Check number of teams
        num_teams = len(df_elo)
        logger.info(f"Number of teams found: {num_teams}")
        
        if num_teams != 20:
            logger.error(f"Expected 20 teams, but found {num_teams}")
            return False
            
        # Display the data
        logger.info("\nTeam ELO Ratings:")
        for _, row in df_elo.iterrows():
            logger.info(f"{row['Team']}: {row['Elo']}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_elo_scraping()
    if success:
        logger.info("\nTest completed successfully!")
    else:
        logger.error("\nTest failed!") 