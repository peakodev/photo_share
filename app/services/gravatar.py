from libgravatar import Gravatar


async def get_gravatar(email: str) -> str:
    g = Gravatar(email)
    return g.get_image()