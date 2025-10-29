#!/usr/bin/env python3
"""
Generate NEW batch of 400 Cannes-level slogans with different seed
Export to clean JSON format
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from modules.ai_generator import generate_cannes_slogans
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Generate new batch with different seed"""
    logger.info("="*80)
    logger.info("CANNES SLOGAN GENERATOR - NEW BATCH")
    logger.info("="*80)
    
    # Paths
    corpus_ru = "russian_slogans_numbered — копия.txt"
    corpus_en = "English slogans"
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    
    # Configuration - NEW SEED for different results
    TARGET_COUNT = 400
    POOL_SIZE = 2500
    SEED = 2025  # Different seed = different slogans!
    
    logger.info(f"Configuration:")
    logger.info(f"  - Target: {TARGET_COUNT} slogans")
    logger.info(f"  - Pool size: {POOL_SIZE} candidates")
    logger.info(f"  - Seed: {SEED} (NEW - different from previous)")
    logger.info(f"  - Corpus RU: {corpus_ru}")
    logger.info(f"  - Corpus EN: {corpus_en}")
    
    # Generate slogans
    logger.info("\nGenerating NEW batch of slogans...")
    slogans = generate_cannes_slogans(
        corpus_ru, 
        corpus_en,
        target_count=TARGET_COUNT,
        pool_size=POOL_SIZE,
        seed=SEED  # NEW SEED!
    )
    
    logger.info(f"\nGenerated {len(slogans)} new slogans")
    
    # Export to clean JSON (not JSONL)
    logger.info("\nExporting to JSON...")
    
    json_output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_count": len(slogans),
            "seed": SEED,
            "batch_number": 2,
            "method": "AI-Powered Pipeline (Factory AI)",
            "corpus_size": "~15,000 slogans (RU + EN)"
        },
        "statistics": {
            "avg_score": sum(s['score'] for s in slogans) / len(slogans),
            "avg_punchiness": sum(s['punchiness'] for s in slogans) / len(slogans),
            "avg_wit": sum(s['wit'] for s in slogans) / len(slogans),
            "avg_clarity": sum(s['clarity'] for s in slogans) / len(slogans),
            "avg_twist": sum(s['twist'] for s in slogans) / len(slogans),
            "avg_length": sum(len(s['text']) for s in slogans) / len(slogans),
            "avg_word_count": sum(len(s['text'].split()) for s in slogans) / len(slogans),
        },
        "slogans": slogans
    }
    
    json_path = out_dir / "cannes_400_batch2.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    logger.info(f"  ✓ Exported to {json_path}")
    
    # Also export compact version (top 100)
    top100_output = {
        "metadata": json_output["metadata"],
        "statistics": json_output["statistics"],
        "slogans": slogans[:100]
    }
    
    top100_path = out_dir / "cannes_top100_batch2.json"
    with open(top100_path, 'w', encoding='utf-8') as f:
        json.dump(top100_output, f, ensure_ascii=False, indent=2)
    logger.info(f"  ✓ Exported top-100 to {top100_path}")
    
    # Export just texts for easy use
    texts_path = out_dir / "cannes_400_texts_batch2.json"
    texts_output = {
        "generated_at": datetime.now().isoformat(),
        "count": len(slogans),
        "slogans": [s['text'] for s in slogans]
    }
    with open(texts_path, 'w', encoding='utf-8') as f:
        json.dump(texts_output, f, ensure_ascii=False, indent=2)
    logger.info(f"  ✓ Exported texts only to {texts_path}")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("✅ NEW BATCH COMPLETE")
    logger.info("="*80)
    logger.info(f"Generated: {len(slogans)} NEW slogans")
    logger.info(f"Average score: {json_output['statistics']['avg_score']:.3f}")
    logger.info(f"\nOutput files:")
    logger.info(f"  - {json_path} (full data)")
    logger.info(f"  - {top100_path} (top 100)")
    logger.info(f"  - {texts_path} (texts only)")
    logger.info("\nTop 20 NEW slogans:")
    for i, slogan in enumerate(slogans[:20], 1):
        logger.info(f"  {i:2d}. {slogan['text']} ({slogan['score']:.3f})")
    logger.info("="*80)


if __name__ == "__main__":
    main()
