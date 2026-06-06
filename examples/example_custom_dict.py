#!/usr/bin/env python3
"""
Example 3: Using custom dictionary
Ví dụ 3: Sử dụng từ điển tuỳ chỉnh
"""

from optimizer import VietnameseTokenOptimizer

# Initialize with custom dictionary
optimizer = VietnameseTokenOptimizer(
    custom_dict_path='custom_dict.json'
)

# Add custom entries to cache
optimizer.add_to_cache("mình", "m")
optimizer.add_to_cache("tôi", "t")

# Test with Vietnamese text containing slang/domain terms
text = "Mình là developer làm việc với Hermes Token Optimizer"

print("Original:", text)
print("Optimized:", optimizer.optimize(text))
print()

# Show cache stats
print("Cache stats:", optimizer.cache_stats())
