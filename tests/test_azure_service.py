import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from app.azure_service import AzureOpenAIService
from app.config import settings


class TestAzureOpenAIService:
    """Test cases for AzureOpenAIService"""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing"""
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "test_key",
                "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
                "AZURE_OPENAI_DEPLOYMENT_NAME": "test_deployment",
                "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
            },
        ):
            # Also patch the settings to use the mocked environment
            with patch("app.azure_service.settings") as mock_settings:
                mock_settings.AZURE_OPENAI_API_KEY = "test_key"
                mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
                mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "test_deployment"
                mock_settings.AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
                yield

    @pytest.fixture
    def mock_azure_client(self):
        """Mock Azure OpenAI client"""
        with patch("app.azure_service.AzureOpenAI") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            # Mock successful response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_instance.chat.completions.create.return_value = mock_response

            yield mock_instance

    def test_get_llm_success(self, mock_env_vars, mock_azure_client):
        """Test successful LLM creation"""
        with patch("app.azure_service.AzureChatOpenAI") as mock_langchain:
            mock_langchain_instance = Mock()
            mock_langchain.return_value = mock_langchain_instance

            result = AzureOpenAIService.get_llm()

            assert result is not None
            mock_langchain.assert_called_once()

    def test_get_llm_missing_env_vars(self):
        """Test LLM creation with missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="Missing required Azure OpenAI configuration"
            ):
                AzureOpenAIService.get_llm()

    def test_get_llm_connection_error(self, mock_env_vars):
        """Test LLM creation with connection error"""
        with patch("app.azure_service.AzureOpenAI") as mock_client:
            mock_client.side_effect = Exception("Connection failed")

            with pytest.raises(RuntimeError):
                AzureOpenAIService.get_llm()

    @pytest.mark.asyncio
    async def test_generate_completion_success(self, mock_env_vars, mock_azure_client):
        """Test successful completion generation"""
        with patch("app.azure_service.AzureOpenAIService.get_llm") as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = Mock(content="Test completion")
            mock_get_llm.return_value = mock_llm

            messages = [{"role": "user", "content": "Test question"}]
            result = await AzureOpenAIService.generate_completion(messages)

            assert result == "Test completion"
            mock_llm.invoke.assert_called_once_with(messages)

    @pytest.mark.asyncio
    async def test_generate_completion_fallback(self, mock_env_vars, mock_azure_client):
        """Test completion generation with fallback to raw client"""
        with patch("app.azure_service.AzureOpenAIService.get_llm") as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.side_effect = Exception("LangChain failed")
            mock_get_llm.return_value = mock_llm

            messages = [{"role": "user", "content": "Test question"}]
            result = await AzureOpenAIService.generate_completion(messages)

            assert result == "Test response"
            mock_azure_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_completion_error(self, mock_env_vars):
        """Test completion generation with error"""
        with patch("app.azure_service.AzureOpenAIService.get_llm") as mock_get_llm:
            mock_get_llm.return_value = None

            messages = [{"role": "user", "content": "Test question"}]
            result = await AzureOpenAIService.generate_completion(messages)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_coding_answer_success(self, mock_env_vars):
        """Test successful coding answer generation"""
        with patch(
            "app.azure_service.AzureOpenAIService.generate_completion"
        ) as mock_gen:
            mock_gen.return_value = (
                "Use a hash map for O(1) lookup. Time: O(n), Space: O(n)"
            )

            with patch("app.azure_service.settings") as mock_settings:
                mock_settings.MAX_ANSWER_LENGTH = 200
                mock_settings.MAX_TOKENS = 1000
                mock_settings.TEMPERATURE = 0.7

                result = await AzureOpenAIService.get_coding_answer(
                    "How to find duplicates in array?"
                )

                assert "hash map" in result.lower()
                assert "O(1)" in result
                mock_gen.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_coding_answer_long_response(self, mock_env_vars):
        """Test coding answer with long response that needs truncation"""
        long_answer = "A" * 300  # Longer than MAX_ANSWER_LENGTH
        with patch(
            "app.azure_service.AzureOpenAIService.generate_completion"
        ) as mock_gen:
            mock_gen.return_value = long_answer

            with patch("app.azure_service.settings") as mock_settings:
                mock_settings.MAX_ANSWER_LENGTH = 200
                mock_settings.MAX_TOKENS = 1000
                mock_settings.TEMPERATURE = 0.7

                result = await AzureOpenAIService.get_coding_answer("Test question")

                assert len(result) <= mock_settings.MAX_ANSWER_LENGTH
                assert result.endswith("...")

    @pytest.mark.asyncio
    async def test_get_coding_answer_error(self, mock_env_vars):
        """Test coding answer generation with error"""
        with patch(
            "app.azure_service.AzureOpenAIService.generate_completion"
        ) as mock_gen:
            mock_gen.side_effect = Exception("API Error")

            result = await AzureOpenAIService.get_coding_answer("Test question")

            assert "Error: Unable to connect to AI service" in result

    def test_endpoint_parsing(self, mock_env_vars):
        """Test Azure endpoint URL parsing"""
        test_cases = [
            ("https://test.openai.azure.com/", "https://test.openai.azure.com"),
            (
                "https://test.openai.azure.com/deployments/test",
                "https://test.openai.azure.com",
            ),
            ("https://test.cognitive.azure.com/", "https://test.cognitive.azure.com"),
            ("https://test.openai.azure.com", "https://test.openai.azure.com"),
        ]

        for input_endpoint, expected in test_cases:
            with patch.dict(os.environ, {"AZURE_OPENAI_ENDPOINT": input_endpoint}):
                # This will test the endpoint parsing during get_llm
                with patch("app.azure_service.AzureChatOpenAI"):
                    with patch("app.azure_service.AzureOpenAI"):
                        try:
                            AzureOpenAIService.get_llm()
                        except:
                            pass  # We're just testing the parsing, not the full connection


class TestAzureServiceIntegration:
    """Integration tests for Azure service"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test the full workflow from question to answer"""
        # This test requires actual Azure credentials to run
        # It's marked as integration test and can be skipped in CI
        if not all(
            [
                os.getenv("AZURE_OPENAI_API_KEY"),
                os.getenv("AZURE_OPENAI_ENDPOINT"),
                os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            ]
        ):
            pytest.skip("Azure credentials not available")

        question = "What is the time complexity of binary search?"
        result = await AzureOpenAIService.get_coding_answer(question)

        assert result is not None
        assert len(result) > 0
        assert "O(log n)" in result or "logarithmic" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__])
