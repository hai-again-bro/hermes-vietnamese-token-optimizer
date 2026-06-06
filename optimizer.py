"""
Vietnamese Token Optimizer for Hermes Agent
Tối ưu hóa token cho ngôn ngữ Tiếng Việt

Main optimizer module with word segmentation, normalization, and caching.
"""

import re
import json
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from collections import OrderedDict
import logging

try:
    from pyvi import ViTokenizer
except ImportError:
    ViTokenizer = None

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LRUCache:
    """Simple LRU Cache for token optimization results"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: str):
        """Put value in cache"""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)


class VietnameseStopWords:
    """Vietnamese stop words list"""
    
    STOPWORDS = {
        'à', 'ạ', 'ả', 'ấy', 'ai', 'anh', 'ấn', 'b', 'ba', 'bả', 'bác', 
        'bạn', 'bất', 'bằng', 'bây', 'bé', 'bên', 'bì', 'biết', 'bò', 'bộ', 
        'bốn', 'bốt', 'buổi', 'bụi', 'bước', 'bữa', 'c', 'ca', 'các', 'cách', 
        'cai', 'can', 'cần', 'căn', 'càng', 'cảnh', 'cáo', 'canh', 'cao', 'cập', 
        'cây', 'cả', 'cảm', 'cần', 'cáp', 'cát', 'cấu', 'cấy', 'cầu', 'cê', 
        'cè', 'cê', 'cha', 'chả', 'chác', 'cham', 'chan', 'chân', 'chặc', 'chặn', 
        'chặp', 'chặt', 'chạ', 'chạc', 'chạm', 'chạp', 'chạy', 'che', 'chè', 'chém', 
        'chen', 'chêm', 'chép', 'chết', 'chê', 'chêu', 'chi', 'chia', 'chía', 'chiám', 
        'chiếc', 'chiến', 'chiếp', 'chiêu', 'chịc', 'chịn', 'chị', 'chịu', 'chó', 'chòm', 
        'chon', 'chồng', 'chớp', 'chớt', 'chơi', 'chơn', 'chơu', 'chở', 'chỡ', 'chỗ', 
        'chỡn', 'chở', 'chỡu', 'chỗi', 'chỗng', 'chởn', 'chởu', 'chủ', 'chuà', 'chuẩn',
        'chuối', 'chuối', 'chuỗi', 'chuỳ', 'chuỷ', 'chứ', 'chứa', 'chứng', 'chứu', 'chứng',
        'chư', 'chưa', 'chưởng', 'chưỡng', 'chương', 'chười', 'chước', 'chười', 'chười',
        'chủi', 'chủng', 'chủy', 'chổ', 'chỗ', 'chỗi', 'chỗng', 'chỗu',
        'chuỗ', 'có', 'cô', 'cơ', 'cơm', 'cơn', 'có', 'còn', 'cốc', 'côi', 'cốp', 'cốt',
        'cớ', 'cờ', 'cờ', 'cời', 'cờu', 'cớ', 'cớm', 'cớn', 'cớp', 'cớt', 'cờ', 'cừ',
        'cứ', 'cứa', 'cứng', 'cứt', 'cứu', 'cứu', 'cứơ', 'cứư'
    }
    
    @classmethod
    def is_stopword(cls, word: str) -> bool:
        """Check if word is Vietnamese stopword"""
        return word.lower() in cls.STOPWORDS


class VietnameseTokenOptimizer:
    """Main Vietnamese token optimizer"""
    
    def __init__(
        self,
        use_cache: bool = True,
        max_cache_size: int = 10000,
        language: str = 'vi',
        strategy: str = 'balanced',
        custom_dict_path: Optional[str] = None,
        stopwords_path: Optional[str] = None
    ):
        """
        Initialize optimizer
        
        Args:
            use_cache: Enable LRU caching
            max_cache_size: Max cache entries
            language: Language code ('vi' for Vietnamese)
            strategy: Optimization strategy (light, balanced, aggressive)
            custom_dict_path: Path to custom dictionary JSON
            stopwords_path: Path to custom stopwords file
        """
        self.use_cache = use_cache
        self.language = language
        self.strategy = strategy
        self.cache = LRUCache(max_cache_size) if use_cache else None
        
        # Load custom dictionary
        self.custom_dict = self._load_custom_dict(custom_dict_path)
        
        # Strategy parameters
        self.strategies = {
            'light': {
                'remove_stopwords': False,
                'normalize_diacritics': True,
                'segment_words': False,
                'remove_extra_spaces': True
            },
            'balanced': {
                'remove_stopwords': True,
                'normalize_diacritics': True,
                'segment_words': True,
                'remove_extra_spaces': True
            },
            'aggressive': {
                'remove_stopwords': True,
                'normalize_diacritics': True,
                'segment_words': True,
                'remove_extra_spaces': True,
                'lowercase': True,
                'remove_punctuation': False
            }
        }
        
        self.config = self.strategies.get(strategy, self.strategies['balanced'])
        
        logger.info(f"VietnameseTokenOptimizer initialized with strategy={strategy}")
    
    def _load_custom_dict(self, dict_path: Optional[str]) -> Dict:
        """Load custom dictionary from JSON file"""
        if not dict_path:
            return {}
        
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load custom dict from {dict_path}: {e}")
            return {}
    
    def _normalize_spaces(self, text: str) -> str:
        """Normalize whitespace"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _normalize_diacritics(self, text: str) -> str:
        """Normalize Vietnamese diacritics and characters"""
        # Already normalized by pyvi if available
        return text
    
    def _remove_extra_spaces(self, text: str) -> str:
        """Remove extra spaces and normalize"""
        return self._normalize_spaces(text)
    
    def _segment_words(self, text: str) -> str:
        """Segment Vietnamese words using pyvi"""
        if not ViTokenizer:
            logger.warning("pyvi not available, skipping word segmentation")
            return text
        
        try:
            return ViTokenizer.tokenize(text)
        except Exception as e:
            logger.warning(f"Word segmentation failed: {e}")
            return text
    
    def _remove_stopwords(self, text: str) -> str:
        """Remove Vietnamese stopwords"""
        words = text.split()
        filtered = [w for w in words if not VietnameseStopWords.is_stopword(w)]
        return ' '.join(filtered)
    
    def _apply_custom_dict(self, text: str) -> str:
        """Apply custom dictionary replacements"""
        if not self.custom_dict:
            return text
        
        for old, new in self.custom_dict.items():
            text = text.replace(old, new)
        return text
    
    def optimize(self, text: str) -> str:
        """
        Optimize Vietnamese text for token reduction
        
        Args:
            text: Input Vietnamese text
            
        Returns:
            Optimized text
        """
        if not text or not isinstance(text, str):
            return text
        
        # Check cache
        if self.use_cache:
            cached = self.cache.get(text)
            if cached:
                return cached
        
        original_text = text
        
        # Apply optimizations based on strategy
        if self.config.get('remove_extra_spaces'):
            text = self._remove_extra_spaces(text)
        
        if self.config.get('segment_words'):
            text = self._segment_words(text)
        
        if self.config.get('normalize_diacritics'):
            text = self._normalize_diacritics(text)
        
        if self.config.get('remove_stopwords'):
            text = self._remove_stopwords(text)
        
        if self.config.get('lowercase'):
            text = text.lower()
        
        text = self._apply_custom_dict(text)
        text = self._remove_extra_spaces(text)
        
        # Cache result
        if self.use_cache:
            self.cache.put(original_text, text)
        
        return text
    
    def optimize_with_stats(self, text: str) -> Dict:
        """
        Optimize text and return statistics
        
        Args:
            text: Input Vietnamese text
            
        Returns:
            Dict with optimization stats
        """
        start_time = time.time()
        
        optimized = self.optimize(text)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Estimate token count (rough: ~1 token per 4 chars)
        original_tokens = len(text) // 4 + 1
        optimized_tokens = len(optimized) // 4 + 1
        tokens_saved = original_tokens - optimized_tokens
        
        return {
            'original_text': text,
            'optimized_text': optimized,
            'original_length': len(text),
            'optimized_length': len(optimized),
            'original_tokens_est': original_tokens,
            'optimized_tokens_est': optimized_tokens,
            'tokens_saved': tokens_saved,
            'compression_ratio': len(optimized) / len(text) if text else 1.0,
            'processing_time_ms': round(elapsed_ms, 2),
            'strategy': self.strategy
        }
    
    def batch_optimize(self, texts: List[str]) -> List[str]:
        """
        Optimize batch of texts efficiently
        
        Args:
            texts: List of Vietnamese texts
            
        Returns:
            List of optimized texts
        """
        return [self.optimize(text) for text in texts]
    
    def add_to_cache(self, original: str, optimized: str):
        """Add custom entry to cache"""
        if self.use_cache:
            self.cache.put(original, optimized)
    
    def clear_cache(self):
        """Clear optimization cache"""
        if self.use_cache:
            self.cache.clear()
    
    def cache_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.use_cache:
            return {'enabled': False}
        
        return {
            'enabled': True,
            'size': self.cache.size(),
            'max_size': self.cache.max_size
        }
