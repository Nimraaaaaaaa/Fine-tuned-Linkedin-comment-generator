import random
import re
from typing import Dict, List, Tuple
from collections import defaultdict
import json
from load_and_embed import vectordb
import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import pandas as pd


class HumanStyleGenerator:
    def __init__(self):
        # Real human patterns from saywhat.ai data
        self.human_patterns = {
            "agreement_short": [
                "Haha, been there!", "Honestly, that's so true.", "I felt this.", "So real.", "This made me smile."
            ],
            "agreement_extended": [
                "So true. {insight} really makes a difference.",
                "Exactly. {topic} is so important.",
                "Love this. {point} changes everything.",
                "Great point. {observation} is key.",
                "Makes sense. {reason} explains a lot.",
                "So true. The point about {specific_point} really stands out."
            ],
            "observations": [
                "Interesting point about {topic}.",
                "Good perspective on {subject}.",
                "The point about {quote} is so important.",
                "What a freeing statement.",
                "Very important point.",
                "Interesting observation.",
                "Interesting point about {specific_point}."
            ],
            
            "business_insights": [
                "Most brands just don't understand this.",
                "Strategic approach is everything.",
                "Consistency breeds trust.",
                "Actions speak louder than promises.",
                "Reputation is earned over years.",
                "True success is found in actions."
            ],
            "practical_feedback": [
                "I especially like {specific_point} because {reason}.",
                "Totally agree with what you said about {specific_point} ",
                "Really appreciate the focus on {specific_point}."
            ],
            "experience_sharing": [
                "Been there — it's true that {lesson} makes a difference.",
                "Felt something similar — {realization} really stands out.",
                "Can relate — {experience} is something many overlook.",
                "Faced this before — {situation} is more common than we think.",
                "Seen this myself — {outcome} often comes with time."
            ],

            "personal_endorsement": [
                "This resonates with me {personal_experience}.",
                "Love how you highlighted {specific_point}" 
                 "It's so relatable {specific_point} ",
                "Your take on {topic} really hits home for me."
            ]
        }
        
        # Extract words/phrases to avoid from post
        self.stop_words = {
            'the', 'is', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during'
        }
        
        # Banned AI words (absolutely avoid)
        self.ai_banned_words = {
            'truly', 'amazing', 'incredible', 'fantastic', 'outstanding',
            'remarkable', 'exceptional', 'phenomenal', 'game-changer',
            'disruptive', 'innovative', 'revolutionary', 'cutting-edge',
            'leverage', 'utilize', 'optimize', 'maximize', 'synergy',
            'paradigm', 'holistic', 'strategic', 'dynamic', 'robust',
            'Truly', 'often', 'clarity comes', 'gamechanger', 'approach',
             'This is a powerful reminder', 'Such a powerful reminder', 'unlock', 
            "It's so easy to get caught", 'this is such a refreshing and grounding reminder..' , 
            'We spend so much time chasing', 'can truly transform', 'can shift everything.' , "that's where the power is.", 
            'really is the secret sauce', 'captured', 'Spot on', 'hits hard', 'this is how real transformation begins', 
            'Powerful message', 'game changer','its about','its not about','Its where magic happens','milstones','foster','real driver'
        }
        
        # Real conversation connectors
        self.natural_connectors = [
            "and here's the thing", "but here's what i learned",
            "what strikes me is", "the reality is", "i think the key is",
            "from what i see", "in my experience", "honestly"
        ]
        
        # Memory for avoiding repetition
        self.used_patterns = defaultdict(set)
        
    def extract_specific_points(self, post_content: str) -> List[str]:
        """Extract numbered or bulleted points from post content"""
        pattern = r'(?:\d+\.\s+|-\s+)(.*)'
        points = re.findall(pattern, post_content)
        return [point.strip() for point in points if point.strip()]
    
    def extract_post_keywords(self, post_content: str) -> set:
        """Extract meaningful words from post to avoid repetition"""
        words = re.findall(r'\b\w+\b', post_content.lower())
        meaningful_words = {
            word for word in words
            if len(word) > 3 and word not in self.stop_words
        }
        return meaningful_words
    
    def analyze_post_theme(self, post_content: str) -> str:
        """Analyze post to determine theme"""
        content_lower = post_content.lower()
        
        themes = {
            'career_growth': ['career', 'growth', 'promotion', 'success', 'achievement'],
            'leadership': ['leadership', 'team', 'management', 'culture', 'people'],
            'business_strategy': ['business', 'strategy', 'roi', 'revenue', 'growth'],
            'personal_story': ['journey', 'experience', 'learned', 'challenge', 'overcome'],
            'advice_sharing': ['advice', 'tip', 'lesson', 'learned', 'mistake'],
            'networking': ['connection', 'relationship', 'network', 'community'],
            'motivation': ['motivation', 'inspiration', 'mindset', 'attitude'],
            'well_being': ['mental health', 'burnout', 'well-being', 'health', 'rest']
        }
        
        for theme, keywords in themes.items():
            if any(keyword in content_lower for keyword in keywords):
                return theme
                
        return 'general_business'
    
    def get_post_sentiment(self, post_content: str) -> str:
        """Determine post sentiment"""
        positive_indicators = ['success', 'achievement', 'great', 'love', 'excited', 'proud']
        negative_indicators = ['challenge', 'difficult', 'problem', 'struggle', 'failed']
        
        content_lower = post_content.lower()
        pos_count = sum(1 for word in positive_indicators if word in content_lower)
        neg_count = sum(1 for word in negative_indicators if word in content_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'challenging'
        else:
            return 'neutral'
    
    def select_human_pattern(self, theme: str, sentiment: str, post_id: str, has_specific_point: bool) -> Tuple[str, str]:
        """Select appropriate human pattern based on context and available content"""
        used_for_post = self.used_patterns.get(post_id, set())
        
        pattern_options = []
        if sentiment == 'positive':
            if theme in ['career_growth', 'personal_story', 'well_being']:
                pattern_options.extend(['agreement_extended', 'personal_endorsement'])
                if has_specific_point:
                    pattern_options.append('practical_feedback')
            else:
                pattern_options.extend(['agreement_short', 'observations'])
        elif sentiment == 'challenging':
            pattern_options.extend(['experience_sharing', 'personal_endorsement'])
        else:
            pattern_options.extend(['observations', 'agreement_short', 'questions_engagement'])
        
        if theme == 'business_strategy':
            pattern_options.append('business_insights')
        
        available_patterns = []
        for pattern_type in pattern_options:
            for pattern in self.human_patterns[pattern_type]:
                if '{specific_point}' in pattern and not has_specific_point:
                    continue
                if pattern not in used_for_post:
                    available_patterns.append((pattern_type, pattern))
        
        if not available_patterns:
            self.used_patterns[post_id] = set()
            for pattern_type in pattern_options:
                for pattern in self.human_patterns[pattern_type]:
                    if '{specific_point}' in pattern and not has_specific_point:
                        continue
                    available_patterns.append((pattern_type, pattern))
        
        selected_pattern = random.choice(available_patterns)
        self.used_patterns[post_id].add(selected_pattern[1])
        
        return selected_pattern
    
    def extract_fillable_content(self, post_content: str, theme: str) -> Dict[str, str]:
        """Extract content to fill in pattern placeholders"""
        sentences = [s.strip() for s in post_content.split('.') if len(s.strip()) > 10]
        if sentences:
            fill_content = {}
            fill_content['specific_point'] = sentences[0]
        
        if '{insight}' in post_content or theme == 'advice_sharing':
            fill_content['insight'] = random.choice(['this approach', 'this mindset', 'this perspective'])
        
        if '{topic}' in post_content or theme in ['business_strategy', 'leadership', 'well_being']:
            fill_content['topic'] = random.choice(['this strategy', 'this approach', 'building trust', 'mental health'])
        
        if '{lesson}' in post_content or theme == 'personal_story':
            fill_content['lesson'] = random.choice(['persistence', 'patience', 'consistency'])
        
        fill_content.update({
            'point': random.choice(['building relationships', 'taking action', 'consistency']),
            'observation': random.choice(['timing', 'approach', 'mindset']),
            'reason': random.choice(['experience', 'timing', 'approach']),
            'outcome': random.choice(['the learning', 'the growth', 'the experience']),
            'action': random.choice(['implement this', 'make the change', 'take action']),
            'subject': random.choice(['leadership', 'growth', 'culture', 'well-being']),
            'quote': random.choice(sentences) if sentences else 'this idea',
            'realization': random.choice(['clarity', 'focus', 'priority']),
            'experience': random.choice(['facing challenges', 'learning from mistakes', 'building trust']),
            'situation': random.choice(['this challenge', 'this scenario', 'this experience']),
            'challenge': random.choice(['resistance', 'setbacks', 'time management']),
            'personal_experience': random.choice(['my own journey', 'a similar situation', 'past challenges'])
        })
        
        return fill_content
    
    def humanize_comment(self, comment: str) -> str:
        """Final humanization pass"""
        ai_phrases = [
            'it is important to note', 'it is worth mentioning',
            'in conclusion', 'furthermore', 'moreover', 'additionally'
        ]
        
        for phrase in ai_phrases:
            comment = comment.replace(phrase, '')
        
        comment = comment.replace('!', '.')
        comment = comment.replace('..', '.')
        
        sentences = comment.split('.')
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                words = sentence.split()
                if words:
                    words[0] = words[0].capitalize()
                    cleaned_sentences.append(' '.join(words))
        
        return '. '.join(cleaned_sentences) + ('.' if cleaned_sentences else '')
    
    def extract_and_fill_pattern_from_sample(self, sample_comment: str, post_content: str) -> str:
        """Extracts a simple pattern from the sample comment and fills it with content from the new post."""
        # Try to find a key phrase in the sample comment (e.g., 'point about', 'because', etc.)
        # and replace it with content from the new post
        specific_points = self.extract_specific_points(post_content)
        sentences = [s.strip() for s in post_content.split('.') if len(s.strip()) > 10]
        # Default fallback if nothing found
        fill_point = specific_points[0] if specific_points else (sentences[0] if sentences else "this topic")
        # Replace common patterns
        comment = sample_comment
        # Replace 'about ...' with about {fill_point}
        comment = re.sub(r'(about )[^ ,.]+', f"about {fill_point}", comment)
        # Replace 'because ...' with because {fill_point}
        comment = re.sub(r'(because )[^ ,.]+', f"because {fill_point}", comment)
        # If there are any curly braces, fill them
        comment = re.sub(r'\{[^}]+\}', fill_point, comment)
        # If nothing replaced, just append the fill_point at the end
        if comment == sample_comment:
            comment = f"{sample_comment} ({fill_point})"
        return self.humanize_comment(comment)
    
    def extract_properties_from_comments(self, comments: list) -> dict:
        """Extract theme, sentiment, style, and average length from saved comments."""
        if not comments:
            return {}
        texts = [c['comment'] if isinstance(c, dict) and 'comment' in c else str(c) for c in comments]
        avg_length = sum(len(t.split()) for t in texts) // len(texts) if texts else None
        # For theme and sentiment, use majority or first detected
        themes = [self.analyze_post_theme(t) for t in texts]
        sentiments = [self.get_post_sentiment(t) for t in texts]
        from collections import Counter
        theme = Counter(themes).most_common(1)[0][0] if themes else None
        sentiment = Counter(sentiments).most_common(1)[0][0] if sentiments else None
        # Style: crude detection (e.g., emoji, exclamation, question, etc.)
        style = {
            'has_emoji': any(any(char in t for char in '😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚🙂🤗🤩🤔🤨😐😑😶🙄😏😣😥😮🤐😯😪😫😴😌😛😜😝🤤😒😓😔😕🙃🤑😲☹️🙁😖😞😟😤😢😭😦😧😨😩🤯😬😰😱🥵🥶😳🤪😵😡😠🤬😷🤒🤕🤢🤮🤧😇🥳🥺🤠🤡🤥🤫🤭🧐🤓😈👿👹👺💀👻👽👾🤖😺😸😹😻😼😽🙀😿😾') for t in texts),
            'has_exclamation': any('!' in t for t in texts),
            'has_question': any('?' in t for t in texts),
            'avg_length': avg_length
        }
        return {'theme': theme, 'sentiment': sentiment, 'style': style, 'avg_length': avg_length}

    def generate_comment(self, post_content: str, post_id: str, user_id: str = None, saved_comment_props: dict = None) -> Dict:
        """Generate human-style comment, prioritizing saved comment properties if provided."""
        try:
            # Use saved comment properties if available
            if saved_comment_props:
                theme = saved_comment_props.get('theme')
                sentiment = saved_comment_props.get('sentiment')
                avg_length = saved_comment_props.get('avg_length')
            else:
                theme = self.analyze_post_theme(post_content)
                sentiment = self.get_post_sentiment(post_content)
                avg_length = None
            post_keywords = self.extract_post_keywords(post_content)
            specific_points = self.extract_specific_points(post_content)
            # Try to select a human pattern
            try:
                pattern_type, selected_pattern = self.select_human_pattern(theme, sentiment, post_id, bool(specific_points))
            except Exception:
                pattern_type, selected_pattern = None, None
            comment = None
            if selected_pattern:
                if '{' in selected_pattern:
                    fill_content = self.extract_fillable_content(post_content, theme)
                    comment = selected_pattern
                    for placeholder, content in fill_content.items():
                        comment = comment.replace(f'{{{placeholder}}}', content)
                else:
                    comment = selected_pattern
                comment_words = set(re.findall(r'\b\w+\b', comment.lower()))
                overlap = comment_words.intersection(post_keywords)
                if len(overlap) > 2:
                    simple_patterns = self.human_patterns['agreement_short']
                    comment = random.choice([p for p in simple_patterns if p not in self.used_patterns[post_id]])
                comment = self.humanize_comment(comment)
                # Filter out banned words from the generated comment
                for banned in self.ai_banned_words:
                    if banned.lower() in comment.lower():
                        simple_patterns = [p for p in self.human_patterns['agreement_short'] if p not in self.used_patterns[post_id]]
                        if simple_patterns:
                            comment = random.choice(simple_patterns)
                            break
                        else:
                            comment = re.sub(re.escape(banned), '', comment, flags=re.IGNORECASE)
            # Fallback: If no pattern or comment, use ChromaDB similarity search
            if not comment or not comment.strip():
                try:
                    results = vectordb.similarity_search(post_content, k=5)
                    clean_comment = None
                    for r in results:
                        c = r.page_content
                        # Filter out AI-banned words
                        if not any(banned.lower() in c.lower() for banned in self.ai_banned_words):
                            # Instead of using c as-is, extract and fill pattern
                            clean_comment = self.extract_and_fill_pattern_from_sample(c, post_content)
                            break
                    if clean_comment:
                        comment = clean_comment
                        pattern_type = 'chromadb_fallback_pattern'
                    else:
                        comment = 'Thanks for sharing your thoughts.'
                        pattern_type = 'simple_fallback'
                except Exception:
                    comment = 'Thanks for sharing your thoughts.'
                    pattern_type = 'simple_fallback'
            quality_score = self.calculate_quality_score(comment, post_content, theme)
            # Truncate or pad to match avg_length if provided
            if avg_length and comment:
                words = comment.split()
                if len(words) > avg_length:
                    comment = ' '.join(words[:avg_length])
                elif len(words) < avg_length:
                    comment = comment + ' ...'  # crude padding
            return {
                'success': True,
                'comment': comment,
                'pattern_type': pattern_type,
                'theme': theme,
                'sentiment': sentiment,
                'quality_score': quality_score,
                'post_id': post_id,
                'style': saved_comment_props.get('style') if saved_comment_props else None,
                'avg_length': avg_length
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'post_id': post_id
            }
    
    def calculate_quality_score(self, comment: str, post_content: str, theme: str) -> float:
        """Calculate comment quality score"""
        score = 1.0
        
        word_count = len(comment.split())
        if 3 <= word_count <= 15:
            score += 0.2
        elif word_count > 25:
            score -= 0.3
        
        comment_lower = comment.lower()
        for ai_word in self.ai_banned_words:
            if ai_word in comment_lower:
                score -= 0.4
        
        natural_starters = ['so true', 'exactly', 'love this', 'great point', 'makes sense']
        if any(starter in comment_lower for starter in natural_starters):
            score += 0.2
        
        post_words = set(re.findall(r'\b\w+\b', post_content.lower()))
        comment_words = set(re.findall(r'\b\w+\b', comment_lower))
        overlap_ratio = len(post_words.intersection(comment_words)) / len(comment_words) if comment_words else 0
        
        if overlap_ratio > 0.3:
            score -= 0.5
        
        return max(0.1, min(1.0, score)) 
