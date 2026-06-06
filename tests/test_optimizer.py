"""
Tests for Vietnamese Token Optimizer
Kiểm thử các tính năng tối ưu hóa token
"""

import pytest
from optimizer import VietnameseTokenOptimizer, VietnameseStopWords, LRUCache


class TestLRUCache:
    """Test LRU Cache functionality"""
    
    def test_cache_put_get(self):
        """Test basic cache put/get"""
        cache = LRUCache(max_size=3)
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when max size exceeded"""
        cache = LRUCache(max_size=2)
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_clear(self):
        """Test cache clearing"""
        cache = LRUCache(max_size=10)
        cache.put("key", "value")
        cache.clear()
        assert cache.size() == 0


class TestVietnameseStopWords:
    """Test Vietnamese stopwords"""
    
    def test_stopword_detection(self):
        """Test stopword detection"""
        assert VietnameseStopWords.is_stopword('và')
        assert VietnameseStopWords.is_stopword('là')
        assert VietnameseStopWords.is_stopword('của')
    
    def test_non_stopword(self):
        """Test non-stopword detection"""
        assert not VietnameseStopWords.is_stopword('tiếng')
        assert not VietnameseStopWords.is_stopword('việt')


class TestVietnameseTokenOptimizer:
    """Test main optimizer functionality"""
    
    def test_initialization(self):
        """Test optimizer initialization"""
        optimizer = VietnameseTokenOptimizer(strategy='balanced')
        assert optimizer.strategy == 'balanced'
        assert optimizer.use_cache is True
    
    def test_normalize_spaces(self):
        """Test space normalization"""
        optimizer = VietnameseTokenOptimizer()
        text = "Xin   chào    bạn"
        result = optimizer._normalize_spaces(text)
        assert result == "Xin chào bạn"
    
    def test_optimize_basic(self):
        """Test basic optimization"""
        optimizer = VietnameseTokenOptimizer(strategy='light')
        text = "Xin   chào   bạn"
        result = optimizer.optimize(text)
        assert "  " not in result  # No double spaces
    
    def test_optimize_with_stats(self):
        """Test optimization with statistics"""
        optimizer = VietnameseTokenOptimizer()
        text = "Xin chào bạn"
        stats = optimizer.optimize_with_stats(text)
        
        assert 'optimized_text' in stats
        assert 'original_length' in stats
        assert 'optimized_length' in stats
        assert 'compression_ratio' in stats
        assert 'processing_time_ms' in stats
    
    def test_cache_functionality(self):
        """Test caching during optimization"""
        optimizer = VietnameseTokenOptimizer(use_cache=True)
        text = "Xin chào"
        
        # First call
        result1 = optimizer.optimize(text)
        cache_size_1 = optimizer.cache.size()
        
        # Second call (should hit cache)
        result2 = optimizer.optimize(text)
        cache_size_2 = optimizer.cache.size()
        
        assert result1 == result2
        assert cache_size_1 == cache_size_2
    
    def test_batch_optimize(self):
        """Test batch optimization"""
        optimizer = VietnameseTokenOptimizer()
        texts = [
            "Xin   chào",
            "Đây    là   test",
            "Tiếng  Việt"
        ]
        results = optimizer.batch_optimize(texts)
        
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)
    
    def test_strategy_light(self):
        """Test light strategy"""
        optimizer = VietnameseTokenOptimizer(strategy='light')
        text = "Xin   chào   bạn"
        result = optimizer.optimize(text)
        assert result == "Xin chào bạn"
    
    def test_strategy_balanced(self):
        """Test balanced strategy"""
        optimizer = VietnameseTokenOptimizer(strategy='balanced')
        text = "Xin chào bạn"
        result = optimizer.optimize(text)
        assert len(result) > 0
    
    def test_strategy_aggressive(self):
        """Test aggressive strategy"""
        optimizer = VietnameseTokenOptimizer(strategy='aggressive')
        text = "Xin Chào Bạn"
        result = optimizer.optimize(text)
        # Aggressive should lowercase
        assert result == result.lower()
    
    def test_cache_stats(self):
        """Test cache statistics"""
        optimizer = VietnameseTokenOptimizer(use_cache=True)
        stats = optimizer.cache_stats()
        
        assert stats['enabled'] is True
        assert 'size' in stats
        assert 'max_size' in stats


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_string(self):
        """Test with empty string"""
        optimizer = VietnameseTokenOptimizer()
        result = optimizer.optimize("")
        assert result == ""
    
    def test_none_input(self):
        """Test with None input"""
        optimizer = VietnameseTokenOptimizer()
        result = optimizer.optimize(None)
        assert result is None
    
    def test_single_word(self):
        """Test with single word"""
        optimizer = VietnameseTokenOptimizer()
        result = optimizer.optimize("Xin")
        assert len(result) > 0
    
    def test_special_characters(self):
        """Test with special characters"""
        optimizer = VietnameseTokenOptimizer()
        text = "Xin chào!!! Bạn???"
        result = optimizer.optimize(text)
        assert len(result) > 0
    
    def test_numbers(self):
        """Test with numbers"""
        optimizer = VietnameseTokenOptimizer()
        text = "Năm 2026 là một năm tốt"
        result = optimizer.optimize(text)
        assert "2026" in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
