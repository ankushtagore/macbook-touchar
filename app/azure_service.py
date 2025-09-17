import logging
import os
import re
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from app.config import settings

# Make tenacity import optional
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

    # Create dummy decorators for development
    def retry(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def stop_after_attempt(n):
        return None

    def wait_exponential(*args, **kwargs):
        return None

    class RetryError(Exception):
        pass


# Make langchain import optional
try:
    from langchain_openai import AzureChatOpenAI

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

    # Create dummy class for development
    class AzureChatOpenAI:
        pass


logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Service for handling Azure OpenAI operations"""

    @classmethod
    def get_llm(cls, fallback_to_openai=False):
        """
        Get configured LangChain Azure OpenAI LLM instance

        Args:
            fallback_to_openai (bool): Whether to fallback to OpenAI if Azure is not configured
                                      This is kept for backward compatibility but should be set to False
                                      as we're focusing exclusively on Azure OpenAI

        Returns:
            AzureChatOpenAI: The Azure OpenAI language model instance

        Raises:
            ValueError: If Azure configuration is missing or invalid.
            RuntimeError: If connection to Azure OpenAI fails after retries.
        """
        try:
            # Make sure all required Azure OpenAI environment variables are set
            required_vars = {
                "AZURE_OPENAI_API_KEY": settings.AZURE_OPENAI_API_KEY,
                "AZURE_OPENAI_ENDPOINT": settings.AZURE_OPENAI_ENDPOINT,
                "AZURE_OPENAI_DEPLOYMENT_NAME": settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                "AZURE_OPENAI_API_VERSION": settings.AZURE_OPENAI_API_VERSION,
            }

            missing_vars = [k for k, v in required_vars.items() if not v]
            if missing_vars:
                error_msg = f"Missing required Azure OpenAI configuration values: {', '.join(missing_vars)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # IMPORTANT: Don't set the regular OPENAI_API_KEY from Azure key - this causes auth errors
            # Regular OpenAI uses different API keys than Azure OpenAI
            if (
                "OPENAI_API_KEY" in os.environ
                and os.environ.get("OPENAI_API_KEY") == settings.AZURE_OPENAI_API_KEY
            ):
                logger.warning(
                    "Removing OPENAI_API_KEY from environment as it contains an Azure key"
                )
                del os.environ["OPENAI_API_KEY"]

            # Clean up endpoint URL if needed - properly extract base URL
            endpoint = settings.AZURE_OPENAI_ENDPOINT

            # Pattern to match and extract the base Azure endpoint
            base_endpoint_pattern = (
                r"(https://[^/]+\.(?:openai|cognitive)\.azure\.com)(?:/.*)?"
            )
            match = re.match(base_endpoint_pattern, endpoint)

            if match:
                endpoint = match.group(1)
                logger.info(f"Extracted base Azure endpoint: {endpoint}")
            else:
                logger.warning(f"Unable to parse Azure endpoint from: {endpoint}")
                # Default fallback if unable to parse
                if "/deployments/" in endpoint:
                    endpoint = endpoint.split("/deployments/")[0]
                    logger.info(
                        f"Using fallback method to extract endpoint: {endpoint}"
                    )
                elif endpoint.endswith("/"):
                    endpoint = endpoint.rstrip("/")
                    logger.info(f"Removing trailing slash from endpoint: {endpoint}")

            # Create the Azure OpenAI client with retries
            try:
                llm = cls._create_azure_llm_with_retry(endpoint)
                if (
                    llm is None
                ):  # Should not happen if _create_azure_llm_with_retry raises exceptions
                    raise RuntimeError(
                        "Failed to create Azure OpenAI client after retries, returned None unexpectedly."
                    )
                return llm
            except RetryError as retry_error:
                error_msg = f"Failed to create Azure OpenAI client after retries: {str(retry_error)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            except Exception as llm_creation_error:
                error_msg = f"Failed during Azure LLM creation or verification: {str(llm_creation_error)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        except ValueError as ve:
            # Re-raise configuration errors directly
            raise ve
        except Exception as e:
            # Catch any other unexpected errors during setup
            error_msg = f"Unexpected error initializing AzureChatOpenAI: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)

    @staticmethod
    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _create_azure_llm_with_retry(endpoint):
        """
        Create Azure OpenAI client with retry logic

        Args:
            endpoint (str): The Azure endpoint URL

        Returns:
            AzureChatOpenAI: The LangChain Azure OpenAI client
        """
        try:
            # Set request timeout (in seconds)
            request_timeout = 60.0

            # Create the Azure OpenAI client for testing the connection
            client = AzureOpenAI(
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                timeout=request_timeout,
            )

            # Verify the client works by making a simple test call
            logger.info("Testing connection to Azure OpenAI...")
            try:
                # Test the connection with a simple completion - ACTUALLY RUN THE TEST
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant.",
                        },
                        {
                            "role": "user",
                            "content": "Hello, are you working?",
                        },
                    ],
                    max_tokens=5,
                    temperature=0.7,
                    top_p=1.0,
                    model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                    timeout=request_timeout,
                )
                # If we get here, the connection works
                logger.info("Successfully connected to Azure OpenAI")

                # Return a LangChain-compatible AzureChatOpenAI model
                # For LiteLLM compatibility, we need to specify the model in azure/ format
                deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME

                return AzureChatOpenAI(
                    azure_deployment=deployment_name,
                    openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    temperature=0.7,
                    request_timeout=request_timeout,
                    # Specify model in LiteLLM-compatible format for CrewAI
                    model=f"azure/{deployment_name}",
                )
            except Exception as e:
                logger.error(f"Error testing Azure OpenAI connection: {str(e)}")
                raise  # Re-raise for retry
        except Exception as e:
            logger.error(f"Error creating Azure OpenAI client: {str(e)}")
            raise  # Re-raise for retry

    @classmethod
    async def generate_completion(
        cls, messages, max_tokens=4096, temperature=0.7, top_p=1.0
    ):
        """
        Generate a chat completion using Azure OpenAI

        Args:
            messages (list): List of message dictionaries with role and content
            max_tokens (int): Maximum tokens to generate
            temperature (float): Temperature parameter for generation
            top_p (float): Top p parameter for generation

        Returns:
            str: The generated completion text
        """
        try:
            # Set request timeout (in seconds)
            request_timeout = 60.0

            client = cls.get_llm(fallback_to_openai=False)
            if not client:
                logger.error("Failed to get Azure OpenAI client")
                return None

            # Check if we got a LangChain model (has an invoke method) or raw client
            if hasattr(client, "invoke"):
                # Using LangChain AzureChatOpenAI or ChatOpenAI
                try:
                    # For LangChain, timeout is set during client creation
                    response = client.invoke(messages)
                    return response.content
                except Exception as e:
                    logger.error(f"Error with LangChain invoke: {str(e)}")
                    # Fall back to using a raw client
                    raw_client = AzureOpenAI(
                        api_version=settings.AZURE_OPENAI_API_VERSION,
                        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                        api_key=settings.AZURE_OPENAI_API_KEY,
                        timeout=request_timeout,
                    )
                    response = raw_client.chat.completions.create(
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                        timeout=request_timeout,
                    )
                    return response.choices[0].message.content
            else:
                # Using raw AzureOpenAI client
                response = client.chat.completions.create(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                    timeout=request_timeout,
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            return None

    @classmethod
    async def get_coding_answer(cls, question: str) -> str:
        """
        Get a coding interview answer for a specific question

        Args:
            question (str): The coding interview question

        Returns:
            str: The answer optimized for Touch Bar display
        """
        system_prompt = """You are an expert coding interview assistant. Provide concise, 
        practical answers to coding interview questions. Focus on:
        1. Key concepts and approaches
        2. Time and space complexity
        3. Code examples when helpful
        4. Common pitfalls to avoid
        
        Keep answers brief and suitable for display on a small screen (max 200 characters).
        If the answer is longer, provide the most essential information first."""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Answer this coding interview question: {question}",
            },
        ]

        try:
            response = await cls.generate_completion(
                messages=messages,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
            )

            if response:
                # Truncate to fit Touch Bar
                if len(response) > settings.MAX_ANSWER_LENGTH:
                    response = response[: settings.MAX_ANSWER_LENGTH - 3] + "..."
                return response
            else:
                return "Unable to generate answer. Please try again."

        except Exception as e:
            logger.error(f"Error getting coding answer: {str(e)}")
            return "Error: Unable to connect to AI service."
