#!/usr/bin/env python3
"""
Example 2: Batch processing
Ví dụ 2: Xử lý hàng loạt
"""

from optimizer import VietnameseTokenOptimizer

# Initialize optimizer
optimizer = VietnameseTokenOptimizer(strategy='aggressive')

# Sample texts
texts = [
    "Xin chào các bạn",
    "Đây là ví dụ về batch processing",
    "Chúng tôi đang tối ưu hóa nhiều văn bản cùng lúc",
    "Token optimization cho Tiếng Việt rất quan trọng",
    "Hermes Agent sử dụng công cụ này để tiết kiệm chi phí"
]

print("Original texts:")
for i, text in enumerate(texts, 1):
    print(f"  {i}. {text} ({len(text)} chars)")
print()

# Batch optimize
optimized_texts = optimizer.batch_optimize(texts)

print("Optimized texts:")
for i, text in enumerate(optimized_texts, 1):
    print(f"  {i}. {text} ({len(text)} chars)")
print()

# Calculate total savings
total_original = sum(len(t) for t in texts)
total_optimized = sum(len(t) for t in optimized_texts)
savings = total_original - total_optimized
savings_pct = (1 - total_optimized / total_original) * 100

print(f"Total savings: {savings} chars ({savings_pct:.1f}%)")
print(f"Cache stats: {optimizer.cache_stats()}")
