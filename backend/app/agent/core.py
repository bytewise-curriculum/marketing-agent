from typing import Optional
from sqlalchemy.orm import Session
from app.providers import registry
from app.agent.prompts import DEFAULT_PROMPTS
from app.agent.training import get_feedback_context
from app.models.content import Content
from app.models.training import PromptTemplate


class MarketingAgent:
    def __init__(self, db: Session, llm_provider: str | None = None):
        self.db = db
        self.llm = registry.get_llm(llm_provider)

    def _get_prompt_template(self, content_type: str) -> str:
        template = (
            self.db.query(PromptTemplate)
            .filter(PromptTemplate.type == content_type, PromptTemplate.is_active == True)
            .order_by(PromptTemplate.version.desc())
            .first()
        )
        if template:
            return template.template_text
        default = DEFAULT_PROMPTS.get(content_type)
        if default:
            return default["template"]
        raise ValueError(f"No prompt template found for type: {content_type}")

    async def generate_social_post(
        self,
        platform: str,
        topic: str,
        tone: str = "professional",
        max_length: int = 280,
    ) -> Content:
        template = self._get_prompt_template("social_post")
        feedback_context = get_feedback_context(self.db, "social_post")

        prompt = template.format(
            platform=platform,
            topic=topic,
            tone=tone,
            max_length=max_length,
            feedback_context=feedback_context,
        )

        response = await self.llm.generate(prompt)

        content = Content(
            type="social_post",
            title=f"{platform} post: {topic[:50]}",
            body=response.text,
            platform=platform,
            prompt_used=prompt,
            llm_provider=self.llm.name,
            metadata_={"tone": tone, "model": response.model},
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    async def generate_newsletter(
        self,
        topic: str,
        sections: int = 3,
        audience: str = "general",
        tone: str = "professional",
    ) -> Content:
        template = self._get_prompt_template("newsletter")
        feedback_context = get_feedback_context(self.db, "newsletter")

        prompt = template.format(
            topic=topic,
            sections=sections,
            audience=audience,
            tone=tone,
            feedback_context=feedback_context,
        )

        response = await self.llm.generate(prompt, max_tokens=8192)

        body = response.text
        subject = ""
        if "SUBJECT:" in body:
            parts = body.split("---", 1)
            subject = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip() if len(parts) > 1 else body

        content = Content(
            type="newsletter",
            title=subject or f"Newsletter: {topic[:50]}",
            body=body,
            prompt_used=prompt,
            llm_provider=self.llm.name,
            metadata_={"sections": sections, "audience": audience, "subject": subject, "model": response.model},
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    async def generate_video_script(
        self,
        topic: str,
        duration: int = 60,
        style: str = "educational",
        audience: str = "general",
    ) -> Content:
        template = self._get_prompt_template("video_script")
        feedback_context = get_feedback_context(self.db, "video_script")

        prompt = template.format(
            topic=topic,
            duration=duration,
            style=style,
            audience=audience,
            feedback_context=feedback_context,
        )

        response = await self.llm.generate(prompt, max_tokens=8192)

        content = Content(
            type="video_script",
            title=f"Video: {topic[:50]}",
            body=response.text,
            prompt_used=prompt,
            llm_provider=self.llm.name,
            metadata_={"duration": duration, "style": style, "model": response.model},
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    async def generate_short_video_script(
        self,
        topic: str,
        platform: str = "tiktok",
        duration: int = 30,
        style: str = "trendy",
    ) -> Content:
        template = self._get_prompt_template("short_video_script")
        feedback_context = get_feedback_context(self.db, "short_video_script")

        prompt = template.format(
            topic=topic,
            platform=platform,
            duration=min(duration, 60),
            style=style,
            feedback_context=feedback_context,
        )

        response = await self.llm.generate(prompt)

        content = Content(
            type="short_video_script",
            title=f"Short: {topic[:50]}",
            body=response.text,
            platform=platform,
            prompt_used=prompt,
            llm_provider=self.llm.name,
            metadata_={"duration": duration, "style": style, "model": response.model},
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    async def generate_email_content(
        self,
        topic: str,
        goal: str = "engagement",
        tone: str = "professional",
        audience: str = "subscribers",
    ) -> Content:
        template = self._get_prompt_template("email_blast")
        feedback_context = get_feedback_context(self.db, "email_blast")

        prompt = template.format(
            topic=topic,
            goal=goal,
            tone=tone,
            audience=audience,
            feedback_context=feedback_context,
        )

        response = await self.llm.generate(prompt, max_tokens=4096)

        body = response.text
        subject = ""
        preview = ""
        if "SUBJECT:" in body:
            lines = body.split("\n")
            for line in lines:
                if line.startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                elif line.startswith("PREVIEW:"):
                    preview = line.replace("PREVIEW:", "").strip()
            if "---" in body:
                body = body.split("---", 1)[1].strip()

        content = Content(
            type="email_blast",
            title=subject or f"Email: {topic[:50]}",
            body=body,
            prompt_used=prompt,
            llm_provider=self.llm.name,
            metadata_={"subject": subject, "preview": preview, "goal": goal, "model": response.model},
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    async def generate_image_prompt(
        self,
        purpose: str,
        brand: str = "",
        style: str = "modern",
        platform: str = "general",
    ) -> str:
        template = self._get_prompt_template("image_prompt")
        feedback_context = get_feedback_context(self.db, "image_prompt")

        prompt = template.format(
            purpose=purpose,
            brand=brand,
            style=style,
            platform=platform,
            feedback_context=feedback_context,
        )

        response = await self.llm.generate(prompt)
        return response.text
