import requests
import json
from typing import List, Dict, Optional
import langdetect
import iso639
from datetime import datetime

class LanguageHandler:
    """Verwaltet die Sprachverarbeitung und -erkennung"""
    
    def __init__(self):
        self.supported_languages = {
            'de': {'name': 'Deutsch', 'formatting': {'date': 'DD.MM.YYYY', 'quotes': '„"'}},
            'en': {'name': 'English', 'formatting': {'date': 'YYYY-MM-DD', 'quotes': '""'}},
            'fr': {'name': 'Français', 'formatting': {'date': 'DD/MM/YYYY', 'quotes': '« »'}},
            'es': {'name': 'Español', 'formatting': {'date': 'DD/MM/YYYY', 'quotes': '«»'}},
            'it': {'name': 'Italiano', 'formatting': {'date': 'DD/MM/YYYY', 'quotes': '«»'}}
        }
    
    def detect_language(self, text: str) -> str:
        """Erkennt die Sprache des Textes"""
        try:
            lang_code = langdetect.detect(text)
            return lang_code if lang_code in self.supported_languages else 'en'
        except:
            return 'en'
    
    def get_language_name(self, lang_code: str) -> str:
        """Gibt den vollständigen Sprachnamen zurück"""
        try:
            return iso639.languages.get(alpha2=lang_code).name
        except:
            return self.supported_languages.get(lang_code, {}).get('name', 'English')
    
    def get_formatting_rules(self, lang_code: str) -> Dict:
        """Gibt sprachspezifische Formatierungsregeln zurück"""
        return self.supported_languages.get(lang_code, {}).get('formatting', {})
    
    def format_text(self, text: str, lang_code: str) -> str:
        """Formatiert Text nach sprachspezifischen Regeln"""
        rules = self.get_formatting_rules(lang_code)
        quotes = rules.get('quotes', '""')
        
        # Anführungszeichen anpassen
        if '"' in text:
            text = text.replace('"', quotes[0], 1)
            text = text.replace('"', quotes[1], 1)
            
        return text

class AdaptiveLanguageHandler(LanguageHandler):
    """Erweiterte Sprachverarbeitung mit Lernfähigkeit und kultureller Intelligenz"""
    
    def __init__(self):
        super().__init__()
        self.cultural_contexts = {
            'de': {
                'formal_address': True,
                'idioms': {
                    'time_is_money': 'Zeit ist Geld',
                    'better_safe_than_sorry': 'Vorsicht ist besser als Nachsicht'
                },
                'cultural_norms': {
                    'punctuality': 'sehr wichtig',
                    'directness': 'bevorzugt',
                    'formality': 'hoch'
                }
            },
            'en': {
                'formal_address': False,
                'idioms': {
                    'time_is_money': 'time is money',
                    'better_safe_than_sorry': 'better safe than sorry'
                },
                'cultural_norms': {
                    'punctuality': 'important',
                    'directness': 'moderate',
                    'formality': 'context-dependent'
                }
            }
        }
        self.language_patterns = {}
        self.feedback_history = []
        
    def learn_from_feedback(self, original_text: str, improved_text: str, feedback_score: int, language: str):
        """Lernt aus Nutzerfeedback"""
        self.feedback_history.append({
            'original': original_text,
            'improved': improved_text,
            'score': feedback_score,
            'language': language,
            'timestamp': datetime.now()
        })
        
        # Muster aus erfolgreichen Verbesserungen extrahieren
        if feedback_score > 7:
            patterns = self._extract_patterns(original_text, improved_text)
            if language not in self.language_patterns:
                self.language_patterns[language] = []
            self.language_patterns[language].extend(patterns)
    
    def _extract_patterns(self, original: str, improved: str) -> List[Dict]:
        """Extrahiert Verbesserungsmuster aus Text-Paaren"""
        patterns = []
        # Einfache Wort-für-Wort Ersetzungen
        orig_words = original.split()
        impr_words = improved.split()
        
        for i in range(len(orig_words)):
            if i < len(impr_words) and orig_words[i] != impr_words[i]:
                patterns.append({
                    'type': 'word_replacement',
                    'original': orig_words[i],
                    'improved': impr_words[i],
                    'context': ' '.join(orig_words[max(0, i-2):min(len(orig_words), i+3)])
                })
        
        return patterns
    
    def get_cultural_context(self, lang_code: str) -> Dict:
        """Liefert kulturspezifische Informationen"""
        return self.cultural_contexts.get(lang_code, {})
    
    def apply_learned_patterns(self, text: str, language: str) -> str:
        """Wendet gelernte Verbesserungsmuster an"""
        if language not in self.language_patterns:
            return text
            
        improved_text = text
        for pattern in self.language_patterns[language]:
            if pattern['type'] == 'word_replacement':
                improved_text = improved_text.replace(pattern['original'], pattern['improved'])
                
        return improved_text
    
    def get_improvement_suggestions(self, language: str) -> List[Dict]:
        """Generiert Verbesserungsvorschläge basierend auf der Feedback-Historie"""
        if not self.feedback_history:
            return []
            
        recent_feedback = sorted(
            [f for f in self.feedback_history if f['language'] == language],
            key=lambda x: x['score'],
            reverse=True
        )[:5]
        
        return [{
            'original': f['original'],
            'improved': f['improved'],
            'score': f['score']
        } for f in recent_feedback]

class PromptOptimizer:
    def __init__(self, base_url="http://localhost:1234"):
        self.base_url = base_url
        self.completion_url = f"{base_url}/v1/chat/completions"
        self.language_handler = AdaptiveLanguageHandler()  # Verwende die erweiterte Handler-Klasse
        
    def optimize_prompt(self, original_prompt: str, target_language: Optional[str] = None) -> str:
        """Optimiert einen Prompt mit erweiterter Sprachunterstützung und KI-Funktionen"""
        # Sprache erkennen oder Zielsprache verwenden
        source_language = self.language_handler.detect_language(original_prompt)
        target_language = target_language or source_language
        
        # Kulturellen Kontext abrufen
        cultural_context = self.language_handler.get_cultural_context(target_language)
        
        # Gelernte Muster anwenden
        pre_processed_prompt = self.language_handler.apply_learned_patterns(original_prompt, target_language)
        
        # Systemnachricht mit erweiterten Einstellungen vorbereiten
        system_message = '''You are a multilingual AI assistant capable of understanding and communicating in various languages.

Source language: {source_lang}
Target language: {target_lang}

<language>
{target_lang}
</language>

<formatting_rules>
{formatting_rules}
</formatting_rules>

<cultural_context>
{cultural_context}
</cultural_context>

<user_input>
{{user_prompt}}
</user_input>

Instructions:
1. Analyze the input in the source language
2. Consider cultural context and norms
3. Apply language-specific patterns and improvements
4. Maintain cultural appropriateness
5. Return optimized prompt in target language

Remember to:
- Use appropriate formality level ({formality})
- Apply cultural-specific idioms when appropriate
- Maintain original intent while being culturally sensitive
- Use language-specific structures and expressions
- Consider formal/informal address ({formal_address})'''

        # Formatierungsregeln und Kontext abrufen
        formatting_rules = self.language_handler.get_formatting_rules(target_language)
        
        # Prompt vorbereiten
        formatted_prompt = system_message.format(
            source_lang=self.language_handler.get_language_name(source_language),
            target_lang=self.language_handler.get_language_name(target_language),
            formatting_rules=json.dumps(formatting_rules, indent=2),
            cultural_context=json.dumps(cultural_context, indent=2),
            formality=cultural_context.get('cultural_norms', {}).get('formality', 'standard'),
            formal_address=cultural_context.get('formal_address', False)
        ).replace("{{user_prompt}}", pre_processed_prompt)

        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": pre_processed_prompt}
        ]
        
        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                improved_prompt = response.json()["choices"][0]["message"]["content"]
                # Führe eine Verifikation durch
                return self.verify_prompt(improved_prompt, original_prompt)
            else:
                return original_prompt
        except Exception as e:
            print(f"Fehler bei der Prompt-Optimierung: {str(e)}")
            return original_prompt

    def verify_prompt(self, improved_prompt: str, original_prompt: str, target_language: Optional[str] = None) -> str:
        """Verifiziert den optimierten Prompt mit Sprachunterstützung"""
        # Sprache erkennen oder Zielsprache verwenden
        target_language = target_language or self.language_handler.detect_language(improved_prompt)
        
        verify_message = '''You are a multilingual AI assistant specializing in prompt verification.

Target language: {target_lang}
Formatting rules: {formatting_rules}

<language>
{target_lang}
</language>

Instructions:
1. Verify the improved prompt maintains the original intent
2. Check for language-specific formatting and cultural appropriateness
3. Ensure proper use of quotation marks and other language-specific elements
4. Return the verified prompt using the correct quotation marks for the target language
5. Do not add any explanations or metadata

Example format:
{quote_start}Verified prompt text goes here{quote_end}

Verification criteria:
- Language-specific correctness
- Cultural appropriateness
- Proper formatting
- Clear objectives

IMPORTANT: Return only the verified text using the language-specific quotation marks.'''

        # Formatierungsregeln und Anführungszeichen abrufen
        formatting_rules = self.language_handler.get_formatting_rules(target_language)
        quotes = formatting_rules.get('quotes', '""')
        
        # Nachricht formatieren
        formatted_message = verify_message.format(
            target_lang=self.language_handler.get_language_name(target_language),
            formatting_rules=json.dumps(formatting_rules, indent=2),
            quote_start=quotes[0],
            quote_end=quotes[1]
        )

        messages = [
            {"role": "system", "content": formatted_message},
            {"role": "user", "content": f"Original:\n{original_prompt}\n\nImproved:\n{improved_prompt}"}
        ]

        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 2000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                # Text zwischen den sprachspezifischen Anführungszeichen extrahieren
                quote_start, quote_end = formatting_rules.get('quotes', '""')
                if quote_start in result and quote_end in result:
                    start = result.find(quote_start) + len(quote_start)
                    end = result.rfind(quote_end)
                    if start > 0 and end > start:
                        return result[start:end]
                return self.language_handler.format_text(improved_prompt, target_language)
            else:
                return self.language_handler.format_text(improved_prompt, target_language)
        except Exception:
            return self.language_handler.format_text(improved_prompt, target_language)
    
    def analyze_context(self, message_history):
        """Analysiert den Kontext der Konversation und gibt Verbesserungsvorschläge"""
        system_message = """Analysiere den Konversationsverlauf und identifiziere wichtige Themen, 
        fehlende Informationen und mögliche Folgefragen. Gib Vorschläge zur Verbesserung der Konversationsqualität."""
        
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in message_history[-5:]])
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Analysiere diesen Konversationskontext:\n\n{context}"}
        ]
        
        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return None
        except Exception:
            return None
    
    def suggest_followup_questions(self, last_response):
        """Generiert Vorschläge für sinnvolle Folgefragen"""
        system_message = """Basierend auf der letzten Antwort, generiere 3-5 relevante Folgefragen, 
        die das Thema vertiefen oder wichtige verwandte Aspekte ansprechen könnten."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Generiere Folgefragen zu dieser Antwort: {last_response}"}
        ]
        
        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                suggestions = response.json()["choices"][0]["message"]["content"]
                return suggestions.split("\n")
            else:
                return []
        except Exception:
            return []

    def summarize_conversation(self, message_history):
        """Erstellt eine Zusammenfassung der bisherigen Konversation"""
        system_message = """Erstelle eine prägnante Zusammenfassung der wichtigsten Punkte 
        dieser Konversation. Hebe Kernthemen, wichtige Erkenntnisse und offene Fragen hervor."""
        
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in message_history])
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Fasse diese Konversation zusammen:\n\n{context}"}
        ]
        
        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return None
        except Exception:
            return None
    
    def provide_feedback(self, original_prompt: str, improved_prompt: str, feedback_score: int, language: str = None) -> Dict:
        """Verarbeitet Nutzerfeedback und aktualisiert die Lernmuster"""
        if not language:
            language = self.language_handler.detect_language(original_prompt)
            
        # Feedback an den Language Handler übergeben
        self.language_handler.learn_from_feedback(
            original_prompt,
            improved_prompt,
            feedback_score,
            language
        )
        
        # Verbesserungsvorschläge abrufen
        suggestions = self.language_handler.get_improvement_suggestions(language)
        
        # Aktuelle Muster für die Sprache abrufen
        patterns = self.language_handler.language_patterns.get(language, [])
        
        return {
            'language': language,
            'feedback_processed': True,
            'improvement_suggestions': suggestions,
            'learned_patterns': len(patterns),
            'cultural_context': self.language_handler.get_cultural_context(language)
        }

    def generate_conversation_flow(self, messages: List[Dict]) -> Dict:
        """Generates a conversation flow visualization"""
        system_message = """Analyze this conversation and generate a flow diagram in Mermaid format.
        Include participants, key topics, and relationships between messages."""
        
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Generate flow for:\n\n{context}"}
        ]
        
        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    'type': 'mermaid',
                    'content': response.json()["choices"][0]["message"]["content"]
                }
            return {'error': 'Failed to generate flow'}
        except Exception:
            return {'error': 'Failed to generate flow'}

    def generate_knowledge_graph(self, messages: List[Dict]) -> Dict:
        """Generates a knowledge graph from conversation"""
        system_message = """Analyze this conversation and generate a knowledge graph in Graphviz DOT format.
        Include entities, relationships, and key concepts."""
        
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Generate graph for:\n\n{context}"}
        ]
        
        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    'type': 'graphviz',
                    'content': response.json()["choices"][0]["message"]["content"]
                }
            return {'error': 'Failed to generate graph'}
        except Exception:
            return {'error': 'Failed to generate graph'}

    def generate_topic_evolution(self, messages: List[Dict]) -> Dict:
        """Generates topic evolution timeline"""
        system_message = """Analyze this conversation and generate a timeline of topics in JSON format.
        Include topic names, start/end points, and importance scores."""
        
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Generate timeline for:\n\n{context}"}
        ]
        
        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    'type': 'timeline',
                    'content': response.json()["choices"][0]["message"]["content"]
                }
            return {'error': 'Failed to generate timeline'}
        except Exception:
            return {'error': 'Failed to generate timeline'}

    def generate_sentiment_timeline(self, messages: List[Dict]) -> Dict:
        """Generates sentiment analysis timeline"""
        system_message = """Analyze this conversation and generate a sentiment timeline in JSON format.
        Include sentiment scores for each message and overall trend."""
        
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Generate sentiment analysis for:\n\n{context}"}
        ]
        
        try:
            response = requests.post(
                self.completion_url,
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    'type': 'sentiment',
                    'content': response.json()["choices"][0]["message"]["content"]
                }
            return {'error': 'Failed to generate sentiment analysis'}
        except Exception:
            return {'error': 'Failed to generate sentiment analysis'}
