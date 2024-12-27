from typing import Optional
from .eastern_chart import EasternChart
from .northern_chart import NorthernChart
from .southern_chart import SouthernChart

class ChartFactory:
    """Factory class for creating different types of charts"""
    
    @staticmethod
    def create_chart(chart_type: str, parent=None, input_page=None):
        """
        Create a chart of the specified type
        
        Args:
            chart_type: Type of chart to create ('eastern', 'northern', 'southern')
            parent: Parent widget
            input_page: Input page widget
            
        Returns:
            Instance of the specified chart type
        """
        chart_types = {
            'eastern': EasternChart,
            'northern': NorthernChart,
            'southern': SouthernChart
        }
        
        chart_class = chart_types.get(chart_type.lower())
        if chart_class:
            return chart_class(parent, input_page)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
            
    @staticmethod
    def get_available_charts():
        """Get list of available chart types"""
        return ['Eastern', 'Northern', 'Southern']
