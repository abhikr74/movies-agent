#!/usr/bin/env python3
"""
Movie Evaluation Pipeline Runner
Evaluates RAG system performance on movie information extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.evaluation_pipeline import MovieEvaluationPipeline
from app.database.database import SessionLocal, create_tables
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the complete movie evaluation pipeline"""
    
    print("Starting Movie RAG Evaluation Pipeline")
    print("=" * 50)
    
    # Ensure database exists
    create_tables()
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Initialize evaluation pipeline
        print("Initializing evaluation pipeline...")
        pipeline = MovieEvaluationPipeline(db)
        
        # Run complete evaluation
        print("Running evaluation on 15 ground truth observations...")
        print("This may take a few minutes...\n")
        
        results = pipeline.run_complete_evaluation()
        
        # Print summary
        pipeline.print_evaluation_summary(results)
        
        # Save detailed results
        pipeline.save_evaluation_results(results)
        
        print(f"\nDetailed results saved to: data/processed/evaluation_results.json")
        print("Evaluation completed successfully!")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        print(f"Error: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()