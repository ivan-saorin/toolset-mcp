"""
Enhanced Text Analyzer Engine with advanced text processing capabilities
"""

import re
import string
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
from ...shared.base import BaseFeature, ToolResponse
from ...shared.types import TextAnalysisMode


class TextAnalyzerEngine(BaseFeature):
    """Advanced text analyzer with readability, sentiment, and keyword extraction"""
    
    def __init__(self):
        super().__init__("text_analyzer", "2.0.0")
        
        # Common stop words for keyword extraction
        self.stop_words = set([
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'shall', 'to',
            'of', 'in', 'for', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
            'just', 'don', 'now', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them',
            'their', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',
            'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by',
            'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
            'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
        ])
        
        # Sentiment words
        self.positive_words = set([
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love',
            'perfect', 'best', 'beautiful', 'awesome', 'nice', 'happy', 'fun', 'brilliant',
            'outstanding', 'super', 'positive', 'fortunate', 'correct', 'superior'
        ])
        
        self.negative_words = set([
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'ugly', 'disgusting',
            'sad', 'angry', 'disappointing', 'poor', 'negative', 'unfortunate', 'wrong',
            'inferior', 'unpleasant', 'nasty', 'evil', 'fail', 'failed'
        ])
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of text analyzer tools"""
        return [
            {
                "name": "text_analyze",
                "description": "Analyze text with various metrics",
                "parameters": {
                    "text": "Text to analyze",
                    "mode": f"Analysis mode: {', '.join(TextAnalysisMode.values())}"
                }
            },
            {
                "name": "text_compare",
                "description": "Compare two texts",
                "parameters": {
                    "text1": "First text",
                    "text2": "Second text"
                }
            },
            {
                "name": "text_extract",
                "description": "Extract specific information from text",
                "parameters": {
                    "text": "Source text",
                    "extract_type": "Type: urls, emails, numbers, dates, hashtags, mentions"
                }
            },
            {
                "name": "text_transform",
                "description": "Transform text",
                "parameters": {
                    "text": "Text to transform",
                    "transformation": "Type: uppercase, lowercase, title, reverse, remove_punctuation, remove_spaces"
                }
            }
        ]
    
    def text_analyze(self, text: str, mode: str = "basic") -> ToolResponse:
        """
        Analyze text with various metrics
        
        Args:
            text: Text to analyze
            mode: Analysis mode (basic, detailed, readability, sentiment, keywords)
        """
        try:
            if not text:
                return ToolResponse(success=False, error="No text provided")
            
            mode = mode.lower()
            
            if mode == "basic":
                return self._basic_analysis(text)
            elif mode == "detailed":
                return self._detailed_analysis(text)
            elif mode == "readability":
                return self._readability_analysis(text)
            elif mode == "sentiment":
                return self._sentiment_analysis(text)
            elif mode == "keywords":
                return self._keyword_extraction(text)
            else:
                # Default to basic with a note
                result = self._basic_analysis(text)
                result.data["note"] = f"Unknown mode '{mode}', defaulting to basic"
                return result
                
        except Exception as e:
            return self.handle_error(f"text_analyze({mode})", e)
    
    def text_compare(self, text1: str, text2: str) -> ToolResponse:
        """
        Compare two texts for similarity and differences
        
        Args:
            text1: First text
            text2: Second text
        """
        try:
            # Basic metrics comparison
            words1 = text1.lower().split()
            words2 = text2.lower().split()
            
            set1 = set(words1)
            set2 = set(words2)
            
            # Calculate similarity metrics
            common_words = set1.intersection(set2)
            unique_to_1 = set1 - set2
            unique_to_2 = set2 - set1
            
            # Jaccard similarity
            jaccard = len(common_words) / len(set1.union(set2)) if set1 or set2 else 1.0
            
            # Character-level similarity
            chars1 = set(text1.lower())
            chars2 = set(text2.lower())
            char_similarity = len(chars1.intersection(chars2)) / len(chars1.union(chars2)) if chars1 or chars2 else 1.0
            
            # Length comparison
            len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2)) if text1 or text2 else 1.0
            
            return ToolResponse(
                success=True,
                data={
                    "text1_stats": {
                        "characters": len(text1),
                        "words": len(words1),
                        "unique_words": len(set1)
                    },
                    "text2_stats": {
                        "characters": len(text2),
                        "words": len(words2),
                        "unique_words": len(set2)
                    },
                    "comparison": {
                        "common_words": len(common_words),
                        "unique_to_text1": len(unique_to_1),
                        "unique_to_text2": len(unique_to_2),
                        "jaccard_similarity": round(jaccard, 3),
                        "character_similarity": round(char_similarity, 3),
                        "length_ratio": round(len_ratio, 3),
                        "overall_similarity": round((jaccard + char_similarity + len_ratio) / 3, 3)
                    },
                    "samples": {
                        "common_words_sample": list(common_words)[:10],
                        "unique_to_1_sample": list(unique_to_1)[:10],
                        "unique_to_2_sample": list(unique_to_2)[:10]
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("text_compare", e)
    
    def text_extract(self, text: str, extract_type: str) -> ToolResponse:
        """
        Extract specific information from text
        
        Args:
            text: Source text
            extract_type: Type of information to extract
        """
        try:
            extract_type = extract_type.lower()
            results = []
            
            if extract_type == "urls":
                pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                results = re.findall(pattern, text)
                
            elif extract_type == "emails":
                pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                results = re.findall(pattern, text)
                
            elif extract_type == "numbers":
                # Extract all numbers (integers and decimals)
                pattern = r'-?\d+\.?\d*'
                results = re.findall(pattern, text)
                # Convert to appropriate type
                converted = []
                for num in results:
                    if '.' in num:
                        converted.append(float(num))
                    else:
                        converted.append(int(num))
                results = converted
                
            elif extract_type == "dates":
                # Common date patterns
                patterns = [
                    r'\d{1,2}/\d{1,2}/\d{2,4}',  # DD/MM/YYYY or MM/DD/YYYY
                    r'\d{1,2}-\d{1,2}-\d{2,4}',  # DD-MM-YYYY
                    r'\d{4}-\d{1,2}-\d{1,2}',    # YYYY-MM-DD
                    r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',
                    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}'
                ]
                for pattern in patterns:
                    results.extend(re.findall(pattern, text, re.IGNORECASE))
                
            elif extract_type == "hashtags":
                pattern = r'#\w+'
                results = re.findall(pattern, text)
                
            elif extract_type == "mentions":
                pattern = r'@\w+'
                results = re.findall(pattern, text)
                
            else:
                return ToolResponse(
                    success=False,
                    error=f"Unknown extract type: {extract_type}"
                )
            
            return ToolResponse(
                success=True,
                data={
                    "extract_type": extract_type,
                    "found": len(results),
                    "results": results,
                    "unique_count": len(set(results)) if results else 0
                }
            )
            
        except Exception as e:
            return self.handle_error(f"text_extract({extract_type})", e)
    
    def text_transform(self, text: str, transformation: str) -> ToolResponse:
        """
        Transform text in various ways
        
        Args:
            text: Text to transform
            transformation: Type of transformation
        """
        try:
            transformation = transformation.lower()
            
            if transformation == "uppercase":
                result = text.upper()
            elif transformation == "lowercase":
                result = text.lower()
            elif transformation == "title":
                result = text.title()
            elif transformation == "reverse":
                result = text[::-1]
            elif transformation == "remove_punctuation":
                result = text.translate(str.maketrans('', '', string.punctuation))
            elif transformation == "remove_spaces":
                result = ''.join(text.split())
            elif transformation == "snake_case":
                result = re.sub(r'[\s\-]+', '_', text.lower())
            elif transformation == "camel_case":
                words = re.sub(r'[^\w\s]', '', text).split()
                result = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
            elif transformation == "pascal_case":
                words = re.sub(r'[^\w\s]', '', text).split()
                result = ''.join(w.capitalize() for w in words)
            elif transformation == "remove_numbers":
                result = re.sub(r'\d+', '', text)
            elif transformation == "extract_letters":
                result = ''.join(c for c in text if c.isalpha())
            elif transformation == "extract_numbers":
                result = ''.join(c for c in text if c.isdigit())
            else:
                return ToolResponse(
                    success=False,
                    error=f"Unknown transformation: {transformation}"
                )
            
            return ToolResponse(
                success=True,
                data={
                    "transformation": transformation,
                    "original": text[:100] + "..." if len(text) > 100 else text,
                    "result": result,
                    "original_length": len(text),
                    "result_length": len(result)
                }
            )
            
        except Exception as e:
            return self.handle_error(f"text_transform({transformation})", e)
    
    def _basic_analysis(self, text: str) -> ToolResponse:
        """Perform basic text analysis"""
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        return ToolResponse(
            success=True,
            data={
                "mode": "basic",
                "statistics": {
                    "characters": len(text),
                    "characters_no_spaces": len(text.replace(' ', '')),
                    "words": len(words),
                    "sentences": len(sentences),
                    "paragraphs": len(paragraphs),
                    "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
                    "average_sentence_length": len(words) / len(sentences) if sentences else 0
                },
                "preview": text[:200] + "..." if len(text) > 200 else text
            }
        )
    
    def _detailed_analysis(self, text: str) -> ToolResponse:
        """Perform detailed text analysis"""
        basic = self._basic_analysis(text)
        words = text.lower().split()
        
        # Word frequency
        word_freq = Counter(words)
        
        # Character frequency
        char_freq = Counter(text.lower())
        
        # Most common words (excluding stop words)
        content_words = [w for w in words if w not in self.stop_words]
        common_content = Counter(content_words).most_common(10)
        
        # Unique words
        unique_words = set(words)
        
        # Lexical diversity
        lexical_diversity = len(unique_words) / len(words) if words else 0
        
        data = basic.data
        data["mode"] = "detailed"
        data["word_analysis"] = {
            "unique_words": len(unique_words),
            "lexical_diversity": round(lexical_diversity, 3),
            "most_common_words": word_freq.most_common(10),
            "most_common_content_words": common_content,
            "longest_word": max(words, key=len) if words else "",
            "shortest_word": min(words, key=len) if words else ""
        }
        data["character_analysis"] = {
            "most_common_chars": char_freq.most_common(10),
            "alphabetic": sum(1 for c in text if c.isalpha()),
            "numeric": sum(1 for c in text if c.isdigit()),
            "punctuation": sum(1 for c in text if c in string.punctuation),
            "whitespace": sum(1 for c in text if c.isspace())
        }
        
        return ToolResponse(success=True, data=data)
    
    def _readability_analysis(self, text: str) -> ToolResponse:
        """Analyze text readability"""
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Count syllables (simple approximation)
        def count_syllables(word):
            word = word.lower()
            vowels = "aeiou"
            syllable_count = 0
            previous_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = is_vowel
            
            # Ensure at least one syllable
            return max(1, syllable_count)
        
        total_syllables = sum(count_syllables(word) for word in words)
        
        # Flesch Reading Ease
        # 206.835 - 1.015(total words/total sentences) - 84.6(total syllables/total words)
        if sentences and words:
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables_per_word = total_syllables / len(words)
            
            flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
            
            # Interpret score
            if flesch_score >= 90:
                level = "Very Easy (5th grade)"
            elif flesch_score >= 80:
                level = "Easy (6th grade)"
            elif flesch_score >= 70:
                level = "Fairly Easy (7th grade)"
            elif flesch_score >= 60:
                level = "Standard (8th-9th grade)"
            elif flesch_score >= 50:
                level = "Fairly Difficult (10th-12th grade)"
            elif flesch_score >= 30:
                level = "Difficult (College)"
            else:
                level = "Very Difficult (College graduate)"
        else:
            flesch_score = 0
            level = "Unable to calculate"
        
        # Complex words (3+ syllables)
        complex_words = [w for w in words if count_syllables(w) >= 3]
        
        return ToolResponse(
            success=True,
            data={
                "mode": "readability",
                "metrics": {
                    "flesch_reading_ease": round(flesch_score, 1),
                    "reading_level": level,
                    "average_sentence_length": len(words) / len(sentences) if sentences else 0,
                    "average_syllables_per_word": total_syllables / len(words) if words else 0,
                    "complex_words": len(complex_words),
                    "complex_word_percentage": (len(complex_words) / len(words) * 100) if words else 0
                },
                "statistics": {
                    "words": len(words),
                    "sentences": len(sentences),
                    "syllables": total_syllables
                }
            }
        )
    
    def _sentiment_analysis(self, text: str) -> ToolResponse:
        """Analyze text sentiment"""
        words = text.lower().split()
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        neutral_count = len(words) - positive_count - negative_count
        
        # Calculate sentiment score
        if positive_count + negative_count > 0:
            sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            sentiment_score = 0
        
        # Determine overall sentiment
        if sentiment_score > 0.1:
            overall = "Positive"
        elif sentiment_score < -0.1:
            overall = "Negative"
        else:
            overall = "Neutral"
        
        # Find emotional words
        found_positive = [w for w in words if w in self.positive_words]
        found_negative = [w for w in words if w in self.negative_words]
        
        return ToolResponse(
            success=True,
            data={
                "mode": "sentiment",
                "sentiment": {
                    "overall": overall,
                    "score": round(sentiment_score, 3),
                    "confidence": round(abs(sentiment_score), 3)
                },
                "word_counts": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "total": len(words)
                },
                "emotional_words": {
                    "positive_found": list(set(found_positive))[:10],
                    "negative_found": list(set(found_negative))[:10]
                },
                "percentages": {
                    "positive": round(positive_count / len(words) * 100, 1) if words else 0,
                    "negative": round(negative_count / len(words) * 100, 1) if words else 0,
                    "neutral": round(neutral_count / len(words) * 100, 1) if words else 0
                }
            }
        )
    
    def _keyword_extraction(self, text: str) -> ToolResponse:
        """Extract keywords from text"""
        # Simple keyword extraction based on frequency and filtering
        words = text.lower().split()
        
        # Filter out stop words and short words
        content_words = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        # Count frequencies
        word_freq = Counter(content_words)
        
        # Get most common keywords
        keywords = word_freq.most_common(20)
        
        # Extract noun phrases (simple approach)
        # Look for capitalized words that might be proper nouns
        proper_nouns = set()
        for word in text.split():
            if word[0].isupper() and word.lower() not in self.stop_words:
                proper_nouns.add(word)
        
        # Bigrams (two-word phrases)
        bigrams = []
        words_original = text.split()
        for i in range(len(words_original) - 1):
            if (words_original[i].lower() not in self.stop_words and 
                words_original[i+1].lower() not in self.stop_words):
                bigrams.append(f"{words_original[i]} {words_original[i+1]}")
        
        bigram_freq = Counter(bigrams).most_common(10)
        
        return ToolResponse(
            success=True,
            data={
                "mode": "keywords",
                "keywords": {
                    "top_keywords": keywords,
                    "proper_nouns": list(proper_nouns)[:15],
                    "top_bigrams": bigram_freq
                },
                "statistics": {
                    "total_words": len(words),
                    "unique_keywords": len(set(content_words)),
                    "keyword_density": round(len(content_words) / len(words) * 100, 1) if words else 0
                }
            }
        )
