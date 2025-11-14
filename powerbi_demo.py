#!/usr/bin/env python3
"""
Gaming Sentiment Analysis with Power BI Integration
===================================================

This script demonstrates the complete pipeline for gaming sentiment analysis
and Power BI dashboard data preparation.

Author: Gaming Analytics Team
Date: November 2024
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

# Sample data generation for demonstration
def create_comprehensive_sample_data():
    """Create realistic sample data for demonstration"""
    
    games = {
        "Counter-Strike: Global Offensive": {"base_sentiment": 0.2, "volatility": 0.3},
        "Dota 2": {"base_sentiment": 0.1, "volatility": 0.4},
        "Apex Legends": {"base_sentiment": 0.15, "volatility": 0.25},
        "PUBG: Battlegrounds": {"base_sentiment": -0.05, "volatility": 0.35},
        "Grand Theft Auto V": {"base_sentiment": 0.3, "volatility": 0.2}
    }
    
    reviews_data = {}
    
    for game_name, props in games.items():
        reviews = []
        
        # Generate 12 months of data with realistic patterns
        start_date = datetime(2024, 1, 1)
        
        for month in range(12):
            current_date = start_date + timedelta(days=30 * month)
            
            # Seasonal patterns (summer tends to have more positive sentiment)
            seasonal_boost = 0.1 * np.sin((month / 12) * 2 * np.pi)
            
            # Generate reviews for this month
            reviews_this_month = np.random.randint(20, 80)
            
            for day in range(reviews_this_month):
                review_date = current_date + timedelta(days=np.random.randint(0, 30))
                
                # Generate sentiment with trends and noise
                base_sentiment = props["base_sentiment"]
                volatility = props["volatility"]
                sentiment = np.random.normal(
                    base_sentiment + seasonal_boost, 
                    volatility
                )
                
                # Clip to realistic sentiment range
                sentiment = np.clip(sentiment, -1.0, 1.0)
                
                # Generate realistic review text based on sentiment
                if sentiment > 0.3:
                    review_texts = [
                        "Amazing game! Love the graphics and gameplay mechanics.",
                        "Great experience, highly recommend to all gamers!",
                        "Excellent update, developers really listen to community.",
                        "Fantastic multiplayer experience, very addictive!"
                    ]
                elif sentiment > 0:
                    review_texts = [
                        "Pretty good game overall, has some nice features.",
                        "Decent gameplay but could use some improvements.",
                        "Not bad, worth trying if you like this genre.",
                        "Good game but not exceptional, solid 7/10."
                    ]
                elif sentiment > -0.3:
                    review_texts = [
                        "It's okay I guess, nothing special though.",
                        "Meh, expected more from this game honestly.",
                        "Average game, has potential but needs work.",
                        "Not impressed, many better alternatives available."
                    ]
                else:
                    review_texts = [
                        "Terrible experience, full of bugs and glitches.",
                        "Waste of money, developers don't care about players.",
                        "Awful gameplay, very disappointing overall.",
                        "Broken mechanics, would not recommend to anyone."
                    ]
                
                review_text = np.random.choice(review_texts)
                
                reviews.append({
                    'review': review_text,
                    'date': review_date,
                    'sentiment_score': round(sentiment, 4),
                    'user': f'User_{np.random.randint(1000, 9999)}',
                    'playtime': np.random.randint(10, 2000),
                    'helpfulness': np.random.randint(0, 50),
                    'recommend': 'Recommended' if sentiment > 0 else 'Not Recommended',
                    'early_access': None
                })
        
        reviews_data[game_name] = reviews
    
    return reviews_data

def prepare_powerbi_data_tables(reviews_data):
    """Prepare all required tables for Power BI"""
    
    # 1. Summary Table
    summary_data = []
    
    for game_name, reviews in reviews_data.items():
        if not reviews:
            continue
            
        # Calculate sentiment metrics
        sentiments = [r['sentiment_score'] for r in reviews]
        positive_count = len([s for s in sentiments if s > 0.1])
        negative_count = len([s for s in sentiments if s < -0.1])
        neutral_count = len(sentiments) - positive_count - negative_count
        
        avg_sentiment = np.mean(sentiments)
        
        # Recent vs Historical comparison
        recent_date = datetime.now() - timedelta(days=90)
        recent_reviews = [r for r in reviews if pd.to_datetime(r['date']) > recent_date]
        recent_avg_sentiment = np.mean([r['sentiment_score'] for r in recent_reviews]) if recent_reviews else 0
        
        summary_data.append({
            'Game_Name': game_name,
            'Total_Reviews': len(reviews),
            'Positive_Reviews': positive_count,
            'Negative_Reviews': negative_count,
            'Neutral_Reviews': neutral_count,
            'Positive_Percentage': round((positive_count / len(reviews)) * 100, 2),
            'Negative_Percentage': round((negative_count / len(reviews)) * 100, 2),
            'Neutral_Percentage': round((neutral_count / len(reviews)) * 100, 2),
            'Average_Sentiment_Score': round(avg_sentiment, 4),
            'Recent_Sentiment_Score': round(recent_avg_sentiment, 4),
            'Sentiment_Trend': 'Improving' if recent_avg_sentiment > avg_sentiment else 'Declining',
            'Sentiment_Volatility': round(np.std(sentiments), 4),
            'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # 2. Detailed Reviews Table
    detailed_data = []
    
    for game_name, reviews in reviews_data.items():
        for review in reviews:
            detailed_data.append({
                'Game_Name': game_name,
                'Review_Text': review['review'][:500],  # Limit text length
                'Review_Date': review['date'],
                'Sentiment_Score': review['sentiment_score'],
                'Sentiment_Label': (
                    'Positive' if review['sentiment_score'] > 0.1
                    else 'Negative' if review['sentiment_score'] < -0.1
                    else 'Neutral'
                ),
                'User_Name': review['user'],
                'Playtime_Hours': review['playtime'],
                'Helpfulness_Score': review['helpfulness'],
                'Recommendation': review['recommend'],
                'Text_Length': len(review['review']),
                'Year': pd.to_datetime(review['date']).year,
                'Month': pd.to_datetime(review['date']).month,
                'Quarter': f"Q{((pd.to_datetime(review['date']).month-1)//3)+1}",
                'Month_Name': pd.to_datetime(review['date']).strftime('%B'),
                'Weekday': pd.to_datetime(review['date']).strftime('%A')
            })
    
    detailed_df = pd.DataFrame(detailed_data)
    
    # 3. Time Series Table
    time_series_data = []
    
    for game_name, reviews in reviews_data.items():
        df = pd.DataFrame(reviews)
        if df.empty:
            continue
            
        df['date'] = pd.to_datetime(df['date'])
        df['year_month'] = df['date'].dt.to_period('M')
        
        monthly_stats = df.groupby('year_month').agg({
            'sentiment_score': ['count', 'mean', 'std', 'min', 'max'],
            'playtime': 'mean',
            'helpfulness': 'mean'
        }).round(4)
        
        monthly_stats.columns = [
            'Review_Count', 'Avg_Sentiment', 'Sentiment_StdDev', 
            'Min_Sentiment', 'Max_Sentiment', 'Avg_Playtime', 'Avg_Helpfulness'
        ]
        monthly_stats = monthly_stats.reset_index()
        monthly_stats['Game_Name'] = game_name
        monthly_stats['Year_Month'] = monthly_stats['year_month'].astype(str)
        monthly_stats['Year'] = monthly_stats['year_month'].dt.year
        monthly_stats['Month'] = monthly_stats['year_month'].dt.month
        monthly_stats['Month_Name'] = monthly_stats['year_month'].dt.strftime('%B')
        
        # Calculate moving averages
        monthly_stats['Sentiment_MA_3'] = monthly_stats['Avg_Sentiment'].rolling(window=3, min_periods=1).mean()
        monthly_stats = monthly_stats.round(4)
        
        time_series_data.append(monthly_stats[[
            'Game_Name', 'Year_Month', 'Year', 'Month', 'Month_Name',
            'Review_Count', 'Avg_Sentiment', 'Sentiment_StdDev',
            'Min_Sentiment', 'Max_Sentiment', 'Sentiment_MA_3',
            'Avg_Playtime', 'Avg_Helpfulness'
        ]])
    
    if time_series_data:
        timeseries_df = pd.concat(time_series_data, ignore_index=True)
    else:
        timeseries_df = pd.DataFrame()
    
    return summary_df, detailed_df, timeseries_df

def export_to_powerbi_formats(summary_df, detailed_df, timeseries_df, export_dir="data_exports"):
    """Export data to multiple formats for Power BI"""
    
    # Create export directory
    os.makedirs(export_dir, exist_ok=True)
    
    export_results = {
        'success': True,
        'files_created': [],
        'errors': []
    }
    
    # Export formats
    formats = {
        'excel': '.xlsx',
        'csv': '.csv'
    }
    
    tables = {
        "gaming_summary": summary_df,
        "gaming_reviews": detailed_df,
        "gaming_timeseries": timeseries_df
    }
    
    for table_name, df in tables.items():
        if df.empty:
            print(f"⚠️  Skipping empty table: {table_name}")
            continue
            
        for format_name, extension in formats.items():
            try:
                filepath = f"{export_dir}/{table_name}{extension}"
                
                if format_name == 'excel':
                    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name=table_name[:30])
                else:  # CSV
                    df.to_csv(filepath, index=False, encoding='utf-8')
                
                export_results['files_created'].append(filepath)
                print(f"✅ Exported: {filepath}")
                
            except Exception as e:
                error_msg = f"Error exporting {table_name} as {format_name}: {str(e)}"
                export_results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
    
    # Create metadata file
    metadata = {
        "export_timestamp": datetime.now().isoformat(),
        "total_games_analyzed": len(summary_df) if not summary_df.empty else 0,
        "total_reviews": int(summary_df['Total_Reviews'].sum()) if not summary_df.empty else 0,
        "games_list": summary_df['Game_Name'].tolist() if not summary_df.empty else [],
        "date_range": {
            "start_date": detailed_df['Review_Date'].min().isoformat() if not detailed_df.empty else None,
            "end_date": detailed_df['Review_Date'].max().isoformat() if not detailed_df.empty else None
        },
        "data_schema": {
            "summary_table": {
                "description": "Aggregated sentiment metrics by game",
                "row_count": len(summary_df),
                "columns": summary_df.columns.tolist() if not summary_df.empty else []
            },
            "detailed_table": {
                "description": "Individual review records with sentiment scores", 
                "row_count": len(detailed_df),
                "columns": detailed_df.columns.tolist() if not detailed_df.empty else []
            },
            "timeseries_table": {
                "description": "Monthly aggregated sentiment trends",
                "row_count": len(timeseries_df),
                "columns": timeseries_df.columns.tolist() if not timeseries_df.empty else []
            }
        },
        "export_results": export_results
    }
    
    try:
        metadata_file = f"{export_dir}/export_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        export_results['files_created'].append(metadata_file)
        print(f"✅ Created metadata: {metadata_file}")
    except Exception as e:
        error_msg = f"Error creating metadata: {str(e)}"
        export_results['errors'].append(error_msg)
        print(f"❌ {error_msg}")
    
    return export_results

def main():
    """Main execution function"""
    
    print("🎮 Gaming Sentiment Analysis - Power BI Integration")
    print("=" * 60)
    
    # Generate sample data
    print("📊 Generating comprehensive sample data...")
    reviews_data = create_comprehensive_sample_data()
    
    total_reviews = sum(len(reviews) for reviews in reviews_data.values())
    print(f"✅ Generated {total_reviews} reviews across {len(reviews_data)} games")
    
    # Prepare Power BI tables
    print("\n📋 Preparing Power BI data tables...")
    summary_df, detailed_df, timeseries_df = prepare_powerbi_data_tables(reviews_data)
    
    print(f"✅ Summary table: {len(summary_df)} rows")
    print(f"✅ Detailed table: {len(detailed_df)} rows") 
    print(f"✅ Time series table: {len(timeseries_df)} rows")
    
    # Export data
    print("\n💾 Exporting data for Power BI...")
    export_results = export_to_powerbi_formats(summary_df, detailed_df, timeseries_df)
    
    # Display summary
    print(f"\n📊 Export Summary:")
    print("=" * 40)
    print(f"✅ Files created: {len(export_results['files_created'])}")
    print(f"❌ Errors: {len(export_results['errors'])}")
    
    if export_results['files_created']:
        print("\n📁 Created files:")
        for file in export_results['files_created']:
            print(f"  • {file}")
    
    if export_results['errors']:
        print("\n⚠️  Errors encountered:")
        for error in export_results['errors']:
            print(f"  • {error}")
    
    # Display sample data
    print(f"\n📋 Sample Summary Data:")
    print("=" * 60)
    if not summary_df.empty:
        print(summary_df.to_string(index=False))
    else:
        print("No summary data available")
    
    print(f"\n🎯 Next Steps:")
    print("1. Open Power BI at: https://app.powerbi.com")
    print("2. Click 'Get Data' → 'Files' → 'Local File'")
    print("3. Import files from 'data_exports' folder")
    print("4. Create dashboards using the imported data")
    
    return export_results

if __name__ == "__main__":
    results = main()