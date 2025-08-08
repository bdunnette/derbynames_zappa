from logging import getLogger
from pathlib import Path
from django.db import models
from django.conf import settings
from django.core.files.images import ImageFile
from huggingface_hub import InferenceClient
from zappa.asynchronous import task
import tempfile

logger = getLogger(__name__)


class DerbyName(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Derby Name"
        verbose_name_plural = "Derby Names"
        ordering = ["name"]


@task
def generate_jersey_image(jersey_id):
    try:
        jersey = DerbyJersey.objects.get(id=jersey_id)
        if jersey.image:
            logger.info(f"Jersey image for {jersey.name} already exists.")
        else:
            prompt = settings.JERSEY_IMAGE_PROMPT.format(name=jersey.name)
            logger.info(f"Prompt for image generation: {prompt}")
            client = InferenceClient(provider="auto", token=settings.HF_TOKEN)
            logger.info("Client created for image generation.")
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            logger.info(f"Temporary file created at {temp_file.name}")
            generated_image = client.text_to_image(
                prompt,
                model="black-forest-labs/FLUX.1-schnell",
            )
            logger.info(f"Generated image for {jersey.name}: {generated_image}")
            generated_image.save(temp_file.name)
            logger.info(f"Image saved to temporary file: {temp_file.name}")
            # Save the image to the model's image field
            jersey.image = ImageFile(temp_file, name=f"jersey_{jersey.name}.png")
            logger.info(f"Image for {jersey.name} saved to model: {jersey.image.url}")
            # Add prompt to metadata
            logger.info(f"Saving jersey {jersey.name} with generated image.")
            logger.info(f"Jersey {jersey.name} saved with generated image.")
            jersey.set_metadata("prompt", prompt)
            jersey.set_metadata("image_generation_attempted", True)
            jersey.save()
            if temp_file is not None:
                temp_path = Path(temp_file.name)
                if temp_path.exists():
                    logger.info(f"Temporary file at {temp_path} exists - deleting...")
                    temp_path.unlink()
        return jersey.image.url if jersey.image and hasattr(jersey.image, "url") else None
    except Exception as e:
        logger.error(f"Error generating jersey image: {e}")
        return None


class DerbyJersey(models.Model):
    name = models.ForeignKey(DerbyName, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(blank=True, null=True, default=lambda: {})
    image = models.ImageField(upload_to="jerseys/", blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def set_metadata(self, key, value):
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value

    def get_metadata(self, key, default=None):
        if self.metadata is not None:
            return self.metadata.get(key, default)
        return default

    # If no image is provided, generate one using huggingface
    def save(self, *args, **kwargs):
        # Check if image generation has already been attempted
        image_generation_attempted = self.get_metadata(
            "image_generation_attempted", False
        )
        if not self.image and not image_generation_attempted:
            # generate_jersey_image(self.id)
            logger.info(
                f"No jersey image found for {self.name}. Generating one using Hugging Face..."
            )
            task = generate_jersey_image(self.id)
            logger.info(f"Image generation task initiated for {self.name} - {task}")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Derby Jersey"
        verbose_name_plural = "Derby Jerseys"
        ordering = ["name"]
