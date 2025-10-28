#!/usr/bin/env python3
"""
Generate 400 Cannes-level slogans using AI
"""
import sys
import os
import json
import csv
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
    """Main generation pipeline"""
    logger.info("="*80)
    logger.info("CANNES SLOGAN GENERATOR - AI-Powered Pipeline")
    logger.info("="*80)
    
    # Paths
    corpus_ru = "russian_slogans_numbered — копия.txt"
    corpus_en = "English slogans"
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    
    # Configuration
    TARGET_COUNT = 400
    POOL_SIZE = 2500
    SEED = 42
    
    logger.info(f"Configuration:")
    logger.info(f"  - Target: {TARGET_COUNT} slogans")
    logger.info(f"  - Pool size: {POOL_SIZE} candidates")
    logger.info(f"  - Seed: {SEED}")
    logger.info(f"  - Corpus RU: {corpus_ru}")
    logger.info(f"  - Corpus EN: {corpus_en}")
    
    # Generate slogans
    logger.info("\nStep 1: Generating candidate pool...")
    slogans = generate_cannes_slogans(
        corpus_ru, 
        corpus_en,
        target_count=TARGET_COUNT,
        pool_size=POOL_SIZE,
        seed=SEED
    )
    
    logger.info(f"\nStep 2: Generated {len(slogans)} slogans")
    
    # Export to JSONL
    logger.info("\nStep 3: Exporting results...")
    
    jsonl_path = out_dir / "cannes_400.jsonl"
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for slogan in slogans:
            f.write(json.dumps(slogan, ensure_ascii=False) + '\n')
    logger.info(f"  ✓ Exported to {jsonl_path}")
    
    # Export to CSV
    csv_path = out_dir / "cannes_400.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['rank', 'text', 'score', 'punchiness', 'wit', 'clarity', 'twist'])
        writer.writeheader()
        writer.writerows(slogans)
    logger.info(f"  ✓ Exported to {csv_path}")
    
    # Export to TXT
    txt_path = out_dir / "cannes_400.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + '\n')
        f.write("400 CANNES-LEVEL SLOGANS\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + '\n\n')
        for slogan in slogans:
            f.write(f"{slogan['rank']:3d}. {slogan['text']}\n")
            f.write(f"     Score: {slogan['score']:.3f} | ")
            f.write(f"Punch: {slogan['punchiness']:.2f} | ")
            f.write(f"Wit: {slogan['wit']:.2f} | ")
            f.write(f"Clarity: {slogan['clarity']:.2f} | ")
            f.write(f"Twist: {slogan['twist']:.2f}\n\n")
    logger.info(f"  ✓ Exported to {txt_path}")
    
    # Generate quality report
    logger.info("\nStep 4: Generating quality report...")
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    report_path = report_dir / "quality_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 📊 Quality Report - Cannes Slogan Generation\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("## 📈 Statistics\n\n")
        f.write(f"- **Total Generated**: {len(slogans)} slogans\n")
        f.write(f"- **Target**: {TARGET_COUNT}\n")
        f.write(f"- **Candidate Pool**: {POOL_SIZE}\n")
        f.write(f"- **Selection Rate**: {len(slogans)/POOL_SIZE*100:.1f}%\n\n")
        
        f.write("## 🎯 Quality Metrics\n\n")
        avg_score = sum(s['score'] for s in slogans) / len(slogans)
        avg_punch = sum(s['punchiness'] for s in slogans) / len(slogans)
        avg_wit = sum(s['wit'] for s in slogans) / len(slogans)
        avg_clarity = sum(s['clarity'] for s in slogans) / len(slogans)
        avg_twist = sum(s['twist'] for s in slogans) / len(slogans)
        
        f.write(f"- **Average Score**: {avg_score:.3f}\n")
        f.write(f"- **Average Punchiness**: {avg_punch:.3f}\n")
        f.write(f"- **Average Wit**: {avg_wit:.3f}\n")
        f.write(f"- **Average Clarity**: {avg_clarity:.3f}\n")
        f.write(f"- **Average Twist**: {avg_twist:.3f}\n\n")
        
        f.write("## 🏆 Top 20 Slogans\n\n")
        for i, slogan in enumerate(slogans[:20], 1):
            f.write(f"{i}. **{slogan['text']}** (Score: {slogan['score']:.3f})\n")
        
        f.write("\n## 📊 Distribution\n\n")
        f.write("### Length Distribution\n")
        lengths = [len(s['text']) for s in slogans]
        f.write(f"- Min: {min(lengths)} chars\n")
        f.write(f"- Max: {max(lengths)} chars\n")
        f.write(f"- Average: {sum(lengths)/len(lengths):.1f} chars\n\n")
        
        f.write("### Word Count Distribution\n")
        word_counts = [len(s['text'].split()) for s in slogans]
        f.write(f"- Min: {min(word_counts)} words\n")
        f.write(f"- Max: {max(word_counts)} words\n")
        f.write(f"- Average: {sum(word_counts)/len(word_counts):.1f} words\n\n")
        
        f.write("---\n\n")
        f.write("Generated by **Cannes Slogan Generator** - AI-Powered Pipeline\n")
    
    logger.info(f"  ✓ Report saved to {report_path}")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("✅ GENERATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Generated: {len(slogans)} slogans")
    logger.info(f"Average score: {avg_score:.3f}")
    logger.info(f"\nOutput files:")
    logger.info(f"  - {jsonl_path}")
    logger.info(f"  - {csv_path}")
    logger.info(f"  - {txt_path}")
    logger.info(f"  - {report_path}")
    logger.info("\nTop 10 slogans:")
    for i, slogan in enumerate(slogans[:10], 1):
        logger.info(f"  {i:2d}. {slogan['text']} ({slogan['score']:.3f})")
    logger.info("="*80)


if __name__ == "__main__":
    main()
