# config.py
import os
import boto3
from strands.models import BedrockModel


class ExpansionPlaningInputs:
    """
    All Expansion planning Inputs are configured here
    """
    PROFILE_NAME = 'kfadmin' #AWS CLI profile to access account where workloads are deployed
    SOURCE_REGION = 'us-east-1' # Source region where workloads are deployed 
    TARGET_REGIONS = ['ap-southeast-7', 'ap-southeast-5', 'eu-south-1', 'mx-central-1'] # Target regions where workloads need to be expanded to
    CTRAIL_LOOKBACK_DAYS = 7


class Constants:
    """Constants that don't change between environments"""
    # Bedrock Agent constants
    INFRA_REGION = "us-east-1" 
    INFRA_ACCOUNT = "606357619201" # Replace with your actual account ID to use Bedrock Models
    BEDROCK_AWS_CLI_PROFILE = "kfadmin" #Replace with actual AWS CLI Profile to access Bedrock Models

    # Agent-specific configurations
    ORCHESTRATOR_TEMPERATURE = 0.7
    DEPENDENCY_COLLECTOR_TEMPERATURE = 0.9
    DEPENDENCY_AUDITOR_TEMPERATURE = 0.7
    RECOMMENDER_TEMPERATURE = 0.2
    
    # Rate limiting configurations
    REQUEST_DELAY = 1.0  # Delay between requests in seconds
    MAX_RETRIES = 3      # Maximum retry attempts for throttling

    # Output directories
    OUTPUT_DIR = "analysis_output"

    @classmethod
    def set_tool_configurations(cls):
        """Sets up required environment variables for tool configurations."""
        os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"
        os.environ["BYPASS_TOOL_CONSENT"] = "true"



class Config:
    @staticmethod
    def get_infra_account_id() -> str:
        """Get the infrastructure account ID."""
        return Constants.INFRA_ACCOUNT  

    @staticmethod
    def get_bedrock_model_id() -> str:
        """Get the Bedrock model ID. Returns default if not specified."""
        return os.environ.get(
            "BEDROCK_MODEL_ID",
            #"anthropic.claude-3-5-sonnet-20241022-v2:0"
            "us.anthropic.claude-sonnet-4-20250514-v1:0"  # Alternative model with potentially higher limits
        )

    @classmethod
    def construct_bedrock_model(cls, temperature: float, profile: str='kfadmin') -> BedrockModel:
        """
        Constructs a BedrockModel with the specified temperature and retry configuration.
        """
        model_id = (
            f"arn:aws:bedrock:{Constants.INFRA_REGION}:"
            f"{cls.get_infra_account_id()}:inference-profile/"
            f"{cls.get_bedrock_model_id()}"
        )
        bedrock_session = boto3.Session(profile_name=Constants.AWS_CLI_PROFILE, region_name=Constants.INFRA_REGION)

        # Configure retry settings for the boto3 client
        from botocore.config import Config as BotocoreConfig
        retry_config = BotocoreConfig(
            retries={
                'max_attempts': Constants.MAX_RETRIES,
                'mode': 'adaptive'  # Use adaptive retry mode for better throttling handling
            }
        )

        return BedrockModel(
            model_id=model_id,
            boto_session=bedrock_session,
            temperature=temperature,
            # Add retry configuration to the underlying boto3 client
            client_kwargs={'config': retry_config}
        )