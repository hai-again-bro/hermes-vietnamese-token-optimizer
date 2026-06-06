#!/usr/bin/env python3
"""
Vietnamese Token Optimizer CLI
Command-line interface for token optimization
"""

import argparse
import json
import sys
from pathlib import Path
from optimizer import VietnameseTokenOptimizer


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Vietnamese Token Optimizer - Giảm token cho Tiếng Việt',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ví dụ sử dụng:
  python -m optimizer --text "Xin chào bạn"
  python -m optimizer --input input.txt --output output.txt
  python -m optimizer --batch --input-dir ./texts/ --output-dir ./optimized/
  python -m optimizer --text "..." --stats --strategy aggressive
        '''
    )
    
    parser.add_argument(
        '--text',
        help='Optimize single text input'
    )
    parser.add_argument(
        '--input',
        help='Input file path'
    )
    parser.add_argument(
        '--output',
        help='Output file path'
    )
    parser.add_argument(
        '--input-dir',
        help='Input directory for batch processing'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for batch results'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Enable batch mode processing'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show optimization statistics'
    )
    parser.add_argument(
        '--strategy',
        choices=['light', 'balanced', 'aggressive'],
        default='balanced',
        help='Optimization strategy (default: balanced)'
    )
    parser.add_argument(
        '--config',
        help='Path to config JSON file'
    )
    parser.add_argument(
        '--cache-size',
        type=int,
        default=10000,
        help='LRU cache size (default: 10000)'
    )
    
    args = parser.parse_args()
    
    # Initialize optimizer
    optimizer = VietnameseTokenOptimizer(
        use_cache=True,
        max_cache_size=args.cache_size,
        strategy=args.strategy
    )
    
    # Single text optimization
    if args.text:
        if args.stats:
            result = optimizer.optimize_with_stats(args.text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            optimized = optimizer.optimize(args.text)
            print(optimized)
    
    # File optimization
    elif args.input and args.output:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                content = f.read()
            
            optimized = optimizer.optimize(content)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(optimized)
            
            print(f"✓ Optimized: {args.input} → {args.output}")
            
            if args.stats:
                stats = optimizer.optimize_with_stats(content)
                print(f"  Original: {stats['original_length']} chars ({stats['original_tokens_est']} tokens)")
                print(f"  Optimized: {stats['optimized_length']} chars ({stats['optimized_tokens_est']} tokens)")
                print(f"  Saved: {stats['tokens_saved']} tokens ({stats['compression_ratio']:.1%} size)")
        
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Batch processing
    elif args.batch and args.input_dir and args.output_dir:
        try:
            input_path = Path(args.input_dir)
            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            txt_files = list(input_path.glob('*.txt'))
            if not txt_files:
                print(f"✗ No .txt files found in {args.input_dir}")
                sys.exit(1)
            
            total_saved = 0
            for i, file in enumerate(txt_files, 1):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    optimized = optimizer.optimize(content)
                    
                    out_file = output_path / file.name
                    with open(out_file, 'w', encoding='utf-8') as f:
                        f.write(optimized)
                    
                    tokens_before = len(content) // 4 + 1
                    tokens_after = len(optimized) // 4 + 1
                    saved = tokens_before - tokens_after
                    total_saved += saved
                    
                    print(f"  [{i}/{len(txt_files)}] {file.name}: -{saved} tokens")
                
                except Exception as e:
                    print(f"  [!] {file.name}: {e}")
            
            print(f"✓ Batch complete: {len(txt_files)} files → {args.output_dir}")
            print(f"  Total tokens saved: {total_saved}")
        
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
