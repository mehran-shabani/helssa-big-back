"""
Text Processing Core - {APP_NAME}
Part of HELSSA Platform

This core handles:
- Natural Language Processing (NLP)
- AI text generation and analysis
- Medical text processing
- Text summarization
- Entity extraction
- Sentiment analysis
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Unified AI imports
from unified_ai.services import UnifiedAIService
from unified_ai.models import AIRequest, AIResponse

logger = logging.getLogger(__name__)


@dataclass
class TextProcessingResult:
    """Result structure for text processing operations"""
    original_text: str
    processed_text: str
    entities: List[Dict[str, Any]]
    summary: str
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]


class TextProcessingCore:
    """
    Text Processing Core for {APP_NAME}
    
    Handles all text-related AI operations including medical text analysis,
    content generation, and NLP tasks specific to {APP_DESCRIPTION}.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.TextProcessingCore')
        self.ai_service = UnifiedAIService()
        
        # {APP_NAME} specific prompts and configurations
        self.prompts = {
            'medical_analysis': self._get_medical_analysis_prompt(),
            'content_generation': self._get_content_generation_prompt(),
            'summary': self._get_summary_prompt(),
            'entity_extraction': self._get_entity_extraction_prompt()
        }
    
    def process_medical_text(
        self, 
        text: str, 
        context: Dict[str, Any] = None,
        user_type: str = 'patient'
    ) -> TextProcessingResult:
        """
        Process medical text with AI analysis
        
        Args:
            text: Input text to process
            context: Additional context information
            user_type: Type of user (patient/doctor)
            
        Returns:
            TextProcessingResult with processed information
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting medical text processing for {APP_NAME}")
            
            # Prepare AI request
            ai_request = self._prepare_ai_request(
                text=text,
                task_type='medical_analysis',
                context=context,
                user_type=user_type
            )
            
            # Process with unified AI service
            ai_response = self.ai_service.process_request(ai_request)
            
            # Extract and structure results
            result = self._structure_ai_response(
                original_text=text,
                ai_response=ai_response,
                processing_time=time.time() - start_time
            )
            
            self.logger.info(f"Medical text processing completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Medical text processing error: {str(e)}")
            raise Exception(f"خطا در پردازش متن پزشکی: {str(e)}")
    
    def generate_content(
        self,
        prompt: str,
        content_type: str = '{CONTENT_TYPE}',
        user_type: str = 'patient',
        max_length: int = 1000
    ) -> TextProcessingResult:
        """
        Generate content using AI
        
        Args:
            prompt: Generation prompt
            content_type: Type of content to generate
            user_type: Type of user requesting generation
            max_length: Maximum length of generated content
            
        Returns:
            TextProcessingResult with generated content
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting content generation for {APP_NAME}")
            
            # Prepare specialized prompt for {APP_NAME}
            specialized_prompt = self._prepare_generation_prompt(
                prompt=prompt,
                content_type=content_type,
                user_type=user_type
            )
            
            # AI request for content generation
            ai_request = self._prepare_ai_request(
                text=specialized_prompt,
                task_type='content_generation',
                context={'max_length': max_length, 'content_type': content_type}
            )
            
            # Generate content
            ai_response = self.ai_service.process_request(ai_request)
            
            # Structure result
            result = self._structure_ai_response(
                original_text=prompt,
                ai_response=ai_response,
                processing_time=time.time() - start_time
            )
            
            self.logger.info(f"Content generation completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Content generation error: {str(e)}")
            raise Exception(f"خطا در تولید محتوا: {str(e)}")
    
    def extract_entities(
        self,
        text: str,
        entity_types: List[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract named entities from text
        
        Args:
            text: Input text
            entity_types: Types of entities to extract
            
        Returns:
            Dictionary of extracted entities by type
        """
        try:
            self.logger.info(f"Starting entity extraction for {APP_NAME}")
            
            if entity_types is None:
                entity_types = ['{ENTITY_TYPE_1}', '{ENTITY_TYPE_2}', '{ENTITY_TYPE_3}']
            
            # Prepare entity extraction request
            ai_request = self._prepare_ai_request(
                text=text,
                task_type='entity_extraction',
                context={'entity_types': entity_types}
            )
            
            # Extract entities
            ai_response = self.ai_service.process_request(ai_request)
            
            # Parse entity response
            entities = self._parse_entities_response(ai_response)
            
            self.logger.info(f"Entity extraction completed, found {len(entities)} entity types")
            return entities
            
        except Exception as e:
            self.logger.error(f"Entity extraction error: {str(e)}")
            return {}
    
    def summarize_text(
        self,
        text: str,
        summary_type: str = 'medical',
        max_length: int = 200
    ) -> str:
        """
        Generate summary of text
        
        Args:
            text: Text to summarize
            summary_type: Type of summary (medical, general, etc.)
            max_length: Maximum length of summary
            
        Returns:
            Summary text
        """
        try:
            self.logger.info(f"Starting text summarization for {APP_NAME}")
            
            # Prepare summarization request
            ai_request = self._prepare_ai_request(
                text=text,
                task_type='summary',
                context={
                    'summary_type': summary_type,
                    'max_length': max_length
                }
            )
            
            # Generate summary
            ai_response = self.ai_service.process_request(ai_request)
            
            summary = ai_response.get('summary', text[:max_length])
            
            self.logger.info(f"Text summarization completed")
            return summary
            
        except Exception as e:
            self.logger.error(f"Text summarization error: {str(e)}")
            return text[:max_length] + "..."
    
    def _prepare_ai_request(
        self,
        text: str,
        task_type: str,
        context: Dict[str, Any] = None,
        user_type: str = 'patient'
    ) -> Dict[str, Any]:
        """Prepare AI service request"""
        
        prompt_template = self.prompts.get(task_type, "")
        
        return {
            'text': text,
            'prompt_template': prompt_template,
            'task_type': task_type,
            'app_name': '{APP_NAME}',
            'context': context or {},
            'user_type': user_type,
            'model_preferences': {
                'temperature': 0.7,
                'max_tokens': 2000,
                'top_p': 0.9
            }
        }
    
    def _structure_ai_response(
        self,
        original_text: str,
        ai_response: Dict[str, Any],
        processing_time: float
    ) -> TextProcessingResult:
        """Structure AI response into TextProcessingResult"""
        
        return TextProcessingResult(
            original_text=original_text,
            processed_text=ai_response.get('text', ''),
            entities=ai_response.get('entities', []),
            summary=ai_response.get('summary', ''),
            confidence=ai_response.get('confidence', 0.0),
            processing_time=processing_time,
            metadata=ai_response.get('metadata', {})
        )
    
    def _parse_entities_response(self, ai_response: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Parse entities from AI response"""
        
        entities_data = ai_response.get('entities', [])
        organized_entities = {}
        
        for entity in entities_data:
            entity_type = entity.get('type', 'unknown')
            if entity_type not in organized_entities:
                organized_entities[entity_type] = []
            organized_entities[entity_type].append(entity)
        
        return organized_entities
    
    def _prepare_generation_prompt(
        self,
        prompt: str,
        content_type: str,
        user_type: str
    ) -> str:
        """Prepare specialized prompt for content generation"""
        
        base_prompt = self.prompts['content_generation']
        
        specialized_prompt = f"""
        {base_prompt}
        
        نوع محتوا: {content_type}
        نوع کاربر: {user_type}
        درخواست: {prompt}
        
        لطفاً پاسخی مناسب و دقیق ارائه دهید.
        """
        
        return specialized_prompt
    
    # Prompt templates for {APP_NAME}
    def _get_medical_analysis_prompt(self) -> str:
        return """
        شما یک دستیار پزشکی هوشمند هستید که برای سیستم {APP_NAME} کار می‌کنید.
        لطفاً متن پزشکی ارائه شده را تحلیل کنید و اطلاعات مهم را استخراج کنید.
        
        نکات مهم:
        - تنها اطلاعات موثق و علمی ارائه دهید
        - از ارائه تشخیص قطعی خودداری کنید
        - همیشه تأکید کنید که باید با پزشک مشورت شود
        
        متن: {text}
        """
    
    def _get_content_generation_prompt(self) -> str:
        return """
        شما یک دستیار هوشمند برای سیستم {APP_NAME} هستید.
        لطفاً محتوای مناسب و مفیدی برای کاربر تولید کنید.
        
        ملاحظات:
        - محتوا باید دقیق و قابل اعتماد باشد
        - زبان ساده و قابل فهم استفاده کنید
        - اطلاعات پزشکی به صورت کلی و آموزشی ارائه دهید
        """
    
    def _get_summary_prompt(self) -> str:
        return """
        لطفاً خلاصه‌ای کوتاه و مفید از متن زیر تهیه کنید:
        - نکات کلیدی را حفظ کنید
        - اطلاعات مهم را حذف نکنید
        - خلاصه باید قابل فهم و سازمان‌یافته باشد
        
        متن: {text}
        """
    
    def _get_entity_extraction_prompt(self) -> str:
        return """
        لطفاً موجودیت‌های مهم را از متن استخراج کنید:
        - نام‌های افراد، مکان‌ها، تاریخ‌ها
        - اصطلاحات پزشکی
        - علائم و نشانه‌ها
        - داروها و درمان‌ها
        
        متن: {text}
        """