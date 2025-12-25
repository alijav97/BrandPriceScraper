"""
OpenAI Integration for intelligent data analysis
"""

import os
import json
import logging
from typing import List, Dict, Optional
import pandas as pd
from openai import OpenAI, APIError, RateLimitError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """Intelligent price analysis using OpenAI"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.timeout = int(os.getenv("OPENAI_TIMEOUT", 30))
        
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in .env file"
            )
        
        self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)
    
    def analyze_prices(self, products_df: pd.DataFrame, brand_name: str) -> Dict:
        """
        Analyze product prices and generate insights
        
        Args:
            products_df: DataFrame with product data
            brand_name: Name of the brand being analyzed
            
        Returns:
            Dictionary with analysis results
        """
        if products_df.empty:
            return {"error": "No products to analyze"}
        
        try:
            # Prepare data for analysis
            data_summary = self._prepare_data_summary(products_df, brand_name)
            
            # Generate insights
            insights = self._get_insights(data_summary)
            
            # Generate recommendations
            recommendations = self._get_recommendations(data_summary)
            
            # Generate summary
            summary = self._get_summary(data_summary)
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "summary": summary,
                "data_points": len(products_df),
                "platforms": products_df["site"].nunique(),
                "regions": products_df["region"].nunique(),
            }
        
        except RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            return {"error": "API rate limit exceeded. Please try again in a moment."}
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {"error": f"API Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _prepare_data_summary(self, df: pd.DataFrame, brand_name: str) -> str:
        """Prepare data summary for AI analysis"""
        
        stats = {
            "brand": brand_name,
            "total_products": len(df),
            "platforms": df["site"].unique().tolist(),
            "regions": df["region"].unique().tolist(),
            "avg_price": f"${df['current_price'].mean():.2f}",
            "min_price": f"${df['current_price'].min():.2f}",
            "max_price": f"${df['current_price'].max():.2f}",
            "price_range": f"${df['current_price'].max() - df['current_price'].min():.2f}",
            "products_on_sale": len(df[df['current_price'] < df['original_price']]),
            "price_by_site": df.groupby('site')['current_price'].mean().round(2).to_dict(),
            "price_by_region": df.groupby('region')['current_price'].mean().round(2).to_dict(),
        }
        
        return json.dumps(stats, indent=2)
    
    def _get_insights(self, data_summary: str) -> str:
        """Get market insights from OpenAI"""
        
        prompt = f"""
        Analyze the following pricing data for {data_summary} and provide 3-4 key market insights in bullet points.
        Focus on:
        - Price patterns across regions/platforms
        - Competition and pricing strategies
        - Opportunities for consumers
        
        Keep each insight to 1-2 sentences and be specific with data references.
        """
        
        return self._call_openai(prompt, "insights")
    
    def _get_recommendations(self, data_summary: str) -> str:
        """Get purchase recommendations from OpenAI"""
        
        prompt = f"""
        Based on this pricing data: {data_summary}
        
        Provide 3-4 specific purchasing recommendations for someone wanting to buy this brand.
        Include:
        - Best places to buy
        - Best timing considerations
        - Value vs price considerations
        
        Make recommendations practical and actionable.
        """
        
        return self._call_openai(prompt, "recommendations")
    
    def _get_summary(self, data_summary: str) -> str:
        """Get executive summary from OpenAI"""
        
        prompt = f"""
        Summarize the following price analysis in 2-3 sentences: {data_summary}
        
        Focus on the most important findings for someone researching this brand.
        """
        
        return self._call_openai(prompt, "summary")
    
    def _call_openai(self, prompt: str, analysis_type: str) -> str:
        """Call OpenAI API and get response"""
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert market analyst specializing in e-commerce pricing and consumer insights. Provide clear, actionable, and data-driven analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response = message.choices[0].message.content
            logger.info(f"Generated {analysis_type} via OpenAI")
            return response
        
        except Exception as e:
            logger.error(f"OpenAI API call failed for {analysis_type}: {e}")
            raise
    
    def detect_anomalies(self, products_df: pd.DataFrame) -> List[Dict]:
        """
        Detect price anomalies using AI
        
        Args:
            products_df: DataFrame with product data
            
        Returns:
            List of detected anomalies
        """
        if products_df.empty:
            return []
        
        try:
            # Prepare anomaly detection data
            data = {
                "products": products_df[["title", "site", "current_price", "original_price"]].head(10).to_dict("records"),
                "statistics": {
                    "mean_price": float(products_df["current_price"].mean()),
                    "std_price": float(products_df["current_price"].std()),
                    "min_price": float(products_df["current_price"].min()),
                    "max_price": float(products_df["current_price"].max()),
                }
            }
            
            prompt = f"""
            Identify any price anomalies in this product data: {json.dumps(data)}
            
            Look for:
            - Unusually high prices
            - Unusually low prices
            - Suspicious discounts
            - Pricing inconsistencies
            
            Return a JSON list with anomalies found, each with: product_title, anomaly_type, severity (high/medium/low), explanation.
            """
            
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a price analysis expert. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            response = message.choices[0].message.content
            
            # Try to parse JSON response
            try:
                anomalies = json.loads(response)
                if not isinstance(anomalies, list):
                    anomalies = [anomalies] if isinstance(anomalies, dict) else []
            except json.JSONDecodeError:
                anomalies = []
            
            return anomalies
        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def generate_report(self, products_df: pd.DataFrame, brand_name: str) -> str:
        """
        Generate a comprehensive market report
        
        Args:
            products_df: DataFrame with product data
            brand_name: Name of the brand
            
        Returns:
            Formatted market report
        """
        
        try:
            analysis = self.analyze_prices(products_df, brand_name)
            
            if "error" in analysis:
                return f"Error generating report: {analysis['error']}"
            
            report = f"""
╔════════════════════════════════════════════════════════════╗
║          {brand_name.upper()} - MARKET ANALYSIS REPORT
║════════════════════════════════════════════════════════════╝

📊 DATA OVERVIEW
─────────────────────────────────────────────────────────────
Products Analyzed: {analysis['data_points']}
Platforms: {analysis['platforms']}
Regions: {analysis['regions']}

💡 KEY INSIGHTS
─────────────────────────────────────────────────────────────
{analysis['insights']}

✅ RECOMMENDATIONS
─────────────────────────────────────────────────────────────
{analysis['recommendations']}

📋 SUMMARY
─────────────────────────────────────────────────────────────
{analysis['summary']}

════════════════════════════════════════════════════════════════
Generated using AI-powered analysis
"""
            return report
        
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"Report generation failed: {str(e)}"


class PricePrediction:
    """AI-powered price predictions"""
    
    def __init__(self):
        """Initialize predictor"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found")
        self.client = OpenAI(api_key=self.api_key)
    
    def predict_trend(self, products_df: pd.DataFrame) -> str:
        """
        Predict future price trends
        
        Args:
            products_df: DataFrame with product data
            
        Returns:
            Trend prediction text
        """
        
        if products_df.empty:
            return "No data available for prediction"
        
        try:
            # Prepare current prices and discounts
            data = {
                "average_price": float(products_df["current_price"].mean()),
                "products_on_sale": int(len(products_df[products_df["current_price"] < products_df["original_price"]])),
                "max_discount": float((1 - products_df["current_price"].min() / products_df["original_price"].max()) * 100),
                "price_variance": float(products_df["current_price"].std()),
                "regions_covered": products_df["region"].nunique(),
            }
            
            prompt = f"""
            Based on this current pricing snapshot: {json.dumps(data)}
            
            Predict the likely price trend for the next 30 days.
            Consider:
            - Current discount levels
            - Price variance across regions
            - Seasonal factors
            - Competition patterns
            
            Provide a 2-3 sentence prediction with confidence level (high/medium/low).
            """
            
            message = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert market analyst. Provide realistic price predictions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=300
            )
            
            return message.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return f"Prediction unavailable: {str(e)}"
