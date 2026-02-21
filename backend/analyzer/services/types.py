from typing import Optional

from pydantic import BaseModel, Field


class ActorBasic(BaseModel):
    did: str = Field(default="", description="Actor DID")
    handle: str = Field(description="Actor handle")
    display_name: Optional[str] = Field(default=None, description="Actor display name")
    avatar: Optional[str] = Field(default=None, description="Actor avatar URL")


class ProfileInfo(BaseModel):
    handle: str = Field(description="Profile handle ...")
    display_name: str = Field(description="Profile display name ...")
    description: str = Field(description="Profile description ...")
    avatar: str = Field(description="Profile avatar")


class PostFeed(BaseModel):
    post: dict = Field(description="Post")
    record: dict = Field(description="Record")
    text: str = Field(description="Text")


class PersonalityAnalysis(BaseModel):
    mbti: str = Field(description="Inferred MBTI type, e.g. INTJ")
    animal: str = Field(description="Inferred Spirit Animal figure, e.g. Black Panther")
    description: str = Field(description="Brief personality portrait description, about 200-300 words")


class ProfileResult(BaseModel):
    profile: ProfileInfo = Field(description="Profile information")
    posts: list[PostFeed] = Field(description="List of post feeds")

    @property
    def full_text_for_analysis(self) -> str:
        posts_text = "\n".join(post.text for post in self.posts)
        return f"User Description:\n{self.profile.description}\n\nRecent Posts:\n{posts_text}"
