"""
Google Gemini AI integration service.
"""

import httpx
from typing import List, Dict, Any, Optional
import time

from app.config import get_settings
from app.database import Database
from app.utils.logger import get_logger, log_external_api_call
from app.utils.error_handler import ExternalAPIException
from app.models.conversation import MessageIntent

logger = get_logger(__name__)
settings = get_settings()


class GeminiService:
    """
    Service for Google Gemini AI integration.

    Handles:
    - AI response generation
    - Product context injection
    - Intent detection
    - Conversation history management
    """

    def __init__(self, db: Database):
        """
        Initialize Gemini service.

        Args:
            db: Database instance
        """
        self.db = db
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
        self.api_key = settings.gemini_api_key

    async def generate_response(
        self,
        user_id: str,
        customer_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI response to customer message.

        Args:
            user_id: Store owner UUID
            customer_message: Customer's message
            conversation_history: Previous messages in conversation

        Returns:
            Dict with AI response, intent, and referenced products

        Example:
            result = await gemini_service.generate_response(
                user_id="123",
                customer_message="Do you have wireless headphones?"
            )
        """
        start_time = time.time()

        try:
            # Get store context (products, settings)
            context = await self._build_context(user_id)

            # Build system prompt
            system_prompt = await self._build_system_prompt(user_id, context)

            # Build conversation prompt
            prompt = self._build_prompt(
                customer_message=customer_message,
                system_prompt=system_prompt,
                conversation_history=conversation_history,
            )

            # Call Gemini API
            response_data = await self._call_gemini_api(prompt)

            # Extract response text
            ai_response = self._extract_response_text(response_data)

            # Detect intent and extract product references
            intent = self._detect_intent(customer_message, ai_response)
            product_ids = self._extract_product_references(
                ai_response, context.get("products", [])
            )

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "AI response generated",
                extra={
                    "user_id": user_id,
                    "intent": intent,
                    "product_count": len(product_ids),
                    "response_time_ms": response_time_ms,
                },
            )

            return {
                "ai_response": ai_response,
                "intent_detected": intent,
                "products_referenced": product_ids,
                "response_time_ms": response_time_ms,
            }

        except Exception as e:
            logger.error(
                "AI response generation failed",
                extra={"user_id": user_id, "error": str(e)},
            )
            raise ExternalAPIException(
                "Failed to generate AI response",
                service="gemini",
                details={"error": str(e)},
            )

    async def _build_context(self, user_id: str) -> Dict[str, Any]:
        """
        Build context from user's store data.

        Args:
            user_id: Store owner UUID

        Returns:
            Dict with store context (products, settings)
        """
        # Get user settings
        user = await self.db.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Get products (limit to 100 for context size)
        products = await self.db.get_products(user_id, limit=100)

        return {
            "store_name": user.get("store_name", "our store"),
            "ai_tone": user.get("ai_tone", "friendly"),
            "products": products,
        }

    async def _build_system_prompt(self, user_id: str, context: Dict[str, Any]) -> str:
        """
        Build system prompt with store context.

        Args:
            user_id: Store owner UUID
            context: Store context dict

        Returns:
            System prompt string
        """
        store_name = context.get("store_name", "our store")
        ai_tone = context.get("ai_tone", "friendly")
        products = context.get("products", [])

        # Tone instructions
        tone_instructions = {
            "friendly": "Be warm, welcoming, and conversational. Use a friendly tone.",
            "professional": "Be polite, clear, and professional. Maintain a business-like tone.",
            "casual": "Be relaxed and casual. Use simple language and feel approachable.",
            "energetic": "Be enthusiastic and upbeat! Show excitement about products.",
        }

        tone_instruction = tone_instructions.get(ai_tone, tone_instructions["friendly"])

        # Build product catalog summary
        if products:
            product_list = "\n".join(
                [
                    f"- {p['name']} (${p['price']}) - {p.get('description', 'No description')[:100]}"
                    for p in products[:20]  # Limit to 20 for prompt size
                ]
            )
        else:
            product_list = "No products available yet."

        system_prompt = f"""You are an AI customer service assistant for {store_name}.

TONE: {tone_instruction}

CAPABILITIES:
- Answer product questions
- Help customers find products
- Provide order status information
- Handle general inquiries

PRODUCT CATALOG:
{product_list}

INSTRUCTIONS:
1. If asked about products, recommend relevant items from the catalog
2. If asked about orders, acknowledge and explain you'll look it up
3. Be helpful and answer questions based on available information
4. If you don't know something, say so politely
5. Keep responses concise (2-3 paragraphs max)
6. When mentioning a product, include the product name

IMPORTANT: When recommending products, use their exact names from the catalog above.
"""

        return system_prompt

    def _build_prompt(
        self,
        customer_message: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Build complete prompt with context and history.

        Args:
            customer_message: Customer's current message
            system_prompt: System instructions
            conversation_history: Previous messages

        Returns:
            Complete prompt string
        """
        prompt_parts = [system_prompt]

        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("\nCONVERSATION HISTORY:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                prompt_parts.append(f"Customer: {msg.get('customer_message', '')}")
                prompt_parts.append(f"Assistant: {msg.get('ai_response', '')}")

        # Add current message
        prompt_parts.append(f"\nCustomer: {customer_message}")
        prompt_parts.append("Assistant:")

        return "\n".join(prompt_parts)

    async def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """
        Call Gemini API with prompt.

        Args:
            prompt: Complete prompt string

        Returns:
            API response data

        Raises:
            ExternalAPIException: If API call fails
        """
        start_time = time.time()

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": settings.gemini_temperature,
                "maxOutputTokens": settings.gemini_max_tokens,
            },
        }

        headers = {"Content-Type": "application/json"}

        url = f"{self.api_url}?key={self.api_key}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)

                duration_ms = int((time.time() - start_time) * 1000)

                log_external_api_call(
                    service="gemini",
                    endpoint=self.api_url,
                    method="POST",
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Gemini API HTTP error",
                    extra={
                        "status_code": e.response.status_code,
                        "response": e.response.text,
                    },
                )
                raise ExternalAPIException(
                    "Gemini API returned an error",
                    service="gemini",
                    details={"status_code": e.response.status_code},
                )
            except httpx.TimeoutException:
                logger.error("Gemini API timeout")
                raise ExternalAPIException(
                    "Gemini API request timed out", service="gemini"
                )
            except Exception as e:
                logger.error("Gemini API error", extra={"error": str(e)})
                raise ExternalAPIException(
                    "Failed to call Gemini API",
                    service="gemini",
                    details={"error": str(e)},
                )

    def _extract_response_text(self, response_data: Dict[str, Any]) -> str:
        """
        Extract text from Gemini API response.

        Args:
            response_data: API response data

        Returns:
            Response text string
        """
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates in response")

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            if not parts:
                raise ValueError("No parts in response")

            text = parts[0].get("text", "")
            return text.strip()

        except Exception as e:
            logger.error(
                "Failed to extract response text",
                extra={"error": str(e), "response": response_data},
            )
            return "I apologize, but I couldn't generate a proper response. Please try again."

    def _detect_intent(self, customer_message: str, ai_response: str) -> str:
        """
        Detect customer intent from message.

        Args:
            customer_message: Customer's message
            ai_response: AI's response

        Returns:
            Intent type string
        """
        message_lower = customer_message.lower()

        # Order lookup keywords
        order_keywords = [
            "order",
            "tracking",
            "track",
            "delivery",
            "shipped",
            "where is",
        ]
        if any(kw in message_lower for kw in order_keywords):
            return MessageIntent.ORDER_LOOKUP

        # Product inquiry keywords
        product_keywords = [
            "product",
            "buy",
            "purchase",
            "price",
            "cost",
            "sell",
            "have",
        ]
        if any(kw in message_lower for kw in product_keywords):
            return MessageIntent.PRODUCT_INQUIRY

        # Return/refund keywords
        return_keywords = ["return", "refund", "exchange", "cancel"]
        if any(kw in message_lower for kw in return_keywords):
            return MessageIntent.RETURN_REQUEST

        # Shipping keywords
        shipping_keywords = ["shipping", "ship", "deliver", "delivery time"]
        if any(kw in message_lower for kw in shipping_keywords):
            return MessageIntent.SHIPPING_QUESTION

        return MessageIntent.GENERAL_QUESTION

    def _extract_product_references(
        self, ai_response: str, products: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract product IDs referenced in AI response.

        Args:
            ai_response: AI's response text
            products: List of available products

        Returns:
            List of product UUIDs mentioned in response
        """
        referenced_ids = []
        response_lower = ai_response.lower()

        for product in products:
            product_name = product.get("name", "").lower()
            if product_name and product_name in response_lower:
                referenced_ids.append(product["id"])

        return referenced_ids[:5]  # Limit to 5 products


__all__ = ["GeminiService"]
