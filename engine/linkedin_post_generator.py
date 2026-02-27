"""
LinkedIn Post Generator
Uses Qwen AI to generate LinkedIn posts for business promotion
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PENDING_APPROVAL_FOLDER, DONE_FOLDER, ensure_folders_exist
from engine.ai_client import AIClient
from engine.logger import logger


class LinkedInPostGenerator:
    """
    Generates LinkedIn posts using Qwen AI
    """

    def __init__(self):
        """Initialize post generator"""
        self.ai_client = AIClient()
        logger.info("✅ LinkedIn post generator initialized")

    def generate_service_post(self, service_description: str, benefits: List[str]) -> str:
        """
        Generate a post promoting services

        Args:
            service_description: Description of service
            benefits: List of benefits

        Returns:
            Generated post content
        """
        try:
            logger.info("🤖 Generating service promotion post...")

            prompt = f"""Create a professional LinkedIn post promoting this service:

Service: {service_description}

Benefits:
{chr(10).join(f'- {b}' for b in benefits)}

Requirements:
- Professional but engaging tone
- Include relevant hashtags
- Call to action at the end
- Keep it under 200 words
- Use emojis sparingly (1-2 max)

Generate ONLY the post content, no explanations."""

            post_content = self.ai_client.generate_response(
                prompt,
                "You are a professional LinkedIn content creator."
            )

            logger.info("✅ Service post generated")
            return post_content.strip()

        except Exception as e:
            logger.error(f"❌ Error generating service post: {e}")
            return ""

    def generate_achievement_post(self, achievement: str, details: str) -> str:
        """
        Generate a post about an achievement

        Args:
            achievement: Main achievement
            details: Additional details

        Returns:
            Generated post content
        """
        try:
            logger.info("🤖 Generating achievement post...")

            prompt = f"""Create a LinkedIn post about this achievement:

Achievement: {achievement}

Details: {details}

Requirements:
- Celebrate the achievement professionally
- Show value delivered
- Include relevant hashtags
- Keep it authentic and humble
- Under 150 words

Generate ONLY the post content, no explanations."""

            post_content = self.ai_client.generate_response(
                prompt,
                "You are a professional LinkedIn content creator."
            )

            logger.info("✅ Achievement post generated")
            return post_content.strip()

        except Exception as e:
            logger.error(f"❌ Error generating achievement post: {e}")
            return ""

    def generate_insight_post(self, topic: str, key_points: List[str]) -> str:
        """
        Generate a thought leadership post

        Args:
            topic: Main topic
            key_points: Key insights

        Returns:
            Generated post content
        """
        try:
            logger.info("🤖 Generating insight post...")

            prompt = f"""Create a thought leadership LinkedIn post about:

Topic: {topic}

Key Points:
{chr(10).join(f'- {p}' for p in key_points)}

Requirements:
- Share valuable insights
- Professional and authoritative tone
- Encourage discussion
- Include relevant hashtags
- Under 200 words

Generate ONLY the post content, no explanations."""

            post_content = self.ai_client.generate_response(
                prompt,
                "You are a professional LinkedIn thought leader."
            )

            logger.info("✅ Insight post generated")
            return post_content.strip()

        except Exception as e:
            logger.error(f"❌ Error generating insight post: {e}")
            return ""

    def generate_from_recent_work(self) -> str:
        """
        Generate a post based on recent completed work

        Returns:
            Generated post content
        """
        try:
            logger.info("🤖 Analyzing recent work for post ideas...")

            # Get recent completed tasks
            done_files = sorted(
                DONE_FOLDER.glob("*.md"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:5]

            if not done_files:
                logger.warning("⚠️ No recent work found")
                return ""

            # Read recent tasks
            recent_work = []
            for file in done_files:
                try:
                    content = file.read_text(encoding='utf-8')
                    # Get first 200 chars as summary
                    summary = content[:200].replace('#', '').strip()
                    recent_work.append(summary)
                except:
                    continue

            if not recent_work:
                return ""

            prompt = f"""Based on these recent completed tasks, create a LinkedIn post that:
1. Highlights the value delivered
2. Demonstrates expertise
3. Attracts potential clients

Recent work:
{chr(10).join(f'- {w}' for w in recent_work)}

Requirements:
- Professional tone
- Focus on outcomes and value
- Include call to action
- Relevant hashtags
- Under 200 words

Generate ONLY the post content, no explanations."""

            post_content = self.ai_client.generate_response(
                prompt,
                "You are a professional LinkedIn content creator."
            )

            logger.info("✅ Post generated from recent work")
            return post_content.strip()

        except Exception as e:
            logger.error(f"❌ Error generating post from recent work: {e}")
            return ""

    def create_post_approval_request(
        self,
        content: str,
        post_type: str = "general",
        image_path: Optional[str] = None
    ) -> str:
        """
        Create a post approval request file

        Args:
            content: Post content
            post_type: Type of post
            image_path: Optional image path

        Returns:
            Path to approval file
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"LINKEDIN_POST_{post_type}_{timestamp}.md"

            approval_content = f"""# LinkedIn Post Approval Request

**Type:** {post_type.title()}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** ⏳ Pending Approval
**Image:** {image_path if image_path else 'None'}

## Post Content

{content}

## Instructions

**To Approve:** Move this file to the "Approved" folder
**To Reject:** Move this file to the "Rejected" folder
**To Edit:** Modify the content above, then move to "Approved"

## Notes

- This post will be published to your LinkedIn profile after approval
- You can edit the content above before approving
- The post will be published automatically when moved to Approved folder

---
*Generated by Qwen AI*
"""

            filepath = PENDING_APPROVAL_FOLDER / filename
            filepath.write_text(approval_content, encoding='utf-8')

            logger.info(f"✅ Post approval request created: {filename}")
            return str(filepath)

        except Exception as e:
            logger.error(f"❌ Error creating approval request: {e}")
            return ""

    def generate_weekly_post(self) -> bool:
        """
        Generate a weekly summary post

        Returns:
            True if post was created
        """
        try:
            logger.info("📅 Generating weekly summary post...")

            post_content = self.generate_from_recent_work()

            if post_content:
                self.create_post_approval_request(
                    post_content,
                    post_type="weekly_summary"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Error generating weekly post: {e}")
            return False


# Example usage functions
def create_service_post():
    """Example: Create a service promotion post"""
    generator = LinkedInPostGenerator()

    service = "AI automation and business process optimization"
    benefits = [
        "Save 10+ hours per week on repetitive tasks",
        "Reduce operational costs by 40%",
        "24/7 automated monitoring and responses",
        "Seamless integration with existing tools"
    ]

    content = generator.generate_service_post(service, benefits)

    if content:
        generator.create_post_approval_request(content, "service_promotion")
        print("✅ Service post created! Check Pending Approval folder.")
    else:
        print("❌ Failed to generate post")


def create_achievement_post():
    """Example: Create an achievement post"""
    generator = LinkedInPostGenerator()

    achievement = "Successfully automated 50+ business processes for clients"
    details = "Helped businesses save over 500 hours per month through intelligent automation"

    content = generator.generate_achievement_post(achievement, details)

    if content:
        generator.create_post_approval_request(content, "achievement")
        print("✅ Achievement post created! Check Pending Approval folder.")
    else:
        print("❌ Failed to generate post")


def create_weekly_summary():
    """Example: Create weekly summary post"""
    generator = LinkedInPostGenerator()

    if generator.generate_weekly_post():
        print("✅ Weekly summary post created! Check Pending Approval folder.")
    else:
        print("❌ Failed to generate weekly post")


if __name__ == "__main__":
    ensure_folders_exist()

    print("=" * 60)
    print("🤖 LINKEDIN POST GENERATOR")
    print("=" * 60)
    print()
    print("Choose an option:")
    print("1. Generate service promotion post")
    print("2. Generate achievement post")
    print("3. Generate weekly summary post")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        create_service_post()
    elif choice == "2":
        create_achievement_post()
    elif choice == "3":
        create_weekly_summary()
    else:
        print("Invalid choice")
