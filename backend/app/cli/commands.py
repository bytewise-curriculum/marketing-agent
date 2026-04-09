import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(name="agent", help="Marketing AI Agent CLI")
console = Console()

generate_app = typer.Typer(help="Generate marketing content")
blast_app = typer.Typer(help="Send email/SMS blasts")
app.add_typer(generate_app, name="generate")
app.add_typer(blast_app, name="blast")


def get_db():
    from app.models.database import SessionLocal
    return SessionLocal()


# === Generate Commands ===

@generate_app.command("social")
def generate_social(
    platform: str = typer.Option(..., help="Platform: twitter, instagram, linkedin, facebook, tiktok"),
    topic: str = typer.Option(..., help="Topic for the post"),
    tone: str = typer.Option("professional", help="Tone: professional, casual, humorous, urgent"),
    image: bool = typer.Option(False, help="Also generate an image"),
    provider: str = typer.Option(None, help="LLM provider override"),
):
    """Generate a social media post."""
    from app.services.social_media import create_social_post

    db = get_db()
    try:
        with console.status(f"Generating {platform} post..."):
            content = asyncio.run(create_social_post(
                db=db, platform=platform, topic=topic, tone=tone,
                generate_image=image, llm_provider=provider,
            ))
        console.print(Panel(content.body, title=f"[bold]{content.title}[/bold]", border_style="green"))
        if content.metadata_ and content.metadata_.get("image_url"):
            console.print(f"[blue]Image URL:[/blue] {content.metadata_['image_url']}")
        console.print(f"[dim]ID: {content.id} | Provider: {content.llm_provider}[/dim]")
    finally:
        db.close()


@generate_app.command("newsletter")
def generate_newsletter(
    topic: str = typer.Option(..., help="Newsletter topic"),
    sections: int = typer.Option(3, help="Number of sections"),
    audience: str = typer.Option("general", help="Target audience"),
    tone: str = typer.Option("professional", help="Tone"),
    provider: str = typer.Option(None, help="LLM provider override"),
):
    """Generate a newsletter."""
    from app.services.newsletter import create_newsletter

    db = get_db()
    try:
        with console.status("Generating newsletter..."):
            content = asyncio.run(create_newsletter(
                db=db, topic=topic, sections=sections, audience=audience,
                tone=tone, llm_provider=provider,
            ))
        console.print(Panel(content.body[:2000], title=f"[bold]{content.title}[/bold]", border_style="blue"))
        console.print(f"[dim]ID: {content.id} | Provider: {content.llm_provider}[/dim]")
    finally:
        db.close()


@generate_app.command("video")
def generate_video(
    topic: str = typer.Option(..., help="Video topic"),
    duration: int = typer.Option(60, help="Duration in seconds"),
    style: str = typer.Option("educational", help="Style: educational, promotional, storytelling"),
    provider: str = typer.Option(None, help="LLM provider override"),
):
    """Generate a video script."""
    from app.services.video import create_video_script

    db = get_db()
    try:
        with console.status("Generating video script..."):
            content = asyncio.run(create_video_script(
                db=db, topic=topic, duration=duration, style=style, llm_provider=provider,
            ))
        console.print(Panel(content.body, title=f"[bold]{content.title}[/bold]", border_style="magenta"))
        console.print(f"[dim]ID: {content.id} | Provider: {content.llm_provider}[/dim]")
    finally:
        db.close()


@generate_app.command("short-video")
def generate_short_video(
    topic: str = typer.Option(..., help="Video topic"),
    platform: str = typer.Option("tiktok", help="Platform: tiktok, reels, shorts"),
    duration: int = typer.Option(30, help="Duration in seconds (max 60)"),
    style: str = typer.Option("trendy", help="Style"),
    provider: str = typer.Option(None, help="LLM provider override"),
):
    """Generate a short-form video script."""
    from app.services.video import create_short_video_script

    db = get_db()
    try:
        with console.status("Generating short video script..."):
            content = asyncio.run(create_short_video_script(
                db=db, topic=topic, platform=platform, duration=duration,
                style=style, llm_provider=provider,
            ))
        console.print(Panel(content.body, title=f"[bold]{content.title}[/bold]", border_style="yellow"))
        console.print(f"[dim]ID: {content.id} | Provider: {content.llm_provider}[/dim]")
    finally:
        db.close()


# === Blast Commands ===

@blast_app.command("email")
def blast_email(
    name: str = typer.Option(..., help="Campaign name"),
    topic: str = typer.Option(..., help="Email topic"),
    list_id: int = typer.Option(None, help="Contact list ID"),
    send: bool = typer.Option(False, "--send", help="Actually send (default is draft only)"),
    provider: str = typer.Option(None, help="LLM provider override"),
):
    """Create and optionally send an email blast."""
    from app.services.email_blast import create_and_send_email_blast

    db = get_db()
    try:
        with console.status("Creating email campaign..."):
            campaign = asyncio.run(create_and_send_email_blast(
                db=db, name=name, topic=topic, list_id=list_id,
                send_now=send, llm_provider=provider,
            ))
        status_color = "green" if campaign.status == "sent" else "yellow"
        console.print(f"[{status_color}]Campaign '{campaign.name}' — {campaign.status}[/{status_color}]")
        console.print(f"Recipients: {campaign.recipient_count}")
        console.print(f"[dim]ID: {campaign.id}[/dim]")
    finally:
        db.close()


@blast_app.command("sms")
def blast_sms(
    name: str = typer.Option(..., help="Campaign name"),
    message: str = typer.Option(..., help="SMS message"),
    list_id: int = typer.Option(None, help="Contact list ID"),
    send: bool = typer.Option(False, "--send", help="Actually send"),
):
    """Create and optionally send an SMS blast."""
    from app.services.sms_blast import create_and_send_sms_blast

    db = get_db()
    try:
        with console.status("Creating SMS campaign..."):
            campaign = asyncio.run(create_and_send_sms_blast(
                db=db, name=name, message=message, list_id=list_id, send_now=send,
            ))
        status_color = "green" if campaign.status == "sent" else "yellow"
        console.print(f"[{status_color}]Campaign '{campaign.name}' — {campaign.status}[/{status_color}]")
        console.print(f"Recipients: {campaign.recipient_count}")
        console.print(f"[dim]ID: {campaign.id}[/dim]")
    finally:
        db.close()


# === Feedback Command ===

@app.command("feedback")
def submit_feedback(
    content_id: int = typer.Option(..., help="Content ID to rate"),
    rating: int = typer.Option(..., help="Rating 1-5"),
    comment: str = typer.Option("", help="Feedback comment"),
):
    """Submit feedback on generated content."""
    from app.models.training import TrainingFeedback
    from app.models.content import Content

    db = get_db()
    try:
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            console.print("[red]Content not found[/red]")
            raise typer.Exit(1)

        feedback = TrainingFeedback(
            content_id=content_id,
            rating=rating,
            feedback_text=comment if comment else None,
            original_prompt=content.prompt_used,
        )
        db.add(feedback)
        db.commit()
        console.print(f"[green]Feedback submitted! Rating: {rating}/5[/green]")
    finally:
        db.close()


# === Providers Command ===

@app.command("providers")
def list_providers():
    """Show available providers."""
    from app.providers import registry

    providers = registry.list_providers()
    table = Table(title="Provider Status")
    table.add_column("Category", style="cyan")
    table.add_column("Active", style="green")
    table.add_column("Available", style="dim")

    for category, info in providers.items():
        table.add_row(category, info["active"], ", ".join(info["available"]))

    console.print(table)


# === List Content Command ===

@app.command("list")
def list_content(
    type: str = typer.Option(None, help="Filter by type"),
    limit: int = typer.Option(20, help="Max items"),
):
    """List generated content."""
    from app.models.content import Content

    db = get_db()
    try:
        query = db.query(Content)
        if type:
            query = query.filter(Content.type == type)
        items = query.order_by(Content.created_at.desc()).limit(limit).all()

        table = Table(title="Generated Content")
        table.add_column("ID", style="cyan")
        table.add_column("Type")
        table.add_column("Title")
        table.add_column("Platform")
        table.add_column("Provider", style="dim")
        table.add_column("Created")

        for c in items:
            table.add_row(
                str(c.id), c.type, (c.title or "")[:40],
                c.platform or "-", c.llm_provider or "-", str(c.created_at)[:16],
            )

        console.print(table)
    finally:
        db.close()


def main():
    from app.models.database import create_tables
    create_tables()
    app()


if __name__ == "__main__":
    main()
