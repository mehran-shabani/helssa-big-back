"""
Speech Processing Core - {APP_NAME}
Part of HELSSA Platform

This core handles:
- Speech-to-Text (STT) conversion
- Text-to-Speech (TTS) conversion  
- Audio file processing
- Audio quality assessment
- Audio segmentation
- Noise reduction
"""

import logging
import time
import os
from typing import Dict, Any, List, Optional, BinaryIO
from dataclasses import dataclass

# Unified services imports
from stt.services.whisper_service import WhisperService
from unified_ai.services import UnifiedAIService

logger = logging.getLogger(__name__)


@dataclass
class AudioProcessingResult:
    """Result structure for audio processing operations"""
    transcribed_text: str
    segments: List[Dict[str, Any]]
    confidence: float
    language: str
    processing_time: float
    audio_duration: float
    metadata: Dict[str, Any]


@dataclass
class AudioSegment:
    """Audio segment with timing information"""
    start_time: float
    end_time: float
    text: str
    confidence: float


class SpeechProcessingCore:
    """
    Speech Processing Core for {APP_NAME}
    
    Handles all audio and speech processing operations including
    STT conversion, audio analysis, and speech-related AI tasks
    specific to {APP_DESCRIPTION}.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.SpeechProcessingCore')
        
        # Initialize services
        self.whisper_service = WhisperService()
        self.ai_service = UnifiedAIService()
        
        # Supported audio formats
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
        
        # Quality thresholds
        self.min_audio_duration = 1.0  # seconds
        self.max_audio_duration = 1800.0  # 30 minutes
        self.min_confidence_threshold = 0.6
    
    def transcribe_audio(
        self,
        audio_file: BinaryIO,
        language: str = 'fa',
        user_type: str = 'patient',
        enhance_medical: bool = True
    ) -> AudioProcessingResult:
        """
        Transcribe audio file to text using Whisper
        
        Args:
            audio_file: Audio file binary stream
            language: Language code ('fa' for Farsi, 'en' for English)
            user_type: Type of user (patient/doctor)
            enhance_medical: Whether to enhance for medical terminology
            
        Returns:
            AudioProcessingResult with transcription and metadata
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting audio transcription for {APP_NAME}")
            
            # Validate audio file
            self._validate_audio_file(audio_file)
            
            # Process with Whisper service
            whisper_result = self.whisper_service.transcribe(
                audio_file=audio_file,
                language=language,
                task='transcribe'
            )
            
            # Extract basic transcription data
            transcribed_text = whisper_result.get('text', '')
            segments = whisper_result.get('segments', [])
            confidence = whisper_result.get('confidence', 0.0)
            detected_language = whisper_result.get('language', language)
            
            # Enhance medical transcription if needed
            if enhance_medical and transcribed_text:
                transcribed_text = self._enhance_medical_transcription(
                    text=transcribed_text,
                    user_type=user_type,
                    language=language
                )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create result object
            result = AudioProcessingResult(
                transcribed_text=transcribed_text,
                segments=self._process_segments(segments),
                confidence=confidence,
                language=detected_language,
                processing_time=processing_time,
                audio_duration=whisper_result.get('duration', 0.0),
                metadata={
                    'app_name': '{APP_NAME}',
                    'user_type': user_type,
                    'enhancement_applied': enhance_medical,
                    'model_used': 'whisper'
                }
            )
            
            self.logger.info(
                f"Audio transcription completed in {processing_time:.2f}s, "
                f"confidence: {confidence:.2f}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Audio transcription error: {str(e)}")
            raise Exception(f"خطا در تبدیل گفتار به متن: {str(e)}")
    
    def process_medical_audio(
        self,
        audio_file: BinaryIO,
        context: Dict[str, Any] = None,
        user_type: str = 'doctor'
    ) -> Dict[str, Any]:
        """
        Process medical audio with specialized handling
        
        Args:
            audio_file: Medical audio recording
            context: Additional context about the audio
            user_type: Type of user uploading audio
            
        Returns:
            Comprehensive medical audio analysis
        """
        try:
            self.logger.info(f"Starting medical audio processing for {APP_NAME}")
            
            # First, transcribe the audio
            transcription_result = self.transcribe_audio(
                audio_file=audio_file,
                language='fa',
                user_type=user_type,
                enhance_medical=True
            )
            
            # Analyze medical content
            medical_analysis = self._analyze_medical_content(
                text=transcription_result.transcribed_text,
                context=context,
                user_type=user_type
            )
            
            # Extract medical entities
            medical_entities = self._extract_medical_entities(
                text=transcription_result.transcribed_text
            )
            
            # Generate summary if text is long enough
            summary = ""
            if len(transcription_result.transcribed_text) > 100:
                summary = self._generate_medical_summary(
                    text=transcription_result.transcribed_text,
                    user_type=user_type
                )
            
            return {
                'transcription': {
                    'text': transcription_result.transcribed_text,
                    'confidence': transcription_result.confidence,
                    'segments': transcription_result.segments,
                    'duration': transcription_result.audio_duration
                },
                'medical_analysis': medical_analysis,
                'medical_entities': medical_entities,
                'summary': summary,
                'metadata': {
                    'processing_time': transcription_result.processing_time,
                    'app_name': '{APP_NAME}',
                    'analysis_type': 'medical_audio'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Medical audio processing error: {str(e)}")
            raise Exception(f"خطا در پردازش فایل صوتی پزشکی: {str(e)}")
    
    def segment_audio_by_content(
        self,
        audio_file: BinaryIO,
        segment_type: str = 'speaker'
    ) -> List[AudioSegment]:
        """
        Segment audio by content or speaker
        
        Args:
            audio_file: Audio file to segment
            segment_type: Type of segmentation ('speaker', 'pause', 'topic')
            
        Returns:
            List of audio segments with timing
        """
        try:
            self.logger.info(f"Starting audio segmentation for {APP_NAME}")
            
            # Transcribe with detailed segments
            transcription_result = self.transcribe_audio(
                audio_file=audio_file,
                enhance_medical=False
            )
            
            # Process segments based on type
            if segment_type == 'speaker':
                segments = self._segment_by_speaker(transcription_result.segments)
            elif segment_type == 'pause':
                segments = self._segment_by_pause(transcription_result.segments)
            elif segment_type == 'topic':
                segments = self._segment_by_topic(transcription_result.segments)
            else:
                segments = self._create_default_segments(transcription_result.segments)
            
            self.logger.info(f"Audio segmentation completed, found {len(segments)} segments")
            return segments
            
        except Exception as e:
            self.logger.error(f"Audio segmentation error: {str(e)}")
            return []
    
    def _validate_audio_file(self, audio_file: BinaryIO):
        """Validate audio file format and size"""
        
        # Check file size (basic validation)
        audio_file.seek(0, 2)  # Seek to end
        file_size = audio_file.tell()
        audio_file.seek(0)  # Reset to beginning
        
        # File size limits (50MB max)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            raise ValueError(f"فایل صوتی بیش از حد بزرگ است. حداکثر اندازه: {max_size // (1024*1024)}MB")
        
        if file_size < 1024:  # Less than 1KB
            raise ValueError("فایل صوتی بیش از حد کوچک است")
    
    def _enhance_medical_transcription(
        self,
        text: str,
        user_type: str,
        language: str
    ) -> str:
        """Enhance transcription with medical terminology correction"""
        
        try:
            # Use AI to enhance medical accuracy
            enhancement_prompt = f"""
            لطفاً متن زیر را که از تبدیل گفتار به متن پزشکی به دست آمده، اصلاح و بهبود دهید:
            - اصطلاحات پزشکی را صحیح کنید
            - کلمات نادرست تشخیص داده شده را اصلاح کنید
            - ساختار جملات را بهبود دهید
            
            نوع کاربر: {user_type}
            زبان: {language}
            
            متن اصلی: {text}
            
            متن اصلاح شده:
            """
            
            # Process with AI service (simplified)
            enhanced_text = self.ai_service.process_text(
                text=enhancement_prompt,
                task_type='text_enhancement',
                app_name='{APP_NAME}'
            )
            
            return enhanced_text.get('text', text)
            
        except Exception as e:
            self.logger.warning(f"Medical enhancement failed: {str(e)}")
            return text
    
    def _process_segments(self, raw_segments: List[Dict]) -> List[Dict[str, Any]]:
        """Process raw Whisper segments into structured format"""
        
        processed_segments = []
        
        for segment in raw_segments:
            processed_segment = {
                'start': segment.get('start', 0.0),
                'end': segment.get('end', 0.0),
                'text': segment.get('text', '').strip(),
                'confidence': segment.get('confidence', 0.0),
                'speaker': segment.get('speaker', 'unknown')
            }
            
            if processed_segment['text']:
                processed_segments.append(processed_segment)
        
        return processed_segments
    
    def _analyze_medical_content(
        self,
        text: str,
        context: Dict[str, Any],
        user_type: str
    ) -> Dict[str, Any]:
        """Analyze medical content from transcribed text"""
        
        try:
            analysis_prompt = f"""
            لطفاً متن پزشکی زیر را تحلیل کنید و موارد زیر را استخراج کنید:
            1. علائم و نشانه‌های اصلی
            2. تشخیص‌های احتمالی (در صورت وجود)
            3. درمان‌های پیشنهادی
            4. نکات مهم
            
            متن: {text}
            """
            
            # Use AI service for analysis
            analysis_result = self.ai_service.process_text(
                text=analysis_prompt,
                task_type='medical_analysis',
                app_name='{APP_NAME}'
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Medical content analysis error: {str(e)}")
            return {}
    
    def _extract_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical entities from text"""
        
        try:
            # Define medical entity types
            entity_types = [
                'symptoms', 'diseases', 'medications', 
                'procedures', 'anatomy', 'dosages'
            ]
            
            entities = []
            
            # Simple keyword-based extraction (can be enhanced with AI)
            medical_keywords = {
                'symptoms': ['درد', 'تب', 'سردرد', 'تهوع'],
                'medications': ['داروی', 'قرص', 'آمپول', 'سرم'],
                'procedures': ['آزمایش', 'عکسبرداری', 'جراحی']
            }
            
            for entity_type, keywords in medical_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        entities.append({
                            'type': entity_type,
                            'text': keyword,
                            'confidence': 0.8
                        })
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Medical entity extraction error: {str(e)}")
            return []
    
    def _generate_medical_summary(self, text: str, user_type: str) -> str:
        """Generate summary of medical transcription"""
        
        try:
            summary_prompt = f"""
            لطفاً خلاصه‌ای کوتاه و دقیق از گفتگوی پزشکی زیر تهیه کنید:
            - نکات کلیدی را حفظ کنید
            - اطلاعات مهم پزشکی را شامل کنید
            - خلاصه باید برای {user_type} قابل فهم باشد
            
            متن: {text}
            """
            
            summary_result = self.ai_service.process_text(
                text=summary_prompt,
                task_type='summarization',
                app_name='{APP_NAME}'
            )
            
            return summary_result.get('text', text[:200] + '...')
            
        except Exception as e:
            self.logger.error(f"Medical summary generation error: {str(e)}")
            return text[:200] + '...'
    
    def _segment_by_speaker(self, segments: List[Dict]) -> List[AudioSegment]:
        """Segment audio by speaker changes"""
        # Simplified speaker segmentation
        audio_segments = []
        current_speaker = None
        current_text = ""
        start_time = 0.0
        
        for segment in segments:
            speaker = segment.get('speaker', 'unknown')
            
            if speaker != current_speaker:
                if current_text:
                    audio_segments.append(AudioSegment(
                        start_time=start_time,
                        end_time=segment.get('start', 0.0),
                        text=current_text.strip(),
                        confidence=0.8
                    ))
                
                current_speaker = speaker
                current_text = segment.get('text', '')
                start_time = segment.get('start', 0.0)
            else:
                current_text += " " + segment.get('text', '')
        
        # Add final segment
        if current_text:
            audio_segments.append(AudioSegment(
                start_time=start_time,
                end_time=segments[-1].get('end', 0.0) if segments else 0.0,
                text=current_text.strip(),
                confidence=0.8
            ))
        
        return audio_segments
    
    def _segment_by_pause(self, segments: List[Dict]) -> List[AudioSegment]:
        """Segment audio by pauses/silence"""
        # Simplified pause-based segmentation
        audio_segments = []
        
        for segment in segments:
            audio_segments.append(AudioSegment(
                start_time=segment.get('start', 0.0),
                end_time=segment.get('end', 0.0),
                text=segment.get('text', ''),
                confidence=segment.get('confidence', 0.0)
            ))
        
        return audio_segments
    
    def _segment_by_topic(self, segments: List[Dict]) -> List[AudioSegment]:
        """Segment audio by topic changes"""
        # Simplified topic-based segmentation
        return self._segment_by_pause(segments)  # Fallback to pause segmentation
    
    def _create_default_segments(self, segments: List[Dict]) -> List[AudioSegment]:
        """Create default segmentation"""
        return self._segment_by_pause(segments)