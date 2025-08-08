from logging import getLogger
from django.db import models
from django.conf import settings
from django.core.files.images import ImageFile
from huggingface_hub import InferenceClient
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


class DerbyJersey(models.Model):
    name = models.ForeignKey(DerbyName, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(blank=True, null=True)
    image = models.ImageField(upload_to="jerseys/", blank=True, null=True)

    def __str__(self):
        return str(self.name)

    # If no image is provided, generate one using huggingface
    def save(self, *args, **kwargs):
        if not self.image:
            logger.info(
                f"No jersey image found for {self.name}. Generating one using Hugging Face..."
            )
            prompt = settings.JERSEY_IMAGE_PROMPT.format(name=self.name)
            logger.info(f"Prompt for image generation: {prompt}")
            try:
                client = InferenceClient(provider="auto", token=settings.HF_TOKEN)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                generated_image = client.text_to_image(
                    prompt,
                    model="black-forest-labs/FLUX.1-schnell",
                )
                generated_image.save(temp_file.name)
                self.image = ImageFile(temp_file, name=f"jersey_{self.name}.png")
                # Add prompt to metadata
                if not self.metadata:
                    self.metadata = {"prompt": prompt}
                else:
                    self.metadata["prompt"] = prompt
                logger.info(
                    f"Generated image for {self.name} saved to {temp_file.name}"
                )
            except Exception as e:
                logger.error(f"Error generating image for {self.name}: {e}")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Derby Jersey"
        verbose_name_plural = "Derby Jerseys"
        ordering = ["name"]
