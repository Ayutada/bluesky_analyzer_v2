from pydantic import BaseModel, Field


class ProfileInfo(BaseModel):
    handle: str = Field(description="Profile handle ...")
    display_name: str = Field(description="Profile display name ...")
    description: str = Field(description="Profile description ...")
    avatar: str = Field(description="Profile avatar")


class PostFeed(BaseModel):
    post: dict = Field(description="Post")
    record: dict = Field(description="Record")
    text: str = Field(description="Text")


class ProfileResult(BaseModel):
    profile: ProfileInfo = Field(description="Profile information")
    posts: list[PostFeed] = Field(description="List of post feeds")

    @property
    def full_text_for_analysis(self) -> str:
        posts_text = "\n".join(post.text for post in self.posts)
        return f"User Description:\n{self.profile.description}\n\nRecent Posts:\n{posts_text}"
