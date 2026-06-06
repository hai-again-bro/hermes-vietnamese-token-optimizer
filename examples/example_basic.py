#!/usr/bin/env python3
"""
Example 1: Basic text optimization
Ví dụ 1: Tối ưu hóa text cơ bản
"""

from optimizer import VietnameseTokenOptimizer

# Initialize optimizer with default (balanced) strategy
optimizer = VietnameseTokenOptimizer()

# Sample Vietnamese text
text = """
Xin   chào   các   bạn.  Đây   là   một   ví   dụ   về   tối   ưu   hóa   token   cho   Tiếng   Việt.
Chúng   tôi   sử   dụng   các   kỹ   thuật   xử   lý   ngôn   ngữ   tự   nhiên   để   giảm   chi   phí   token.
"""

print("Original text:")
print(text)
print(f"Length: {len(text)} characters")
print()

# Optimize
optimized = optimizer.optimize(text)
print("Optimized text:")
print(optimized)
print(f"Length: {len(optimized)} characters")
print()

# Statistics
stats = optimizer.optimize_with_stats(text)
print("Statistics:")
print(f"  Original tokens (est): {stats['original_tokens_est']}")
print(f"  Optimized tokens (est): {stats['optimized_tokens_est']}")
print(f"  Tokens saved: {stats['tokens_saved']}")
print(f"  Compression ratio: {stats['compression_ratio']:.2%}")
print(f"  Processing time: {stats['processing_time_ms']}ms")
