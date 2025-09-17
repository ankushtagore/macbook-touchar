import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.config import settings

# Try to import tkinter, skip tests if not available
try:
    import tkinter as tk

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# Only import UI classes if tkinter is available
if TKINTER_AVAILABLE:
    from app.touch_bar_ui import TouchBarUI, TouchBarSimulator


class TestTouchBarUI:
    """Test cases for TouchBarUI"""

    @pytest.fixture
    def ui(self):
        """Create a TouchBarUI instance for testing"""
        if not TKINTER_AVAILABLE:
            pytest.skip("Tkinter not available")
        return TouchBarUI()

    @pytest.fixture
    def mock_tkinter(self):
        """Mock tkinter components"""
        with patch("app.touch_bar_ui.tk.Tk") as mock_tk:
            with patch("app.touch_bar_ui.ttk") as mock_ttk:
                with patch("app.touch_bar_ui.messagebox") as mock_messagebox:
                    mock_root = Mock()
                    mock_tk.return_value = mock_root
                    mock_root.winfo_screenheight.return_value = 1080

                    yield {
                        "tk": mock_tk,
                        "ttk": mock_ttk,
                        "messagebox": mock_messagebox,
                        "root": mock_root,
                    }

    def test_ui_initialization(self, ui):
        """Test UI initialization"""
        assert ui.root is None
        assert ui.search_entry is None
        assert ui.answer_label is None
        assert ui.is_searching is False

    def test_create_ui(self, ui, mock_tkinter):
        """Test UI creation"""
        ui.create_ui()

        assert ui.root is not None
        mock_tkinter["tk"].assert_called_once()
        mock_tkinter["root"].title.assert_called_with("Touch Bar Coding Assistant")

    def test_on_search_empty_question(self, ui, mock_tkinter):
        """Test search with empty question"""
        ui.create_ui()
        ui.search_entry = Mock()
        ui.search_entry.get.return_value = ""

        ui._on_search()

        mock_tkinter["messagebox"].showwarning.assert_called_once()

    def test_on_search_valid_question(self, ui, mock_tkinter):
        """Test search with valid question"""
        ui.create_ui()
        ui.search_entry = Mock()
        ui.search_entry.get.return_value = "What is binary search?"
        ui.search_button = Mock()
        ui.status_label = Mock()
        ui.answer_label = Mock()

        with patch.object(ui, "_start_search") as mock_start:
            ui._on_search()
            mock_start.assert_called_once_with("What is binary search?")

    def test_on_clear(self, ui, mock_tkinter):
        """Test clear functionality"""
        ui.create_ui()
        ui.search_entry = Mock()
        ui.answer_label = Mock()
        ui.status_label = Mock()

        ui._on_clear()

        ui.search_entry.delete.assert_called_once_with(0, tk.END)
        ui.answer_label.config.assert_called_once()
        ui.status_label.config.assert_called_once_with(text="Ready")
        ui.search_entry.focus.assert_called_once()

    def test_start_search(self, ui, mock_tkinter):
        """Test search start process"""
        ui.create_ui()
        ui.search_button = Mock()
        ui.status_label = Mock()
        ui.answer_label = Mock()

        with patch("threading.Thread") as mock_thread:
            ui._start_search("Test question")

            assert ui.is_searching is True
            ui.search_button.config.assert_called_with(state="disabled")
            ui.status_label.config.assert_called_with(text="Searching...")
            ui.answer_label.config.assert_called_with(text="Generating answer...")
            mock_thread.assert_called_once()

    def test_update_answer(self, ui, mock_tkinter):
        """Test answer update"""
        ui.create_ui()
        ui.answer_label = Mock()
        ui.status_label = Mock()
        ui.search_button = Mock()

        ui._update_answer("Test answer")

        ui.answer_label.config.assert_called_with(text="Test answer")
        ui.status_label.config.assert_called_with(text="Ready")
        ui.search_button.config.assert_called_with(state="normal")
        assert ui.is_searching is False

    @pytest.mark.asyncio
    async def test_perform_search_success(self, ui, mock_tkinter):
        """Test successful search performance"""
        ui.create_ui()

        with patch(
            "app.azure_service.AzureOpenAIService.get_coding_answer"
        ) as mock_get_answer:
            mock_get_answer.return_value = (
                "Use binary search for O(log n) time complexity"
            )

            result = await ui._perform_search("What is binary search?")

            assert "binary search" in result.lower()
            mock_get_answer.assert_called_once_with("What is binary search?")

    @pytest.mark.asyncio
    async def test_perform_search_error(self, ui, mock_tkinter):
        """Test search performance with error"""
        ui.create_ui()

        with patch(
            "app.azure_service.AzureOpenAIService.get_coding_answer"
        ) as mock_get_answer:
            mock_get_answer.side_effect = Exception("API Error")

            result = await ui._perform_search("Test question")

            assert "Error: Unable to get answer" in result

    def test_keyboard_shortcuts(self, ui, mock_tkinter):
        """Test keyboard shortcut bindings"""
        ui.create_ui()

        # Test that keyboard shortcuts are bound
        mock_root = mock_tkinter["root"]
        assert mock_root.bind.called

    def test_ui_styling(self, ui, mock_tkinter):
        """Test UI styling configuration"""
        ui.create_ui()

        mock_ttk = mock_tkinter["ttk"]
        style = mock_ttk.Style.return_value

        # Check that styles are configured
        style.configure.assert_called()

        # Verify TouchBar styles are configured
        style_calls = [call[0] for call in style.configure.call_args_list]
        assert "TouchBar.TFrame" in style_calls
        assert "TouchBar.TLabel" in style_calls
        assert "TouchBar.TButton" in style_calls


class TestTouchBarSimulator:
    """Test cases for TouchBarSimulator"""

    def test_simulator_initialization(self):
        """Test simulator initialization"""
        if not TKINTER_AVAILABLE:
            pytest.skip("Tkinter not available")
        simulator = TouchBarSimulator()
        assert simulator.ui is not None
        assert isinstance(simulator.ui, TouchBarUI)

    def test_simulator_run(self):
        """Test simulator run method"""
        if not TKINTER_AVAILABLE:
            pytest.skip("Tkinter not available")
        simulator = TouchBarSimulator()

        with patch.object(simulator.ui, "run") as mock_run:
            with patch("builtins.print") as mock_print:
                simulator.run()

                mock_print.assert_called()
                mock_run.assert_called_once()


class TestTouchBarUIIntegration:
    """Integration tests for Touch Bar UI"""

    @pytest.mark.skipif(True, reason="Requires GUI environment")
    def test_full_ui_workflow(self):
        """Test full UI workflow (requires GUI)"""
        # This test would require a GUI environment to run
        # It's skipped by default but can be run manually
        ui = TouchBarUI()

        # Test the complete workflow
        ui.create_ui()

        # Simulate user interaction
        ui.search_entry.insert(0, "What is the time complexity of merge sort?")
        ui._on_search()

        # Verify UI state changes
        assert ui.is_searching is True

        # Clean up
        ui.root.destroy()


class TestTouchBarUIConfiguration:
    """Test Touch Bar UI configuration"""

    def test_ui_dimensions(self):
        """Test UI dimensions match settings"""
        ui = TouchBarUI()

        with patch("app.touch_bar_ui.tk.Tk") as mock_tk:
            with patch("app.touch_bar_ui.ttk"):
                ui.create_ui()

                mock_root = mock_tk.return_value
                mock_root.geometry.assert_called()

                # Check that geometry includes correct dimensions
                geometry_call = mock_root.geometry.call_args[0][0]
                assert str(settings.TOUCH_BAR_WIDTH) in geometry_call
                assert str(settings.TOUCH_BAR_HEIGHT) in geometry_call

    def test_ui_colors(self):
        """Test UI color configuration"""
        ui = TouchBarUI()

        with patch("app.touch_bar_ui.tk.Tk"):
            with patch("app.touch_bar_ui.ttk") as mock_ttk:
                ui.create_ui()

                style = mock_ttk.Style.return_value

                # Check that colors are configured
                style_calls = style.configure.call_args_list
                for call in style_calls:
                    args, kwargs = call
                    if "TouchBar.TFrame" in args:
                        assert kwargs.get("background") == settings.BACKGROUND_COLOR
                    elif "TouchBar.TLabel" in args:
                        assert kwargs.get("background") == settings.BACKGROUND_COLOR
                        assert kwargs.get("foreground") == settings.TEXT_COLOR


if __name__ == "__main__":
    pytest.main([__file__])
